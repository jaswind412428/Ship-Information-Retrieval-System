# LangChain 核心設計

## 1. 本階段範圍

本階段只負責剪報中的 LangChain 四個部分：

1. LLM：初始化語言模型。
2. Prompt Template：建立提示詞模板。
3. Tools：定義工具。
4. Agent：把模型、提示詞、工具組成代理。

目前先不放 RAG、FastAPI、資料庫、前端與複雜服務包裝。

## 2. 模組責任

| 檔案 | 對應報告內容 | 用途 |
| --- | --- | --- |
| `src/LangChain/config.py` | 輔助設定 | 從 `.env` 讀模型設定 |
| `src/LangChain/model.py` | a. 初始化語言模型 | 建立 LangChain 的 Chat Model |
| `src/LangChain/prompts.py` | b. 建立提示詞模板 | 放系統提示詞與回答規則 |
| `src/LangChain/tools.py` | c. 定義工具 | 放 Agent 可以呼叫的工具 |
| `src/LangChain/agent.py` | d. 實例化代理 | 把 model、prompt、tools 組成 Agent |

## 3. 團隊整合方式

其他隊友如果需要使用 LangChain Agent，可以先從這裡開始：

```python
from LangChain.agent import build_agent

agent = build_agent()
result = agent.invoke(
    {"messages": [{"role": "user", "content": "請計算 Froude number"}]}
)
```

之後做 LangGraph 時，可以把這個 Agent 包成其中一個節點。

## 4. 新增 Tool 的規則

- 使用 `@tool`，docstring 必須說清楚用途、單位與適用條件。
- 計算邏輯必須是確定性的，不能在 Tool 裡再偷偷問 LLM。
- 先寫單元測試，再加入 `DEFAULT_TOOLS`。
- 無效輸入回傳清楚錯誤，不可靜默修正或猜測。

## 5. 後續串接順序

1. 先完成 LangChain 四件事：LLM、Prompt、Tools、Agent。
2. 再建立 LangGraph 流程：例如 retrieve → generate → answer。
3. 在 LangGraph 中加入 Checkpointer，保存每次對話狀態。
4. 最後才和 RAG、FastAPI、前端整合。
