from sqlalchemy import Column, Integer, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel # Import the new base model

class QueryUsageStats(BaseModel): # Inherit from BaseModel
    __tablename__ = 'query_usage_stats'

    # Remove id, created_at, updated_at as they are in BaseModel
    database_id = Column(Integer, ForeignKey('databases.id'), nullable=False)
    sql_sample_id = Column(Integer, ForeignKey('sql_samples.id'))
    nl_query = Column(Text, nullable=False)
    similarity_score = Column(Float)
    execution_time_ms = Column(Integer)
    success = Column(Boolean)
    error_message = Column(Text)

    database = relationship("Database") # Assuming Database model exists in databases.py
    sql_sample = relationship("SqlSample") # Assuming SqlSample model exists in sql_samples.py
