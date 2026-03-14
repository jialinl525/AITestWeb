from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# 测试进度相关
class TestProgressBase(BaseModel):
    test_name: str
    model_name: str  # 功能描述，简述FR功能
    description: str = ""  # 功能的具体描述
    config_method: str = ""  # 配置方式
    status: str
    l0_total_cases: int = 0
    l0_passed_cases: int = 0
    l0_failed_cases: int = 0
    l2_total_cases: int = 0
    l2_passed_cases: int = 0
    l2_failed_cases: int = 0
    l4_total_cases: int = 0
    l4_passed_cases: int = 0
    l4_failed_cases: int = 0
    test_owners: str = ""
    developers: str = ""

class TestProgressCreate(TestProgressBase):
    """progress 由 passed_cases/total_cases 自动计算"""
    pass

class TestProgress(TestProgressBase):
    id: int
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    progress: float = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Bug相关
class BugBase(BaseModel):
    title: str
    description: str
    severity: str
    status: str
    assigned_to: Optional[str] = None

class BugCreate(BugBase):
    test_progress_id: int

class Bug(BugBase):
    id: int
    test_progress_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TestProgressDetail(TestProgress):
    """测试任务详情，包含关联的 Bug 列表"""
    bugs: List[Bug] = []
    
    class Config:
        from_attributes = True

# KPI相关
class KPIMetricBase(BaseModel):
    model_category: str
    model_name: str
    source: str = ""
    model_size: str = ""
    description: str = ""
    metric_name: str
    metric_value: float

class KPIMetricCreate(KPIMetricBase):
    test_date: Optional[datetime] = None

class KPIMetric(KPIMetricBase):
    id: int
    test_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# 用于图表展示的数据结构
class ModelPerformance(BaseModel):
    model_name: str
    metrics: dict  # {metric_name: value}
    
class KPIChartData(BaseModel):
    models: List[ModelPerformance]
    date_range: Optional[tuple] = None

