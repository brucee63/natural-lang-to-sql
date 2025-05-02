# filepath: c:\github\brucee63\natural-lang-to-sql\app\models\db_tables.py
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import BaseModel

class DbTable(BaseModel):
    __tablename__ = 'db_tables'

    # id, created_at, updated_at are inherited from BaseModel
    schema_id = Column(UUID(as_uuid=True), ForeignKey('database_schemas.id', ondelete='CASCADE'), nullable=False)
    table_name = Column(String(255), nullable=False)
    description = Column(Text) # Nullable based on SQL
    embedding = Column(Vector(1536)) # Nullable based on SQL
    include_in_context = Column(Boolean, nullable=False, default=True)
    sample_data = Column(JSON)
    extra_metadata = Column(JSON) # Renamed from metadata

    schema = relationship("DatabaseSchema", back_populates="tables")
    columns = relationship("DbColumn", back_populates="table")
    relationships_from = relationship("TableRelationship", foreign_keys='TableRelationship.from_table_id', back_populates="from_table")
    relationships_to = relationship("TableRelationship", foreign_keys='TableRelationship.to_table_id', back_populates="to_table")


    __table_args__ = (UniqueConstraint('schema_id', 'table_name', name='uq_db_tables_schema_id_table_name'),)
