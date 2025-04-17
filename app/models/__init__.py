# app/models/__init__.py
from .base import Base

# Import all your models here
from .databases import Database
from .query_feedback import QueryFeedback
from .query_usage_stats import QueryUsageStats
from .schema_metadata import SchemaMetadata
from .sql_samples import SqlSample
from .table_relationships import TableRelationship