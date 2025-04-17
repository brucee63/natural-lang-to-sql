from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import BaseModel # Import the new base model

class TableRelationship(BaseModel): # Inherit from BaseModel
    __tablename__ = 'table_relationships'

    # Remove id, created_at, updated_at as they are in BaseModel
    database_id = Column(Integer, ForeignKey('databases.id'), nullable=False)
    from_table = Column(String(100), nullable=False)
    to_table = Column(String(100), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    from_column = Column(String(100), nullable=False)
    to_column = Column(String(100), nullable=False)
    description = Column(Text)
    embedding = Column(Vector(1536))

    database = relationship("Database") # Assuming Database model exists in databases.py
