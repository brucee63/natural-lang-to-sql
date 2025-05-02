from sqlalchemy import Column, Integer, Text, Boolean, SmallInteger, ForeignKey, CheckConstraint, String, JSON # Add String, JSON
from sqlalchemy.dialects.postgresql import UUID # Import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import BaseModel # Import the new base model

class QueryFeedback(BaseModel): # Inherit from BaseModel
    __tablename__ = 'query_feedback'

    # id, created_at, updated_at are inherited from BaseModel
    database_id = Column(UUID(as_uuid=True), ForeignKey('databases.id', ondelete='CASCADE'), nullable=False) # Use UUID FK
    sql_sample_id = Column(UUID(as_uuid=True), ForeignKey('sql_samples.id', ondelete='SET NULL')) # Use UUID FK, SET NULL
    nl_query = Column(Text) # Nullable based on SQL
    embedding = Column(Vector(1536)) # Rename nl_query_embedding, nullable based on SQL
    generated_sql = Column(Text)
    rating = Column(SmallInteger, CheckConstraint('rating BETWEEN 1 AND 5')) # Nullable based on SQL
    feedback_text = Column(Text)
    is_correct = Column(Boolean) # Nullable based on SQL
    correction = Column(Text) # Add correction column
    user_id = Column(String(255)) # Add user_id column
    extra_metadata = Column(JSON) # Renamed from metadata

    database = relationship("Database", back_populates="query_feedback")
    sql_sample = relationship("SqlSample", back_populates="feedback")
