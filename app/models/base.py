from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID # Import UUID type
import uuid # Import uuid module for default generation
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True  # Mark this class as abstract, so it doesn't create a table

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True) # Use UUID
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False) # Use TIMESTAMPTZ, ensure not nullable
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True) # Use TIMESTAMPTZ, ensure not nullable
