"""LangGraph 節點函式。"""

from langchain_core.messages import HumanMessage, SystemMessage

from LangChain.model import build_chat_model
from LangChain.prompts import SYSTEM_PROMPT
from LangGraph.memory_store import append_node_record, upsert_chat_record
from LangGraph.states import GraphState


def retrieve_node(state: GraphState, docs: list[dict[str, object]] | None = None) -> GraphState:
    """第一節點：記錄查詢資料。

    目前第一版先做最小能力：
    將 state 寫入 `memory/chat_records.json`。

    之後這個節點會再擴充成真正的 retrieve：
    從記憶庫或資料來源查詢相關內容。
    """

    append_node_record(
        state=state,
        node="retrieve",
        status="success",
        data={
            "docs": docs or [],
            "message": "retrieve 節點已記錄原始查詢。",
        },
    )
    upsert_chat_record(state)
    return state


def rerank_node(
    state: GraphState,
    docs: list[dict[str, object]] | None = None,
) -> GraphState:
    """第二節點：記錄 rerank 階段，確保流程順序。

    目前此節點只做流程佔位與 JSON 紀錄：
    retrieve_node 執行後，再執行 rerank_node，並將 docs 寫入紀錄。

    之後和同學的向量排序功能對接時，docs 會放 rerank 後的文件結果。
    """

    append_node_record(
        state=state,
        node="rerank",
        status="success",
        data={
            "docs": docs or [],
            "message": "rerank 節點已執行並儲存 docs，目前尚未接入實際排序。",
        },
    )
    upsert_chat_record(state)
    return state


def generate_node(
    state: GraphState,
    question_for_ai: str | None = None,
    memory_context: str | None = None,
) -> GraphState:
    """第三節點：呼叫 AI 產生回答，並更新 JSON 紀錄。

    目前第一版預設使用 original_question 產生回答。
    如果 router 已經產生 rewritten_question，可以透過 question_for_ai 傳入。
    如果回答需要短期記憶，可以透過 memory_context 傳入。
    之後可以再加入 router、memory_context、retrieve/rerank 的 context。
    """

    try:
        question = question_for_ai or state["original_question"]
        user_content = question
        if memory_context:
            user_content = (
                f"短期對話記憶：\n{memory_context}\n\n"
                f"使用者原始問題：{state['original_question']}\n\n"
                f"Router 重組後的問題：{question}\n\n"
                "請根據以上內容回答使用者。"
            )

        llm = build_chat_model()
        response = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_content),
            ]
        )
        state["ai_answer"] = str(response.content)
        state["status"] = "success"
        append_node_record(
            state=state,
            node="generate",
            status="success",
            data={
                "question_for_ai": question,
                "memory_context": memory_context or "",
                "ai_answer": state["ai_answer"],
                "message": "generate 節點已產生 AI 回覆。",
            },
        )
    except Exception as error:
        state["ai_answer"] = f"AI 回覆失敗：{error}"
        state["status"] = "error"
        append_node_record(
            state=state,
            node="generate",
            status="error",
            data={
                "error": str(error),
                "message": "generate 節點產生 AI 回覆失敗。",
            },
        )

    upsert_chat_record(state)
    return state
