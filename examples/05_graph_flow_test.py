r"""測試正式 LangGraph 流程是否可以執行。

這個範例會執行：

router → LangGraph(retrieve → rerank → generate)

重點不是測 hsu 的資料庫，也不是測真正的向量搜尋；
而是確認我們自己的 LangGraph 流程順序、JSON 紀錄、AI 回覆是否能串起來。

執行方式一：互動模式

    C:\Users\User\miniconda3\python.exe examples\05_graph_flow_test.py

執行方式二：單次問題測試

    C:\Users\User\miniconda3\python.exe examples\05_graph_flow_test.py --question "你好"
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from LangGraph.flow import run_chat_flow  # noqa: E402


def print_state_result(state: dict[str, object]) -> None:
    """把 Graph 執行結果用適合初學者觀察的格式印出來。"""

    print()
    print("=" * 60)
    print("Graph 執行完成")
    print("=" * 60)
    print(f"id：{state.get('id')}")
    print(f"user_id：{state.get('user_id')}")
    print(f"thread_id：{state.get('thread_id')}")
    print(f"created_at：{state.get('created_at')}")
    print(f"status：{state.get('status')}")
    print(f"original_question：{state.get('original_question')}")
    print(f"rewritten_question：{state.get('rewritten_question', '')}")
    print(f"use_memory：{state.get('use_memory', '')}")

    print()
    print("[節點執行順序]")
    node_records = state.get("node_records") or []
    if not isinstance(node_records, list) or not node_records:
        print("目前沒有 node_records。")
    else:
        for index, record in enumerate(node_records, start=1):
            if not isinstance(record, dict):
                continue

            node = record.get("node", "")
            status = record.get("status", "")
            data = record.get("data") or {}
            message = ""
            docs_count = ""

            if isinstance(data, dict):
                message = str(data.get("message", ""))
                docs = data.get("docs")
                if isinstance(docs, list):
                    docs_count = f"，docs 數量：{len(docs)}"

            print(f"{index}. {node} / {status}{docs_count}")
            if message:
                print(f"   message：{message}")

    print()
    print("[AI 回答]")
    print(state.get("ai_answer", ""))
    print("=" * 60)
    print()


def run_once(question: str, user_id: str, thread_id: str) -> None:
    """執行一次完整流程。"""

    state = run_chat_flow(
        question=question,
        user_id=user_id,
        thread_id=thread_id,
    )
    print_state_result(state)


def run_interactive(user_id: str, thread_id: str) -> None:
    """啟動互動模式，直到使用者輸入 exit 或 quit。"""

    print("05 正式 LangGraph 流程測試已啟動。")
    print("流程：router → retrieve → rerank → generate")
    print("輸入問題後按 Enter；輸入 exit 或 quit 結束。")
    print()

    while True:
        question = input("你：").strip()

        if question.lower() in {"exit", "quit"}:
            print("結束 05 Graph 測試。")
            break

        if not question:
            print("請先輸入問題。")
            continue

        run_once(
            question=question,
            user_id=user_id,
            thread_id=thread_id,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="測試正式 LangGraph 流程。")
    parser.add_argument("--question", help="單次測試用問題；不填則進入互動模式。")
    parser.add_argument("--user-id", default="demo-user", help="使用者 ID。")
    parser.add_argument("--thread-id", default="demo-thread", help="對話 ID。")
    args = parser.parse_args()

    if args.question:
        run_once(
            question=args.question,
            user_id=args.user_id,
            thread_id=args.thread_id,
        )
    else:
        run_interactive(
            user_id=args.user_id,
            thread_id=args.thread_id,
        )


if __name__ == "__main__":
    main()
