import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

system_prompt = """You are a routing assistant. Classify the user's question into exactly one category:

- document: questions about a company's identity, products, vision, or history
- sql: questions about numeric/financial data (funding, valuation, founding year)
- web: questions about recent news or current events

Examples:
"What is Anthropic's vision?" -> document
"When was Mistral founded?" -> document
"What is OpenAI's current valuation?" -> sql
"Compare Groq's funding to Mistral's" -> sql
"What is the latest news about Anthropic?" -> web

Respond with ONLY one word: document, sql, web, or none. No explanation."""


def decision_router(user_question: str) -> str | None:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0
    )

    decision = response.choices[0].message.content.strip().lower()

    if decision in ["document", "sql", "web", "none"]:
        return decision
    else:
        print(f"⚠️ Router couldn't classify. Raw model output: '{decision}'")
        return None


if __name__ == "__main__":
    test_questions = [
        "What is Anthropic's vision?",
        "What is OpenAI's current valuation?",
        "What is the latest news about Mistral?",
        "hello", 
    ]

    for q in test_questions:
        decision = decision_router(q)
        print(f"{q} -> {decision}")
