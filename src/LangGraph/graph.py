"""正式 LangGraph：retrieve → rerank → generate。

Router 目前維持在 graph 外面，作為前處理：

使用者問題 → router → StateGraph(retrieve → rerank → generate)
"""

from functools import lru_cache
from typing import Any

from langgraph.graph import END, START, StateGraph

from LangGraph.nodes import generate_node, rerank_node, retrieve_node
from LangGraph.states import GraphState


def graph_retrieve_node(state: GraphState) -> GraphState:
    """LangGraph 第一節點：retrieve。"""

    return retrieve_node(state)


def graph_rerank_node(state: GraphState) -> GraphState:
    """LangGraph 第二節點：rerank。"""

    return rerank_node(state)


def graph_generate_node(state: GraphState) -> GraphState:
    """LangGraph 第三節點：generate。

    這裡會讀取 router 事先放入 state 的 rewritten_question / memory_context。
    """

    return generate_node(
        state,
        question_for_ai=state.get("rewritten_question"),
        memory_context=state.get("memory_context") if state.get("use_memory") else None,
    )


def build_graph() -> Any:
    """建立未編譯的 StateGraph。"""

    builder = StateGraph(GraphState)

    builder.add_node("retrieve", graph_retrieve_node)
    builder.add_node("rerank", graph_rerank_node)
    builder.add_node("generate", graph_generate_node)

    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "rerank")
    builder.add_edge("rerank", "generate")
    builder.add_edge("generate", END)

    return builder


@lru_cache
def get_compiled_graph() -> Any:
    """建立並快取 LangGraph。

    注意：依照目前專案討論，這裡不使用記憶體版 checkpointer。
    Checkpointer 之後若需要，會改接 SQLite、資料庫或自訂儲存方式。
    """

    return build_graph().compile()
