"""組裝 LangChain Agent。"""

from collections.abc import Sequence
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool

from LangChain.model import build_chat_model
from LangChain.prompts import SYSTEM_PROMPT
from LangChain.tools import DEFAULT_TOOLS


def build_agent(
    model: BaseChatModel | None = None,
    tools: Sequence[BaseTool] | None = None,
) -> Any:
    """建立 Agent；注入參數的設計方便測試及未來更換模型。"""

    return create_agent(
        model=model or build_chat_model(),
        tools=list(tools) if tools is not None else DEFAULT_TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )
