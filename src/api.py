from fastapi import FastAPI
from pydantic import BaseModel
from .graph import app as graph_app

app = FastAPI(title="Multi-Source Research Assistant")


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    question: str
    answer: str


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    result = graph_app.invoke({"question": request.question})
    return AnswerResponse(
        question=request.question,
        answer=result["final_answer"]
    )
