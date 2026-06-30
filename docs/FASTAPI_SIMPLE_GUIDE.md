# FastAPI 最小串接說明

這份文件說明如何啟動目前的 LangGraph API，讓其他組員可以用 HTTP 方式串接。

## 1. API 位置

目前 FastAPI 程式放在：

```text
src/API/app.py
```

目前提供兩個 endpoint：

```text
GET  /health
POST /chat
```

## 2. 安裝套件

如果尚未安裝 FastAPI / uvicorn，請先執行：

```powershell
C:\Users\User\miniconda3\python.exe -m pip install -e .
```

## 3. 啟動 API

在專案根目錄執行：

```powershell
C:\Users\User\miniconda3\python.exe -m uvicorn API.app:app --app-dir src --reload --port 8000
```

啟動後可以打開：

```text
http://127.0.0.1:8000/docs
```

這是 FastAPI 自動產生的測試頁面。

## 4. 健康檢查

```text
GET http://127.0.0.1:8000/health
```

回傳：

```json
{
  "status": "ok"
}
```

## 5. 聊天 API

```text
POST http://127.0.0.1:8000/chat
```

輸入 JSON：

```json
{
  "user_id": "demo-user",
  "thread_id": "demo-thread",
  "question": "造船的流程是什麼？"
}
```

回傳 JSON：

```json
{
  "id": "本輪紀錄 ID",
  "user_id": "demo-user",
  "thread_id": "demo-thread",
  "original_question": "造船的流程是什麼？",
  "ai_answer": "AI 回答",
  "status": "success",
  "node_records": []
}
```

## 6. 給其他組員的重點

其他組員目前只需要會呼叫：

```text
POST /chat
```

並傳入：

```json
{
  "user_id": "使用者 ID",
  "thread_id": "對話 ID",
  "question": "使用者問題"
}
```

我們這邊會負責：

```text
router → retrieve → rerank → generate → memory JSON
```

之後如果要接同學的向量檢索 API，會在 retrieve / rerank 節點內呼叫他們的 API。
