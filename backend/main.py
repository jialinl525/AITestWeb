from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from database import Base, SessionLocal, engine
import models  # noqa: F401
from routers import test_progress, bugs, kpi, personnel, work_tasks
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
