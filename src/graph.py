import os
from typing import TypedDict, Optional
from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import StateGraph, END

from .router import decision_router
from .search_web import search_web
from .search_documents import search_documents
from .query_sql import query_sql

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])


# ---------- 1. الـ State ----------
class GraphState(TypedDict):
    question: str
    decision: Optional[str]
    raw_result: Optional[str]
    final_answer: Optional[str]


# ---------- 2. العقد (Nodes) ----------
def router_node(state: GraphState) -> dict:
    question = state["question"]
    decision = decision_router(question)
    return {"decision": decision}


def document_node(state: GraphState) -> dict:
    question = state["question"]
    raw_result = search_documents(question)
    return {"raw_result": raw_result}


def sql_node(state: GraphState) -> dict:
    question = state["question"]
    raw_result = query_sql(question)
    return {"raw_result": raw_result}


def web_node(state: GraphState) -> dict:
    question = state["question"]
    raw_result = search_web(question)
    return {"raw_result": raw_result}


def none_node(state: GraphState) -> dict:
    return {"final_answer": "عذرًا، ما قدرت أفهم سؤالك بوضوح. ممكن تعيدي صياغته؟"}


def generation_node(state: GraphState) -> dict:
    question = state["question"]
    raw_result = state["raw_result"]

    if not raw_result:
        return {"final_answer": "عذرًا، ما لقيت معلومة كافية للإجابة على سؤالك."}

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are a helpful research assistant. Answer the user's question naturally based only on the provided context."},
            {"role": "user", "content": f"Question: {question}\n\nContext:\n{raw_result}\n\nAnswer the question based on the context above."}
        ],
        temperature=0.3
    )

    return {"final_answer": response.choices[0].message.content.strip()}


# ---------- 3. دالة التوجيه الشرطي (Conditional Edge) ----------
def route_decision(state: GraphState) -> str:
    return state["decision"]


# ---------- 4. بناء الـ Graph ----------
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


# ---------- 5. اختبار ----------
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
