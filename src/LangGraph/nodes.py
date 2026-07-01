"""LangGraph 節點函式。

目前正式流程：

retrieve → rerank → generate

其中 retrieve / generate 會接 hsu RAG。
第三節點 generate 只使用 hsu generator，不再額外呼叫自己的 LangChain 模型，
避免同一批資料被兩個 AI 重複生成、浪費 token。
"""

from LangGraph.memory_store import append_node_record, upsert_chat_record
from LangGraph.rag_adapter import (
    build_context_from_documents,
    generate_answer_from_documents,
    search_documents,
)
from LangGraph.states import GraphState


def build_rag_question(
    original_question: str,
    memory_context: str | None = None,
    use_memory: bool = False,
    max_memory_chars: int = 1200,
) -> str:
    """建立交給 hsu RAG 的問題。

    hsu 已經有自己的 query_rewriter，所以這裡不改寫問題。
    只有在 router 判斷需要短期記憶時，才把記憶一起交給 hsu，
    讓 hsu 的查詢改寫與最後生成都能理解上下文。
    """

    if not use_memory or not memory_context:
        return original_question

    trimmed_memory = memory_context.strip()
    if len(trimmed_memory) > max_memory_chars:
        trimmed_memory = "……（前文略）\n" + trimmed_memory[-max_memory_chars:]

    return (
        "以下是短期對話記憶，請用來理解使用者最新問題的上下文。\n\n"
        f"{trimmed_memory}\n\n"
        f"使用者最新問題：{original_question}"
    )


def retrieve_node(
    state: GraphState,
    docs: list[dict[str, object]] | None = None,
) -> GraphState:
    """第一節點：呼叫 hsu RAG 取得相關文件。"""

    question = state.get("rag_question") or build_rag_question(
        original_question=state["original_question"],
        memory_context=state.get("memory_context"),
        use_memory=bool(state.get("use_memory")),
    )
    state["rag_question"] = question

    try:
        retrieved_docs = docs or search_documents(question)
        state["retrieved_docs"] = retrieved_docs
        state["context"] = build_context_from_documents(retrieved_docs)

        append_node_record(
            state=state,
            node="retrieve",
            status="success",
            data={
                "query": question,
                "use_memory": state.get("use_memory", False),
                "docs": retrieved_docs,
                "message": "retrieve 節點已呼叫 hsu RAG 並儲存查詢結果。",
            },
        )
    except Exception as error:
        state["retrieved_docs"] = []
        state["context"] = ""
        state["rag_error"] = str(error)

        append_node_record(
            state=state,
            node="retrieve",
            status="error",
            data={
                "query": question,
                "use_memory": state.get("use_memory", False),
                "docs": [],
                "error": str(error),
                "message": "retrieve 節點呼叫 hsu RAG 失敗。",
            },
        )

    upsert_chat_record(state)
    return state


def rerank_node(
    state: GraphState,
    docs: list[dict[str, object]] | None = None,
) -> GraphState:
    """第二節點：保存排序後 docs。

    目前 hsu.search() 已經完成 hybrid search + rerank，
    所以這裡先把 retrieved_docs 視為 reranked_docs。
    """

    reranked_docs = docs or state.get("retrieved_docs", [])
    state["reranked_docs"] = reranked_docs

    append_node_record(
        state=state,
        node="rerank",
        status="success" if not state.get("rag_error") else "error",
        data={
            "docs": reranked_docs,
            "message": "rerank 節點已儲存 hsu RAG 排序後 docs；hsu.search 已包含 rerank。",
        },
    )
    upsert_chat_record(state)
    return state


def generate_node(
    state: GraphState,
    question_for_ai: str | None = None,
    memory_context: str | None = None,
) -> GraphState:
    """第三節點：使用 hsu generator 產生最終回答。

    注意：這裡不再呼叫自己的 LangChain 模型。
    hsu generator 已經會根據 docs 生成答案，第三節點只負責把結果接住、
    寫回 state 與 JSON 紀錄。
    """

    question = state.get("rag_question") or question_for_ai or state["original_question"]
    docs = state.get("reranked_docs", [])

    if state.get("rag_error") and not docs:
        state["ai_answer"] = (
            "RAG 檢索失敗，因此無法根據文件產生回答。\n\n"
            f"錯誤原因：{state['rag_error']}\n\n"
            "請確認根目錄 .env 是否已填入 OPENAI_API_KEY、QDRANT_URL、QDRANT_API_KEY，"
            "以及 hsu 的索引是否已建立。"
        )
        state["status"] = "error"
        append_node_record(
            state=state,
            node="generate",
            status="error",
            data={
                "question_for_ai": question,
                "ai_answer": state["ai_answer"],
                "message": "generate 節點因 RAG 檢索失敗而停止。",
            },
        )
        upsert_chat_record(state)
        return state

    try:
        if not docs:
            state["ai_answer"] = "RAG 沒有回傳可用文件，因此第三節點不額外呼叫 AI 生成答案。"
            state["status"] = "error"
            append_node_record(
                state=state,
                node="generate",
                status="error",
                data={
                    "question_for_ai": question,
                    "memory_context": memory_context or "",
                    "docs": docs,
                    "ai_answer": state["ai_answer"],
                    "message": "generate 節點沒有 docs，因此停止，避免額外浪費 token。",
                },
            )
            upsert_chat_record(state)
            return state

        state["ai_answer"] = generate_answer_from_documents(question, docs)
        message = "generate 節點已接收 hsu generator 的 RAG 回答，未再呼叫自己的 LangChain 模型。"

        state["status"] = "success"
        append_node_record(
            state=state,
            node="generate",
            status="success",
            data={
                "question_for_ai": question,
                "memory_context": memory_context or "",
                "docs": docs,
                "ai_answer": state["ai_answer"],
                "message": message,
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
                "question_for_ai": question,
                "docs": docs,
                "error": str(error),
                "message": "generate 節點產生 AI 回覆失敗。",
            },
        )

    upsert_chat_record(state)
    return state
