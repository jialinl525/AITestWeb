"""
Generate KPI CSV templates from centralized KPI schema.

Usage:
  python generate_kpi_csv_templates.py --all
  python generate_kpi_csv_templates.py --category ASR --category "LPI Recording"

Examples:
  python generate_kpi_csv_templates.py --all --output-dir .\kpi_templates
  python generate_kpi_csv_templates.py --category Translation --include-example
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List

from kpi_schema import get_kpi_schema_payload

BASE_COLUMNS = [
    "model_name",
    "source",
    "model_size",
    "description",
    "test_platform",
    "test_version",
    "test_condition",
    "test_date",
]


def _slugify(value: str) -> str:
    token = "".join(ch.lower() if ch.isalnum() else "_" for ch in value.strip())
    while "__" in token:
        token = token.replace("__", "_")
    return token.strip("_")


def _build_header(metric_keys: List[str]) -> List[str]:
    return BASE_COLUMNS + metric_keys


def _build_example_row(header: List[str]) -> Dict[str, str]:
    row = {key: "" for key in header}
    row["model_name"] = "example_model"
    row["source"] = "Internal"
    row["model_size"] = "100MB"
    row["description"] = "Generated KPI template row"
    row["test_platform"] = "Windows"
    row["test_version"] = "2026.03.19"
    row["test_condition"] = "lab"
    row["test_date"] = "2026-03-19T10:00:00"
    for key in header:
        if key in BASE_COLUMNS:
            continue
        row[key] = "0"
    return row


def generate_templates(selected_categories: List[str], output_dir: Path, include_example: bool) -> List[Path]:
    schema = get_kpi_schema_payload()
    categories = schema.get("categories", [])

    category_map: Dict[str, Dict[str, object]] = {
        str(item.get("key")): item for item in categories if item.get("key")
    }

    if not selected_categories:
        selected_categories = sorted(category_map.keys())

    invalid = [name for name in selected_categories if name not in category_map]
    if invalid:
        raise ValueError(
            f"Unsupported categories: {invalid}. Allowed values: {sorted(category_map.keys())}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    generated: List[Path] = []

    for category in selected_categories:
        category_item = category_map[category]
        metrics = category_item.get("metrics", [])
        metric_keys = [str(metric.get("key")) for metric in metrics if metric.get("key")]
        header = _build_header(metric_keys)

        file_path = output_dir / f"kpi_{_slugify(category)}.csv"
        with file_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            if include_example:
                writer.writerow(_build_example_row(header))

        generated.append(file_path)

    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate KPI CSV templates from KPI schema")
    parser.add_argument(
        "--category",
        action="append",
        default=[],
        help="Category key in KPI schema (can be used multiple times)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate templates for all categories",
    )
    parser.add_argument(
        "--output-dir",
        default="kpi_templates",
        help="Output directory for generated template CSV files",
    )
    parser.add_argument(
        "--include-example",
        action="store_true",
        help="Write one example data row under header",
    )

    args = parser.parse_args()

    selected_categories = [] if args.all else (args.category or [])
    if not args.all and not selected_categories:
        raise ValueError("Please pass --all or at least one --category")

    output_dir = Path(args.output_dir)
    generated = generate_templates(selected_categories, output_dir, args.include_example)

    print("Generated KPI template files:")
    for file_path in generated:
        print(f"- {file_path}")


if __name__ == "__main__":
    main()
