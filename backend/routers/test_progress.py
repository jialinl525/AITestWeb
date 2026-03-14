from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from auth import get_user_role, require_manager
import schemas, models

router = APIRouter()


def _calc_totals_and_progress(data: dict) -> tuple:
    """从 L0/L2/L4 阶段计算总计和进度"""
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


@router.get("/", response_model=List[schemas.TestProgress])
def get_test_progress_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取测试进度列表"""
    progress_list = db.query(models.TestProgress).offset(skip).limit(limit).all()
    return progress_list

@router.get("/model/{model_name}", response_model=List[schemas.TestProgress])
def get_test_progress_by_model(model_name: str, db: Session = Depends(get_db)):
    """根据模型名称获取测试进度"""
    progress_list = db.query(models.TestProgress).filter(models.TestProgress.model_name == model_name).all()
    return progress_list

@router.get("/{test_id}", response_model=schemas.TestProgress)
def get_test_progress(test_id: int, db: Session = Depends(get_db)):
    """获取单个测试进度"""
    test_progress = db.query(models.TestProgress).filter(models.TestProgress.id == test_id).first()
    if not test_progress:
        raise HTTPException(status_code=404, detail="测试进度未找到")
    return test_progress

@router.get("/{test_id}/detail", response_model=schemas.TestProgressDetail)
def get_test_progress_detail(test_id: int, db: Session = Depends(get_db)):
    """获取测试任务详情（含关联Bug列表）"""
    test_progress = db.query(models.TestProgress).filter(models.TestProgress.id == test_id).first()
    if not test_progress:
        raise HTTPException(status_code=404, detail="测试进度未找到")
    return test_progress

@router.post("/", response_model=schemas.TestProgress)
def create_test_progress(
    test_progress: schemas.TestProgressCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_manager)
):
    """创建新的测试进度（需 manager 权限）"""
    data = test_progress.model_dump()
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
    """更新测试进度（需 manager 权限）"""
    db_test_progress = db.query(models.TestProgress).filter(models.TestProgress.id == test_id).first()
    if not db_test_progress:
        raise HTTPException(status_code=404, detail="测试进度未找到")
    
    for key, value in test_progress.model_dump().items():
        setattr(db_test_progress, key, value)
    data = test_progress.model_dump()
    total, passed, failed, progress = _calc_totals_and_progress(data)
    db_test_progress.total_cases = total
    db_test_progress.passed_cases = passed
    db_test_progress.failed_cases = failed
    db_test_progress.progress = progress
    
    db.commit()
    db.refresh(db_test_progress)
    return db_test_progress
