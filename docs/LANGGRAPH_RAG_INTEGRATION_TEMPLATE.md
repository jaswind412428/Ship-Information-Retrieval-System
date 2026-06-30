# LangGraph 與向量檢索組對接模板

這份文件根據目前同學端的執行結果整理，目標是讓 LangGraph 可以清楚接上向量檢索、rerank 與 LLM 生成結果。

目前同學端輸出大致包含：

1. 使用者原始問題。
2. 查詢改寫或查詢詞。
3. embedding 進度。
4. 前幾筆相關文件結果。
5. 每筆文件的來源 PDF、頁碼、重排分數與文字片段。
6. LLM 最終生成答案。
7. 答案中引用的來源與頁碼。

## 1. 對接流程

目前我們這邊的 LangGraph 流程預計是：

```text
使用者輸入
↓
router
  - 讀取 memory/chat_records.json
  - 判斷 use_memory
  - 產生 rewritten_question
↓
retrieve
  - 將 rewritten_question 交給同學的檢索系統
  - 接收初步檢索結果
↓
rerank
  - 接收同學的重排結果
  - 選出最適合給 generate 的文件內容
↓
generate
  - 使用 original_question
  - 使用 rewritten_question
  - 使用 reranked_docs / context
  - 產生 AI 回答
↓
memory JSON
  - 紀錄本輪問題、節點資料與 AI 回答
```

## 2. 我們給同學的輸入

LangGraph 這邊會提供給檢索組：

```json
{
  "user_id": "demo-user",
  "thread_id": "demo-thread",
  "question_id": "本輪 GraphState 的 id",
  "original_question": "使用者原始問題",
  "rewritten_question": "router 重寫後、適合查詢的問題",
  "use_memory": true
}
```

欄位說明：

| 欄位 | 意義 |
| --- | --- |
| `user_id` | 哪個使用者，之後 UI 會用 |
| `thread_id` | 哪一段對話，給記憶與 Checkpointer 使用 |
| `question_id` | 這一輪問答紀錄 ID |
| `original_question` | 使用者真正輸入的問題，不可被改寫覆蓋 |
| `rewritten_question` | router 重寫後給檢索用的問題 |
| `use_memory` | 這輪回答是否需要使用短期記憶 |

## 3. 希望同學回傳的格式

建議同學回傳一個物件：

```json
{
  "query": "實際送進檢索系統的查詢文字",
  "embedding_status": {
    "current": 1,
    "total": 1,
    "message": "embedding 進度：1/1"
  },
  "retrieved_docs": [],
  "reranked_docs": [],
  "context": "整理後要交給 generate 的參考內容"
}
```

## 4. 單筆文件格式

不管是 `retrieved_docs` 或 `reranked_docs`，建議每筆文件都使用同一種格式：

```json
{
  "rank": 1,
  "source": "1-Engineering_Mechanics_Dynamics.pdf",
  "page": 311,
  "score": 0.9182,
  "content": "CHAPTER 15 KINETICS OF A PARTICLE: IMPULSE AND MOMENTUM ...",
  "metadata": {
    "document_type": "pdf",
    "search_method": "vector + rerank"
  }
}
```

欄位說明：

| 欄位 | 意義 |
| --- | --- |
| `rank` | 排名，第 1 相關、第 2 相關等 |
| `source` | 來源檔名 |
| `page` | 來源頁碼 |
| `score` | 重排分數或相關度分數 |
| `content` | 文件片段文字 |
| `metadata` | 其他補充資訊，可先空著 |

## 5. 對應到同學目前畫面

畫面中的輸出可以先對應成：

```text
查詢：什麼是角動量守恆
↓
query

[第 1 相關] 1-Engineering_Mechanics_Dynamics.pdf 第 311 頁 重排分數：0.9182
↓
reranked_docs[0]

[第 2 相關] 1-Engineering_Mechanics_Dynamics.pdf 第 582 頁 重排分數：0.9169
↓
reranked_docs[1]

LLM 生成答案
↓
generate 節點產生的 ai_answer
```

## 6. LangGraph JSON 紀錄建議

之後 JSON 中可以在 `node_records` 記錄：

```json
{
  "node": "retrieve",
  "status": "success",
  "data": {
    "query": "什麼是角動量守恆",
    "docs": [],
    "retrieved_count": "5"
  }
}
```

```json
{
  "node": "rerank",
  "status": "success",
  "data": {
    "top_source": "1-Engineering_Mechanics_Dynamics.pdf",
    "top_page": "311",
    "top_score": "0.9182",
    "docs": [],
    "reranked_count": "5"
  }
}
```

```json
{
  "node": "generate",
  "status": "success",
  "data": {
    "question_for_ai": "什麼是角動量守恆",
    "used_context_sources": "1-Engineering_Mechanics_Dynamics.pdf p.311, p.565, p.582",
    "ai_answer": "角動量守恆是指..."
  }
}
```

## 7. 對接時要問同學的問題

對接前建議先確認：

1. 他的檢索函式名稱是什麼？
2. 輸入是 `str` 還是 dict？
3. 回傳結果是 list、dict，還是直接印在 terminal？
4. `score` 越大越相關，還是越小越相關？
5. 頁碼是 PDF 實際頁碼，還是陣列 index？
6. 是否已經有 LLM 生成答案？還是只提供 reranked docs 給我們生成？
7. 是否可以不要直接 `print`，改成 `return` 結果給 LangGraph？

## 8. 最小對接目標

第一版不要追求完整，只要先做到：

```text
LangGraph router 產生 rewritten_question
↓
呼叫同學檢索函式
↓
取得 reranked_docs
↓
將 top 3~5 筆整理成 context
↓
generate 依 context 回答
↓
JSON 記錄每個節點結果
```

如果能做到這樣，就已經可以完整展示：

```text
router → retrieve → rerank → generate
```

這也剛好對應剪報中的 LangGraph 三節點設計。
