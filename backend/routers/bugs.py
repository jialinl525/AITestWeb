from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas, models
from database import get_db
from auth import require_manager

router = APIRouter()

@router.get("/", response_model=List[schemas.Bug])
def get_bugs_list(
    status: str = None,
    severity: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取Bug列表，支持按状态和严重程度筛选"""
    query = db.query(models.Bug)
    
    if status:
        query = query.filter(models.Bug.status == status)
    if severity:
        query = query.filter(models.Bug.severity == severity)
    
    bugs = query.offset(skip).limit(limit).all()
    return bugs

@router.get("/{bug_id}", response_model=schemas.Bug)
def get_bug(bug_id: int, db: Session = Depends(get_db)):
    """获取单个Bug详情"""
    bug = db.query(models.Bug).filter(models.Bug.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug未找到")
    return bug

@router.post("/", response_model=schemas.Bug)
def create_bug(bug: schemas.BugCreate, db: Session = Depends(get_db), _=Depends(require_manager)):
    """创建新的Bug（需 manager 权限）"""
    db_bug = models.Bug(**bug.model_dump())
    db.add(db_bug)
    db.commit()
    db.refresh(db_bug)
    return db_bug

@router.put("/{bug_id}", response_model=schemas.Bug)
def update_bug(bug_id: int, bug: schemas.BugBase, db: Session = Depends(get_db), _=Depends(require_manager)):
    """更新Bug信息（需 manager 权限）"""
    db_bug = db.query(models.Bug).filter(models.Bug.id == bug_id).first()
    if not db_bug:
        raise HTTPException(status_code=404, detail="Bug未找到")
    
    for key, value in bug.model_dump().items():
        setattr(db_bug, key, value)
    
    db.commit()
    db.refresh(db_bug)
    return db_bug

@router.delete("/{bug_id}")
def delete_bug(bug_id: int, db: Session = Depends(get_db), _=Depends(require_manager)):
    """删除Bug（需 manager 权限）"""
    db_bug = db.query(models.Bug).filter(models.Bug.id == bug_id).first()
    if not db_bug:
        raise HTTPException(status_code=404, detail="Bug未找到")
    
    db.delete(db_bug)
    db.commit()
    return {"message": "Bug已删除"}

@router.get("/test/{test_id}", response_model=List[schemas.Bug])
def get_bugs_by_test(test_id: int, db: Session = Depends(get_db)):
    """获取指定测试的Bug列表"""
    bugs = db.query(models.Bug).filter(models.Bug.test_progress_id == test_id).all()
    return bugs

@router.get("/stats/summary")
def get_bug_stats(db: Session = Depends(get_db)):
    """获取Bug统计信息"""
    total_bugs = db.query(models.Bug).count()
    open_bugs = db.query(models.Bug).filter(models.Bug.status == "open").count()
    in_progress_bugs = db.query(models.Bug).filter(models.Bug.status == "in_progress").count()
    resolved_bugs = db.query(models.Bug).filter(models.Bug.status == "resolved").count()
    
    critical_bugs = db.query(models.Bug).filter(models.Bug.severity == "critical").count()
    high_bugs = db.query(models.Bug).filter(models.Bug.severity == "high").count()
    medium_bugs = db.query(models.Bug).filter(models.Bug.severity == "medium").count()
    low_bugs = db.query(models.Bug).filter(models.Bug.severity == "low").count()
    
    return {
        "total": total_bugs,
        "by_status": {
            "open": open_bugs,
            "in_progress": in_progress_bugs,
            "resolved": resolved_bugs
        },
        "by_severity": {
            "critical": critical_bugs,
            "high": high_bugs,
            "medium": medium_bugs,
            "low": low_bugs
        }
    }
