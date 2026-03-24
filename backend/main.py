import json
from datetime import date

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.orm import joinedload

from database import Base, SessionLocal, engine
import models  # noqa: F401
from auth import user_can_edit_test
from routers import test_progress, bugs, kpi, personnel, work_tasks, audit
from routers.personnel import bootstrap_security_data

app = FastAPI(title="Test Management System", version="1.0.0")

# Configure CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers.
app.include_router(test_progress.router, prefix="/api/test-progress", tags=["Test Progress"])
app.include_router(bugs.router, prefix="/api/bugs", tags=["Bug Tracking"])
app.include_router(kpi.router, prefix="/api/kpi", tags=["KPI Data"])
app.include_router(personnel.router, prefix="/api/personnel", tags=["Personnel Management"])
app.include_router(work_tasks.router, prefix="/api/work-tasks", tags=["Work Task Management"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])


WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
SENSITIVE_KEYS = {"password", "old_password", "new_password"}


def _truncate_text(value: str, max_len: int) -> str:
    text = value or ""
    if len(text) <= max_len:
        return text
    return f"{text[:max_len]}...(truncated)"


def _sanitize_payload(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            key_text = str(key).strip().lower()
            if key_text in SENSITIVE_KEYS:
                cleaned[key] = "***"
            else:
                cleaned[key] = _sanitize_payload(item)
        return cleaned

    if isinstance(value, list):
        return [_sanitize_payload(item) for item in value[:50]]

    if isinstance(value, str):
        return _truncate_text(value, 200)

    return value


def _extract_login_username(content_type: str, body: bytes) -> str:
    if "application/json" not in (content_type or "") or not body:
        return ""

    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return ""

    if not isinstance(payload, dict):
        return ""

    return str(payload.get("username") or "").strip().lower()


def _extract_payload_snapshot(content_type: str, body: bytes) -> str:
    if not body:
        return ""

    if "application/json" not in (content_type or ""):
        return ""

    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return _truncate_text(body.decode("utf-8", errors="replace"), 1200)

    sanitized = _sanitize_payload(payload)
    return _truncate_text(json.dumps(sanitized, ensure_ascii=False), 1200)


def _extract_client_ip(request: Request) -> str:
    x_forwarded_for = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    if x_forwarded_for:
        return x_forwarded_for
    if request.client and request.client.host:
        return request.client.host
    return ""


def _get_identity_from_header(db, header_username: str):
    username = (header_username or "").strip().lower()
    if not username:
        return "", "viewer", False

    user = db.query(models.User).filter(models.User.username == username, models.User.is_active.is_(True)).first()
    if not user:
        return username, "viewer", False

    can_edit = user_can_edit_test(user)
    role = "manager" if can_edit else ((user.role or "viewer").strip().lower() or "viewer")
    return user.username, role, can_edit


@app.middleware("http")
async def audit_request_activity(request: Request, call_next):
    path = request.url.path or ""
    method = (request.method or "").upper()
    should_log = path.startswith("/api/") and method != "OPTIONS"

    body = await request.body()

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    replayable_request = Request(request.scope, receive)
    response = None
    status_code = 500

    try:
        response = await call_next(replayable_request)
        status_code = response.status_code
    except Exception:
        status_code = 500
        raise
    finally:
        if should_log:
            db = SessionLocal()
            try:
                header_username = replayable_request.headers.get("X-User-Name")
                username, role, can_edit = _get_identity_from_header(db, header_username)
                content_type = replayable_request.headers.get("content-type", "")
                is_login_attempt = method == "POST" and path == "/api/personnel/login"

                if is_login_attempt and not username:
                    username = _extract_login_username(content_type, body)

                is_login_success = is_login_attempt and status_code < 400
                is_manager_write = method in WRITE_METHODS and status_code < 400 and can_edit

                if is_login_attempt:
                    action_summary = "LOGIN"
                elif is_manager_write:
                    action_summary = f"{method} {path}"
                else:
                    action_summary = f"{method} {path}"

                payload_snapshot = ""
                if is_login_attempt or is_manager_write:
                    payload_snapshot = _extract_payload_snapshot(content_type, body)

                db.add(
                    models.ApiActivityLog(
                        activity_date=date.today(),
                        username=username or "",
                        role=role or "viewer",
                        client_ip=_truncate_text(_extract_client_ip(replayable_request), 128),
                        method=method,
                        path=_truncate_text(path, 255),
                        query_string=_truncate_text(replayable_request.url.query or "", 500),
                        status_code=int(status_code or 0),
                        user_agent=_truncate_text(replayable_request.headers.get("user-agent", ""), 500),
                        is_login_attempt=is_login_attempt,
                        is_login_success=is_login_success,
                        is_manager_write=is_manager_write,
                        action_summary=_truncate_text(action_summary, 500),
                        action_payload=payload_snapshot,
                    )
                )
                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()

    return response


def _ensure_compat_columns():
    with engine.begin() as conn:
        inspector = inspect(conn)
        table_names = set(inspector.get_table_names())

        if "test_progress" in table_names:
            columns = {item["name"] for item in inspector.get_columns("test_progress")}
            if "estimated_hours" not in columns:
                conn.execute(text("ALTER TABLE test_progress ADD COLUMN estimated_hours FLOAT DEFAULT 0"))
            if "start_date" not in columns:
                conn.execute(text("ALTER TABLE test_progress ADD COLUMN start_date DATE"))
            if "completion_date" not in columns:
                conn.execute(text("ALTER TABLE test_progress ADD COLUMN completion_date DATE"))

        if "task_owner_allocations" in table_names:
            columns = {item["name"] for item in inspector.get_columns("task_owner_allocations")}
            if "part_description" not in columns:
                conn.execute(text("ALTER TABLE task_owner_allocations ADD COLUMN part_description TEXT DEFAULT ''"))

        if "bugs" in table_names:
            columns = {item["name"] for item in inspector.get_columns("bugs")}
            if "work_task_id" not in columns:
                conn.execute(text("ALTER TABLE bugs ADD COLUMN work_task_id INTEGER"))
            if "external_cr_number" not in columns:
                conn.execute(text("ALTER TABLE bugs ADD COLUMN external_cr_number TEXT"))
            if "created_by" not in columns:
                conn.execute(text("ALTER TABLE bugs ADD COLUMN created_by TEXT DEFAULT ''"))
            if "cr_created_on" not in columns:
                conn.execute(text("ALTER TABLE bugs ADD COLUMN cr_created_on DATETIME"))
            if "software_image_integration_build" not in columns:
                conn.execute(text("ALTER TABLE bugs ADD COLUMN software_image_integration_build TEXT DEFAULT ''"))
            if "available_images" not in columns:
                conn.execute(text("ALTER TABLE bugs ADD COLUMN available_images TEXT DEFAULT ''"))

        if "work_tasks" in table_names:
            columns = {item["name"] for item in inspector.get_columns("work_tasks")}
            if "task_summary" not in columns:
                conn.execute(text("ALTER TABLE work_tasks ADD COLUMN task_summary TEXT DEFAULT ''"))
            if "task_detail" not in columns:
                conn.execute(text("ALTER TABLE work_tasks ADD COLUMN task_detail TEXT DEFAULT ''"))
            if "estimated_hours" not in columns:
                conn.execute(text("ALTER TABLE work_tasks ADD COLUMN estimated_hours FLOAT DEFAULT 0"))
            if "status" not in columns:
                conn.execute(text("ALTER TABLE work_tasks ADD COLUMN status TEXT DEFAULT 'Planned'"))
            if "task_type" not in columns:
                conn.execute(text("ALTER TABLE work_tasks ADD COLUMN task_type TEXT DEFAULT 'Other'"))

        if "users" in table_names:
            columns = {item["name"] for item in inspector.get_columns("users")}
            if "email" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''"))
            if "responsibilities" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN responsibilities TEXT DEFAULT ''"))
            if "specialty_tasks" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN specialty_tasks TEXT DEFAULT ''"))


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    _ensure_compat_columns()
    db = SessionLocal()
    try:
        bootstrap_security_data(db)
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Test Management System API"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
