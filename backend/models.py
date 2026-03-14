from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class TestProgress(Base):
    __tablename__ = "test_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String, index=True)
    model_name = Column(String, index=True)  # 功能描述，简述FR功能
    fr_number = Column(String, default="", index=True)  # FR号码，用于 issue 标题追踪
    description = Column(Text, default="")  # 功能的具体描述
    config_method = Column(Text, default="")  # 配置方式
    status = Column(String)  # pending, running, completed, failed
    progress = Column(Float, default=0.0)  # 0-100
    # L0/L2/L4 阶段用例统计
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
    # 总计（可冗余存储便于查询，也可从各阶段求和）
    total_cases = Column(Integer, default=0)
    passed_cases = Column(Integer, default=0)
    failed_cases = Column(Integer, default=0)
    # 测试负责人、开发人员，多个用逗号分隔
    test_owners = Column(String, default="")
    developers = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    bugs = relationship("Bug", back_populates="test_progress")

class Bug(Base):
    __tablename__ = "bugs"
    
    id = Column(Integer, primary_key=True, index=True)
    test_progress_id = Column(Integer, ForeignKey("test_progress.id"))
    title = Column(String, index=True)
    description = Column(Text)
    severity = Column(String)  # critical, high, medium, low
    status = Column(String)  # open, in_progress, resolved, closed
    assigned_to = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    test_progress = relationship("TestProgress", back_populates="bugs")

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
