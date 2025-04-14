from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from timescale_vector.sqlalchemy import Vector
from .base import BaseModel # Import the new base model

class SchemaMetadata(BaseModel): # Inherit from BaseModel
    __tablename__ = 'schema_metadata'

    # Remove id, created_at, updated_at as they are in BaseModel
    database_id = Column(Integer, ForeignKey('databases.id'), nullable=False)
    table_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    columns = Column(JSON, nullable=False)
    sample_data = Column(JSON)

    database = relationship("Database") # Assuming Database model exists in databases.py
