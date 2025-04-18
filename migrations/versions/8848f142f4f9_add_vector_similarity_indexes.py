"""Add vector similarity indexes

Revision ID: 8848f142f4f9
Revises: befc7b7ab2c2
Create Date: 2025-04-17 20:17:08.463217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8848f142f4f9'
down_revision: Union[str, None] = 'befc7b7ab2c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Execute raw SQL to create the vector similarity indexes
    op.execute("""
        -- Create vector similarity indexes
        CREATE INDEX idx_sql_samples_query_embedding ON sql_samples USING hnsw (query_embedding vector_cosine_ops);
        CREATE INDEX idx_sql_samples_description_embedding ON sql_samples USING hnsw (description_embedding vector_cosine_ops);
        CREATE INDEX idx_schema_metadata_embedding ON schema_metadata USING hnsw (embedding vector_cosine_ops);
        CREATE INDEX idx_table_relationships_embedding ON table_relationships USING hnsw (embedding vector_cosine_ops);
        CREATE INDEX idx_query_feedback_nl_embedding ON query_feedback USING hnsw (nl_query_embedding vector_cosine_ops);

        CREATE INDEX idx_sql_samples_tags ON sql_samples USING GIN (tags);
        CREATE INDEX idx_schema_metadata_table_name ON schema_metadata (database_id, table_name);
        CREATE INDEX idx_query_feedback_is_correct ON query_feedback (is_correct);
        CREATE INDEX idx_query_feedback_rating ON query_feedback (rating);
    """)

def downgrade() -> None:
    # Drop the indexes in the reverse order if needed
    op.execute("""
        DROP INDEX IF EXISTS idx_query_feedback_rating;
        DROP INDEX IF EXISTS idx_query_feedback_is_correct;
        DROP INDEX IF EXISTS idx_schema_metadata_table_name;
        DROP INDEX IF EXISTS idx_sql_samples_tags;
        
        DROP INDEX IF EXISTS idx_query_feedback_nl_embedding;
        DROP INDEX IF EXISTS idx_table_relationships_embedding;
        DROP INDEX IF EXISTS idx_schema_metadata_embedding;
        DROP INDEX IF EXISTS idx_sql_samples_description_embedding;
        DROP INDEX IF EXISTS idx_sql_samples_query_embedding;
    """)
