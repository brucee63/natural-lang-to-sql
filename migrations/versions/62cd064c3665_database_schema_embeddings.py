"""database schema embeddings

Revision ID: 62cd064c3665
Revises: 6471384fde86
Create Date: 2025-04-29 21:26:52.652334

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision: str = '62cd064c3665'
down_revision: Union[str, None] = '6471384fde86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define paths relative to this script's location (migrations/versions)
SQL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sql'))
ENABLED_EXTENSIONS_SQL_DIR = os.path.join(SQL_DIR, 'enabled_extensions.sql')
DATABASES_SQL_PATH = os.path.join(SQL_DIR, 'databases_inserts.sql')
DATABASE_SCHEMAS_SQL_PATH = os.path.join(SQL_DIR, 'database_schemas_inserts.sql')
DB_TABLES_SQL_PATH = os.path.join(SQL_DIR, 'db_tables_inserts.sql')
DB_COLUMNS_SQL_PATH = os.path.join(SQL_DIR, 'db_columns_inserts.sql')

def upgrade() -> None:
    """Reads SQL files from migrations/sql and executes their content."""

    # Execute enabled_extensions.sql if it exists
    if os.path.exists(ENABLED_EXTENSIONS_SQL_DIR):
        with open(ENABLED_EXTENSIONS_SQL_DIR, 'r') as f:
            sql_commands = f.read()
            # Execute the entire file content; ensure it doesn't contain problematic transaction controls
            # Split commands if necessary, but often reading the whole file works if statements are ; terminated
            op.execute(sql_commands)
            print(f"Executed content from {ENABLED_EXTENSIONS_SQL_DIR}")
    else:
        print(f"Warning: {ENABLED_EXTENSIONS_SQL_DIR} not found. Skipping.")

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
    if os.path.exists(DATABASE_SCHEMAS_SQL_PATH):
        with open(DATABASE_SCHEMAS_SQL_PATH, 'r') as f:
            sql_commands = f.read()
            op.execute(sql_commands)
            print(f"Executed content from {DATABASE_SCHEMAS_SQL_PATH}") # Optional: for logging/debugging
    else:
        print(f"Warning: {DATABASE_SCHEMAS_SQL_PATH} not found. Skipping.")
    
    # Execute db_tables_inserts.sql if it exists
    if os.path.exists(DB_TABLES_SQL_PATH):
        with open(DB_TABLES_SQL_PATH, 'r') as f:
            sql_commands = f.read()
            op.execute(sql_commands)
            print(f"Executed content from {DB_TABLES_SQL_PATH}") # Optional: for logging/debugging
    else:
        print(f"Warning: {DB_TABLES_SQL_PATH} not found. Skipping.")
    
    # Execute db_columns_inserts.sql if it exists
    if os.path.exists(DB_COLUMNS_SQL_PATH):
        with open(DB_COLUMNS_SQL_PATH, 'r') as f:
            sql_commands = f.read()
            op.execute(sql_commands)
            print(f"Executed content from {DB_COLUMNS_SQL_PATH}") # Optional: for logging/debugging
    else:
        print(f"Warning: {DB_COLUMNS_SQL_PATH} not found. Skipping.")

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

