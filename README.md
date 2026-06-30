# Ship LangChain Core

這是依《大暑－檢索系統設計》整理出的最小 LangChain 專案。

目前只保留報告需要的四個重點：

1. 初始化語言模型：`src/LangChain/model.py`
2. 建立提示詞模板：`src/LangChain/prompts.py`
3. 定義工具：`src/LangChain/tools.py`
4. 建立 Agent：`src/LangChain/agent.py`

LangGraph 與 Checkpointer 之後會另外新增，避免初學階段一次混入太多東西。

## 快速開始

如果你使用 Miniconda，可以用你的 Python 執行檔安裝：

```powershell
C:\Users\User\miniconda3\python.exe -m pip install -e .
Copy-Item .env.example .env
```

預設模型是本地 Ollama 的 `qwen2.5:7b`。請先確認 Ollama 已啟動，並下載模型：

```powershell
ollama pull qwen2.5:7b
```

接著執行：

```powershell
C:\Users\User\miniconda3\python.exe d:/CODE/Python/GAI/main.py
```

如果要測試 LangGraph 第一節點，將原始問題寫入 JSON：

```powershell
C:\Users\User\miniconda3\python.exe d:/CODE/Python/GAI/examples/02_record_question_node.py
```

如果要測試記錄 AI 回覆：

```powershell
C:\Users\User\miniconda3\python.exe d:/CODE/Python/GAI/examples/03_record_ai_answer.py
```

如果要測試 Router 是否能讀取 JSON 記憶並持續對話：

```powershell
C:\Users\User\miniconda3\python.exe d:/CODE/Python/GAI/examples/04_router_memory_chat.py
```

如果要啟動 FastAPI 讓組員串接：

```powershell
C:\Users\User\miniconda3\python.exe -m uvicorn API.app:app --app-dir src --reload --port 8000
```

啟動後打開：

```text
http://127.0.0.1:8000/docs
```

資料夾用途請見 [專案資料夾說明](docs/PROJECT_STRUCTURE.md)。

LangChain 與 LangGraph 的差別請見 [第一項：初始化語言模型](docs/01_LLM_INITIALIZATION.md)。
