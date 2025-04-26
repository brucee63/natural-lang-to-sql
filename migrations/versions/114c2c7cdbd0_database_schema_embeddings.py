"""database schema embeddings

Revision ID: 114c2c7cdbd0
Revises: 8848f142f4f9
Create Date: 2025-04-25 22:23:56.574918

"""
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '114c2c7cdbd0'
down_revision: Union[str, None] = '8848f142f4f9' # Make sure this points to your previous migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define paths relative to this script's location (migrations/versions)
SQL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sql'))
DATABASES_SQL_PATH = os.path.join(SQL_DIR, 'databases.sql')
SCHEMA_METADATA_SQL_PATH = os.path.join(SQL_DIR, 'schema_metadata_inserts.sql')

def upgrade() -> None:
    """Reads SQL files from migrations/sql and executes their content."""
    # Execute databases.sql if it exists
    if os.path.exists(DATABASES_SQL_PATH):
        with open(DATABASES_SQL_PATH, 'r') as f:
            sql_commands = f.read()
            # Execute the entire file content; ensure it doesn't contain problematic transaction controls
            # Split commands if necessary, but often reading the whole file works if statements are ; terminated
            op.execute(sql_commands)
            print(f"Executed content from {DATABASES_SQL_PATH}") # Optional: for logging/debugging
    else:
        print(f"Warning: {DATABASES_SQL_PATH} not found. Skipping.")

    # Execute schema_metadata_inserts.sql if it exists
    if os.path.exists(SCHEMA_METADATA_SQL_PATH):
        with open(SCHEMA_METADATA_SQL_PATH, 'r') as f:
            sql_commands = f.read()
            op.execute(sql_commands)
            print(f"Executed content from {SCHEMA_METADATA_SQL_PATH}") # Optional: for logging/debugging
    else:
        print(f"Warning: {SCHEMA_METADATA_SQL_PATH} not found. Skipping.")


def downgrade() -> None:
    """Removes the data inserted by the upgrade."""
    # IMPORTANT: Verify that these DELETE statements correctly target the data
    # inserted by your .sql files. This assumes database_id = 1 was used.
    # Adjust the WHERE clauses if necessary.

    # Delete from schema_metadata first due to potential foreign key constraints
    op.execute("DELETE FROM schema_metadata WHERE database_id = 1;") # Adjust database_id if needed
    print("Executed DELETE FROM schema_metadata for database_id = 1") # Optional

    # Delete from databases
    op.execute("DELETE FROM databases WHERE id = 1;") # Adjust ID if needed
    print("Executed DELETE FROM databases for id = 1") # Optional
