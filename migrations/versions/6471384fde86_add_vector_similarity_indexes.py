"""Add vector similarity indexes

Revision ID: 6471384fde86
Revises: 204f97e8c17a
Create Date: 2025-04-29 21:21:17.123547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6471384fde86'
down_revision: Union[str, None] = '204f97e8c17a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        -- Create vector similarity indexes using HNSW with cosine distance
        CREATE INDEX idx_sql_samples_embedding ON sql_samples USING hnsw (embedding vector_cosine_ops);
        CREATE INDEX idx_database_schemas_embedding ON database_schemas USING hnsw (embedding vector_cosine_ops);
        CREATE INDEX idx_db_tables_embedding ON db_tables USING hnsw (embedding vector_cosine_ops);
        CREATE INDEX idx_db_columns_embedding ON db_columns USING hnsw (embedding vector_cosine_ops);
        CREATE INDEX idx_table_relationships_embedding ON table_relationships USING hnsw (embedding vector_cosine_ops);
        CREATE INDEX idx_query_feedback_embedding ON query_feedback USING hnsw (embedding vector_cosine_ops);
    """)


def downgrade() -> None:
    op.execute("""
        -- Drop vector similarity indexes
        DROP INDEX IF EXISTS idx_sql_samples_embedding;
        DROP INDEX IF EXISTS idx_database_schemas_embedding;
        DROP INDEX IF EXISTS idx_db_tables_embedding;
        DROP INDEX IF EXISTS idx_db_columns_embedding;
        DROP INDEX IF EXISTS idx_table_relationships_embedding;
        DROP INDEX IF EXISTS idx_query_feedback_embedding;
    """)
