# app/models/__init__.py
from .base import Base, BaseModel # Import BaseModel too

# Import all your models here
from .databases import Database
from .database_schemas import DatabaseSchema # Renamed from SchemaMetadata
from .db_tables import DbTable # New model
from .db_columns import DbColumn # New model
from .table_relationships import TableRelationship
from .sql_samples import SqlSample
from .query_feedback import QueryFeedback
from .query_usage_stats import QueryUsageStats

__all__ = [
    'Base',
    'BaseModel',
    'Database',
    'DatabaseSchema',
    'DbTable',
    'DbColumn',
    'TableRelationship',
    'SqlSample',
    'QueryFeedback',
    'QueryUsageStats',
]