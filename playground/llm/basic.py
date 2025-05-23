import json
import os
import sys

from openai import OpenAI

current_dir = os.path.dirname(os.path.abspath(__file__))

# Move two levels up to the project root directory
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
from dotenv import load_dotenv
# Explicitly load .env from the app directory
load_dotenv(os.path.join(project_root, 'app', '.env'))  # Load environment variables from app/.env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Add the project root to sys.path
sys.path.append(project_root)

from app.prompts.prompt_manager import PromptManager

# read the table_descriptions.json file
path = os.path.abspath(os.path.join(current_dir, "..", "..", "data", "table_descriptions.json"))
with open(path) as f:
    table_descriptions = json.load(f)

sql_system_prompt = PromptManager.get_prompt("system_sql", db_platform="sqlite", schema=table_descriptions)

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": sql_system_prompt},
        {
            "role": "user",
            "content": "How many courses are there?",
        },
    ],
)

response = completion.choices[0].message.content
print(response)