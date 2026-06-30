"""示範第一個 LangGraph 節點：將原始問題記錄成 JSON。"""

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

from LangGraph.nodes import retrieve_node  # noqa: E402
from LangGraph.states import create_initial_state  # noqa: E402


def main() -> None:
    """建立 state，並呼叫第一節點寫入 JSON。"""

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

    print("已寫入 memory/chat_records.json")
    print(f"紀錄 id：{state['id']}")


if __name__ == "__main__":
    main()
