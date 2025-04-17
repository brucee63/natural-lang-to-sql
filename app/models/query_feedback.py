from sqlalchemy import Column, Integer, Text, Boolean, SmallInteger, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import BaseModel # Import the new base model

class QueryFeedback(BaseModel): # Inherit from BaseModel
    __tablename__ = 'query_feedback'

    # Remove id, created_at, updated_at as they are in BaseModel
    database_id = Column(Integer, ForeignKey('databases.id'), nullable=False)
    sql_sample_id = Column(Integer, ForeignKey('sql_samples.id'))
    nl_query = Column(Text, nullable=False)
    nl_query_embedding = Column(Vector(1536), nullable=False)
    generated_sql = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    feedback_text = Column(Text)
    rating = Column(SmallInteger, CheckConstraint('rating BETWEEN 1 AND 5'))

    database = relationship("Database") # Assuming Database model exists in databases.py
    sql_sample = relationship("SqlSample") # Assuming SqlSample model exists in sql_samples.py
