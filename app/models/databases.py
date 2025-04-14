from sqlalchemy import Column, String, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from .base import BaseModel # Import the new base model

class Database(BaseModel): # Inherit from BaseModel
    __tablename__ = 'databases'

    # Remove id, created_at, updated_at as they are in BaseModel
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
