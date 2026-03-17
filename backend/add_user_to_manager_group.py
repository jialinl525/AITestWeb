"""
Convenience script for adding a user to manager-group.

Usage:
    python add_user_to_manager_group.py <username> [--create-if-missing] [--display-name NAME] [--password PASSWORD] [--role viewer|manager] [--activate]

Examples:
    python add_user_to_manager_group.py alice
    python add_user_to_manager_group.py bob --create-if-missing --display-name Bob --password 123456
"""

from __future__ import annotations

import argparse
import sys

from database import Base, SessionLocal, engine
import models

MANAGER_GROUP_NAME = "manager-group"
MANAGER_GROUP_DESC = "Personnel group allowed to edit test progress and bugs"


def normalize_username(username: str) -> str:
    return (username or "").strip().lower()


def ensure_manager_group(db) -> models.PermissionGroup:
    group = db.query(models.PermissionGroup).filter(models.PermissionGroup.name == MANAGER_GROUP_NAME).first()
    if group:
        if not group.can_edit_test:
            group.can_edit_test = True
            db.flush()
        return group

    group = models.PermissionGroup(
        name=MANAGER_GROUP_NAME,
        description=MANAGER_GROUP_DESC,
        can_edit_test=True,
    )
    db.add(group)
    db.flush()
    return group


def get_or_create_user(
    db,
    username: str,
    create_if_missing: bool,
    display_name: str,
    password: str,
    role: str,
) -> tuple[models.User, bool]:
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        return user, False

    if not create_if_missing:
        raise ValueError(
            f"User does not exist: {username}. Add --create-if-missing to create it automatically."
        )

    user = models.User(
        username=username,
        display_name=(display_name or username).strip(),
        password=password,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user, True


def ensure_membership(db, user_id: int, group_id: int) -> bool:
    exists = (
        db.query(models.UserGroupMembership)
        .filter(
            models.UserGroupMembership.user_id == user_id,
            models.UserGroupMembership.group_id == group_id,
        )
        .first()
    )
    if exists:
        return False

    db.add(models.UserGroupMembership(user_id=user_id, group_id=group_id))
    db.flush()
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Add a user to manager-group")
    parser.add_argument("username", help="Username, for example alice")
    parser.add_argument(
        "--create-if-missing",
        action="store_true",
        help="Create the user automatically when it does not exist",
    )
    parser.add_argument(
        "--display-name",
        default="",
        help="Display name for the created user (only valid with --create-if-missing)",
    )
    parser.add_argument(
        "--password",
        default="123456",
        help="Password for the created user (only valid with --create-if-missing)",
    )
    parser.add_argument(
        "--role",
        choices=["viewer", "manager"],
        default="viewer",
        help="Role for the created user (default: viewer)",
    )
    parser.add_argument(
        "--activate",
        action="store_true",
        help="Activate the user automatically if it already exists but is disabled",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    username = normalize_username(args.username)

    if not username:
        print("[ERROR] Username cannot be empty")
        return 1

    # Ensure the model tables exist, including users, permission_groups, and user_group_memberships.
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        group = ensure_manager_group(db)
        user, created = get_or_create_user(
            db=db,
            username=username,
            create_if_missing=args.create_if_missing,
            display_name=args.display_name,
            password=args.password,
            role=args.role,
        )

        if args.activate and not user.is_active:
            user.is_active = True
            db.flush()

        added = ensure_membership(db, user.id, group.id)

        db.commit()

        if created:
            print(f"[OK] User created: {user.username} ({user.display_name or user.username})")
        if added:
            print(f"[OK] Added user {user.username} to {MANAGER_GROUP_NAME}")
        else:
            print(f"[INFO] User {user.username} is already in {MANAGER_GROUP_NAME}")

        can_edit = (user.role or "").lower() == "manager" or group.can_edit_test
        print(f"[INFO] Current status: role={user.role}, is_active={user.is_active}, can_edit_test={can_edit}")
        return 0
    except Exception as exc:
        db.rollback()
        print(f"[ERROR] Operation failed: {exc}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
