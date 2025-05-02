# filepath: c:\\github\\brucee63\\natural-lang-to-sql\\app\\database\\generate_db_columns_embeddings.py
import os
import json
import logging
import re
from openai import OpenAI, OpenAIError
import sys

# Add project root to sys.path to allow imports from app package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.database.sqlite_client import SQLiteClient
# Assuming settings load .env correctly as discussed previously
from app.config.settings import get_settings

# --- Configuration ---
SQLITE_DB_PATH = os.path.join(project_root, 'data', 'spider', 'sqlite', 'student_transcripts_tracking.sqlite')
# Descriptions not directly used for columns, but kept for potential future use or consistency
DESCRIPTIONS_PATH = os.path.join(project_root, 'data', 'table_descriptions.json')
OUTPUT_SQL_PATH = os.path.join(project_root, 'migrations', 'sql', 'db_columns_inserts.sql') # Updated output path
TARGET_DATABASE_NAME = 'student_transcripts_tracking' # Database name to look up
TARGET_SCHEMA_NAME = 'public' # Schema name to look up
EMBEDDING_MODEL = "text-embedding-3-small" # Or your preferred OpenAI model
# Ensure OPENAI_API_KEY environment variable is set via .env loaded by settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- OpenAI Client ---
try:
    # Assumes OPENAI_API_KEY is loaded from .env when settings are imported (even if not used directly here)
    # or set directly in the environment
    openai_client = OpenAI()
except OpenAIError as e:
    logging.error(f"Failed to initialize OpenAI client: {e}. Ensure OPENAI_API_KEY is set.")
    sys.exit(1)
except Exception as e:
    logging.error(f"An unexpected error occurred during OpenAI client initialization: {e}")
    sys.exit(1)


# --- Helper Functions ---
def get_openai_embedding(text_to_embed: str):
    """Generates embedding for the given text using OpenAI."""
    if not text_to_embed:
        logging.warning("Empty text provided for embedding. Skipping.")
        return None
    try:
        response = openai_client.embeddings.create(
            input=text_to_embed,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except OpenAIError as e:
        logging.error(f"OpenAI API error during embedding generation: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during embedding: {e}")
        return None

def get_tables(client: SQLiteClient):
    """Retrieves a list of table names from the SQLite database."""
    try:
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        df = client.execute_query(query)
        return df['name'].tolist()
    except Exception as e:
        logging.error(f"Failed to retrieve tables: {e}")
        return []

def get_table_schema(client: SQLiteClient, table_name: str):
    """Retrieves the CREATE TABLE statement for a given table."""
    try:
        query = "SELECT sql FROM sqlite_master WHERE type='table' AND name = :table_name"
        df = client.execute_query(query, params={"table_name": table_name})
        if not df.empty:
            return df['sql'].iloc[0]
        else:
            logging.warning(f"Schema not found for table: {table_name}")
            return None
    except Exception as e:
        logging.error(f"Failed to retrieve schema for table {table_name}: {e}")
        return None

def parse_column_definitions(create_table_sql: str):
    """Parses a CREATE TABLE statement to extract column names and their definitions."""
    columns = {}
    if not create_table_sql:
        return columns

    # Basic parsing: find content within the first level parentheses
    match = re.search(r'\((.*)\)', create_table_sql, re.DOTALL)
    if not match:
        logging.warning(f"Could not parse columns from schema: {create_table_sql}")
        return columns

    content = match.group(1).strip()

    # Split columns, handling potential complexities like constraints defined separately
    # This regex attempts to split by comma, but not commas inside parentheses (e.g., for CHECK constraints)
    # It's not perfect for all SQL dialects but works for many common SQLite cases.
    # It also tries to ignore table-level constraints like PRIMARY KEY (col1, col2) or FOREIGN KEY
    column_parts = re.split(r',(?!(?:[^()]|\([^()]*\))*\))', content)

    for part in column_parts:
        part = part.strip()
        if not part or part.upper().startswith(('CONSTRAINT', 'PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK')):
            # Skip table-level constraints or empty parts
            continue

        # Extract column name (usually the first word)
        # Handle quoted identifiers if necessary (though less common in SQLite column names)
        match_name = re.match(r'["`]?([\w]+)["`]?', part)
        if match_name:
            column_name = match_name.group(1)
            # The definition is the whole part for simplicity, including constraints
            columns[column_name] = part
        else:
            logging.warning(f"Could not extract column name from part: {part}")


    return columns

def parse_column_details(column_def_str, table_level_pks=None):
    """Extracts data_type, is_primary_key, is_nullable from a column definition string and table-level PKs."""
    # Remove column name
    tokens = column_def_str.strip().split()
    if not tokens:
        return None, False, True
    col_name = tokens[0]
    # Data type is the next token (may be more than one word, e.g., 'DOUBLE PRECISION')
    # We'll take tokens until we hit a constraint keyword
    constraint_keywords = {'PRIMARY', 'KEY', 'NOT', 'NULL', 'UNIQUE', 'CHECK', 'REFERENCES', 'DEFAULT', 'AUTOINCREMENT', 'COLLATE'}
    data_type_tokens = []
    for token in tokens[1:]:
        if token.upper() in constraint_keywords:
            break
        data_type_tokens.append(token)
    data_type = ' '.join(data_type_tokens) if data_type_tokens else None
    # Primary key (column or table level)
    is_primary_key = 'PRIMARY KEY' in column_def_str.upper()
    if table_level_pks and col_name in table_level_pks:
        is_primary_key = True
    # Nullability
    if 'NOT NULL' in column_def_str.upper() or is_primary_key:
        is_nullable = False
    else:
        is_nullable = True
    return data_type, is_primary_key, is_nullable

def parse_table_level_primary_keys(create_table_sql):
    """Returns a set of column names that are part of a table-level PRIMARY KEY constraint."""
    # Look for PRIMARY KEY (...) outside of column definitions
    matches = re.findall(r'PRIMARY KEY\s*\(([^)]+)\)', create_table_sql, re.IGNORECASE)
    pk_cols = set()
    for match in matches:
        cols = [col.strip(' "`') for col in match.split(',')]
        pk_cols.update(cols)
    return pk_cols

def parse_foreign_keys(create_table_sql):
    """Returns a dict mapping column names to (referenced_table, referenced_column) for foreign keys."""
    fk_map = {}
    # Inline REFERENCES: col_name ... REFERENCES ref_table(ref_col)
    inline = re.findall(r'([`"\w]+)\s+[^,]*REFERENCES\s+([`"\w]+)\s*\(([^)]+)\)', create_table_sql, re.IGNORECASE)
    for col, ref_table, ref_col in inline:
        fk_map[col.strip('`"')] = (ref_table.strip('`"'), ref_col.strip('`" '))
    # Table-level FOREIGN KEY (col) REFERENCES ref_table(ref_col)
    table_level = re.findall(r'FOREIGN KEY\s*\(([^)]+)\)\s*REFERENCES\s+([`"\w]+)\s*\(([^)]+)\)', create_table_sql, re.IGNORECASE)
    for cols, ref_table, ref_cols in table_level:
        col_list = [c.strip('`" ') for c in cols.split(',')]
        ref_col_list = [c.strip('`" ') for c in ref_cols.split(',')]
        for c, rc in zip(col_list, ref_col_list):
            fk_map[c] = (ref_table.strip('`"'), rc)
    return fk_map


# --- Main Script ---
if __name__ == "__main__":
    logging.info("Starting db_columns embedding generation process...")

    # Check if SQLite DB exists
    if not os.path.exists(SQLITE_DB_PATH):
        logging.error(f"SQLite database not found at: {SQLITE_DB_PATH}")
        sys.exit(1)

    sql_inserts = []
    sqlite_client = None

    try:
        # Connect to SQLite
        logging.info(f"Connecting to SQLite database: {SQLITE_DB_PATH}")
        sqlite_client = SQLiteClient(db_path=SQLITE_DB_PATH)

        # Get table names
        tables = get_tables(sqlite_client)
        logging.info(f"Found tables: {tables}")

        if not tables:
            logging.warning("No tables found in the database.")
            sys.exit(0)

        # Process each table
        for table_name in tables:
            logging.info(f"Processing table: {table_name}")
            table_schema_sql = get_table_schema(sqlite_client, table_name)
            if not table_schema_sql:
                logging.warning(f"Skipping table {table_name} due to missing schema.")
                continue

            table_level_pks = parse_table_level_primary_keys(table_schema_sql)
            fk_map = parse_foreign_keys(table_schema_sql)

            column_definitions = parse_column_definitions(table_schema_sql)
            if not column_definitions:
                logging.warning(f"No column definitions parsed for table {table_name}.")
                continue

            logging.info(f"Found columns for {table_name}: {list(column_definitions.keys())}")

            # Escape table name for use in subquery
            table_name_sql = table_name.replace("'", "''")

            # Process each column
            for column_name, column_def_str in column_definitions.items():
                logging.info(f"  Processing column: {column_name}")

                # Prepare text for embedding (only column name)
                text_to_embed = f"Column Name: {column_name}"

                # Generate embedding
                embedding = get_openai_embedding(text_to_embed)
                if not embedding:
                    logging.warning(f"  Could not generate embedding for column {column_name}. Skipping.")
                    continue

                # Format embedding list as string for PostgreSQL vector type
                embedding_str = str(embedding).replace(" ", "") # Compact string representation

                # Prepare extra_metadata
                extra_metadata = {"column_definition": column_def_str}
                escaped_metadata = json.dumps(extra_metadata).replace("'", "''")
                extra_metadata_sql = f"'{escaped_metadata}'"

                # Escape column name for SQL
                column_name_sql = column_name.replace("'", "''")

                data_type, is_primary_key, is_nullable = parse_column_details(column_def_str, table_level_pks)
                # Foreign key info
                fk_info = fk_map.get(column_name)
                is_foreign_key = fk_info is not None
                references_table = f"'{fk_info[0]}'" if fk_info else 'NULL'
                references_column = f"'{fk_info[1]}'" if fk_info else 'NULL'

                # Prepare SQL value for data_type
                data_type_sql = f"'{data_type}'" if data_type else "NULL"

                # Create INSERT statement for db_columns
                insert_sql = (
                    f"INSERT INTO db_columns (id, table_id, column_name, data_type, description, embedding, is_primary_key, is_foreign_key, is_nullable, references_table, references_column, include_in_context, extra_metadata, created_at, updated_at) VALUES (\n"
                    f"    uuid_generate_v4(),\n"
                    f"    (SELECT dt.id FROM db_tables dt JOIN database_schemas ds ON dt.schema_id = ds.id JOIN databases d ON ds.database_id = d.id WHERE d.name = '{TARGET_DATABASE_NAME}' AND ds.schema_name = '{TARGET_SCHEMA_NAME}' AND dt.table_name = '{table_name_sql}' LIMIT 1),\n"
                    f"    '{column_name_sql}',\n"
                    f"    {data_type_sql},\n"
                    f"    NULL, -- description (can be added manually or from another source)\n"
                    f"    '{embedding_str}',\n"
                    f"    {'TRUE' if is_primary_key else 'FALSE'},\n"
                    f"    {'TRUE' if is_foreign_key else 'FALSE'},\n"
                    f"    {'TRUE' if is_nullable else 'FALSE'},\n"
                    f"    {references_table},\n"
                    f"    {references_column},\n"
                    f"    TRUE, -- include_in_context\n"
                    f"    {extra_metadata_sql}, -- extra_metadata (JSON with column definition)\n"
                    f"    NOW(), -- created_at\n"
                    f"    NULL -- updated_at\n"
                    f");"
                )
                sql_inserts.append(insert_sql)
                logging.info(f"  Generated INSERT statement for column {column_name}")

    except ConnectionError as e:
         logging.error(f"Database connection error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        if sqlite_client:
            logging.info("Closing SQLite connection.")
            sqlite_client.close()

    # Write INSERT statements to file
    if sql_inserts:
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(OUTPUT_SQL_PATH), exist_ok=True)
            with open(OUTPUT_SQL_PATH, 'w') as f:
                f.write("-- SQL INSERT statements for db_columns\n")
                f.write(f"-- Generated on: {logging.Formatter().formatTime(logging.LogRecord(None, None, '', 0, '', (), None, None))}\n\n")
                for stmt in sql_inserts:
                    f.write(stmt + "\n\n") # Add extra newline for readability
            logging.info(f"Successfully wrote {len(sql_inserts)} INSERT statements to {OUTPUT_SQL_PATH}")
        except IOError as e:
            logging.error(f"Failed to write SQL output file: {e}")
    else:
        logging.warning("No INSERT statements were generated.")

    logging.info("db_columns embedding generation process finished.")

