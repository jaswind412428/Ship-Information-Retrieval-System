r"""最簡單的 AI 試用入口。

使用方式：

1. 先建立虛擬環境並安裝套件：
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install -e .

2. 複製 .env.example 成 .env。
   預設會使用本地 Ollama 模型 qwen2.5:7b。

3. 執行：
   C:\Users\User\miniconda3\python.exe d:/CODE/Python/GAI/main.py
"""

from pathlib import Path
import sys

from langchain_core.messages import HumanMessage, SystemMessage


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

# 讓初學階段可以直接執行 python main.py，不一定要先理解 Python package 路徑。
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from LangChain.model import build_chat_model  # noqa: E402
from LangChain.prompts import SYSTEM_PROMPT  # noqa: E402


def main() -> None:
    """啟動一個簡單的終端機 AI 對話。"""

    llm = build_chat_model()

    print("AI 助理已啟動。輸入問題後按 Enter。")
    print("如果想離開，請輸入 exit 或 quit。")
    print()

    while True:
        user_input = input("你：").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("AI：再見！")
            break

        if not user_input:
            print("AI：請先輸入問題。")
            continue

        response = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_input),
            ]
        )
        print(f"AI：{response.content}")
        print()


if __name__ == "__main__":
    main()
