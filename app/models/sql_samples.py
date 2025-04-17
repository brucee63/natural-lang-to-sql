from sqlalchemy import Column, Integer, Text, Float, SmallInteger, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .base import BaseModel # Import the new base model

class SqlSample(BaseModel): # Inherit from BaseModel
    __tablename__ = 'sql_samples'

    # Remove id, created_at, updated_at as they are in BaseModel
    database_id = Column(Integer, ForeignKey('databases.id'), nullable=False)
    query_text = Column(Text, nullable=False)
    nl_description = Column(Text, nullable=False)
    query_embedding = Column(Vector(1536), nullable=False)
    description_embedding = Column(Vector(1536), nullable=False)
    complexity = Column(SmallInteger)
    tags = Column(ARRAY(Text))
    avg_rating = Column(Float)
    feedback_count = Column(Integer, default=0)

    database = relationship("Database") # Assuming Database model exists in databases.py
