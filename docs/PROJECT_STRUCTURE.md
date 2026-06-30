# 專案資料夾說明

這份專案已經先整理成「報告需要什麼，就先保留什麼」的版本。

## 目前重要資料夾

### `src/LangChain`

這是目前最重要的資料夾，放 LangChain 相關 Python 程式。

目前只保留 LangChain 報告需要的四個部分：

| 檔案 | 對應報告內容 | 用途 |
| --- | --- | --- |
| `model.py` | a. 初始化語言模型 | 建立 Chat Model，目前預設連到本地 Ollama 的 qwen2.5:7b |
| `prompts.py` | b. 建立提示詞模板 | 放系統提示詞與回答規則 |
| `tools.py` | c. 定義工具 | 放可被 Agent 呼叫的工具 |
| `agent.py` | d. 實例化代理 | 把模型、提示詞、工具組成 Agent |
| `config.py` | 輔助設定 | 從 `.env` 讀 API Key、模型名稱等設定 |

你主要需要看這個資料夾。

### `src/LangGraph`

這裡放 LangGraph 相關程式。

目前先建立：

- `states.py`：定義三個 node 都可以共用的公版 State。

現在的 State 會記錄：

1. id
2. user_id
3. thread_id
4. created_at
5. original_question
6. ai_answer
7. status

### `examples`

這裡放可以直接執行的小範例。

目前只有：

- `01_init_llm.py`：示範如何初始化語言模型。

如果你要報告第一項 LangChain 程式，可以從這個檔案開始講。

### `docs`

這裡放報告用說明文件。

目前重要文件：

- `01_LLM_INITIALIZATION.md`：說明第一項「初始化語言模型」
- `LANGCHAIN_DESIGN.md`：說明 LangChain 四個核心模組
- `PROJECT_STRUCTURE.md`：也就是本文件，解釋專案結構

## 目前重要檔案

### `.env.example`

這是環境變數範本。

你之後要複製成 `.env`，再把自己的 OpenAI API Key 填進去。

### `pyproject.toml`

這是 Python 專案設定檔。

它會告訴 Python 這個專案需要安裝哪些套件，例如 LangChain、langchain-openai、pydantic。

### `README.md`

這是專案首頁說明。

通常給隊友看的第一份文件就是 README。

### `大暑-檢索系統設計.pdf`

這是原始報告／剪報內容，保留作為需求來源。

## 已刪除或不需要先看的東西

以下內容對初學與報告主線不是必要，所以已先移除：

- 測試快取
- Python 暫存檔
- PDF 轉出的臨時圖片
- 虛擬環境 `.venv`
- 額外的 service/schema/demo 包裝

如果之後要正式開發，這些東西可以再慢慢加回來；現在先保持專案乾淨，讓你能專心完成報告。
