from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database import get_db
from auth import require_manager
import schemas, models

router = APIRouter()

TEST_STATUS_ALIASES = {
    "pending": "Planning",
    "plan": "Planning",
    "planned": "Planning",
    "planning": "Planning",
    "running": "Inprogress",
    "ongoing": "Inprogress",
    "in progress": "Inprogress",
    "inprogress": "Inprogress",
    "completed": "Completed",
    "complete": "Completed",
    "done": "Completed",
    "paused": "Paused",
    "pause": "Paused",
    "on hold": "Paused",
    "hold": "Paused",
    "failed": "Failed",
    "fail": "Failed",
}
TEST_STATUS_OPTIONS = {"Planning", "Inprogress", "Completed", "Paused", "Failed"}


def _normalize_status(status: Optional[str]) -> str:
    raw = (status or "").strip()
    normalized = TEST_STATUS_ALIASES.get(raw.lower(), raw)
    if normalized not in TEST_STATUS_OPTIONS:
        raise HTTPException(status_code=400, detail="Invalid test task status")
    return normalized


def _calc_totals_and_progress(data: dict) -> tuple:
    """Calculate totals and progress from the L0/L2/L4 stages."""
    data["estimated_hours"] = round(max(0.0, float(data.get("estimated_hours", 0) or 0)), 2)

    def normalize_stage(stage: str):
        total = max(0, int(data.get(f"{stage}_total_cases", 0) or 0))
        passed = max(0, int(data.get(f"{stage}_passed_cases", 0) or 0))
        passed = min(passed, total)

        failed_input = max(0, int(data.get(f"{stage}_failed_cases", 0) or 0))
        failed = min(failed_input, max(0, total - passed))

        data[f"{stage}_total_cases"] = total
        data[f"{stage}_passed_cases"] = passed
        data[f"{stage}_failed_cases"] = failed
        return total, passed, failed

    l0_t, l0_p, l0_f = normalize_stage("l0")
    l2_t, l2_p, l2_f = normalize_stage("l2")
    l4_t, l4_p, l4_f = normalize_stage("l4")

    total = l0_t + l2_t + l4_t
    passed = l0_p + l2_p + l4_p
    failed = l0_f + l2_f + l4_f
    progress = round(min(100, max(0, passed / total * 100)), 2) if total > 0 else 0.0
    return total, passed, max(0, failed), progress


def _apply_lifecycle_dates(data: dict, existing: Optional[models.TestProgress] = None) -> None:
    """Maintain independent lifecycle dates for start/completion without deriving from timestamps."""
    status = _normalize_status(data.get("status"))
    data["status"] = status
    today = date.today()

    current_start = existing.start_date if existing else None
    current_completion = existing.completion_date if existing else None

    start_date = data.get("start_date", current_start)
    completion_date = data.get("completion_date", current_completion)

    if status in {"Inprogress", "Completed"} and not start_date:
        start_date = today
    if status == "Completed" and not completion_date:
        completion_date = today

    data["start_date"] = start_date
    data["completion_date"] = completion_date


@router.get("/", response_model=List[schemas.TestProgress])
def get_test_progress_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get the test progress list."""
    progress_list = db.query(models.TestProgress).offset(skip).limit(limit).all()
    return progress_list

@router.get("/model/{model_name}", response_model=List[schemas.TestProgress])
def get_test_progress_by_model(model_name: str, db: Session = Depends(get_db)):
    """Get test progress records by model name."""
    progress_list = db.query(models.TestProgress).filter(models.TestProgress.model_name == model_name).all()
    return progress_list

@router.get("/{test_id}", response_model=schemas.TestProgress)
def get_test_progress(test_id: int, db: Session = Depends(get_db)):
    """Get a single test progress record."""
    test_progress = db.query(models.TestProgress).filter(models.TestProgress.id == test_id).first()
    if not test_progress:
        raise HTTPException(status_code=404, detail="Test progress not found")
    return test_progress

@router.get("/{test_id}/detail", response_model=schemas.TestProgressDetail)
def get_test_progress_detail(test_id: int, db: Session = Depends(get_db)):
    """Get test task details, including linked bugs."""
    test_progress = db.query(models.TestProgress).filter(models.TestProgress.id == test_id).first()
    if not test_progress:
        raise HTTPException(status_code=404, detail="Test progress not found")
    return test_progress

@router.post("/", response_model=schemas.TestProgress)
def create_test_progress(
    test_progress: schemas.TestProgressCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_manager)
):
    """Create a new test progress record. Manager permission is required."""
    data = test_progress.model_dump()
    _apply_lifecycle_dates(data)
    total, passed, failed, progress = _calc_totals_and_progress(data)
    data["total_cases"] = total
    data["passed_cases"] = passed
    data["failed_cases"] = failed
    data["progress"] = progress
    db_test_progress = models.TestProgress(**data)
    db.add(db_test_progress)
    db.commit()
    db.refresh(db_test_progress)
    return db_test_progress

@router.put("/{test_id}", response_model=schemas.TestProgress)
def update_test_progress(
    test_id: int,
    test_progress: schemas.TestProgressCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_manager)
):
    """Update a test progress record. Manager permission is required."""
    db_test_progress = db.query(models.TestProgress).filter(models.TestProgress.id == test_id).first()
    if not db_test_progress:
        raise HTTPException(status_code=404, detail="Test progress not found")
    
    data = test_progress.model_dump()
    _apply_lifecycle_dates(data, db_test_progress)

    for key, value in data.items():
        setattr(db_test_progress, key, value)
    total, passed, failed, progress = _calc_totals_and_progress(data)
    db_test_progress.total_cases = total
    db_test_progress.passed_cases = passed
    db_test_progress.failed_cases = failed
    db_test_progress.progress = progress
    
    db.commit()
    db.refresh(db_test_progress)
    return db_test_progress
