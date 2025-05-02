from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON # Add JSON
from sqlalchemy.dialects.postgresql import UUID # Import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import BaseModel # Import the new base model

class TableRelationship(BaseModel): # Inherit from BaseModel
    __tablename__ = 'table_relationships'

    # id, created_at, updated_at are inherited from BaseModel
    database_id = Column(UUID(as_uuid=True), ForeignKey('databases.id', ondelete='CASCADE'), nullable=False) # Use UUID FK
    from_table_id = Column(UUID(as_uuid=True), ForeignKey('db_tables.id', ondelete='CASCADE'), nullable=False) # Use UUID FK, rename
    to_table_id = Column(UUID(as_uuid=True), ForeignKey('db_tables.id', ondelete='CASCADE'), nullable=False) # Use UUID FK, rename
    relationship_type = Column(String(50)) # Nullable based on SQL
    from_column = Column(String(255), nullable=False) # Match VARCHAR(255)
    to_column = Column(String(255), nullable=False) # Match VARCHAR(255)
    description = Column(Text)
    embedding = Column(Vector(1536)) # Nullable based on SQL
    extra_metadata = Column(JSON) # Renamed from metadata

    database = relationship("Database", back_populates="table_relationships")
    from_table = relationship("DbTable", foreign_keys=[from_table_id], back_populates="relationships_from")
    to_table = relationship("DbTable", foreign_keys=[to_table_id], back_populates="relationships_to")

    # Optional: Add UniqueConstraint if needed based on SQL comment
    # __table_args__ = (UniqueConstraint('from_table_id', 'from_column', 'to_table_id', 'to_column', name='uq_table_relationships_fks_cols'),)
