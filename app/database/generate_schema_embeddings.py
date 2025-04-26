# filepath: c:\github\brucee63\natural-lang-to-sql\app\database\generate_schema_embeddings.py
import os
import json
import logging
from openai import OpenAI, OpenAIError
from sqlalchemy.sql import text # Correct import for text()
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
OUTPUT_SQL_PATH = os.path.join(project_root, 'migrations', 'sql', 'schema_metadata_inserts.sql') # Updated path
DATABASE_ID = 1 # As specified
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
    """Retrieves the CREATE TABLE statement for a given table."""
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
    logging.info("Starting schema embedding generation process...")

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

            # Get schema
            schema = get_table_schema(sqlite_client, table_name)
            if not schema:
                continue # Skip if schema couldn't be retrieved

            # Get description
            description = table_descriptions.get(table_name, f"Schema for the {table_name} table.") # Default description
            if table_name not in table_descriptions:
                 logging.warning(f"No description found for table '{table_name}'. Using default.")

            # Prepare text for embedding
            text_to_embed = f"Table Name: {table_name}\nSchema: {schema}\nDescription: {description}"

            # Generate embedding
            logging.info(f"Generating embedding for {table_name}...")
            embedding = get_openai_embedding(text_to_embed)
            if not embedding:
                logging.warning(f"Could not generate embedding for {table_name}. Skipping.")
                continue

            # Format data for INSERT statement
            # Store the raw schema string within a JSON object for the 'columns' field
            columns_json = json.dumps({"schema_definition": schema})
            # Format embedding list as string for PostgreSQL vector type
            embedding_str = str(embedding).replace(" ", "") # Compact string representation

            # Escape single quotes in text fields for SQL
            table_name_sql = table_name.replace("'", "''")
            description_sql = description.replace("'", "''")
            columns_json_sql = columns_json.replace("'", "''")

            # Create INSERT statement including created_at and updated_at
            # Assumes 'schema_metadata' table columns: database_id, table_name, description, embedding, columns, sample_data, created_at, updated_at
            # id is serial
            insert_sql = (
                f"INSERT INTO schema_metadata (database_id, table_name, description, embedding, columns, sample_data, created_at, updated_at) VALUES "
                f"({DATABASE_ID}, '{table_name_sql}', '{description_sql}', '{embedding_str}', '{columns_json_sql}', NULL, NOW(), NULL);"
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
            with open(OUTPUT_SQL_PATH, 'w') as f:
                f.write("-- SQL INSERT statements for schema_metadata\n")
                f.write("-- Generated on: " + logging.Formatter().formatTime(logging.LogRecord(None, None, "", 0, "", (), None, None)) + "\n\n")
                for stmt in sql_inserts:
                    f.write(stmt + "\n")
            logging.info(f"Successfully wrote {len(sql_inserts)} INSERT statements to {OUTPUT_SQL_PATH}")
        except IOError as e:
            logging.error(f"Failed to write SQL output file: {e}")
    else:
        logging.warning("No INSERT statements were generated.")

    logging.info("Schema embedding generation process finished.")
