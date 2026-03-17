from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List

# Test progress models.
class TestProgressBase(BaseModel):
    test_name: str
    model_name: str  # Feature summary, a brief FR description
    fr_number: str = ""  # FR number used for issue title tracking
    description: str = ""  # Detailed feature description
    config_method: str = ""  # Configuration method
    status: str
    l0_total_cases: int = 0
    l0_passed_cases: int = 0
    l0_failed_cases: int = 0
    l0_due_date: Optional[date] = None
    l2_total_cases: int = 0
    l2_passed_cases: int = 0
    l2_failed_cases: int = 0
    l2_due_date: Optional[date] = None
    l4_total_cases: int = 0
    l4_passed_cases: int = 0
    l4_failed_cases: int = 0
    l4_due_date: Optional[date] = None
    estimated_hours: float = 0.0
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    test_owners: str = ""
    developers: str = ""

class TestProgressCreate(TestProgressBase):
    """Progress is calculated automatically from passed_cases/total_cases."""
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

# Bug models.
class BugBase(BaseModel):
    title: str
    status: str = "other"
    severity: str = "medium"
    created_by: Optional[str] = None
    cr_assignee: Optional[str] = None
    cr_created_on: Optional[str] = None
    software_image_integration_build: Optional[str] = None
    test_progress_id: Optional[int] = None
    work_task_id: Optional[int] = None
    external_cr_number: Optional[str] = None

class BugCreate(BugBase):
    pass

class Bug(BugBase):
    id: int
    cr_assignee: Optional[str] = None
    cr_created_on: Optional[datetime] = None
    test_task_name: Optional[str] = None
    test_fr_number: Optional[str] = None
    work_task_key: Optional[str] = None
    work_task_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BugCsvImportRequest(BaseModel):
    file_path: Optional[str] = None
    limit: int = 0

class TestProgressDetail(TestProgress):
    """Test task details, including the linked bug list."""
    bugs: List[Bug] = []
    
    class Config:
        from_attributes = True

# KPI models.
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

# Data structures used by the charts.
class ModelPerformance(BaseModel):
    model_name: str
    metrics: dict  # {metric_name: value}
    
class KPIChartData(BaseModel):
    models: List[ModelPerformance]
    date_range: Optional[tuple] = None


class PermissionGroupBase(BaseModel):
    name: str
    description: str = ""
    can_edit_test: bool = False


class PermissionGroupCreate(PermissionGroupBase):
    pass


class PermissionGroup(PermissionGroupBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    display_name: str = ""
    role: str = "viewer"
    is_active: bool = True


class UserCreate(UserBase):
    password: str = "123456"
    group_ids: List[int] = Field(default_factory=list)


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    group_ids: Optional[List[int]] = None


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    groups: List[PermissionGroup] = Field(default_factory=list)
    can_edit_test: bool = False

    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    can_edit_test: bool
    groups: List[PermissionGroup] = Field(default_factory=list)


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class TaskOwnerAllocationInput(BaseModel):
    user_id: int
    allocated_hours: float = 0.0
    part_description: str = ""


class TaskAllocationUpdate(BaseModel):
    allocations: List[TaskOwnerAllocationInput] = Field(default_factory=list)


class TaskOwnerAllocationView(BaseModel):
    user_id: int
    username: str
    display_name: str
    allocated_hours: float
    part_description: str = ""


class TaskAllocationDetail(BaseModel):
    test_id: int
    test_name: str
    total_estimated_hours: float
    allocations: List[TaskOwnerAllocationView] = Field(default_factory=list)


class PersonnelOverlapItem(BaseModel):
    task_id_1: int
    task_name_1: str
    task_id_2: int
    task_name_2: str
    overlap_start: date
    overlap_end: date
    overlap_days: int


class PersonnelTaskItem(BaseModel):
    id: int
    fr_number: str = ""
    test_name: str
    model_name: str
    status: str
    progress: float
    estimated_hours: float
    total_cases: int
    passed_cases: int
    failed_cases: int
    l0_due_date: Optional[date] = None
    l2_due_date: Optional[date] = None
    l4_due_date: Optional[date] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    part_description: str = ""


class PersonnelWorkload(BaseModel):
    user_id: int
    username: str
    display_name: str
    can_edit_test: bool
    task_count: int
    total_cases: int
    passed_cases: int
    failed_cases: int
    total_estimated_hours: float
    overlap_count: int
    overlaps: List[PersonnelOverlapItem] = Field(default_factory=list)
    tasks: List[PersonnelTaskItem] = Field(default_factory=list)


class PersonnelSummary(BaseModel):
    members: List[User]
    workload: List[PersonnelWorkload]


class WorkTaskBase(BaseModel):
    task_key: str
    task_type: str
    task_name: str
    task_summary: str = ""
    task_detail: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: float = 0.0
    status: str
    assignee_user_id: Optional[int] = None


class WorkTaskCreate(WorkTaskBase):
    pass


class WorkTaskUpdate(BaseModel):
    task_key: Optional[str] = None
    task_type: Optional[str] = None
    task_name: Optional[str] = None
    task_summary: Optional[str] = None
    task_detail: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    status: Optional[str] = None
    assignee_user_id: Optional[int] = None


class WorkTask(WorkTaskBase):
    id: int
    assignee_username: Optional[str] = None
    assignee_display_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

