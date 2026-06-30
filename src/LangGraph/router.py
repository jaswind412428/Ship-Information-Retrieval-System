"""Router：讀取短期記憶，重組使用者問題並決定後續流程。"""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from typing_extensions import TypedDict

from LangChain.model import build_chat_model
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
    """用短期記憶重組問題。

    第一版先固定 route 為 retrieve。
    之後如果要分流成 chat / retrieve / tool，可以再擴充。
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
            "rewritten_question": "請根據短期對話記憶回答使用者上一句說了什麼。",
            "route": "retrieve",
            "use_memory": True,
        }

    use_memory = _needs_memory_context(original_question)
    if not use_memory:
        return {
            "memory_context": memory_context,
            "rewritten_question": original_question,
            "route": "retrieve",
            "use_memory": False,
        }

    llm = build_chat_model()
    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "你是 LangGraph router。你的工作是根據短期對話記憶，"
                    "把使用者的最新問題改寫成第三節點 generate 可以回答的「任務化問題」。"
                    "你只能改寫問題，不可以回答問題。"
                    "如果問題需要短期記憶才能回答，請把它改寫成「請根據短期對話記憶回答……」。"
                    "如果最新問題本身已經清楚，請保持原句或只做必要補全。"
                    "如果最新問題只是打招呼，例如「你好」，請保持原句，不要改寫成 AI 的回覆。"
                    "禁止輸出任何已經回答問題的句子。"
                    "錯誤示範：您剛剛說了「你好」。"
                    "正確示範：請根據短期對話記憶回答使用者上一句說了什麼。"
                    "只輸出改寫後的問題，不要解釋。"
                    "如果使用者問題包含指代詞或序數詞，請保留短期記憶中最相關的原文內容。"
                    "請使用繁體中文，不要使用簡體中文。"
                )
            ),
            HumanMessage(
                content=(
                    f"短期對話記憶：\n{memory_context}\n\n"
                    f"使用者最新問題：{original_question}\n\n"
                    "請改寫成給 generate 節點使用的任務化問題："
                )
            ),
        ]
    )

    rewritten_question = str(response.content).strip()
    if not rewritten_question:
        rewritten_question = original_question

    return {
        "memory_context": memory_context,
        "rewritten_question": rewritten_question,
        "route": "retrieve",
        "use_memory": use_memory,
    }
