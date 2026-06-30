"""第一項 LangChain 範例：初始化語言模型。

執行前請先建立 .env。

預設使用本地 Ollama：

LLM_PROVIDER=ollama
OLLAMA_CHAT_MODEL=qwen2.5:7b
"""

from pathlib import Path
import sys

from langchain_core.messages import HumanMessage, SystemMessage


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from LangChain.model import build_chat_model


def main() -> None:
    """建立 Chat Model，並用最小範例確認模型可以回應。"""

    llm = build_chat_model()
    response = llm.invoke(
        [
            SystemMessage(content="你是船舶工程檢索系統的助理，請使用繁體中文回答。"),
            HumanMessage(content="請用一句話說明 LangChain 的用途。"),
        ]
    )
    print(response.content)


if __name__ == "__main__":
    main()
