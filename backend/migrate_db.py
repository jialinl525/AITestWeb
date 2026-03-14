"""
数据库迁移脚本：为 test_progress 表添加新字段
运行: python migrate_db.py
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
    ("test_owners", "TEXT DEFAULT ''"),
    ("developers", "TEXT DEFAULT ''"),
]

KPI_NEW_COLUMNS = [
    ("model_category", "TEXT DEFAULT 'ASR'"),
    ("source", "TEXT DEFAULT ''"),
    ("model_size", "TEXT DEFAULT ''"),
    ("description", "TEXT DEFAULT ''"),
]

def migrate():
    if not os.path.exists(DB_PATH):
        print("数据库文件不存在，请先运行 init_db.py")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(test_progress)")
    existing = {row[1] for row in cur.fetchall()}
    for col_name, col_def in NEW_COLUMNS:
        if col_name not in existing:
            try:
                cur.execute(f"ALTER TABLE test_progress ADD COLUMN {col_name} {col_def}")
                print(f"已添加列: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"添加 {col_name} 失败: {e}")
        else:
            print(f"列已存在: {col_name}")

    # kpi_metrics 表新增字段
    cur.execute("PRAGMA table_info(kpi_metrics)")
    kpi_existing = {row[1] for row in cur.fetchall()}
    for col_name, col_def in KPI_NEW_COLUMNS:
        if col_name not in kpi_existing:
            try:
                cur.execute(f"ALTER TABLE kpi_metrics ADD COLUMN {col_name} {col_def}")
                print(f"kpi_metrics 已添加列: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"kpi_metrics 添加 {col_name} 失败: {e}")
        else:
            print(f"kpi_metrics 列已存在: {col_name}")
    # 将旧数据的 total_cases/passed_cases 迁移到 L0 阶段
    cur.execute("UPDATE test_progress SET l0_total_cases=total_cases, l0_passed_cases=passed_cases WHERE l0_total_cases=0 AND total_cases>0")
    conn.commit()
    conn.close()
    print("迁移完成")

if __name__ == "__main__":
    migrate()
