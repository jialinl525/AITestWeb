from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter()

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

CATEGORY_TOKEN_ALIASES: Dict[str, str] = {
    "voicecalltranslationsolution": "VoiceCallTranslation Solution",
    "voicecalltranslation": "VoiceCallTranslation Solution",
}

METRIC_TOKEN_ALIASES: Dict[str, str] = {
    "power": "power_consumption",
    "powerconsumption": "power_consumption",
    "latency": "latency",
    "e2elatency": "e2e_latency",
    "wakeuprate": "wakeup_rate",
    "accuracytotal": "accuracy_total",
    "accuracyoverall": "accuracy_total",
    "accuracyen": "accuracy_en",
    "accuracycn": "accuracy_cn",
    "accuracyzh": "accuracy_cn",
    "accuracyes": "accuracy_es",
    "accuracyentocn": "accuracy_en_to_cn",
    "accuracycntoen": "accuracy_cn_to_en",
    "accuracyentoes": "accuracy_en_to_es",
    "accuracyestoen": "accuracy_es_to_en",
}

METRIC_FILTER_ALIASES: Dict[str, List[str]] = {
    "accuracy_total": ["accuracy_overall"],
    "accuracy_cn": ["accuracy_zh"],
    "e2e_latency": ["latency"],
}

LOWER_IS_BETTER_METRICS = {
    "power_consumption",
    "latency",
    "e2e_latency",
}


def _normalize_text(value: Optional[str]) -> str:
    return (value or "").strip()


def _normalize_token(value: Optional[str]) -> str:
    text = _normalize_text(value).lower()
    return "".join(ch for ch in text if ch.isalnum())


def _canonical_category(value: Optional[str]) -> str:
    raw = _normalize_text(value)
    token = _normalize_token(raw)
    if not token:
        return raw
    for canonical_name in CATEGORY_METRIC_FIELDS.keys():
        if _normalize_token(canonical_name) == token:
            return canonical_name
    return CATEGORY_TOKEN_ALIASES.get(token, raw)


def _canonical_metric_name(value: Optional[str]) -> str:
    raw = _normalize_text(value)
    token = _normalize_token(raw)
    if not token:
        return raw
    return METRIC_TOKEN_ALIASES.get(token, raw)


def _is_lower_better_metric(metric_name: Optional[str]) -> bool:
    return _canonical_metric_name(metric_name) in LOWER_IS_BETTER_METRICS


def _apply_category_filter(query, model_category: Optional[str]):
    if not model_category:
        return query
    token = _normalize_token(model_category)
    if not token:
        return query

    category_expr = func.lower(
        func.replace(
            func.replace(
                func.replace(func.coalesce(models.KPIMetric.model_category, ""), " ", ""),
                "-",
                "",
            ),
            "_",
            "",
        )
    )
    return query.filter(category_expr == token)


def _metric_filter_tokens(metric_name: str) -> List[str]:
    canonical = _canonical_metric_name(metric_name)
    tokens = {_normalize_token(canonical)}
    for alias in METRIC_FILTER_ALIASES.get(canonical, []):
        tokens.add(_normalize_token(alias))
    return [token for token in tokens if token]


def _apply_metric_filter(query, metric_name: str):
    tokens = _metric_filter_tokens(metric_name)
    if not tokens:
        return query
    metric_expr = func.lower(
        func.replace(
            func.replace(
                func.replace(func.coalesce(models.KPIMetric.metric_name, ""), " ", ""),
                "-",
                "",
            ),
            "_",
            "",
        )
    )
    return query.filter(metric_expr.in_(tokens))


def _normalize_payload_metrics(metrics_map: Optional[dict], model_category: Optional[str]) -> Tuple[str, Dict[str, float]]:
    canonical_category = _canonical_category(model_category)
    allowed_metrics = set(CATEGORY_METRIC_FIELDS.get(canonical_category, []))

    normalized: Dict[str, float] = {}
    invalid_metrics: List[str] = []
    for raw_metric_name, raw_metric_value in (metrics_map or {}).items():
        metric_name = _canonical_metric_name(raw_metric_name)
        if not metric_name:
            continue
        if allowed_metrics and metric_name not in allowed_metrics:
            invalid_metrics.append(str(raw_metric_name))
            continue
        normalized[metric_name] = _safe_float(raw_metric_value)

    if invalid_metrics:
        joined = ", ".join(sorted(set(invalid_metrics)))
        raise HTTPException(status_code=400, detail=f"Invalid metrics for {canonical_category}: {joined}")

    return canonical_category, normalized


def _safe_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid metric value: {value}") from exc


def _run_key(metric: models.KPIMetric) -> Tuple[str, str, str]:
    model_name = _normalize_text(metric.model_name)
    model_category = _normalize_text(metric.model_category)
    test_version = _normalize_text(getattr(metric, "test_version", ""))
    if test_version:
        return (model_name, model_category, f"v::{test_version}")

    test_date = (metric.test_date or datetime.min).replace(microsecond=0)
    return (model_name, model_category, f"d::{test_date.isoformat()}")


def _group_runs(metrics: List[models.KPIMetric]) -> Dict[Tuple[str, str, str], List[models.KPIMetric]]:
    grouped: Dict[Tuple[str, str, str], List[models.KPIMetric]] = {}
    for metric in metrics:
        key = _run_key(metric)
        grouped.setdefault(key, []).append(metric)
    return grouped


def _build_model_record(rows: List[models.KPIMetric]) -> schemas.KPIModelRecord:
    if not rows:
        raise HTTPException(status_code=404, detail="Model run not found")

    latest = max(rows, key=lambda row: row.test_date or datetime.min)

    latest_metric_rows: Dict[str, models.KPIMetric] = {}
    for row in rows:
        metric_name = _canonical_metric_name(row.metric_name)
        current = latest_metric_rows.get(metric_name)
        if current is None or (row.test_date or datetime.min) >= (current.test_date or datetime.min):
            latest_metric_rows[metric_name] = row

    metrics = {
        metric_name: _safe_float(metric_row.metric_value)
        for metric_name, metric_row in latest_metric_rows.items()
    }

    return schemas.KPIModelRecord(
        model_category=_canonical_category(latest.model_category),
        model_name=_normalize_text(latest.model_name),
        source=_normalize_text(latest.source),
        model_size=_normalize_text(latest.model_size),
        description=_normalize_text(latest.description),
        test_platform=_normalize_text(getattr(latest, "test_platform", "")),
        test_version=_normalize_text(getattr(latest, "test_version", "")),
        test_condition=_normalize_text(getattr(latest, "test_condition", "")),
        test_date=latest.test_date or datetime.min,
        metrics=metrics,
    )


def _pick_latest_run(rows: List[models.KPIMetric]) -> List[models.KPIMetric]:
    if not rows:
        return []
    grouped = _group_runs(rows)
    return max(
        grouped.values(),
        key=lambda run_rows: max(row.test_date or datetime.min for row in run_rows),
    )


@router.get("/metrics", response_model=List[schemas.KPIMetric])
def get_kpi_metrics(
    model_category: Optional[str] = None,
    model_name: Optional[str] = None,
    metric_name: Optional[str] = None,
    days: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get KPI metric data."""
    query = db.query(models.KPIMetric)

    if days is not None:
        start_date = datetime.now() - timedelta(days=days)
        query = query.filter(models.KPIMetric.test_date >= start_date)

    if model_name:
        query = query.filter(models.KPIMetric.model_name == model_name)
    query = _apply_category_filter(query, model_category)
    if metric_name:
        query = _apply_metric_filter(query, _canonical_metric_name(metric_name))

    return query.order_by(models.KPIMetric.test_date.desc()).all()


@router.post("/metrics", response_model=schemas.KPIMetric)
def create_kpi_metric(metric: schemas.KPIMetricCreate, db: Session = Depends(get_db)):
    """Create a new KPI metric."""
    db_metric = models.KPIMetric(**metric.model_dump())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


@router.get("/models/latest", response_model=List[schemas.KPIModelRecord])
def get_latest_models(
    model_category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.KPIMetric)
    query = _apply_category_filter(query, model_category)
    rows = query.order_by(models.KPIMetric.test_date.desc()).all()

    grouped_runs = _group_runs(rows)
    latest_by_model: Dict[str, schemas.KPIModelRecord] = {}
    for run_rows in grouped_runs.values():
        record = _build_model_record(run_rows)
        existing = latest_by_model.get(record.model_name)
        if existing is None or record.test_date >= existing.test_date:
            latest_by_model[record.model_name] = record

    return sorted(latest_by_model.values(), key=lambda item: item.test_date, reverse=True)


@router.get("/models/{model_name}/versions", response_model=List[schemas.KPIModelVersionOption])
def get_model_versions(
    model_name: str,
    model_category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.KPIMetric).filter(models.KPIMetric.model_name == model_name)
    query = _apply_category_filter(query, model_category)
    rows = query.order_by(models.KPIMetric.test_date.desc()).all()
    if not rows:
        return []

    grouped_runs = _group_runs(rows)
    dedup: Dict[str, schemas.KPIModelVersionOption] = {}
    for run_rows in grouped_runs.values():
        record = _build_model_record(run_rows)
        version_value = record.test_version or record.test_date.isoformat()
        existing = dedup.get(version_value)
        option = schemas.KPIModelVersionOption(test_version=version_value, test_date=record.test_date)
        if existing is None or option.test_date >= existing.test_date:
            dedup[version_value] = option

    return sorted(dedup.values(), key=lambda item: item.test_date, reverse=True)


@router.get("/models/{model_name}/detail", response_model=schemas.KPIModelRecord)
def get_model_detail(
    model_name: str,
    model_category: Optional[str] = None,
    test_version: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.KPIMetric).filter(models.KPIMetric.model_name == model_name)
    query = _apply_category_filter(query, model_category)
    rows = query.order_by(models.KPIMetric.test_date.desc()).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Model not found")

    if test_version:
        normalized_version = _normalize_text(test_version)
        filtered = [row for row in rows if _normalize_text(getattr(row, "test_version", "")) == normalized_version]
        if not filtered:
            try:
                parsed = datetime.fromisoformat(normalized_version).replace(microsecond=0)
                filtered = [
                    row
                    for row in rows
                    if _normalize_text(getattr(row, "test_version", "")) == ""
                    and (row.test_date or datetime.min).replace(microsecond=0) == parsed
                ]
            except ValueError:
                filtered = []
        if not filtered:
            raise HTTPException(status_code=404, detail="Model version not found")
        return _build_model_record(_pick_latest_run(filtered))

    return _build_model_record(_pick_latest_run(rows))


@router.post("/models", response_model=schemas.KPIModelRecord)
def create_model_run(payload: schemas.KPIModelUpsert, db: Session = Depends(get_db)):
    canonical_category, metrics_map = _normalize_payload_metrics(payload.metrics or {}, payload.model_category)
    if not metrics_map:
        raise HTTPException(status_code=400, detail="metrics cannot be empty")

    test_date = payload.test_date or datetime.now()
    created_rows: List[models.KPIMetric] = []
    for metric_name, metric_value in metrics_map.items():
        row = models.KPIMetric(
            model_category=canonical_category,
            model_name=_normalize_text(payload.model_name),
            source=payload.source,
            model_size=payload.model_size,
            description=payload.description,
            test_platform=payload.test_platform,
            test_version=payload.test_version,
            test_condition=payload.test_condition,
            metric_name=metric_name,
            metric_value=metric_value,
            test_date=test_date,
        )
        db.add(row)
        created_rows.append(row)

    if not created_rows:
        raise HTTPException(status_code=400, detail="No valid metrics provided")

    db.commit()
    for row in created_rows:
        db.refresh(row)
    return _build_model_record(created_rows)


@router.put("/models/{model_name}/latest", response_model=schemas.KPIModelRecord)
def update_latest_model_run(model_name: str, payload: schemas.KPIModelUpsert, db: Session = Depends(get_db)):
    route_model_name = _normalize_text(model_name)
    payload_model_name = _normalize_text(payload.model_name)
    if payload_model_name and payload_model_name != route_model_name:
        raise HTTPException(status_code=400, detail="model_name cannot be changed in update")

    canonical_category, metric_updates = _normalize_payload_metrics(payload.metrics or {}, payload.model_category)

    query = db.query(models.KPIMetric).filter(models.KPIMetric.model_name == route_model_name)
    query = _apply_category_filter(query, canonical_category)
    rows = query.order_by(models.KPIMetric.test_date.desc()).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Model not found")

    latest_rows = _pick_latest_run(rows)
    if not latest_rows:
        raise HTTPException(status_code=404, detail="Model run not found")

    latest_version = _normalize_text(getattr(latest_rows[0], "test_version", ""))
    incoming_version = _normalize_text(payload.test_version)

    target_test_date = payload.test_date or max(row.test_date or datetime.min for row in latest_rows)
    allowed_metrics = set(CATEGORY_METRIC_FIELDS.get(canonical_category, []))

    if incoming_version != latest_version:
        # Version changed: create a new run row set instead of mutating the latest run.
        merged_metrics: Dict[str, float] = {}
        for row in latest_rows:
            metric_name = _canonical_metric_name(row.metric_name)
            if metric_name:
                if allowed_metrics and metric_name not in allowed_metrics:
                    continue
                merged_metrics[metric_name] = _safe_float(row.metric_value)

        for metric_name, metric_value in metric_updates.items():
            merged_metrics[metric_name] = _safe_float(metric_value)

        if not merged_metrics:
            raise HTTPException(status_code=400, detail="No valid metrics provided")

        created_rows: List[models.KPIMetric] = []
        for metric_name, metric_value in merged_metrics.items():
            row = models.KPIMetric(
                model_category=canonical_category,
                model_name=route_model_name,
                source=payload.source,
                model_size=payload.model_size,
                description=payload.description,
                test_platform=payload.test_platform,
                test_version=payload.test_version,
                test_condition=payload.test_condition,
                metric_name=metric_name,
                metric_value=_safe_float(metric_value),
                test_date=target_test_date,
            )
            db.add(row)
            created_rows.append(row)

        db.commit()
        for row in created_rows:
            db.refresh(row)
        return _build_model_record(created_rows)

    existing_metric_names = set()
    for row in latest_rows:
        existing_metric_names.add(_canonical_metric_name(row.metric_name))
        row.model_category = canonical_category
        row.model_name = route_model_name
        row.source = payload.source
        row.model_size = payload.model_size
        row.description = payload.description
        row.test_platform = payload.test_platform
        row.test_version = payload.test_version
        row.test_condition = payload.test_condition
        row.test_date = target_test_date

        metric_key = _canonical_metric_name(row.metric_name)
        if metric_key in metric_updates:
            row.metric_value = _safe_float(metric_updates[metric_key])

    appended_rows: List[models.KPIMetric] = []
    for metric_name, metric_value in metric_updates.items():
        if metric_name in existing_metric_names:
            continue
        row = models.KPIMetric(
            model_category=canonical_category,
            model_name=route_model_name,
            source=payload.source,
            model_size=payload.model_size,
            description=payload.description,
            test_platform=payload.test_platform,
            test_version=payload.test_version,
            test_condition=payload.test_condition,
            metric_name=metric_name,
            metric_value=_safe_float(metric_value),
            test_date=target_test_date,
        )
        db.add(row)
        appended_rows.append(row)

    db.commit()
    for row in latest_rows + appended_rows:
        db.refresh(row)

    return _build_model_record(latest_rows + appended_rows)


@router.delete("/models/{model_name}")
def delete_model_runs(
    model_name: str,
    model_category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    normalized_model_name = _normalize_text(model_name)
    if not normalized_model_name:
        raise HTTPException(status_code=400, detail="model_name is required")

    canonical_category = _canonical_category(model_category) if model_category else None

    query = db.query(models.KPIMetric).filter(models.KPIMetric.model_name == normalized_model_name)
    query = _apply_category_filter(query, canonical_category)

    deleted_count = query.delete(synchronize_session=False)
    if deleted_count <= 0:
        raise HTTPException(status_code=404, detail="Model not found")

    db.commit()
    return {
        "model_name": normalized_model_name,
        "model_category": canonical_category,
        "deleted": deleted_count,
    }


@router.get("/models/performance", response_model=List[schemas.ModelPerformance])
def get_models_performance(days: Optional[int] = None, model_category: Optional[str] = None, db: Session = Depends(get_db)):
    """Get model performance data for chart rendering."""
    query = db.query(models.KPIMetric)
    if days is not None:
        start_date = datetime.now() - timedelta(days=days)
        query = query.filter(models.KPIMetric.test_date >= start_date)
    query = _apply_category_filter(query, model_category)
    metrics = query.all()

    model_performance = {}
    for metric in metrics:
        if metric.model_name not in model_performance:
            model_performance[metric.model_name] = {}
        if metric.metric_name not in model_performance[metric.model_name] or metric.test_date > model_performance[metric.model_name].get('_date', datetime.min):
            model_performance[metric.model_name][metric.metric_name] = metric.metric_value
            model_performance[metric.model_name]['_date'] = metric.test_date

    result = []
    for model_name, metrics_dict in model_performance.items():
        metrics_dict.pop('_date', None)
        result.append(schemas.ModelPerformance(model_name=model_name, metrics=metrics_dict))

    return result


@router.get("/chart/ladder")
def get_ladder_chart_data(
    days: Optional[int] = None,
    metric_name: str = "accuracy_total",
    model_category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get ladder chart data."""
    canonical_metric_name = _canonical_metric_name(metric_name)
    query = db.query(models.KPIMetric)
    query = _apply_metric_filter(query, canonical_metric_name)
    if days is not None:
        start_date = datetime.now() - timedelta(days=days)
        query = query.filter(models.KPIMetric.test_date >= start_date)
    query = _apply_category_filter(query, model_category)
    metrics = query.all()

    model_values = {}
    for metric in metrics:
        if metric.model_name not in model_values or metric.test_date > model_values[metric.model_name]['date']:
            model_values[metric.model_name] = {
                'value': metric.metric_value,
                'date': metric.test_date,
            }

    is_lower_better = _is_lower_better_metric(canonical_metric_name)
    sorted_models = sorted(
        model_values.items(),
        key=lambda x: x[1]['value'],
        reverse=not is_lower_better,
    )

    return {
        "metric_name": canonical_metric_name,
        "metric_preference": "lower" if is_lower_better else "higher",
        "data": [
            {
                "model_name": model_name,
                "value": data['value'],
                "date": data['date'].isoformat(),
            }
            for model_name, data in sorted_models
        ],
    }


@router.get("/chart/scatter")
def get_scatter_chart_data(
    x_metric: str = "power_consumption",
    y_metric: str = "latency",
    days: Optional[int] = None,
    model_category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get scatter chart data."""
    canonical_x_metric = _canonical_metric_name(x_metric)
    canonical_y_metric = _canonical_metric_name(y_metric)

    x_query = db.query(models.KPIMetric)
    x_query = _apply_metric_filter(x_query, canonical_x_metric)
    if days is not None:
        start_date = datetime.now() - timedelta(days=days)
        x_query = x_query.filter(models.KPIMetric.test_date >= start_date)
    x_query = _apply_category_filter(x_query, model_category)
    x_metrics = x_query.all()

    y_query = db.query(models.KPIMetric)
    y_query = _apply_metric_filter(y_query, canonical_y_metric)
    if days is not None:
        start_date = datetime.now() - timedelta(days=days)
        y_query = y_query.filter(models.KPIMetric.test_date >= start_date)
    y_query = _apply_category_filter(y_query, model_category)
    y_metrics = y_query.all()

    x_latest = {}
    for metric in x_metrics:
        current = x_latest.get(metric.model_name)
        if current is None or metric.test_date >= current['date']:
            x_latest[metric.model_name] = {
                'value': metric.metric_value,
                'date': metric.test_date,
            }

    y_latest = {}
    for metric in y_metrics:
        current = y_latest.get(metric.model_name)
        if current is None or metric.test_date >= current['date']:
            y_latest[metric.model_name] = {
                'value': metric.metric_value,
                'date': metric.test_date,
            }

    common_models = set(x_latest.keys()) & set(y_latest.keys())
    scatter_data = [
        {
            "model_name": model_name,
            "x": x_latest[model_name]['value'],
            "y": y_latest[model_name]['value'],
        }
        for model_name in common_models
    ]

    return {
        "model_category": model_category,
        "x_metric": canonical_x_metric,
        "y_metric": canonical_y_metric,
        "data": scatter_data,
    }
