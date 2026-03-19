from typing import List, Dict, Tuple
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from auth import require_manager, user_can_edit_test, get_request_identity
from database import get_db

router = APIRouter()

DEFAULT_MANAGER_GROUP = "manager-group"
DEFAULT_MANAGER_GROUP_DESC = "Personnel group allowed to edit test progress and bugs"
LEGACY_MANAGER_GROUP_DESC = "\u53ef\u7f16\u8f91\u6d4b\u8bd5\u8fdb\u5ea6\u4e0eBug\u7684\u4eba\u5458\u7ec4"
DEFAULT_MANAGER_DISPLAY_NAME = "Administrator"
LEGACY_MANAGER_DISPLAY_NAME = "\u7ba1\u7406\u5458"
DEFAULT_INTERNAL_GROUP = "internal-group"
DEFAULT_INTERNAL_GROUP_DESC = "Read-only internal visibility group"
DEFAULT_INTERNAL_DISPLAY_NAME = "Internal"
DEFAULT_INTERNAL_USERNAME = "internal"
DEFAULT_INTERNAL_PASSWORD = "qualcommvoiceai"
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
        raise HTTPException(status_code=403, detail="Only the manager account can edit personnel settings")


def _split_people(raw_names: str) -> List[str]:
    if not raw_names:
        return []
    normalized = raw_names.replace("\uff0c", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def bootstrap_security_data(db: Session):
    group = db.query(models.PermissionGroup).filter(models.PermissionGroup.name == DEFAULT_MANAGER_GROUP).first()
    if not group:
        group = models.PermissionGroup(
            name=DEFAULT_MANAGER_GROUP,
            description=DEFAULT_MANAGER_GROUP_DESC,
            can_edit_test=True,
        )
        db.add(group)
        db.flush()
    elif (group.description or "").strip() in {"", LEGACY_MANAGER_GROUP_DESC}:
        group.description = DEFAULT_MANAGER_GROUP_DESC

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

    exists = (
        db.query(models.UserGroupMembership)
        .filter(
            models.UserGroupMembership.user_id == manager_user.id,
            models.UserGroupMembership.group_id == group.id,
        )
        .first()
    )
    if not exists:
        db.add(models.UserGroupMembership(user_id=manager_user.id, group_id=group.id))

    internal_group = (
        db.query(models.PermissionGroup)
        .filter(models.PermissionGroup.name == DEFAULT_INTERNAL_GROUP)
        .first()
    )
    if not internal_group:
        internal_group = models.PermissionGroup(
            name=DEFAULT_INTERNAL_GROUP,
            description=DEFAULT_INTERNAL_GROUP_DESC,
            can_edit_test=False,
        )
        db.add(internal_group)
        db.flush()
    elif (internal_group.description or "").strip() == "":
        internal_group.description = DEFAULT_INTERNAL_GROUP_DESC

    internal_user = db.query(models.User).filter(models.User.username == DEFAULT_INTERNAL_USERNAME).first()
    if not internal_user:
        internal_user = models.User(
            username=DEFAULT_INTERNAL_USERNAME,
            display_name=DEFAULT_INTERNAL_DISPLAY_NAME,
            password=DEFAULT_INTERNAL_PASSWORD,
            role="viewer",
            is_active=True,
        )
        db.add(internal_user)
        db.flush()
    elif (internal_user.display_name or "").strip() == "":
        internal_user.display_name = DEFAULT_INTERNAL_DISPLAY_NAME

    internal_exists = (
        db.query(models.UserGroupMembership)
        .filter(
            models.UserGroupMembership.user_id == internal_user.id,
            models.UserGroupMembership.group_id == internal_group.id,
        )
        .first()
    )
    if not internal_exists:
        db.add(models.UserGroupMembership(user_id=internal_user.id, group_id=internal_group.id))

    db.commit()


def _get_user_query(db: Session):
    return db.query(models.User).options(
        joinedload(models.User.memberships).joinedload(models.UserGroupMembership.group)
    )


def _serialize_group(group: models.PermissionGroup) -> Dict:
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description or "",
        "can_edit_test": bool(group.can_edit_test),
        "created_at": group.created_at,
    }


def _serialize_user(user: models.User) -> Dict:
    groups = [m.group for m in user.memberships if m.group is not None]
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
        "groups": [_serialize_group(group) for group in groups],
        "can_edit_test": user_can_edit_test(user),
    }


def _replace_user_groups(db: Session, user_id: int, group_ids: List[int]):
    db.query(models.UserGroupMembership).filter(models.UserGroupMembership.user_id == user_id).delete()
    valid_ids = set()
    if group_ids:
        rows = db.query(models.PermissionGroup.id).filter(models.PermissionGroup.id.in_(group_ids)).all()
        valid_ids = {item[0] for item in rows}
    for gid in valid_ids:
        db.add(models.UserGroupMembership(user_id=user_id, group_id=gid))


def _get_visible_users(db: Session, only_active: bool = True) -> List[models.User]:
    query = _get_user_query(db).filter(~models.User.username.in_(PROTECTED_USERNAMES))
    if only_active:
        query = query.filter(models.User.is_active.is_(True))
    return query.order_by(models.User.id.asc()).all()


def _is_manager_group_member(user: models.User) -> bool:
    for membership in user.memberships:
        group = membership.group
        if not group:
            continue
        if (group.name or "").strip().lower() == DEFAULT_MANAGER_GROUP:
            return True
    return False


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
        if not _is_manager_group_member(user):
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
    overlaps: List[Dict] = []
    sized = [item for item in tasks if item.get("period_start") and item.get("period_end")]
    for i in range(len(sized)):
        for j in range(i + 1, len(sized)):
            first = sized[i]
            second = sized[j]
            overlap_start = max(first["period_start"], second["period_start"])
            overlap_end = min(first["period_end"], second["period_end"])
            if overlap_start <= overlap_end:
                overlaps.append(
                    {
                        "task_id_1": first["id"],
                        "task_name_1": first.get("task_label") or first.get("test_name") or "",
                        "task_id_2": second["id"],
                        "task_name_2": second.get("task_label") or second.get("test_name") or "",
                        "overlap_start": overlap_start,
                        "overlap_end": overlap_end,
                        "overlap_days": (overlap_end - overlap_start).days + 1,
                    }
                )
    return overlaps


def _get_work_task_progress(status: str) -> float:
    mapping = {
        "planned": 0.0,
        "in progress": 50.0,
        "completed": 100.0,
        "paused": 20.0,
    }
    return mapping.get((status or "").strip().lower(), 0.0)


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
        "groups": serialized["groups"],
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
        "groups": serialized["groups"],
    }


@router.get("/groups", response_model=List[schemas.PermissionGroup])
def list_groups(db: Session = Depends(get_db)):
    groups = db.query(models.PermissionGroup).order_by(models.PermissionGroup.id.asc()).all()
    return [_serialize_group(group) for group in groups]


@router.post("/groups", response_model=schemas.PermissionGroup)
def create_group(
    payload: schemas.PermissionGroupCreate,
    db: Session = Depends(get_db),
    identity: Dict = Depends(require_manager),
):
    _require_primary_manager(identity)
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Group name cannot be empty")

    exists = db.query(models.PermissionGroup).filter(models.PermissionGroup.name == name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Group name already exists")

    group = models.PermissionGroup(
        name=name,
        description=payload.description or "",
        can_edit_test=payload.can_edit_test,
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return _serialize_group(group)


@router.put("/groups/{group_id}", response_model=schemas.PermissionGroup)
def update_group(
    group_id: int,
    payload: schemas.PermissionGroupCreate,
    db: Session = Depends(get_db),
    identity: Dict = Depends(require_manager),
):
    _require_primary_manager(identity)
    group = db.query(models.PermissionGroup).filter(models.PermissionGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="User group not found")

    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Group name cannot be empty")

    duplicate = (
        db.query(models.PermissionGroup)
        .filter(models.PermissionGroup.name == name, models.PermissionGroup.id != group_id)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="Group name already exists")

    group.name = name
    group.description = payload.description or ""
    group.can_edit_test = payload.can_edit_test
    db.commit()
    db.refresh(group)
    return _serialize_group(group)


@router.get("/users", response_model=List[schemas.User])
def list_users(db: Session = Depends(get_db)):
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
    db.flush()
    _replace_user_groups(db, user.id, payload.group_ids)
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
    _require_primary_manager(identity)
    user = _get_user_query(db).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if _is_protected_user(user):
        raise HTTPException(status_code=403, detail="The default system administrator cannot be modified")

    if payload.display_name is not None:
        user.display_name = payload.display_name.strip()
    if payload.email is not None:
        user.email = payload.email.strip()
    if payload.responsibilities is not None:
        user.responsibilities = payload.responsibilities.strip()
    if payload.specialty_tasks is not None:
        user.specialty_tasks = payload.specialty_tasks.strip()
    if payload.role is not None:
        user.role = _normalize_role(payload.role)
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password is not None:
        user.password = payload.password
    if payload.group_ids is not None:
        _replace_user_groups(db, user.id, payload.group_ids)

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
                "status": task.status,
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
            "status": work_task.status,
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
        row["total_estimated_hours"] = round(row["total_estimated_hours"] + task_item["estimated_hours"], 2)
        row["tasks"].append(task_item)

    for row in workload_map.values():
        row["tasks"].sort(key=lambda item: ((item["period_start"] or date.max), item["id"]))
        overlaps = _build_overlaps(row["tasks"])
        row["overlap_count"] = len(overlaps)
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
