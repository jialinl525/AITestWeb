from datetime import date
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_request_identity
from database import get_db

router = APIRouter()


def _require_primary_admin(identity: Dict):
    username = str(identity.get("username") or "").strip().lower()
    if username != "manager":
        raise HTTPException(status_code=403, detail="Only the admin account can view audit data")


def _resolve_day_range(
    day: Optional[date],
    start_date: Optional[date],
    end_date: Optional[date],
) -> tuple[date, date]:
    if day is not None:
        return day, day

    if start_date and end_date:
        if start_date > end_date:
            return end_date, start_date
        return start_date, end_date

    if start_date is not None:
        return start_date, start_date
    if end_date is not None:
        return end_date, end_date

    today = date.today()
    return today, today


@router.get("/daily-summary", response_model=List[schemas.AuditDailySummary])
def get_daily_summary(
    day: Optional[date] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    identity: Dict = Depends(get_request_identity),
):
    _require_primary_admin(identity)
    from_date, to_date = _resolve_day_range(day, start_date, end_date)

    rows = (
        db.query(
            models.ApiActivityLog.activity_date.label("day"),
            func.count(models.ApiActivityLog.id).label("total_access"),
            func.count(func.distinct(models.ApiActivityLog.client_ip)).label("unique_ips"),
            func.sum(case((models.ApiActivityLog.is_login_attempt.is_(True), 1), else_=0)).label("login_attempts"),
            func.sum(case((models.ApiActivityLog.is_login_success.is_(True), 1), else_=0)).label("login_success"),
            func.sum(case((models.ApiActivityLog.is_manager_write.is_(True), 1), else_=0)).label("manager_write_actions"),
        )
        .filter(
            models.ApiActivityLog.activity_date >= from_date,
            models.ApiActivityLog.activity_date <= to_date,
        )
        .group_by(models.ApiActivityLog.activity_date)
        .order_by(models.ApiActivityLog.activity_date.asc())
        .all()
    )

    result: List[schemas.AuditDailySummary] = []
    for row in rows:
        login_attempts = int(row.login_attempts or 0)
        login_success = int(row.login_success or 0)
        result.append(
            schemas.AuditDailySummary(
                day=row.day,
                total_access=int(row.total_access or 0),
                unique_ips=int(row.unique_ips or 0),
                login_attempts=login_attempts,
                login_success=login_success,
                login_failed=max(0, login_attempts - login_success),
                manager_write_actions=int(row.manager_write_actions or 0),
            )
        )

    return result


@router.get("/login-ip-stats", response_model=List[schemas.AuditLoginIpStat])
def get_login_ip_stats(
    day: date = Query(...),
    db: Session = Depends(get_db),
    identity: Dict = Depends(get_request_identity),
):
    _require_primary_admin(identity)
    rows = (
        db.query(
            models.ApiActivityLog.client_ip.label("client_ip"),
            func.count(models.ApiActivityLog.id).label("total_logins"),
            func.sum(case((models.ApiActivityLog.is_login_success.is_(True), 1), else_=0)).label("successful_logins"),
        )
        .filter(
            models.ApiActivityLog.activity_date == day,
            models.ApiActivityLog.is_login_attempt.is_(True),
        )
        .group_by(models.ApiActivityLog.client_ip)
        .order_by(func.count(models.ApiActivityLog.id).desc(), models.ApiActivityLog.client_ip.asc())
        .all()
    )

    result: List[schemas.AuditLoginIpStat] = []
    for row in rows:
        total = int(row.total_logins or 0)
        success = int(row.successful_logins or 0)
        result.append(
            schemas.AuditLoginIpStat(
                client_ip=row.client_ip or "",
                total_logins=total,
                successful_logins=success,
                failed_logins=max(0, total - success),
            )
        )
    return result


@router.get("/access-top", response_model=List[schemas.AuditAccessStat])
def get_access_top(
    day: date = Query(...),
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
    identity: Dict = Depends(get_request_identity),
):
    _require_primary_admin(identity)
    rows = (
        db.query(
            models.ApiActivityLog.method.label("method"),
            models.ApiActivityLog.path.label("path"),
            func.count(models.ApiActivityLog.id).label("access_count"),
        )
        .filter(models.ApiActivityLog.activity_date == day)
        .group_by(models.ApiActivityLog.method, models.ApiActivityLog.path)
        .order_by(func.count(models.ApiActivityLog.id).desc(), models.ApiActivityLog.path.asc())
        .limit(limit)
        .all()
    )

    return [
        schemas.AuditAccessStat(
            method=row.method or "",
            path=row.path or "",
            access_count=int(row.access_count or 0),
        )
        for row in rows
    ]


@router.get("/admin-actions", response_model=schemas.AuditAdminActionPage)
def get_admin_actions(
    day: date = Query(...),
    username: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    identity: Dict = Depends(get_request_identity),
):
    _require_primary_admin(identity)
    query = db.query(models.ApiActivityLog).filter(
        models.ApiActivityLog.activity_date == day,
        models.ApiActivityLog.is_manager_write.is_(True),
    )

    normalized_username = (username or "").strip().lower()
    if normalized_username:
        query = query.filter(func.lower(models.ApiActivityLog.username) == normalized_username)

    total = query.count()
    rows = query.order_by(models.ApiActivityLog.created_at.desc(), models.ApiActivityLog.id.desc()).offset(skip).limit(limit).all()

    return schemas.AuditAdminActionPage(
        total=total,
        items=[
            schemas.AuditAdminActionItem(
                id=row.id,
                created_at=row.created_at,
                username=row.username or "",
                client_ip=row.client_ip or "",
                method=row.method or "",
                path=row.path or "",
                status_code=int(row.status_code or 0),
                action_summary=row.action_summary or "",
                action_payload=row.action_payload or "",
            )
            for row in rows
        ],
    )
