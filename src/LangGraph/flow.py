"""可被 CLI 與 FastAPI 共用的 LangGraph 流程。"""

from collections.abc import Callable
from typing import Any

from LangGraph.memory_store import append_node_record, upsert_chat_record
from LangGraph.graph import get_compiled_graph
from LangGraph.nodes import build_rag_question, generate_node, rerank_node, retrieve_node
from LangGraph.router import route_question
from LangGraph.states import GraphState, create_initial_state

ProgressCallback = Callable[[str, GraphState | dict[str, Any] | None], None]


def run_chat_flow(
    question: str,
    user_id: str = "demo-user",
    thread_id: str = "demo-thread",
    progress_callback: ProgressCallback | None = None,
) -> GraphState:
    """執行目前的 router → retrieve → rerank → generate 流程。"""

    if progress_callback:
        progress_callback("router_start", None)

    router_result = route_question(
        original_question=question,
        user_id=user_id,
        thread_id=thread_id,
    )

    state = create_initial_state(
        original_question=question,
        user_id=user_id,
        thread_id=thread_id,
    )
    state["rewritten_question"] = router_result["rewritten_question"]
    state["memory_context"] = router_result["memory_context"]
    state["use_memory"] = router_result["use_memory"]
    state["rag_question"] = build_rag_question(
        original_question=state["original_question"],
        memory_context=state.get("memory_context"),
        use_memory=bool(state.get("use_memory")),
    )

    append_node_record(
        state=state,
        node="router",
        status="success",
        data={
            "original_question": state["original_question"],
            "memory_context": router_result["memory_context"],
            "rewritten_question": router_result["rewritten_question"],
            "route": router_result["route"],
            "use_memory": router_result["use_memory"],
            "message": "router 已讀取短期記憶並判斷是否使用記憶；查詢改寫交給 hsu RAG。",
        },
    )
    upsert_chat_record(state)

    if progress_callback:
        progress_callback("router_end", state)
        progress_callback("retrieve_start", state)
        state = retrieve_node(state)
        progress_callback("retrieve_end", state)
        progress_callback("rerank_start", state)
        state = rerank_node(state)
        progress_callback("rerank_end", state)
        progress_callback("generate_start", state)
        state = generate_node(
            state,
            question_for_ai=state.get("rewritten_question"),
            memory_context=state.get("memory_context") if state.get("use_memory") else None,
        )
        progress_callback("generate_end", state)
        return state

    graph = get_compiled_graph()
    result = graph.invoke(
        state,
        config={"configurable": {"thread_id": thread_id}},
    )
    return result
