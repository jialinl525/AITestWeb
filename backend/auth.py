"""
简单权限管理：通过 X-User-Role 请求头识别用户角色
manager: 可创建/修改测试进度和Bug
viewer: 只读
"""
from fastapi import HTTPException, Header, Depends
from typing import Optional

VALID_ROLES = {"manager", "viewer"}


def get_user_role(x_user_role: Optional[str] = Header(default="viewer", alias="X-User-Role")) -> str:
    """从请求头获取用户角色，默认为 viewer"""
    role = (x_user_role or "viewer").lower()
    if role not in VALID_ROLES:
        role = "viewer"
    return role


def require_manager(role: str = Depends(get_user_role)):
    """需要 manager 权限"""
    if role != "manager":
        raise HTTPException(status_code=403, detail="需要 manager 权限")
    return role


