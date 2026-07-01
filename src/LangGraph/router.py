"""Router：讀取短期記憶，判斷是否需要記憶並決定後續流程。

注意：
目前查詢改寫交給 hsu RAG 的 query_rewriter 處理。
因此這裡的 router 不再呼叫 LLM 重寫問題，避免兩層重寫互相干擾。
"""

from __future__ import annotations

from typing import Literal

from typing_extensions import TypedDict

from LangGraph.memory_store import load_chat_records


RouteName = Literal["retrieve"]


class RouterResult(TypedDict):
    """Router 回傳結果。"""

    memory_context: str
    rewritten_question: str
    route: RouteName
    use_memory: bool


def _is_greeting(question: str) -> bool:
    """判斷是否只是簡單打招呼。"""

    normalized = question.strip().lower()
    return normalized in {
        "hi",
        "hello",
        "hey",
        "你好",
        "您好",
        "哈囉",
        "嗨",
    }


def _asks_previous_user_message(question: str) -> bool:
    """判斷使用者是否在問自己上一句說了什麼。"""

    normalized = question.strip().lower()
    chinese_patterns = [
        "我剛剛說",
        "我剛才說",
        "我上一句說",
        "我前面說",
        "剛剛我說",
        "剛才我說",
    ]
    english_patterns = [
        "what did i just say",
        "what did i say",
        "what was my last message",
        "what was my previous message",
    ]
    return any(pattern in normalized for pattern in chinese_patterns + english_patterns)


def _needs_memory_context(question: str) -> bool:
    """判斷這句話是否需要短期記憶才能回答。"""

    normalized = question.strip().lower()
    patterns = [
        "我剛剛",
        "我剛才",
        "我上一句",
        "我前面",
        "你剛剛",
        "你剛才",
        "你說的",
        "剛剛你",
        "剛才你",
        "上一個",
        "上一句",
        "前面",
        "它",
        "這個",
        "那個",
        "第",
        "項",
        "階段",
        "just",
        "previous",
        "last",
        "that",
        "it",
    ]
    return any(pattern in normalized for pattern in patterns)


def build_memory_context(user_id: str, thread_id: str, limit: int = 5) -> str:
    """從 JSON 讀取同一使用者、同一對話的最近幾筆成功紀錄。"""

    records = load_chat_records()
    matched_records = [
        record
        for record in records
        if record.get("user_id") == user_id
        and record.get("thread_id") == thread_id
        and record.get("status") == "success"
        and record.get("original_question")
        and record.get("ai_answer")
    ]
    recent_records = matched_records[-limit:]

    if not recent_records:
        return "目前沒有可用的歷史對話記憶。"

    lines: list[str] = []
    for index, record in enumerate(recent_records, start=1):
        lines.append(f"{index}. 使用者：{record['original_question']}")
        lines.append(f"   AI：{record['ai_answer']}")

    return "\n".join(lines)


def route_question(
    original_question: str,
    user_id: str = "demo-user",
    thread_id: str = "demo-thread",
) -> RouterResult:
    """讀取短期記憶，判斷是否使用記憶。

    查詢改寫目前交給 hsu RAG 的 query_rewriter。
    所以 rewritten_question 保留欄位，但直接使用 original_question。
    """

    memory_context = build_memory_context(user_id=user_id, thread_id=thread_id)

    if _is_greeting(original_question):
        return {
            "memory_context": memory_context,
            "rewritten_question": original_question,
            "route": "retrieve",
            "use_memory": False,
        }

    if _asks_previous_user_message(original_question):
        return {
            "memory_context": memory_context,
            "rewritten_question": original_question,
            "route": "retrieve",
            "use_memory": True,
        }

    use_memory = _needs_memory_context(original_question)

    return {
        "memory_context": memory_context,
        "rewritten_question": original_question,
        "route": "retrieve",
        "use_memory": use_memory,
    }
