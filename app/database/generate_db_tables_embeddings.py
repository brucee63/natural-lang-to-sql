# filepath: c:\github\brucee63\natural-lang-to-sql\app\database\generate_schema_embeddings.py
import os
import json
import logging
from openai import OpenAI, OpenAIError
import sys


# Add project root to sys.path to allow imports from app package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.config.settings import get_settings
from app.database.sqlite_client import SQLiteClient

# --- Configuration ---
SQLITE_DB_PATH = os.path.join(project_root, 'data', 'spider', 'sqlite', 'student_transcripts_tracking.sqlite')
DESCRIPTIONS_PATH = os.path.join(project_root, 'data', 'table_descriptions.json')
OUTPUT_SQL_PATH = os.path.join(project_root, 'migrations', 'sql', 'db_tables_inserts.sql') # Updated output path
TARGET_DATABASE_NAME = 'student_transcripts_tracking' # Database name to look up
TARGET_SCHEMA_NAME = 'public' # Schema name to look up
EMBEDDING_MODEL = "text-embedding-3-small" # Or your preferred OpenAI model
# Ensure OPENAI_API_KEY environment variable is set

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- OpenAI Client ---
try:
    openai_client = OpenAI() # Reads OPENAI_API_KEY from environment variable
except OpenAIError as e:
    logging.error(f"Failed to initialize OpenAI client: {e}")
    sys.exit(1)

# --- Helper Functions ---
def get_openai_embedding(text_to_embed: str):
    """Generates embedding for the given text using OpenAI."""
    try:
        response = openai_client.embeddings.create(
            input=text_to_embed,
            model=EMBEDDING_MODEL
        )
        # Correct access to embedding data based on v1.0+ openai library
        return response.data[0].embedding
    except OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
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
    """Retrieves the CREATE TABLE statement for a given table (used for default description)."""
    try:
        # Pass the query as a plain string
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

def load_descriptions(path: str):
    """Loads table descriptions from a JSON file."""
    try:
        with open(path, 'r') as f:
            descriptions_list = json.load(f)
        # Convert list of dicts to dict keyed by table_name
        return {item['table_name']: item['description'] for item in descriptions_list}
    except FileNotFoundError:
        logging.error(f"Description file not found: {path}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from file: {path}")
        return {}
    except Exception as e:
        logging.error(f"Failed to load descriptions: {e}")
        return {}

# --- Main Script ---
if __name__ == "__main__":
    logging.info("Starting db_tables embedding generation process...")

    # Check if SQLite DB exists
    if not os.path.exists(SQLITE_DB_PATH):
        logging.error(f"SQLite database not found at: {SQLITE_DB_PATH}")
        sys.exit(1)

    # Load descriptions
    table_descriptions = load_descriptions(DESCRIPTIONS_PATH)
    if not table_descriptions:
        logging.warning("No table descriptions loaded. Proceeding without them.")

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

            # Get description (schema is no longer needed for embedding text)
            description = table_descriptions.get(table_name)
            if not description:
                 # Optionally get schema just for a default description if needed
                 # schema_for_desc = get_table_schema(sqlite_client, table_name) or ""
                 # description = f"Definition for the {table_name} table." # Simpler default
                 logging.warning(f"No description found for table '{table_name}'. Using empty description.")
                 description = "" # Use empty string if no description found

            # Prepare text for embedding (only table name and description)
            text_to_embed = f"Table Name: {table_name}\nDescription: {description}"

            # Generate embedding
            logging.info(f"Generating embedding for {table_name}...")
            embedding = get_openai_embedding(text_to_embed)
            if not embedding:
                logging.warning(f"Could not generate embedding for {table_name}. Skipping.")
                continue

            # Format embedding list as string for PostgreSQL vector type
            embedding_str = str(embedding).replace(" ", "") # Compact string representation

            # Escape single quotes in text fields for SQL
            table_name_sql = table_name.replace("'", "''")
            description_sql = description.replace("'", "''")

            # Get table schema for metadata
            table_schema = get_table_schema(sqlite_client, table_name)
            if not table_schema:
                logging.warning(f"Could not retrieve schema for table {table_name} for metadata.")
                table_schema_json_sql = "NULL"
            else:
                # Format schema as JSON string for extra_metadata
                extra_metadata = {"schema_definition": table_schema}
                # Escape single quotes for SQL
                table_schema_json_sql = f"'{json.dumps(extra_metadata).replace("'", "''")}'"

            # Create INSERT statement for db_tables
            # Fetches schema_id dynamically
            # id is now explicitly set using uuid_generate_v4()
            # created_at uses NOW()
            insert_sql = (
                f"INSERT INTO db_tables (id, schema_id, table_name, description, embedding, include_in_context, sample_data, extra_metadata, created_at, updated_at) VALUES (\n"
                f"    uuid_generate_v4(),\n"
                f"    (SELECT ds.id FROM database_schemas ds JOIN databases d ON ds.database_id = d.id WHERE d.name = '{TARGET_DATABASE_NAME}' AND ds.schema_name = '{TARGET_SCHEMA_NAME}' LIMIT 1),\n"
                f"    '{table_name_sql}',\n"
                f"    '{description_sql}',\n"
                f"    '{embedding_str}',\n"
                f"    TRUE, -- include_in_context\n"
                f"    NULL, -- sample_data\n"
                f"    {table_schema_json_sql}, -- extra_metadata (JSON with schema)\n"
                f"    NOW(), -- created_at\n"
                f"    NULL -- updated_at\n"
                f");"
            )
            sql_inserts.append(insert_sql)
            logging.info(f"Generated INSERT statement for {table_name}")

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
                f.write("-- SQL INSERT statements for db_tables\n")
                f.write(f"-- Generated on: {logging.Formatter().formatTime(logging.LogRecord(None, None, '', 0, '', (), None, None))}\n\n")
                for stmt in sql_inserts:
                    f.write(stmt + "\n\n") # Add extra newline for readability
            logging.info(f"Successfully wrote {len(sql_inserts)} INSERT statements to {OUTPUT_SQL_PATH}")
        except IOError as e:
            logging.error(f"Failed to write SQL output file: {e}")
    else:
        logging.warning("No INSERT statements were generated.")

    logging.info("db_tables embedding generation process finished.")
