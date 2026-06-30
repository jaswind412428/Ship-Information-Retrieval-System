# 整合說明：怎麼呼叫 RAG 檢索後端（src/hsu）

這份給負責 LangGraph / API 整合的組員。說明怎麼把這個檢索後端接進你們的流程。

---

## 一句話總覽

這個後端做兩件事：**檢索**（從文件找出相關段落）和 **生成**（用 LLM 根據段落回答）。
你們的 LangGraph 流程在需要查資料時，呼叫這裡的函式即可。

```
你們的流程  →  retriever.search(問題)   → 拿到相關段落
            →  generator.generate_answer_text(問題, 段落)  → 拿到答案
```

---

## 兩個核心函式（你們會用到的）

### 1. 檢索：`retriever.search()`

```python
from hsu import retriever

hits = retriever.search("什麼是功能原理")
```

**參數：**
- `question`（str）：使用者的問題，中文英文都可以
- `top_k`（int，可選）：要回傳幾筆，預設 5
- `use_multi_query`（bool，可選）：是否做查詢改寫，預設 True

**回傳：** 一個 list，每筆是一個 dict：
```python
[
  {
    "text": "段落原文...",
    "source": "1-Engineering_Mechanics_Dynamics.pdf",
    "page": 451,
    "rerank_score": 0.95   # 相關度分數（越高越相關）
  },
  ...
]
```

這已經是「混合檢索 + 重排序」之後的最終結果，直接可用。

---

### 2. 生成：`generator.generate_answer_text()`

```python
from hsu import generator

answer = generator.generate_answer_text("什麼是功能原理", hits)
# answer 是一段繁體中文文字，已標來源頁碼
```

**參數：**
- `question`（str）：原始問題
- `hits`：上面 `retriever.search()` 回傳的結果

**回傳：** 一個字串（完整答案，已標來源、查無資料時會誠實說明）

---

## 最簡單的整合方式：直接用現成的 API

如果你們不想自己串函式，這個後端**已經包好 FastAPI**，直接啟動就能用：

```bash
cd src/hsu
uvicorn api:app --host 0.0.0.0 --port 8000
```

接口：

| 方法 | 路徑 | 送什麼 | 回什麼 |
|------|------|--------|--------|
| POST | /ask | `{"question": "..."}` | `{"answer", "sources"}` |
| POST | /ask-image | form-data: `file=圖片` | `{"image_description", "answer", "sources"}` |
| GET | /health | — | `{"status": "ok"}` |

你們的前端或 LangGraph 可以直接打這個 API，不用 import 函式。

---

## 如果要接進 LangGraph 流程（import 函式）

⚠️ **import 注意**：這個後端的程式用「同層 import」（例如 `import config`），
所以要讓 Python 找得到 `src/hsu` 這個資料夾。兩種做法選一種：

**做法一：把 src/hsu 加進路徑（最簡單）**
```python
import sys
sys.path.insert(0, "src/hsu")   # 路徑指到 hsu 資料夾

import retriever
import generator

def retrieve_node(state):
    question = state["question"]
    hits = retriever.search(question)                        # 檢索
    answer = generator.generate_answer_text(question, hits)  # 生成
    return {
        "answer": answer,
        "sources": [{"file": h["source"], "page": h["page"]} for h in hits],
    }
```

**做法二：直接用 API（更乾脆，完全不用煩惱 import）**
見上面「最簡單的整合方式：直接用現成的 API」。LangGraph 節點裡用 `requests` 打
`http://localhost:8000/ask` 就好，把檢索後端當成一個服務，不用 import。

> 推薦做法二：你們的架構是 LangGraph，把檢索當成一個 API 服務呼叫，
> 比 import 進來更乾淨、也不會有 import 路徑問題。

---

## 以圖搜圖（如果要支援上傳圖片）

```python
# 同樣需要先讓 Python 找到 src/hsu（見上面 import 注意）
import image_processor, retriever, generator

desc = image_processor.describe_uploaded_image("圖片路徑.png")  # Vision 看圖轉文字
hits = retriever.search(desc)                                   # 用描述檢索
answer = generator.generate_answer_text(desc, hits)
```

或直接用 API 的 `/ask-image` 接口（推薦），上傳圖片檔即可。

---

## 設定（重要）

這個後端需要兩組 key，填在 `src/hsu/config.py`（此檔不在 git 上，要自己建）：

1. 複製範本：`copy config.example.py config.py`
2. 填入：
   - `OPENAI_API_KEY`：OpenAI key
   - `QDRANT_URL` / `QDRANT_API_KEY`：向量庫連線（跟我要，團隊共用同一個）

向量庫用 **Qdrant Cloud**，索引已經建好、團隊共用，你們不用自己重建。

---

## 需要先裝的套件

```bash
cd src/hsu
pip install -r requirements.txt
```

第一次跑會下載 BGE reranker 模型（約 600MB），之後快取在本機。

---

## 有問題找我（Nayr）

- 檢索結果怪、想調參數 → 看 `config.py` 的 TOP_K、RERANK_TOP_N
- 想關掉某個功能（重排序、查詢改寫）→ `config.py` 有開關
- 整合卡住 → 直接問我
