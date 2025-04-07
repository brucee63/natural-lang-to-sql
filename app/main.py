import services.llm_factory as llm_factory
import database.sqlite_client as sqlite_client

def load_llm_factory():
    # Load the settings
    settings = llm_factory.get_settings()
    print(f"opeanai api_key set: {settings.openai.api_key is not None}")
    print(f"default model: {settings.openai.default_model}")

if __name__ == "__main__":
    load_llm_factory()    
    # Initialize the SQLite client in the data/spider/sqlite directory
    client = sqlite_client.SQLiteClient('data/spider/sqlite/student_transcripts_tracking.sqlite')
    df = client.execute_query("SELECT * FROM Departments LIMIT 10;")
    print(df.info())
    print(df.head())