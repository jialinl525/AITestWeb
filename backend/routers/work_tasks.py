from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import models
import schemas
from auth import require_manager
from database import get_db

router = APIRouter()

TASK_TYPE_ALIASES = {
    "Customer Support": "Customer Support",
    "\u5ba2\u6237\u652f\u6301": "Customer Support",
    "Automation Development": "Automation Development",
    "\u81ea\u52a8\u5316\u5f00\u53d1": "Automation Development",
    "Other": "Other",
    "\u5176\u5b83": "Other",
    "\u5176\u4ed6": "Other",
}
TASK_STATUS_ALIASES = {
    "Planned": "Planned",
    "\u8ba1\u5212": "Planned",
    "In Progress": "In Progress",
    "\u8fdb\u884c": "In Progress",
    "Completed": "Completed",
    "\u5b8c\u6210": "Completed",
    "Paused": "Paused",
    "\u6682\u505c": "Paused",
}
TASK_TYPE_OPTIONS = ["Customer Support", "Automation Development", "Other"]
TASK_STATUS_OPTIONS = ["Planned", "In Progress", "Completed", "Paused"]
TASK_TYPES = set(TASK_TYPE_OPTIONS)
TASK_STATUS = set(TASK_STATUS_OPTIONS)
PROTECTED_USERNAMES = {"manager"}


def _normalize_text(value: Optional[str]) -> str:
    return (value or "").strip()


def _normalize_hours(value: Optional[float]) -> float:
    return round(max(0.0, float(value or 0.0)), 2)


def _get_alias_variants(alias_map: Dict[str, str], canonical_value: str) -> List[str]:
    return [raw_value for raw_value, normalized_value in alias_map.items() if normalized_value == canonical_value]


def _validate_dates(start_date, end_date):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="End date cannot be earlier than start date")


def _validate_type(task_type: str) -> str:
    normalized = _normalize_text(task_type)
    canonical = TASK_TYPE_ALIASES.get(normalized)
    if canonical not in TASK_TYPES:
        raise HTTPException(status_code=400, detail="Invalid task type")
    return canonical


def _validate_status(status: str) -> str:
    normalized = _normalize_text(status)
    canonical = TASK_STATUS_ALIASES.get(normalized)
    if canonical not in TASK_STATUS:
        raise HTTPException(status_code=400, detail="Invalid task status")
    return canonical


def _resolve_assignee(db: Session, assignee_user_id: Optional[int]) -> Optional[models.User]:
    if assignee_user_id is None:
        return None

    user = (
        db.query(models.User)
        .filter(
            models.User.id == assignee_user_id,
            models.User.is_active.is_(True),
            ~models.User.username.in_(PROTECTED_USERNAMES),
        )
        .first()
    )
    if not user:
        raise HTTPException(status_code=400, detail="Invalid assignee")
    return user


def _serialize_task(task: models.WorkTask) -> Dict:
    assignee = task.assignee
    return {
        "id": task.id,
        "task_key": task.task_key,
        "task_type": TASK_TYPE_ALIASES.get(task.task_type, task.task_type),
        "task_name": task.task_name,
        "task_summary": task.task_summary or "",
        "task_detail": task.task_detail or "",
        "start_date": task.start_date,
        "end_date": task.end_date,
        "estimated_hours": round(max(0.0, float(task.estimated_hours or 0.0)), 2),
        "status": TASK_STATUS_ALIASES.get(task.status, task.status),
        "assignee_user_id": task.assignee_user_id,
        "assignee_username": assignee.username if assignee else None,
        "assignee_display_name": (assignee.display_name or assignee.username) if assignee else None,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.get("", response_model=List[schemas.WorkTask])
def list_work_tasks(
    task_type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    assignee_user_id: Optional[int] = Query(default=None),
    keyword: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(models.WorkTask).order_by(models.WorkTask.id.desc())

    if task_type:
        canonical_task_type = _validate_type(task_type)
        query = query.filter(models.WorkTask.task_type.in_(_get_alias_variants(TASK_TYPE_ALIASES, canonical_task_type)))
    if status:
        canonical_status = _validate_status(status)
        query = query.filter(models.WorkTask.status.in_(_get_alias_variants(TASK_STATUS_ALIASES, canonical_status)))
    if assignee_user_id is not None:
        query = query.filter(models.WorkTask.assignee_user_id == assignee_user_id)

    kw = _normalize_text(keyword)
    if kw:
        like_kw = f"%{kw}%"
        query = query.filter(
            models.WorkTask.task_key.like(like_kw)
            | models.WorkTask.task_name.like(like_kw)
            | models.WorkTask.task_summary.like(like_kw)
            | models.WorkTask.task_detail.like(like_kw)
        )

    rows = query.all()
    return [_serialize_task(row) for row in rows]


@router.post("", response_model=schemas.WorkTask)
def create_work_task(
    payload: schemas.WorkTaskCreate,
    db: Session = Depends(get_db),
    _: Dict = Depends(require_manager),
):
    task_key = _normalize_text(payload.task_key)
    task_name = _normalize_text(payload.task_name)
    if not task_key:
        raise HTTPException(status_code=400, detail="Task key cannot be empty")
    if not task_name:
        raise HTTPException(status_code=400, detail="Task name cannot be empty")

    duplicate = db.query(models.WorkTask.id).filter(models.WorkTask.task_key == task_key).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="Task key already exists")

    _validate_dates(payload.start_date, payload.end_date)
    assignee = _resolve_assignee(db, payload.assignee_user_id)

    row = models.WorkTask(
        task_key=task_key,
        task_type=_validate_type(payload.task_type),
        task_name=task_name,
        task_summary=_normalize_text(payload.task_summary),
        task_detail=_normalize_text(payload.task_detail),
        start_date=payload.start_date,
        end_date=payload.end_date,
        estimated_hours=_normalize_hours(payload.estimated_hours),
        status=_validate_status(payload.status),
        assignee_user_id=assignee.id if assignee else None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _serialize_task(row)


@router.put("/{task_id}", response_model=schemas.WorkTask)
def update_work_task(
    task_id: int,
    payload: schemas.WorkTaskUpdate,
    db: Session = Depends(get_db),
    _: Dict = Depends(require_manager),
):
    row = db.query(models.WorkTask).filter(models.WorkTask.id == task_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    patch = payload.dict(exclude_unset=True)

    if "task_key" in patch:
        new_key = _normalize_text(patch["task_key"])
        if not new_key:
            raise HTTPException(status_code=400, detail="Task key cannot be empty")
        duplicate = (
            db.query(models.WorkTask.id)
            .filter(models.WorkTask.task_key == new_key, models.WorkTask.id != task_id)
            .first()
        )
        if duplicate:
            raise HTTPException(status_code=400, detail="Task key already exists")
        row.task_key = new_key

    if "task_type" in patch:
        row.task_type = _validate_type(patch["task_type"])

    if "task_name" in patch:
        new_name = _normalize_text(patch["task_name"])
        if not new_name:
            raise HTTPException(status_code=400, detail="Task name cannot be empty")
        row.task_name = new_name

    if "task_summary" in patch:
        row.task_summary = _normalize_text(patch["task_summary"])

    if "task_detail" in patch:
        row.task_detail = _normalize_text(patch["task_detail"])

    if "estimated_hours" in patch:
        row.estimated_hours = _normalize_hours(patch["estimated_hours"])

    if "status" in patch:
        row.status = _validate_status(patch["status"])

    if "assignee_user_id" in patch:
        assignee = _resolve_assignee(db, patch["assignee_user_id"])
        row.assignee_user_id = assignee.id if assignee else None

    start_date = patch.get("start_date", row.start_date)
    end_date = patch.get("end_date", row.end_date)
    _validate_dates(start_date, end_date)
    if "start_date" in patch:
        row.start_date = patch["start_date"]
    if "end_date" in patch:
        row.end_date = patch["end_date"]

    db.commit()
    db.refresh(row)
    return _serialize_task(row)


@router.delete("/{task_id}")
def delete_work_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: Dict = Depends(require_manager),
):
    row = db.query(models.WorkTask).filter(models.WorkTask.id == task_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(row)
    db.commit()
    return {"message": "Deleted successfully"}


@router.get("/meta")
def get_work_task_meta():
    return {
        "task_types": TASK_TYPE_OPTIONS,
        "status_options": TASK_STATUS_OPTIONS,
    }
