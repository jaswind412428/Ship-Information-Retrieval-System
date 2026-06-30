"""示範記錄 AI 回覆。

流程：

1. 建立 GraphState。
2. 呼叫 retrieve_node，先把原始問題寫入 JSON，status=pending。
3. 呼叫 generate_node，產生 AI 回答並更新同一筆 JSON，status=success/error。
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

from LangGraph.nodes import generate_node, retrieve_node  # noqa: E402
from LangGraph.states import create_initial_state  # noqa: E402


def main() -> None:
    """輸入問題，記錄原始問題，再記錄 AI 回覆。"""

    question = input("請輸入問題：").strip()
    if not question:
        print("沒有輸入問題，程式結束。")
        return

    state = create_initial_state(
        original_question=question,
        user_id="demo-user",
        thread_id="demo-thread",
    )

    retrieve_node(state)
    print("已先記錄原始問題，status=pending")

    state = generate_node(state)
    print(f"AI：{state['ai_answer']}")
    print(f"已更新 JSON 紀錄，status={state['status']}")
    print(f"紀錄 id：{state['id']}")


if __name__ == "__main__":
    main()
