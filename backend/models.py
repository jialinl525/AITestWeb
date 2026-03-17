from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class TestProgress(Base):
    __tablename__ = "test_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String, index=True)
    model_name = Column(String, index=True)  # Feature summary, a brief FR description
    fr_number = Column(String, default="", index=True)  # FR number used for issue title tracking
    description = Column(Text, default="")  # Detailed feature description
    config_method = Column(Text, default="")  # Configuration method
    status = Column(String)  # pending, running, completed, failed
    progress = Column(Float, default=0.0)  # 0-100
    # L0/L2/L4 stage case statistics
    l0_total_cases = Column(Integer, default=0)
    l0_passed_cases = Column(Integer, default=0)
    l0_failed_cases = Column(Integer, default=0)
    l0_due_date = Column(Date, nullable=True)
    l2_total_cases = Column(Integer, default=0)
    l2_passed_cases = Column(Integer, default=0)
    l2_failed_cases = Column(Integer, default=0)
    l2_due_date = Column(Date, nullable=True)
    l4_total_cases = Column(Integer, default=0)
    l4_passed_cases = Column(Integer, default=0)
    l4_failed_cases = Column(Integer, default=0)
    l4_due_date = Column(Date, nullable=True)
    # Totals (stored redundantly for easier queries, can also be derived from stages)
    total_cases = Column(Integer, default=0)
    passed_cases = Column(Integer, default=0)
    failed_cases = Column(Integer, default=0)
    estimated_hours = Column(Float, default=0.0)
    start_date = Column(Date, nullable=True)
    completion_date = Column(Date, nullable=True)
    # Test owners and developers, comma-separated when multiple values exist
    test_owners = Column(String, default="")
    developers = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    bugs = relationship("Bug", back_populates="test_progress")

class Bug(Base):
    __tablename__ = "bugs"
    
    id = Column(Integer, primary_key=True, index=True)
    test_progress_id = Column(Integer, ForeignKey("test_progress.id"))
    work_task_id = Column(Integer, ForeignKey("work_tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    external_cr_number = Column(String, index=True, nullable=True)
    title = Column(String, index=True)
    description = Column(Text)
    severity = Column(String)  # critical, high, medium, low
    status = Column(String)  # fixed, analysis, other
    created_by = Column(String, default="")
    assigned_to = Column(String)
    cr_created_on = Column(DateTime(timezone=True), nullable=True)
    software_image_integration_build = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    test_progress = relationship("TestProgress", back_populates="bugs")
    work_task = relationship("WorkTask")

class KPIMetric(Base):
    __tablename__ = "kpi_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_category = Column(String, index=True, default="ASR")  # ASR, TTS, Translation, VoicecallTranslation Solution
    model_name = Column(String, index=True)
    source = Column(String, default="")
    model_size = Column(String, default="")
    description = Column(Text, default="")
    metric_name = Column(String)  # accuracy, precision, recall, f1_score, latency
    metric_value = Column(Float)
    test_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    display_name = Column(String, default="")
    password = Column(String)
    role = Column(String, default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    memberships = relationship("UserGroupMembership", back_populates="user", cascade="all, delete-orphan")
    work_tasks = relationship("WorkTask", back_populates="assignee")


class PermissionGroup(Base):
    __tablename__ = "permission_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, default="")
    can_edit_test = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    memberships = relationship("UserGroupMembership", back_populates="group", cascade="all, delete-orphan")


class UserGroupMembership(Base):
    __tablename__ = "user_group_memberships"
    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uq_user_group_membership"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("permission_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="memberships")
    group = relationship("PermissionGroup", back_populates="memberships")


class TaskOwnerAllocation(Base):
    __tablename__ = "task_owner_allocations"
    __table_args__ = (UniqueConstraint("test_progress_id", "user_id", name="uq_task_owner_allocation"),)

    id = Column(Integer, primary_key=True, index=True)
    test_progress_id = Column(Integer, ForeignKey("test_progress.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    allocated_hours = Column(Float, default=0.0)
    part_description = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    test_progress = relationship("TestProgress")
    user = relationship("User")


class WorkTask(Base):
    __tablename__ = "work_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_key = Column(String, unique=True, index=True)
    task_type = Column(String, index=True, default="Other")
    task_name = Column(String, index=True)
    task_summary = Column(Text, default="")
    task_detail = Column(Text, default="")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    estimated_hours = Column(Float, default=0.0)
    status = Column(String, index=True, default="Planned")
    assignee_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    assignee = relationship("User", back_populates="work_tasks")
