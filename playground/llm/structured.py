import json
import os
import sys
from pydantic import BaseModel
import database.sqlite_client as sqlite_client

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

current_dir = os.path.dirname(os.path.abspath(__file__))

# Move two levels up to the 'project' directory
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "app"))

# Add the project root to sys.path
sys.path.append(project_root)

from prompts.prompt_manager import PromptManager

# read the table_descriptions.json file
path = os.path.abspath(os.path.join(current_dir, "..", "..", "data", "table_descriptions.json"))
with open(path) as f:
    table_descriptions = json.load(f)

sql_system_prompt = PromptManager.get_prompt("system_sql_tables", db_platform="sqlite", tables=table_descriptions)

# --------------------------------------------------------------
# Step 1: Define the response format in a Pydantic model
# --------------------------------------------------------------


class TableResponse(BaseModel):
    tables: list[str]

user_query = "Which department offers the most number of degrees? List department name and id."

completion = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": sql_system_prompt},
        {
            "role": "user",
            "content": user_query,
        },
    ],
    response_format=TableResponse
)

response = completion.choices[0].message.parsed
print(response)

schemas=""

if(response.tables):
    print("Tables found:")
    sql_client = sqlite_client.SQLiteClient('../data/spider/sqlite/student_transcripts_tracking.sqlite')
    for table in response.tables:
        print(table)
        query = f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'"
        df = client.execute_query(query)

        # Print the schema for the table
        if not df.empty:
            print(df.iloc[0]['sql'])
            schemas += df.iloc[0]['sql'] + "\n"
        else:
            print(f"No schema found for table: {table}")

        # Optionally, print additional information
        #print(df.info())
        #print(df.head())
    sql_client.close()
    
    sql_system_prompt = PromptManager.get_prompt("system_sql", db_platform="sqlite", schema=schemas)    
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": sql_system_prompt},
            {
                "role": "user",
                "content": user_query,
            },
        ],
    )

    response = completion.choices[0].message.content
    print(response)

    # remove the ```sql from the response
    response = response.replace("```sql", "").replace("```", "").strip()
    print(response)
    
    sql_client = sqlite_client.SQLiteClient('../data/spider/sqlite/student_transcripts_tracking.sqlite')
    df = sql_client.execute_query(response)
    print(df)
    sql_client.close()
else:
    print("No tables found.")