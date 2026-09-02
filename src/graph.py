import os
from typing import TypedDict, Optional
from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import StateGraph, END

from .router import decision_router
from .search_web import search_web
from .search_documents import search_documents
from .query_sql import query_sql
from .logger import get_logger

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])
logger = get_logger(__name__)


# State
class GraphState(TypedDict):
    question: str
    decision: Optional[str]
    raw_result: Optional[str]
    final_answer: Optional[str]


# Nodes
def router_node(state: GraphState) -> dict:
    question = state["question"]
    decision = decision_router(question)
    logger.info(f"Question: '{question}' -> Router decision: '{decision}'")
    return {"decision": decision}


def document_node(state: GraphState) -> dict:
    question = state["question"]
    raw_result = search_documents(question)
    found = bool(raw_result)
    logger.info(f"Question: '{question}' | Document search found result: {found}")
    return {"raw_result": raw_result}


def sql_node(state: GraphState) -> dict:
    question = state["question"]
    raw_result = query_sql(question)
    found = bool(raw_result)
    logger.info(f"Question: '{question}' | SQL query found result: {found}")
    return {"raw_result": raw_result}


def web_node(state: GraphState) -> dict:
    question = state["question"]
    raw_result = search_web(question)
    found = raw_result is not None
    logger.info(f"Question: '{question}' | Web search found result: {found}")
    return {"raw_result": raw_result}


def none_node(state: GraphState) -> dict:
    return {"final_answer": "Sorry, I couldn't understand your question clearly. Could you please rephrase it?"}


def generation_node(state: GraphState) -> dict:
    question = state["question"]
    raw_result = state["raw_result"]

    if not raw_result:
        return {"final_answer": "Sorry, I couldn't understand your question clearly. Could you please rephrase it?"}

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are a helpful research assistant. Answer the user's question naturally based only on the provided context."},
            {"role": "user", "content": f"Question: {question}\n\nContext:\n{raw_result}\n\nAnswer the question based on the context above."}
        ],
        temperature=0.3
    )

    final_answer = response.choices[0].message.content.strip()
    logger.info(f"Source: '{state['decision']}' | Answer length: {len(final_answer)} chars")

    return {"final_answer": final_answer}


# Conditional Edge
def route_decision(state: GraphState) -> str:
    return state["decision"]


# Graph
graph = StateGraph(GraphState)

graph.add_node("router", router_node)
graph.add_node("document", document_node)
graph.add_node("sql", sql_node)
graph.add_node("web", web_node)
graph.add_node("none", none_node)
graph.add_node("generation", generation_node)

graph.set_entry_point("router")

graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "document": "document",
        "sql": "sql",
        "web": "web",
        "none": "none",
    }
)

graph.add_edge("document", "generation")
graph.add_edge("sql", "generation")
graph.add_edge("web", "generation")
graph.add_edge("generation", END)
graph.add_edge("none", END)

app = graph.compile()


# Tests
if __name__ == "__main__":
    test_questions = [
        "What is Anthropic's vision?",
        "What is OpenAI's current valuation?",
        "What is the latest news about Mistral?",
        "hello",
    ]

    for q in test_questions:
        result = app.invoke({"question": q})
        print(f"Q: {q}")
        print(f"A: {result['final_answer']}\n")
