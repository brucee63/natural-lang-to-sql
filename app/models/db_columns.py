# filepath: c:\github\brucee63\natural-lang-to-sql\app\models\db_columns.py
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import BaseModel

class DbColumn(BaseModel):
    __tablename__ = 'db_columns'

    # id, created_at, updated_at are inherited from BaseModel
    table_id = Column(UUID(as_uuid=True), ForeignKey('db_tables.id', ondelete='CASCADE'), nullable=False)
    column_name = Column(String(255), nullable=False)
    data_type = Column(String(100), nullable=False)
    description = Column(Text) # Nullable based on SQL
    embedding = Column(Vector(1536)) # Nullable based on SQL
    is_primary_key = Column(Boolean, default=False)
    is_foreign_key = Column(Boolean, default=False)
    is_nullable = Column(Boolean, nullable=False, default=True)
    references_table = Column(String(255)) # Name of the referenced table
    references_column = Column(String(255)) # Name of the referenced column
    include_in_context = Column(Boolean, nullable=False, default=True)
    extra_metadata = Column(JSON) # Renamed from metadata

    table = relationship("DbTable", back_populates="columns")

    __table_args__ = (UniqueConstraint('table_id', 'column_name', name='uq_db_columns_table_id_column_name'),)
