# filepath: c:\github\brucee63\natural-lang-to-sql\app\models\database_schemas.py
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import BaseModel

class DatabaseSchema(BaseModel):
    __tablename__ = 'database_schemas'

    # id, created_at, updated_at are inherited from BaseModel
    database_id = Column(UUID(as_uuid=True), ForeignKey('databases.id', ondelete='CASCADE'), nullable=False)
    schema_name = Column(String(255), nullable=False)
    description = Column(Text) # Nullable based on SQL
    embedding = Column(Vector(1536)) # Nullable based on SQL
    include_in_context = Column(Boolean, nullable=False, default=True)
    extra_metadata = Column(JSON) # Renamed from metadata

    database = relationship("Database", back_populates="database_schemas")
    tables = relationship("DbTable", back_populates="schema")

    __table_args__ = (UniqueConstraint('database_id', 'schema_name', name='uq_database_schemas_database_id_schema_name'),)
