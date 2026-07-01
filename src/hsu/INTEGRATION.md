# 整合說明：如何呼叫 hsu RAG 後端

這份文件給負責 LangGraph / API 整合的組員看。

hsu 後端主要做兩件事：

```text
檢索：從文件找出相關段落
生成：用 LLM 根據段落回答
```

## 推薦整合方式：用 API 串接

建議把 hsu 當成一個獨立服務，由 LangGraph 節點呼叫 API。

啟動 hsu API：

```powershell
cd src/hsu
uvicorn api:app --host 0.0.0.0 --port 8000
```

API 文件：

```text
http://localhost:8000/docs
```

主要端點：

| 方法 | 路徑 | 用途 |
| --- | --- | --- |
| GET | `/health` | 確認 API 是否啟動 |
| POST | `/ask` | 文字問題檢索與回答 |
| POST | `/ask-image` | 圖片問題檢索與回答 |

LangGraph 之後可以在 retrieve / rerank 節點中呼叫：

```text
http://localhost:8000/ask
```

## 也可以直接 import 函式

如果不走 API，也可以直接 import hsu 的函式。

但 hsu 目前使用同層 import，例如：

```python
import config
import retriever
```

所以直接 import 時，需要先把 `src/hsu` 加進 Python 路徑：

```python
import sys

sys.path.insert(0, "src/hsu")

import retriever
import generator

hits = retriever.search("什麼是角動量守恆")
answer = generator.generate_answer_text("什麼是角動量守恆", hits)
```

## 設定方式

目前設定統一放在專案根目錄。

第一次使用前，請在專案根目錄執行：

```powershell
Copy-Item .env.example .env
Copy-Item config.example.py src/hsu/config.py
```

分工如下：

| 檔案 | 用途 |
| --- | --- |
| `config.example.py` | 公開參數，例如模型名稱、TOP_K、chunk size |
| `.env` | API Key、Token、Qdrant URL 等秘密資料 |

請在根目錄 `.env` 填入：

```env
OPENAI_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
```

`src/hsu/config.py` 是每個人自己的本機設定，已被 `.gitignore` 排除，不會上傳。

## 套件安裝

請在專案根目錄安裝統一套件：

```powershell
pip install -r requirements.txt
```

`src/hsu` 已不再維護獨立 requirements，避免兩邊版本不同。

## LangGraph 對接時的資料格式建議

hsu 的搜尋結果可以放進 LangGraph state 的 `docs` 欄位，例如：

```python
[
    {
        "text": "段落內容",
        "source": "1-Engineering_Mechanics_Dynamics.pdf",
        "page": 311,
        "score": 0.9182,
    }
]
```

之後：

```text
retrieve node：呼叫 hsu API 或 retriever.search，取得 docs
rerank node：保存排序後 docs
generate node：根據 docs 與問題生成回答
```
