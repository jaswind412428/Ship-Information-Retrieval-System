"""提供給組員串接的最小 FastAPI。"""

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from LangGraph.flow import run_chat_flow


app = FastAPI(
    title="Marine GAI LangGraph API",
    description="提供 router → retrieve → rerank → generate 的最小串接 API。",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    """POST /chat 的輸入格式。"""

    question: str = Field(min_length=1, description="使用者原始問題")
    user_id: str = Field(default="demo-user", description="使用者 ID")
    thread_id: str = Field(default="demo-thread", description="對話 ID")


class ChatResponse(BaseModel):
    """POST /chat 的輸出格式。"""

    id: str
    user_id: str
    thread_id: str
    original_question: str
    ai_answer: str
    status: str
    node_records: list[dict[str, Any]]


@app.get("/health")
def health() -> dict[str, str]:
    """確認 API 是否有啟動。"""

    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """執行目前 LangGraph 流程並回傳 AI 回答。"""

    state = run_chat_flow(
        question=request.question,
        user_id=request.user_id,
        thread_id=request.thread_id,
    )
    return ChatResponse(
        id=state["id"],
        user_id=state["user_id"],
        thread_id=state["thread_id"],
        original_question=state["original_question"],
        ai_answer=state["ai_answer"],
        status=state["status"],
        node_records=state.get("node_records", []),
    )
