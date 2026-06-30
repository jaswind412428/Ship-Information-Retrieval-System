"""LangGraph 節點共用 State。

這份 State 是三個 node 都可以共用的公版資料格式。
目前先保留報告與 Checkpointer 需要的最小欄位：

1. id：單次紀錄 ID
2. user_id：使用者 ID，之後 UI 可用來區分不同使用者
3. thread_id：對話 ID，給 Checkpointer 區分不同對話
4. created_at：建立時間
5. original_question：使用者原始問題
6. ai_answer：AI 回答
7. status：流程狀態，例如 pending / success / error
"""

from datetime import datetime
from typing import Literal
from uuid import uuid4

from typing_extensions import NotRequired, TypedDict


GraphStatus = Literal["pending", "success", "error"]
NodeName = Literal["router", "retrieve", "rerank", "generate"]


class NodeRecord(TypedDict):
    """記錄每個節點寫入了什麼資料。"""

    node: NodeName
    status: GraphStatus
    data: dict[str, object]


class GraphState(TypedDict):
    """LangGraph 每個節點都會讀取或更新的共用狀態。"""

    id: str
    user_id: str
    thread_id: str
    created_at: str
    original_question: str
    ai_answer: str
    status: GraphStatus
    node_records: NotRequired[list[NodeRecord]]


def create_initial_state(
    original_question: str,
    user_id: str = "default-user",
    thread_id: str = "default-thread",
) -> GraphState:
    """建立一筆新的 LangGraph 初始狀態。"""

    return {
        "id": str(uuid4()),
        "user_id": user_id,
        "thread_id": thread_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "original_question": original_question,
        "ai_answer": "",
        "status": "pending",
        "node_records": [],
    }
