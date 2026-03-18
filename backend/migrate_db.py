"""
Database migration script for adding new columns to the test_progress table.
Run with: python migrate_db.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "test_management.db")

NEW_COLUMNS = [
    ("fr_number", "TEXT DEFAULT ''"),
    ("description", "TEXT DEFAULT ''"),
    ("config_method", "TEXT DEFAULT ''"),
    ("l0_total_cases", "INTEGER DEFAULT 0"),
    ("l0_passed_cases", "INTEGER DEFAULT 0"),
    ("l0_failed_cases", "INTEGER DEFAULT 0"),
    ("l0_due_date", "DATE"),
    ("l2_total_cases", "INTEGER DEFAULT 0"),
    ("l2_passed_cases", "INTEGER DEFAULT 0"),
    ("l2_failed_cases", "INTEGER DEFAULT 0"),
    ("l2_due_date", "DATE"),
    ("l4_total_cases", "INTEGER DEFAULT 0"),
    ("l4_passed_cases", "INTEGER DEFAULT 0"),
    ("l4_failed_cases", "INTEGER DEFAULT 0"),
    ("l4_due_date", "DATE"),
    ("estimated_hours", "REAL DEFAULT 0"),
    ("start_date", "DATE"),
    ("completion_date", "DATE"),
    ("test_owners", "TEXT DEFAULT ''"),
    ("developers", "TEXT DEFAULT ''"),
]

KPI_NEW_COLUMNS = [
    ("model_category", "TEXT DEFAULT 'ASR'"),
    ("source", "TEXT DEFAULT ''"),
    ("model_size", "TEXT DEFAULT ''"),
    ("description", "TEXT DEFAULT ''"),
    ("test_platform", "TEXT DEFAULT ''"),
    ("test_version", "TEXT DEFAULT ''"),
    ("test_condition", "TEXT DEFAULT ''"),
]

BUG_NEW_COLUMNS = [
    ("work_task_id", "INTEGER"),
    ("external_cr_number", "TEXT"),
    ("created_by", "TEXT DEFAULT ''"),
    ("cr_created_on", "DATETIME"),
    ("software_image_integration_build", "TEXT DEFAULT ''"),
    ("available_images", "TEXT DEFAULT ''"),
]

def migrate():
    if not os.path.exists(DB_PATH):
        print("Database file does not exist. Run init_db.py first.")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(test_progress)")
    existing = {row[1] for row in cur.fetchall()}
    for col_name, col_def in NEW_COLUMNS:
        if col_name not in existing:
            try:
                cur.execute(f"ALTER TABLE test_progress ADD COLUMN {col_name} {col_def}")
                print(f"Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"Failed to add {col_name}: {e}")
        else:
            print(f"Column already exists: {col_name}")

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bugs'")
    bugs_exists = cur.fetchone() is not None
    if bugs_exists:
        cur.execute("PRAGMA table_info(bugs)")
        bug_existing = {row[1] for row in cur.fetchall()}
        for col_name, col_def in BUG_NEW_COLUMNS:
            if col_name not in bug_existing:
                try:
                    cur.execute(f"ALTER TABLE bugs ADD COLUMN {col_name} {col_def}")
                    print(f"Added bugs column: {col_name}")
                except sqlite3.OperationalError as e:
                    print(f"Failed to add bugs column {col_name}: {e}")
            else:
                print(f"bugs column already exists: {col_name}")
    else:
        print("bugs table does not exist. Skipping bug column backfill.")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            display_name TEXT DEFAULT '',
            password TEXT,
            role TEXT DEFAULT 'viewer',
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS ix_users_username ON users(username)")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS permission_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT DEFAULT '',
            can_edit_test BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS ix_permission_groups_name ON permission_groups(name)")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_group_memberships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, group_id),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(group_id) REFERENCES permission_groups(id) ON DELETE CASCADE
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS ix_user_group_memberships_user_id ON user_group_memberships(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_user_group_memberships_group_id ON user_group_memberships(group_id)")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS task_owner_allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_progress_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            allocated_hours REAL DEFAULT 0,
            part_description TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            UNIQUE(test_progress_id, user_id),
            FOREIGN KEY(test_progress_id) REFERENCES test_progress(id) ON DELETE CASCADE,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS ix_task_owner_allocations_test_progress_id ON task_owner_allocations(test_progress_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_task_owner_allocations_user_id ON task_owner_allocations(user_id)")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS work_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_key TEXT UNIQUE,
            task_type TEXT DEFAULT 'Other',
            task_name TEXT,
            task_summary TEXT DEFAULT '',
            task_detail TEXT DEFAULT '',
            start_date DATE,
            end_date DATE,
            estimated_hours REAL DEFAULT 0,
            status TEXT DEFAULT 'Planned',
            progress REAL DEFAULT 0,
            assignee_user_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY(assignee_user_id) REFERENCES users(id) ON DELETE SET NULL
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS ix_work_tasks_task_key ON work_tasks(task_key)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_work_tasks_task_type ON work_tasks(task_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_work_tasks_status ON work_tasks(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_work_tasks_assignee_user_id ON work_tasks(assignee_user_id)")

    cur.execute("PRAGMA table_info(work_tasks)")
    work_task_columns = {row[1] for row in cur.fetchall()}
    required_work_task_columns = {
        "task_summary": "TEXT DEFAULT ''",
        "task_detail": "TEXT DEFAULT ''",
        "estimated_hours": "REAL DEFAULT 0",
        "status": "TEXT DEFAULT 'Planned'",
        "progress": "REAL DEFAULT 0",
        "task_type": "TEXT DEFAULT 'Other'",
    }
    for col_name, col_def in required_work_task_columns.items():
        if col_name not in work_task_columns:
            try:
                cur.execute(f"ALTER TABLE work_tasks ADD COLUMN {col_name} {col_def}")
                print(f"work_tasks column added: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"Failed to add work_tasks column {col_name}: {e}")

    # Backfill progress based on status for old rows where progress is null/0.
    cur.execute(
        """
        UPDATE work_tasks
        SET progress = CASE
            WHEN LOWER(TRIM(COALESCE(status, ''))) = 'completed' THEN 100
            WHEN LOWER(TRIM(COALESCE(status, ''))) = 'in progress' THEN 50
            WHEN LOWER(TRIM(COALESCE(status, ''))) = 'paused' THEN 20
            ELSE 0
        END
        WHERE COALESCE(progress, 0) = 0
        """
    )

    cur.execute("PRAGMA table_info(task_owner_allocations)")
    allocation_columns = {row[1] for row in cur.fetchall()}
    if "part_description" not in allocation_columns:
        try:
            cur.execute("ALTER TABLE task_owner_allocations ADD COLUMN part_description TEXT DEFAULT ''")
            print("task_owner_allocations column added: part_description")
        except sqlite3.OperationalError as e:
            print(f"Failed to add task_owner_allocations.part_description: {e}")

    cur.execute("SELECT id FROM permission_groups WHERE name = ?", ("manager-group",))
    row = cur.fetchone()
    if row:
        group_id = row[0]
    else:
        cur.execute(
            "INSERT INTO permission_groups(name, description, can_edit_test) VALUES (?, ?, ?)",
            ("manager-group", "Personnel group allowed to edit test progress and bugs", 1),
        )
        group_id = cur.lastrowid

    cur.execute("SELECT id FROM users WHERE username = ?", ("manager",))
    row = cur.fetchone()
    if row:
        manager_user_id = row[0]
    else:
        cur.execute(
            "INSERT INTO users(username, display_name, password, role, is_active) VALUES (?, ?, ?, ?, ?)",
            ("manager", "Administrator", "123456", "manager", 1),
        )
        manager_user_id = cur.lastrowid

    cur.execute(
        "SELECT id FROM user_group_memberships WHERE user_id = ? AND group_id = ?",
        (manager_user_id, group_id),
    )
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO user_group_memberships(user_id, group_id) VALUES (?, ?)",
            (manager_user_id, group_id),
        )

    # Add new columns for the kpi_metrics table.
    cur.execute("PRAGMA table_info(kpi_metrics)")
    kpi_existing = {row[1] for row in cur.fetchall()}
    for col_name, col_def in KPI_NEW_COLUMNS:
        if col_name not in kpi_existing:
            try:
                cur.execute(f"ALTER TABLE kpi_metrics ADD COLUMN {col_name} {col_def}")
                print(f"kpi_metrics column added: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"Failed to add kpi_metrics column {col_name}: {e}")
        else:
            print(f"kpi_metrics column already exists: {col_name}")
    # Migrate legacy total_cases/passed_cases values into the L0 stage.
    cur.execute("UPDATE test_progress SET l0_total_cases=total_cases, l0_passed_cases=passed_cases WHERE l0_total_cases=0 AND total_cases>0")
    conn.commit()
    conn.close()
    print("Migration completed")

if __name__ == "__main__":
    migrate()
