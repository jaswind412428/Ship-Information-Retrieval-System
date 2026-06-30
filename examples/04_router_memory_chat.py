"""持續測試 Router 是否能讀取 JSON 記憶。

這個範例會：

1. 讀取 memory/chat_records.json 最近 3~5 筆成功紀錄。
2. 讓 router 根據記憶重組問題。
3. 呼叫 retrieve_node 先記錄原始問題。
4. 呼叫 generate_node 產生 AI 回覆並更新 JSON。
5. 重複對話，直到輸入 exit 或 quit。
"""

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


def main() -> None:
    """啟動可持續對話的 router 測試。"""

    user_id = "demo-user"
    thread_id = "demo-thread"

    print("Router 記憶測試已啟動。")
    print("輸入問題後按 Enter；輸入 exit 或 quit 結束。")
    print()

    while True:
        question = input("你：").strip()
        if question.lower() in {"exit", "quit"}:
            print("結束 router 記憶測試。")
            break

        if not question:
            print("請先輸入問題。")
            continue

        state = run_chat_flow(
            question=question,
            user_id=user_id,
            thread_id=thread_id,
        )

        router_record = next(
            record for record in state["node_records"] if record["node"] == "router"
        )
        router_data = router_record["data"]

        print("\n[Router]")
        print(f"route：{router_data['route']}")
        print(f"use_memory：{router_data['use_memory']}")
        print(f"rewritten_question：{router_data['rewritten_question']}")
        print("memory_context：")
        print(router_data["memory_context"])
        print()

        print(f"AI：{state['ai_answer']}")
        print(f"status：{state['status']}")
        print(f"id：{state['id']}")
        print()


if __name__ == "__main__":
    main()
