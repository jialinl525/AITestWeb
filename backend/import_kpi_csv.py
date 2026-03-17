"""
One-click KPI CSV import script.

Usage:
  python import_kpi_csv.py <csv_file_path> [--clear]

Examples:
    python import_kpi_csv.py .\\kpi_data.csv
    python import_kpi_csv.py .\\kpi_data.csv --clear

Required CSV columns:
    - model_category (required, ASR/TTS/Translation/VoicecallTranslation Solution)
    - model_name     (required)
    - source         (optional, model source)
    - model_size     (optional, model size)
    - description    (optional, model description)
    - power_consumption (required, numeric)
    - latency           (required, numeric)
    - accuracy_en       (required, numeric)
    - accuracy_zh       (required, numeric)
    - accuracy_es       (required, numeric)
    - accuracy_overall  (required, numeric)
    - test_date         (optional, ISO format, for example 2026-03-14T10:30:00)

Notes:
    - The new format stores one model per row, with all KPI metrics for that model in the same row.
    - This script does not support the legacy metric_name/metric_value long-table format.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from database import SessionLocal
from init_db import init_db
import models

ALLOWED_METRICS = {
    "power_consumption",   # Power consumption
    "latency",             # Latency
    "accuracy_en",         # Accuracy - English
    "accuracy_zh",         # Accuracy - Chinese
    "accuracy_es",         # Accuracy - Spanish
    "accuracy_overall",    # Overall accuracy
}

ALLOWED_MODEL_CATEGORIES = {
    "ASR",
    "TTS",
    "Translation",
    "VoicecallTranslation Solution",
}

REQUIRED_COLUMNS = {
    "model_category",
    "model_name",
    "power_consumption",
    "latency",
    "accuracy_en",
    "accuracy_zh",
    "accuracy_es",
    "accuracy_overall",
}


def parse_test_date(value: str) -> Optional[datetime]:
    v = (value or "").strip()
    if not v:
        return None
    try:
        return datetime.fromisoformat(v)
    except ValueError:
        raise ValueError(
            f"Invalid test_date format: {v}. Use ISO format, for example 2026-03-14T10:30:00"
        )


def parse_metric_value(value: str) -> float:
    v = (value or "").strip()
    if not v:
        raise ValueError("metric_value cannot be empty")
    try:
        return float(v)
    except ValueError:
        raise ValueError(f"metric_value is not a valid number: {v}")


def import_csv(csv_path: Path, clear_existing: bool = False) -> None:
    if not csv_path.exists() or not csv_path.is_file():
        raise FileNotFoundError(f"CSV file does not exist: {csv_path}")

    # Ensure the database schema exists.
    init_db()

    db = SessionLocal()
    imported = 0
    skipped = 0

    try:
        if clear_existing:
            deleted = db.query(models.KPIMetric).delete()
            db.commit()
            print(f"Cleared existing KPI data: {deleted} rows")

        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV header is missing")

            headers = {h.strip() for h in reader.fieldnames if h}
            missing = REQUIRED_COLUMNS - headers
            if missing:
                raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

            for line_no, row in enumerate(reader, start=2):
                try:
                    model_name = (row.get("model_name") or "").strip()
                    model_category = (row.get("model_category") or "").strip()
                    source = (row.get("source") or "").strip()
                    model_size = (row.get("model_size") or "").strip()
                    description = (row.get("description") or "").strip()
                    test_date = parse_test_date(row.get("test_date") or "")

                    if not model_category:
                        raise ValueError("model_category cannot be empty")
                    if model_category not in ALLOWED_MODEL_CATEGORIES:
                        raise ValueError(
                            f"model_category is out of range: {model_category}. Allowed values: {sorted(ALLOWED_MODEL_CATEGORIES)}"
                        )
                    if not model_name:
                        raise ValueError("model_name cannot be empty")
                    # Split one model row into multiple KPI metric records.
                    for metric_name in sorted(ALLOWED_METRICS):
                        metric_value = parse_metric_value(row.get(metric_name) or "")

                        obj = models.KPIMetric(
                            model_category=model_category,
                            model_name=model_name,
                            source=source,
                            model_size=model_size,
                            description=description,
                            metric_name=metric_name,
                            metric_value=metric_value,
                        )

                        if test_date is not None:
                            obj.test_date = test_date

                        db.add(obj)
                        imported += 1

                except Exception as e:
                    skipped += 1
                    print(f"[SKIPPED] Failed to import line {line_no}: {e}")

        db.commit()
        print(f"Import complete: {imported} records imported, {skipped} skipped")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="One-click KPI CSV import")
    parser.add_argument("csv_path", help="Path to the CSV file")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing KPI data before import",
    )
    args = parser.parse_args()

    import_csv(Path(args.csv_path), clear_existing=args.clear)


if __name__ == "__main__":
    main()
