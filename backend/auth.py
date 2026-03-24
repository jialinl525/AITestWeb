"""
Permission management based on user roles.

- If the request header includes X-User-Name, permissions are validated against the database user.
- If no username is provided, fall back to the legacy X-User-Role behavior.
"""
from typing import Optional, Dict, Any

from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session

from database import get_db
import models

VALID_ROLES = {"manager", "viewer"}


def _normalize_role(role: Optional[str]) -> str:
    normalized = (role or "viewer").lower()
    return normalized if normalized in VALID_ROLES else "viewer"


def user_can_edit_test(user: models.User) -> bool:
    return _normalize_role(getattr(user, "role", None)) == "manager"


def get_request_identity(
    x_user_name: Optional[str] = Header(default=None, alias="X-User-Name"),
    x_user_role: Optional[str] = Header(default="viewer", alias="X-User-Role"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    fallback_role = _normalize_role(x_user_role)
    username = (x_user_name or "").strip().lower()

    if not username:
        return {
            "username": "",
            "role": fallback_role,
            "can_edit_test": fallback_role == "manager",
            "user": None,
        }

    user = (
        db.query(models.User)
        .filter(models.User.username == username, models.User.is_active.is_(True))
        .first()
    )
    if not user:
        return {
            "username": username,
            "role": "viewer",
            "can_edit_test": False,
            "user": None,
        }

    role = _normalize_role(user.role)
    can_edit = role == "manager"
    return {
        "username": user.username,
        "role": role,
        "can_edit_test": can_edit,
        "user": user,
    }


def get_user_role(identity: Dict[str, Any] = Depends(get_request_identity)) -> str:
    return identity["role"]


def require_manager(identity: Dict[str, Any] = Depends(get_request_identity)) -> Dict[str, Any]:
    if not identity.get("can_edit_test"):
        raise HTTPException(status_code=403, detail="Manager permission required")
    return identity


