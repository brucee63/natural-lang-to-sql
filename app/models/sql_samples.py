from sqlalchemy import Column, Integer, Text, Float, SmallInteger, ForeignKey, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID # Import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .base import BaseModel # Import the new base model

class SqlSample(BaseModel): # Inherit from BaseModel
    __tablename__ = 'sql_samples'

    # id, created_at, updated_at are inherited from BaseModel
    database_id = Column(UUID(as_uuid=True), ForeignKey('databases.id', ondelete='CASCADE'), nullable=False) # Use UUID FK
    query_text = Column(Text, nullable=False)
    nl_description = Column(Text) # Nullable based on SQL
    embedding = Column(Vector(1536)) # Single embedding column, nullable based on SQL
    complexity = Column(SmallInteger)
    tags = Column(ARRAY(Text))
    avg_rating = Column(Float)
    feedback_count = Column(Integer, default=0)
    extra_metadata = Column(JSON) # Renamed from metadata

    database = relationship("Database", back_populates="sql_samples")
    feedback = relationship("QueryFeedback", back_populates="sql_sample")
    usage_stats = relationship("QueryUsageStats", back_populates="sql_sample")
