"""可被 CLI 與 FastAPI 共用的 LangGraph 流程。"""

from LangGraph.memory_store import append_node_record, upsert_chat_record
from LangGraph.graph import get_compiled_graph
from LangGraph.router import route_question
from LangGraph.states import GraphState, create_initial_state


def run_chat_flow(
    question: str,
    user_id: str = "demo-user",
    thread_id: str = "demo-thread",
) -> GraphState:
    """執行目前的 router → retrieve → rerank → generate 流程。"""

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
            "message": "router 已根據記憶重組問題。",
        },
    )
    upsert_chat_record(state)

    graph = get_compiled_graph()
    result = graph.invoke(
        state,
        config={"configurable": {"thread_id": thread_id}},
    )
    return result
