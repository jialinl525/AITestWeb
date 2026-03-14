"""
KPI CSV 一键导入脚本

用法：
  python import_kpi_csv.py <csv文件路径> [--clear]

示例：
    python import_kpi_csv.py .\\kpi_data.csv
    python import_kpi_csv.py .\\kpi_data.csv --clear

CSV 列要求：
    - model_category (必填，ASR/TTS/Translation/VoicecallTranslation Solution)
    - model_name     (必填)
    - source         (可选，模型来源)
    - model_size     (可选，模型大小)
    - description    (可选，模型具体描述)
    - power_consumption (必填，数字)
    - latency           (必填，数字)
    - accuracy_en       (必填，数字)
    - accuracy_zh       (必填，数字)
    - accuracy_es       (必填，数字)
    - accuracy_overall  (必填，数字)
    - test_date      (可选，ISO 格式，如 2026-03-14T10:30:00)

说明：
    - 新格式为“一行一个模型”，每行内包含该模型的全部 KPI 指标。
    - 本脚本不兼容旧的 metric_name/metric_value 长表格式。
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
    "power_consumption",   # 功耗
    "latency",             # 延迟
    "accuracy_en",         # 准确率-英语
    "accuracy_zh",         # 准确率-中文
    "accuracy_es",         # 准确率-西班牙语
    "accuracy_overall",    # 准确率-综合
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
            f"test_date 格式错误: {v}，请使用 ISO 格式，例如 2026-03-14T10:30:00"
        )


def parse_metric_value(value: str) -> float:
    v = (value or "").strip()
    if not v:
        raise ValueError("metric_value 不能为空")
    try:
        return float(v)
    except ValueError:
        raise ValueError(f"metric_value 不是合法数字: {v}")


def import_csv(csv_path: Path, clear_existing: bool = False) -> None:
    if not csv_path.exists() or not csv_path.is_file():
        raise FileNotFoundError(f"CSV 文件不存在: {csv_path}")

    # 确保表结构存在
    init_db()

    db = SessionLocal()
    imported = 0
    skipped = 0

    try:
        if clear_existing:
            deleted = db.query(models.KPIMetric).delete()
            db.commit()
            print(f"已清空旧 KPI 数据: {deleted} 条")

        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV 缺少表头")

            headers = {h.strip() for h in reader.fieldnames if h}
            missing = REQUIRED_COLUMNS - headers
            if missing:
                raise ValueError(f"CSV 缺少必要列: {sorted(missing)}")

            for line_no, row in enumerate(reader, start=2):
                try:
                    model_name = (row.get("model_name") or "").strip()
                    model_category = (row.get("model_category") or "").strip()
                    source = (row.get("source") or "").strip()
                    model_size = (row.get("model_size") or "").strip()
                    description = (row.get("description") or "").strip()
                    test_date = parse_test_date(row.get("test_date") or "")

                    if not model_category:
                        raise ValueError("model_category 不能为空")
                    if model_category not in ALLOWED_MODEL_CATEGORIES:
                        raise ValueError(
                            f"model_category 不在允许范围: {model_category}，允许值: {sorted(ALLOWED_MODEL_CATEGORIES)}"
                        )
                    if not model_name:
                        raise ValueError("model_name 不能为空")
                    # 一行模型数据拆成多条 KPI 指标记录
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
                    print(f"[跳过] 第 {line_no} 行导入失败: {e}")

        db.commit()
        print(f"导入完成: 成功 {imported} 条，跳过 {skipped} 条")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="KPI CSV 一键导入")
    parser.add_argument("csv_path", help="CSV 文件路径")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="导入前清空现有 KPI 数据",
    )
    args = parser.parse_args()

    import_csv(Path(args.csv_path), clear_existing=args.clear)


if __name__ == "__main__":
    main()
