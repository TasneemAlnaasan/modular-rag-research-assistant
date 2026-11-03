import traceback
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from .graph import app as graph_app

app = FastAPI(title="Multi-Source Research Assistant")


class QuestionRequest(BaseModel):
  question: str


class AnswerResponse(BaseModel):
  question: str
  answer: str


@app.get("/")
@app.head("/")  
def health_check():
  return {"status": "ok"}


@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
  try:
    result = graph_app.invoke({"question": request.question})
    final_ans = result.get("final_answer") or result.get("answer") or str(result)
    return AnswerResponse(question=request.question, answer=final_ans)

  except Exception as e:
    print("❌ ERROR DURING GRAPH EXECUTION:")
    traceback.print_exc()

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
    )