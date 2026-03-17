from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import schemas, models
from database import get_db

router = APIRouter()

@router.get("/metrics", response_model=List[schemas.KPIMetric])
def get_kpi_metrics(
    model_category: Optional[str] = None,
    model_name: Optional[str] = None,
    metric_name: Optional[str] = None,
    days: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get KPI metric data."""
    query = db.query(models.KPIMetric)

    # Optional time range filter. By default, no time filter is applied.
    if days is not None:
        start_date = datetime.now() - timedelta(days=days)
        query = query.filter(models.KPIMetric.test_date >= start_date)
    
    if model_name:
        query = query.filter(models.KPIMetric.model_name == model_name)
    if model_category:
        query = query.filter(models.KPIMetric.model_category == model_category)
    if metric_name:
        query = query.filter(models.KPIMetric.metric_name == metric_name)
    
    metrics = query.order_by(models.KPIMetric.test_date.desc()).all()
    return metrics

@router.post("/metrics", response_model=schemas.KPIMetric)
def create_kpi_metric(metric: schemas.KPIMetricCreate, db: Session = Depends(get_db)):
    """Create a new KPI metric."""
    db_metric = models.KPIMetric(**metric.model_dump())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

@router.get("/models/performance", response_model=List[schemas.ModelPerformance])
def get_models_performance(days: Optional[int] = None, model_category: Optional[str] = None, db: Session = Depends(get_db)):
    """Get model performance data for chart rendering."""
    query = db.query(models.KPIMetric)
    if days is not None:
        start_date = datetime.now() - timedelta(days=days)
        query = query.filter(models.KPIMetric.test_date >= start_date)
    if model_category:
        query = query.filter(models.KPIMetric.model_category == model_category)
    metrics = query.all()
    
    # Group by model and keep the latest value for each metric.
    model_performance = {}
    for metric in metrics:
        if metric.model_name not in model_performance:
            model_performance[metric.model_name] = {}
        # If the metric already exists, keep the most recent value.
        if metric.metric_name not in model_performance[metric.model_name] or \
           metric.test_date > model_performance[metric.model_name].get('_date', datetime.min):
            model_performance[metric.model_name][metric.metric_name] = metric.metric_value
            model_performance[metric.model_name]['_date'] = metric.test_date
    
    # Convert to response format.
    result = []
    for model_name, metrics_dict in model_performance.items():
        metrics_dict.pop('_date', None)  # Remove the temporary date field.
        result.append(schemas.ModelPerformance(
            model_name=model_name,
            metrics=metrics_dict
        ))
    
    return result

@router.get("/chart/ladder")
def get_ladder_chart_data(
    days: Optional[int] = None,
    metric_name: str = "accuracy_overall",
    model_category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get ladder chart data."""
    query = db.query(models.KPIMetric).filter(
        models.KPIMetric.metric_name == metric_name
    )
    if days is not None:
        start_date = datetime.now() - timedelta(days=days)
        query = query.filter(models.KPIMetric.test_date >= start_date)
    if model_category:
        query = query.filter(models.KPIMetric.model_category == model_category)
    metrics = query.all()
    
    # Group by model and keep the latest value.
    model_values = {}
    for metric in metrics:
        if metric.model_name not in model_values or \
           metric.test_date > model_values[metric.model_name]['date']:
            model_values[metric.model_name] = {
                'value': metric.metric_value,
                'date': metric.test_date
            }
    
    # Sort by metric value.
    sorted_models = sorted(
        model_values.items(),
        key=lambda x: x[1]['value'],
        reverse=True
    )
    
    return {
        "metric_name": metric_name,
        "data": [
            {
                "model_name": model_name,
                "value": data['value'],
                "date": data['date'].isoformat()
            }
            for model_name, data in sorted_models
        ]
    }

@router.get("/chart/scatter")
def get_scatter_chart_data(
    x_metric: str = "power_consumption",
    y_metric: str = "latency",
    days: Optional[int] = None,
    model_category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get scatter chart data."""
    # Load data for the X and Y metrics.
    x_query = db.query(models.KPIMetric).filter(
        models.KPIMetric.metric_name == x_metric
    )
    if days is not None:
        start_date = datetime.now() - timedelta(days=days)
        x_query = x_query.filter(models.KPIMetric.test_date >= start_date)
    if model_category:
        x_query = x_query.filter(models.KPIMetric.model_category == model_category)
    x_metrics = x_query.all()
    
    y_query = db.query(models.KPIMetric).filter(
        models.KPIMetric.metric_name == y_metric
    )
    if days is not None:
        start_date = datetime.now() - timedelta(days=days)
        y_query = y_query.filter(models.KPIMetric.test_date >= start_date)
    if model_category:
        y_query = y_query.filter(models.KPIMetric.model_category == model_category)
    y_metrics = y_query.all()
    
    # Keep the latest X and Y values per model to avoid overwriting or losing one dimension.
    x_latest = {}
    for metric in x_metrics:
        current = x_latest.get(metric.model_name)
        if current is None or metric.test_date >= current['date']:
            x_latest[metric.model_name] = {
                'value': metric.metric_value,
                'date': metric.test_date
            }

    y_latest = {}
    for metric in y_metrics:
        current = y_latest.get(metric.model_name)
        if current is None or metric.test_date >= current['date']:
            y_latest[metric.model_name] = {
                'value': metric.metric_value,
                'date': metric.test_date
            }

    # Build scatter chart data, keeping only models that have both X and Y values.
    common_models = set(x_latest.keys()) & set(y_latest.keys())
    scatter_data = [
        {
            "model_name": model_name,
            "x": x_latest[model_name]['value'],
            "y": y_latest[model_name]['value']
        }
        for model_name in common_models
    ]
    
    return {
        "model_category": model_category,
        "x_metric": x_metric,
        "y_metric": y_metric,
        "data": scatter_data
    }
