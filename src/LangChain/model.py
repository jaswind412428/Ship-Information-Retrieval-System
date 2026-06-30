"""建立語言模型；其他模組不直接依賴特定供應商設定。"""

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from LangChain.config import Settings, get_settings


def build_chat_model(settings: Settings | None = None) -> ChatOpenAI:
    """依設定建立 Chat Model。

    初學階段預設使用本地 Ollama 的 qwen2.5:7b。
    如果之後要改用 OpenAI，只要在 .env 將 LLM_PROVIDER 改成 openai。
    """

    config = settings or get_settings()

    if config.llm_provider == "ollama":
        return ChatOpenAI(
            api_key=SecretStr("ollama"),
            base_url=config.ollama_base_url,
            model=config.ollama_chat_model,
            temperature=config.openai_temperature,
            timeout=config.openai_timeout_seconds,
            max_retries=config.openai_max_retries,
        )

    if not config.openai_api_key:
        raise ValueError("使用 OpenAI 時，請先在 .env 設定 OPENAI_API_KEY。")

    return ChatOpenAI(
        api_key=SecretStr(config.openai_api_key),
        model=config.openai_chat_model,
        temperature=config.openai_temperature,
        timeout=config.openai_timeout_seconds,
        max_retries=config.openai_max_retries,
    )
