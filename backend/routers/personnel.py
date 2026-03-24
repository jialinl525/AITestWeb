from typing import List, Dict, Tuple
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth import require_manager, user_can_edit_test, get_request_identity
from database import get_db

router = APIRouter()

DEFAULT_MANAGER_DISPLAY_NAME = "Administrator"
LEGACY_MANAGER_DISPLAY_NAME = "\u7ba1\u7406\u5458"
PROTECTED_USERNAMES = {"manager"}


def _normalize_username(username: str) -> str:
    return (username or "").strip().lower()


def _normalize_role(role: str) -> str:
    normalized = (role or "viewer").strip().lower()
    return normalized if normalized in {"manager", "viewer"} else "viewer"


def _is_protected_user(user: models.User) -> bool:
    return _normalize_username(user.username) in PROTECTED_USERNAMES


def _require_primary_manager(identity: Dict):
    username = _normalize_username(identity.get("username", ""))
    if username != "manager":
        raise HTTPException(status_code=403, detail="Only the admin account can manage personnel users")


def _can_manage_personnel_users(identity: Dict) -> bool:
    return _normalize_username(identity.get("username", "")) == "manager"


def _can_edit_user_profile(identity: Dict, user: models.User) -> bool:
    username = _normalize_username(identity.get("username", ""))
    if username == "manager":
        return True
    if not user_can_edit_test(user):
        return False
    return username == _normalize_username(user.username)


def _split_people(raw_names: str) -> List[str]:
    if not raw_names:
        return []
    normalized = raw_names.replace("\uff0c", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def bootstrap_security_data(db: Session):
    manager_user = db.query(models.User).filter(models.User.username == "manager").first()
    if not manager_user:
        manager_user = models.User(
            username="manager",
            display_name=DEFAULT_MANAGER_DISPLAY_NAME,
            password="123456",
            role="manager",
            is_active=True,
        )
        db.add(manager_user)
        db.flush()
    elif (manager_user.display_name or "").strip() in {"", LEGACY_MANAGER_DISPLAY_NAME}:
        manager_user.display_name = DEFAULT_MANAGER_DISPLAY_NAME

    db.commit()


def _get_user_query(db: Session):
    return db.query(models.User)


def _serialize_user(user: models.User) -> Dict:
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name or "",
        "email": user.email or "",
        "responsibilities": user.responsibilities or "",
        "specialty_tasks": user.specialty_tasks or "",
        "role": _normalize_role(user.role),
        "is_active": bool(user.is_active),
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "can_edit_test": user_can_edit_test(user),
    }


def _get_visible_users(db: Session, only_active: bool = True) -> List[models.User]:
    query = _get_user_query(db).filter(~models.User.username.in_(PROTECTED_USERNAMES))
    if only_active:
        query = query.filter(models.User.is_active.is_(True))
    return query.order_by(models.User.id.asc()).all()


def _is_administrator_user(user: models.User) -> bool:
    if _normalize_username(user.username) == "manager":
        return True
    return (user.display_name or "").strip().lower() == DEFAULT_MANAGER_DISPLAY_NAME.lower()


def _get_personnel_statistics_users(db: Session) -> List[models.User]:
    users = _get_user_query(db).filter(models.User.is_active.is_(True)).order_by(models.User.id.asc()).all()
    result = []
    for user in users:
        if _is_administrator_user(user):
            continue
        result.append(user)
    return result


def _get_task_period(task: models.TestProgress) -> Tuple[date, date]:
    stage_dates = [item for item in [task.l0_due_date, task.l2_due_date, task.l4_due_date] if item is not None]
    if not stage_dates:
        return None, None
    stage_dates.sort()
    return stage_dates[0], stage_dates[-1]


def _get_task_allocations_map(db: Session) -> Dict[int, List[models.TaskOwnerAllocation]]:
    rows = db.query(models.TaskOwnerAllocation).order_by(models.TaskOwnerAllocation.test_progress_id.asc()).all()
    allocation_map: Dict[int, List[models.TaskOwnerAllocation]] = {}
    for row in rows:
        allocation_map.setdefault(row.test_progress_id, []).append(row)
    return allocation_map


def _get_fallback_allocations(task: models.TestProgress, users: List[models.User]) -> List[Dict]:
    owners = _split_people(task.test_owners)
    owner_key = {item.strip().lower() for item in owners if item.strip()}
    if not owner_key:
        return []

    matched_ids: List[int] = []
    for user in users:
        display_name = (user.display_name or "").strip().lower()
        username = (user.username or "").strip().lower()
        if display_name in owner_key or username in owner_key:
            matched_ids.append(user.id)

    if not matched_ids:
        return []

    task_estimated_hours = round(max(0.0, float(task.estimated_hours or 0.0)), 2)
    split_hours = round(task_estimated_hours / len(matched_ids), 2) if matched_ids else 0.0
    return [
        {
            "user_id": uid,
            "allocated_hours": split_hours,
            "part_description": "",
        }
        for uid in matched_ids
    ]


def _get_task_allocations(
    task: models.TestProgress,
    users: List[models.User],
    allocation_map: Dict[int, List[models.TaskOwnerAllocation]],
) -> List[Dict]:
    visible_user_ids = {user.id for user in users}
    explicit_rows = allocation_map.get(task.id, [])
    explicit_allocations = [
        {
            "user_id": row.user_id,
            "allocated_hours": round(max(0.0, float(row.allocated_hours or 0.0)), 2),
            "part_description": (row.part_description or "").strip(),
        }
        for row in explicit_rows
        if row.user_id in visible_user_ids and float(row.allocated_hours or 0.0) > 0
    ]
    if explicit_allocations:
        return explicit_allocations
    return _get_fallback_allocations(task, users)


def _build_overlaps(tasks: List[Dict]) -> List[Dict]:
    test_tasks = [
        item
        for item in tasks
        if item.get("task_kind") == "test"
        and item.get("period_start")
        and item.get("period_end")
        and str(item.get("status") or "").strip().lower() != "completed"
    ]
    if len(test_tasks) < 2:
        return []

    boundary_dates = sorted(
        {item["period_start"] for item in test_tasks}
        | {item["period_end"] for item in test_tasks}
        | {(item["period_end"]).fromordinal(item["period_end"].toordinal() + 1) for item in test_tasks}
    )

    overlap_segments: List[Dict] = []
    for index in range(len(boundary_dates) - 1):
        segment_start = boundary_dates[index]
        next_boundary = boundary_dates[index + 1]
        segment_end = date.fromordinal(next_boundary.toordinal() - 1)
        if segment_start > segment_end:
            continue

        active_tasks = [
            item
            for item in test_tasks
            if item["period_start"] <= segment_start <= item["period_end"]
        ]
        if len(active_tasks) < 2:
            continue

        active_task_ids = sorted({int(item["id"]) for item in active_tasks})
        active_task_names = []
        overlap_tasks = []
        seen_names = set()
        seen_task_ids = set()
        for item in sorted(active_tasks, key=lambda task: (task["period_start"], task["period_end"], task["id"])):
            task_id = int(item["id"])
            task_name = item.get("task_label") or item.get("test_name") or ""
            if task_name not in seen_names:
                active_task_names.append(task_name)
                seen_names.add(task_name)
            if task_id not in seen_task_ids:
                overlap_tasks.append(
                    {
                        "id": task_id,
                        "fr_number": (item.get("fr_number") or "").strip(),
                        "task_name": (item.get("test_name") or item.get("task_label") or "").strip(),
                    }
                )
                seen_task_ids.add(task_id)

        signature = tuple(active_task_ids)
        if overlap_segments and tuple(overlap_segments[-1]["task_ids"]) == signature:
            overlap_segments[-1]["overlap_end"] = segment_end
            overlap_segments[-1]["overlap_days"] = (
                overlap_segments[-1]["overlap_end"] - overlap_segments[-1]["overlap_start"]
            ).days + 1
            continue

        overlap_segments.append(
            {
                "overlap_start": segment_start,
                "overlap_end": segment_end,
                "overlap_days": (segment_end - segment_start).days + 1,
                "concurrent_task_count": len(active_task_ids),
                "task_ids": active_task_ids,
                "task_names": active_task_names,
                "tasks": overlap_tasks,
            }
        )

    return overlap_segments


def _normalize_task_status(status: str) -> str:
    raw = (status or "").strip().lower()
    if raw in {"planning", "planned", "plan", "pending"}:
        return "Planning"
    if raw in {"in progress", "inprogress", "running", "ongoing"}:
        return "Inprogress"
    if raw in {"completed", "complete", "done"}:
        return "Completed"
    if raw in {"paused", "pause", "hold", "on hold"}:
        return "Paused"
    if raw in {"failed", "fail"}:
        return "Failed"
    return (status or "").strip()


def _get_work_task_progress(status: str) -> float:
    normalized = _normalize_task_status(status)
    mapping = {
        "Planning": 0.0,
        "Inprogress": 50.0,
        "Completed": 100.0,
        "Paused": 20.0,
        "Failed": 0.0,
    }
    return mapping.get(normalized, 0.0)


def _build_test_task_label(task: models.TestProgress) -> str:
    fr_number = (task.fr_number or "").strip()
    task_name = (task.test_name or "").strip()
    if fr_number and task_name:
        return f"{fr_number} | {task_name}"
    if fr_number:
        return fr_number
    if task_name:
        return task_name
    return f"Test #{task.id}"


def _build_work_task_label(task: models.WorkTask) -> str:
    task_name = (task.task_name or "").strip()
    if task_name:
        return task_name
    task_key = (task.task_key or "").strip()
    if task_key:
        return task_key
    return f"Task #{task.id}"


@router.post("/login", response_model=schemas.UserLoginResponse)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    username = _normalize_username(payload.username)
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    user = _get_user_query(db).filter(models.User.username == username, models.User.is_active.is_(True)).first()
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    serialized = _serialize_user(user)
    return {
        "id": serialized["id"],
        "username": serialized["username"],
        "display_name": serialized["display_name"],
        "role": serialized["role"],
        "can_edit_test": serialized["can_edit_test"],
    }


@router.post("/change-password")
def change_password(
    payload: schemas.PasswordChange,
    identity: Dict = Depends(get_request_identity),
    db: Session = Depends(get_db),
):
    current_user = identity.get("user")
    if current_user is None:
        raise HTTPException(status_code=401, detail="Please log in first")

    if not payload.new_password or len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")

    if current_user.password != payload.old_password:
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.password = payload.new_password
    db.commit()
    return {"message": "Password changed successfully"}


@router.get("/me", response_model=schemas.UserLoginResponse)
def get_me(identity: Dict = Depends(get_request_identity), db: Session = Depends(get_db)):
    user = identity.get("user")
    if user is None:
        raise HTTPException(status_code=401, detail="Not logged in")

    fresh_user = _get_user_query(db).filter(models.User.id == user.id, models.User.is_active.is_(True)).first()
    if not fresh_user:
        raise HTTPException(status_code=401, detail="User does not exist or has been disabled")

    serialized = _serialize_user(fresh_user)
    return {
        "id": serialized["id"],
        "username": serialized["username"],
        "display_name": serialized["display_name"],
        "role": serialized["role"],
        "can_edit_test": serialized["can_edit_test"],
    }


@router.get("/users", response_model=List[schemas.User])
def list_users(
    db: Session = Depends(get_db),
    identity: Dict = Depends(require_manager),
):
    _require_primary_manager(identity)
    users = (
        _get_user_query(db)
        .filter(~models.User.username.in_(PROTECTED_USERNAMES))
        .order_by(models.User.id.asc())
        .all()
    )
    return [_serialize_user(user) for user in users]


@router.post("/users", response_model=schemas.User)
def create_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
    identity: Dict = Depends(require_manager),
):
    _require_primary_manager(identity)
    username = _normalize_username(payload.username)
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    exists = db.query(models.User).filter(models.User.username == username).first()
    if exists:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = models.User(
        username=username,
        display_name=(payload.display_name or username).strip(),
        email=(payload.email or "").strip(),
        responsibilities=(payload.responsibilities or "").strip(),
        specialty_tasks=(payload.specialty_tasks or "").strip(),
        password=payload.password,
        role=_normalize_role(payload.role),
        is_active=payload.is_active,
    )
    db.add(user)
    db.commit()

    created_user = _get_user_query(db).filter(models.User.id == user.id).first()
    return _serialize_user(created_user)


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    identity: Dict = Depends(require_manager),
):
    user = _get_user_query(db).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    admin_account = _can_manage_personnel_users(identity)
    if _is_protected_user(user) and not admin_account:
        raise HTTPException(status_code=403, detail="Only the admin account can modify the admin profile")
    if not _can_edit_user_profile(identity, user):
        raise HTTPException(status_code=403, detail="You can only update your own profile")

    if payload.display_name is not None:
        user.display_name = payload.display_name.strip()
    if payload.email is not None:
        user.email = payload.email.strip()
    if payload.responsibilities is not None:
        user.responsibilities = payload.responsibilities.strip()
    if payload.specialty_tasks is not None:
        user.specialty_tasks = payload.specialty_tasks.strip()
    if payload.role is not None:
        if not admin_account:
            raise HTTPException(status_code=403, detail="Only the admin account can change roles")
        user.role = _normalize_role(payload.role)
    if payload.is_active is not None:
        if not admin_account:
            raise HTTPException(status_code=403, detail="Only the admin account can change activation status")
        user.is_active = payload.is_active
    if payload.password is not None:
        if not admin_account:
            raise HTTPException(status_code=403, detail="Use change password to update your password")
        user.password = payload.password

    db.commit()
    updated_user = _get_user_query(db).filter(models.User.id == user_id).first()
    return _serialize_user(updated_user)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    identity: Dict = Depends(require_manager),
):
    _require_primary_manager(identity)
    user = _get_user_query(db).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if _is_protected_user(user):
        raise HTTPException(status_code=403, detail="The default system administrator cannot be deleted")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.get("/members", response_model=List[schemas.User])
def list_members(db: Session = Depends(get_db)):
    users = _get_personnel_statistics_users(db)
    return [_serialize_user(user) for user in users]


@router.get("/task-allocations/{test_id}", response_model=schemas.TaskAllocationDetail)
def get_task_allocations(test_id: int, db: Session = Depends(get_db)):
    task = db.query(models.TestProgress).filter(models.TestProgress.id == test_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Test task not found")

    users = _get_visible_users(db, only_active=True)
    user_map = {user.id: user for user in users}
    allocation_map = _get_task_allocations_map(db)
    resolved_allocations = _get_task_allocations(task, users, allocation_map)

    allocations = []
    for item in resolved_allocations:
        uid = item["user_id"]
        hours = item["allocated_hours"]
        user = user_map.get(uid)
        if not user:
            continue
        allocations.append(
            {
                "user_id": user.id,
                "username": user.username,
                "display_name": user.display_name or user.username,
                "allocated_hours": round(max(0.0, hours), 2),
                "part_description": (item.get("part_description") or "").strip(),
            }
        )

    return {
        "test_id": task.id,
        "test_name": task.test_name,
        "total_estimated_hours": round(max(0.0, float(task.estimated_hours or 0.0)), 2),
        "allocations": allocations,
    }


@router.put("/task-allocations/{test_id}", response_model=schemas.TaskAllocationDetail)
def update_task_allocations(
    test_id: int,
    payload: schemas.TaskAllocationUpdate,
    db: Session = Depends(get_db),
    _: Dict = Depends(require_manager),
):
    task = db.query(models.TestProgress).filter(models.TestProgress.id == test_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Test task not found")

    if payload.allocations is None:
        raise HTTPException(status_code=400, detail="Allocation data cannot be empty")

    user_ids = [item.user_id for item in payload.allocations]
    if len(set(user_ids)) != len(user_ids):
        raise HTTPException(status_code=400, detail="Duplicate users in allocation")

    visible_users = _get_visible_users(db, only_active=True)
    visible_user_map = {user.id: user for user in visible_users}

    normalized = []
    for item in payload.allocations:
        if item.user_id not in visible_user_map:
            raise HTTPException(status_code=400, detail=f"Invalid user ID: {item.user_id}")
        hours = round(max(0.0, float(item.allocated_hours or 0.0)), 2)
        part_description = (item.part_description or "").strip()
        if hours > 0:
            normalized.append(
                {
                    "user_id": item.user_id,
                    "allocated_hours": hours,
                    "part_description": part_description,
                }
            )

    db.query(models.TaskOwnerAllocation).filter(models.TaskOwnerAllocation.test_progress_id == test_id).delete()
    for item in normalized:
        db.add(
            models.TaskOwnerAllocation(
                test_progress_id=test_id,
                user_id=item["user_id"],
                allocated_hours=item["allocated_hours"],
                part_description=item["part_description"],
            )
        )

    assigned_users = [visible_user_map[item["user_id"]] for item in normalized]
    task.estimated_hours = round(sum(item["allocated_hours"] for item in normalized), 2)
    task.test_owners = ",".join([(user.display_name or user.username).strip() for user in assigned_users])

    db.commit()
    return get_task_allocations(test_id, db)


@router.get("/workload", response_model=List[schemas.PersonnelWorkload])
def get_workload(db: Session = Depends(get_db)):
    users = _get_personnel_statistics_users(db)
    tasks = db.query(models.TestProgress).order_by(models.TestProgress.id.desc()).all()
    user_ids = [user.id for user in users]
    work_tasks = (
        db.query(models.WorkTask)
        .filter(models.WorkTask.assignee_user_id.in_(user_ids))
        .order_by(models.WorkTask.id.desc())
        .all()
        if user_ids
        else []
    )
    allocation_map = _get_task_allocations_map(db)

    workload_map: Dict[int, Dict] = {}
    for user in users:
        workload_map[user.id] = {
            "user_id": user.id,
            "username": user.username,
            "display_name": user.display_name or user.username,
            "email": user.email or "",
            "responsibilities": user.responsibilities or "",
            "specialty_tasks": user.specialty_tasks or "",
            "can_edit_test": user_can_edit_test(user),
            "task_count": 0,
            "test_task_count": 0,
            "other_task_count": 0,
            "total_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "total_estimated_hours": 0.0,
            "overlap_count": 0,
            "overlaps": [],
            "tasks": [],
        }

    for task in tasks:
        resolved_allocations = _get_task_allocations(task, users, allocation_map)
        if not resolved_allocations:
            continue
        failed_cases = int(task.failed_cases or 0)
        period_start, period_end = _get_task_period(task)

        for item in resolved_allocations:
            uid = item["user_id"]
            hours = item["allocated_hours"]
            row = workload_map[uid]
            task_label = _build_test_task_label(task)
            task_item = {
                "id": task.id,
                "task_kind": "test",
                "task_label": task_label,
                "fr_number": task.fr_number or "",
                "test_name": (task.test_name or "").strip() or task_label,
                "model_name": task.model_name,
                "status": _normalize_task_status(task.status),
                "progress": float(task.progress or 0.0),
                "estimated_hours": round(max(0.0, hours), 2),
                "start_date": task.l0_due_date,
                "end_date": task.l4_due_date,
                "total_cases": int(task.total_cases or 0),
                "passed_cases": int(task.passed_cases or 0),
                "failed_cases": failed_cases,
                "l0_due_date": task.l0_due_date,
                "l2_due_date": task.l2_due_date,
                "l4_due_date": task.l4_due_date,
                "period_start": period_start,
                "period_end": period_end,
                "part_description": (item.get("part_description") or "").strip(),
            }
            row["task_count"] += 1
            row["test_task_count"] += 1
            row["total_cases"] += int(task.total_cases or 0)
            row["passed_cases"] += int(task.passed_cases or 0)
            row["failed_cases"] += failed_cases
            row["total_estimated_hours"] = round(row["total_estimated_hours"] + task_item["estimated_hours"], 2)
            row["tasks"].append(task_item)

    for work_task in work_tasks:
        uid = work_task.assignee_user_id
        if uid not in workload_map:
            continue
        row = workload_map[uid]
        task_label = _build_work_task_label(work_task)
        task_item = {
            "id": work_task.id,
            "task_kind": "work_task",
            "task_label": task_label,
            "fr_number": "",
            "test_name": task_label,
            "model_name": work_task.task_type,
            "status": _normalize_task_status(work_task.status),
            "progress": float(work_task.progress) if work_task.progress is not None else _get_work_task_progress(work_task.status),
            "estimated_hours": round(max(0.0, float(work_task.estimated_hours or 0.0)), 2),
            "start_date": work_task.start_date,
            "end_date": work_task.end_date,
            "total_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "l0_due_date": None,
            "l2_due_date": None,
            "l4_due_date": None,
            "period_start": work_task.start_date,
            "period_end": work_task.end_date,
            "part_description": (work_task.task_summary or "").strip(),
        }
        row["task_count"] += 1
        row["other_task_count"] += 1
        row["total_estimated_hours"] = round(row["total_estimated_hours"] + task_item["estimated_hours"], 2)
        row["tasks"].append(task_item)

    for row in workload_map.values():
        row["tasks"].sort(key=lambda item: ((item["period_start"] or date.max), item["id"]))
        overlaps = _build_overlaps(row["tasks"])
        row["overlap_count"] = max([item.get("concurrent_task_count", 0) for item in overlaps], default=0)
        row["overlaps"] = overlaps

    return list(workload_map.values())


@router.get("/workload/{user_id}", response_model=schemas.PersonnelWorkload)
def get_workload_by_user(user_id: int, db: Session = Depends(get_db)):
    rows = get_workload(db)
    for row in rows:
        if int(row.get("user_id", 0)) == user_id:
            return row
    raise HTTPException(status_code=404, detail="Member not found")


@router.get("/summary", response_model=schemas.PersonnelSummary)
def get_personnel_summary(db: Session = Depends(get_db)):
    members = list_members(db)
    workload = get_workload(db)
    return {
        "members": members,
        "workload": workload,
    }
