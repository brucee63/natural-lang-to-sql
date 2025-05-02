from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID # Import UUID
from sqlalchemy.orm import DeclarativeBase, relationship # Import relationship
from sqlalchemy.sql import func
from .base import BaseModel # Import the new base model

class Database(BaseModel): # Inherit from BaseModel
    __tablename__ = 'databases'

    # id, created_at, updated_at are inherited from BaseModel
    name = Column(String(255), nullable=False, unique=True) # Match VARCHAR(255)
    description = Column(Text)

    # Define relationships (optional but good practice)
    sql_samples = relationship("SqlSample", back_populates="database")
    database_schemas = relationship("DatabaseSchema", back_populates="database")
    table_relationships = relationship("TableRelationship", back_populates="database")
    query_feedback = relationship("QueryFeedback", back_populates="database")
    query_usage_stats = relationship("QueryUsageStats", back_populates="database")
