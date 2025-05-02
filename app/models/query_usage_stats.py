from sqlalchemy import Column, Integer, Text, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID # Import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel # Import the new base model

class QueryUsageStats(BaseModel): # Inherit from BaseModel
    __tablename__ = 'query_usage_stats'

    # id, created_at, updated_at are inherited from BaseModel
    database_id = Column(UUID(as_uuid=True), ForeignKey('databases.id', ondelete='CASCADE'), nullable=False) # Use UUID FK
    sql_sample_id = Column(UUID(as_uuid=True), ForeignKey('sql_samples.id', ondelete='SET NULL')) # Use UUID FK, SET NULL
    nl_query = Column(Text) # Nullable based on SQL
    similarity_score = Column(Float)
    execution_time_ms = Column(Integer)
    success = Column(Boolean)
    error_message = Column(Text)

    database = relationship("Database", back_populates="query_usage_stats")
    sql_sample = relationship("SqlSample", back_populates="usage_stats")
