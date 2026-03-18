"""
Category-specific KPI CSV import script.

Usage:
  python import_kpi_csv.py <csv_file_path> --category <category> [--clear]

Examples:
    python import_kpi_csv.py .\kpi_asr.csv --category ASR --clear
    python import_kpi_csv.py .\kpi_translation.csv --category Translation

Required CSV columns:
    - model_name (required)
    - metric columns (required by the category)

Optional CSV columns:
    - source
    - model_size
    - description
    - test_platform
    - test_version
    - test_condition
    - test_date (ISO format, for example 2026-03-14T10:30:00)

Notes:
    - One CSV file should contain models for a single category only.
    - Category is provided by command-line argument --category.
    - Legacy alias compatibility is intentionally not supported.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from database import SessionLocal
from init_db import init_db
import models

CATEGORY_METRIC_FIELDS: Dict[str, List[str]] = {
    "ASR": [
        "power_consumption",
        "latency",
        "accuracy_en",
        "accuracy_cn",
        "accuracy_es",
        "accuracy_total",
    ],
    "TTS": [
        "power_consumption",
        "latency",
        "accuracy_en",
        "accuracy_cn",
        "accuracy_es",
        "accuracy_total",
    ],
    "Translation": [
        "power_consumption",
        "latency",
        "accuracy_en_to_cn",
        "accuracy_cn_to_en",
        "accuracy_en_to_es",
        "accuracy_es_to_en",
        "accuracy_total",
    ],
    "VoiceCallTranslation Solution": [
        "power_consumption",
        "e2e_latency",
        "accuracy_en_to_cn",
        "accuracy_cn_to_en",
        "accuracy_total",
    ],
    "LPI Recording": ["power_consumption"],
    "Multi Model Detection": ["power_consumption", "latency", "wakeup_rate"],
}

BASE_REQUIRED_COLUMNS = {"model_name"}


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


def import_csv(csv_path: Path, model_category: str, clear_existing: bool = False) -> None:
    if not csv_path.exists() or not csv_path.is_file():
        raise FileNotFoundError(f"CSV file does not exist: {csv_path}")

    category = (model_category or "").strip()
    if category not in CATEGORY_METRIC_FIELDS:
        raise ValueError(
            f"Unsupported model category: {model_category}. Allowed values: {sorted(CATEGORY_METRIC_FIELDS.keys())}"
        )

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
            required_columns = BASE_REQUIRED_COLUMNS.union(set(CATEGORY_METRIC_FIELDS[category]))
            missing = required_columns - headers
            if missing:
                raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

            for line_no, row in enumerate(reader, start=2):
                try:
                    model_name = (row.get("model_name") or "").strip()

                    source = (row.get("source") or "").strip()
                    model_size = (row.get("model_size") or "").strip()
                    description = (row.get("description") or "").strip()
                    test_platform = (row.get("test_platform") or "").strip()
                    test_version = (row.get("test_version") or "").strip()
                    test_condition = (row.get("test_condition") or "").strip()
                    test_date = parse_test_date(row.get("test_date") or "")

                    if not model_name:
                        raise ValueError("model_name cannot be empty")

                    metric_names = CATEGORY_METRIC_FIELDS[category]
                    for metric_name in metric_names:
                        metric_value = parse_metric_value(row.get(metric_name) or "")

                        obj = models.KPIMetric(
                            model_category=category,
                            model_name=model_name,
                            source=source,
                            model_size=model_size,
                            description=description,
                            test_platform=test_platform,
                            test_version=test_version,
                            test_condition=test_condition,
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
    parser = argparse.ArgumentParser(description="Category-specific KPI CSV import")
    parser.add_argument("csv_path", help="Path to the CSV file")
    parser.add_argument(
        "--category",
        required=True,
        choices=sorted(CATEGORY_METRIC_FIELDS.keys()),
        help="Model category for this CSV file",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing KPI data before import",
    )
    args = parser.parse_args()

    import_csv(Path(args.csv_path), model_category=args.category, clear_existing=args.clear)


if __name__ == "__main__":
    main()
