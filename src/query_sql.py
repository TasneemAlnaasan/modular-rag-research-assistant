import os
import sqlite3
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

TABLE_SCHEMA = """
Table name: company_funding

Columns:
- company_name (TEXT, PRIMARY KEY) — always stored in lowercase, e.g. 'anthropic', 'openai'
- founded_year (INTEGER)
- headquarters (TEXT)
- total_funding_usd_millions (REAL)
- valuation_usd_millions (REAL)
- last_funding_round (TEXT)
- notes (TEXT)
- last_updated (TEXT)
"""

sql_system_prompt = f"""You are a SQL expert. Given a user's question and the table schema below, write a single valid SQLite SELECT query that answers the question.

{TABLE_SCHEMA}

Rules:
- Only write SELECT queries. Never write INSERT, UPDATE, DELETE, or DROP statements.
- Always match company_name values in lowercase.
- Return ONLY the SQL query, with no explanation, no markdown, no backticks.

Example:
Question: "What is Anthropic's valuation?"
SQL: SELECT valuation_usd_millions FROM company_funding WHERE company_name = 'anthropic';

Example:
Question: "Compare funding of Groq and Mistral"
SQL: SELECT company_name, total_funding_usd_millions FROM company_funding WHERE company_name IN ('groq', 'mistral');
"""


def generate_sql(question: str) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": sql_system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def is_safe_query(sql: str) -> bool:
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        return False
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]
    return not any(word in sql_upper for word in forbidden)


def query_sql(question: str) -> str | None:
    sql = generate_sql(question)

    if not is_safe_query(sql):
        print(f"⚠️ Unsafe or invalid SQL blocked: {sql}")
        return None

    try:
        conn = sqlite3.connect("data/company_data.db")
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
    except sqlite3.Error as e:
        print(f"⚠️ SQL execution error: {e}")
        return None

    if not rows:
        return None

    result_lines = []
    for row in rows:
        line = ", ".join(f"{col}: {val}" for col, val in zip(columns, row))
        result_lines.append(line)

    return "\n".join(result_lines)


if __name__ == "__main__":
    test_questions = [
        "What is Anthropic's valuation?",
        "Compare funding of Groq and Mistral",
    ]
    for q in test_questions:
        print(f"Q: {q}")
        print(f"A: {query_sql(q)}\n")
