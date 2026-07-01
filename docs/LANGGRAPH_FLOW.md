# LangGraph 流程設計紀錄

這份文件記錄目前討論出的 LangGraph 設計。目標不是一次做完整系統，而是先把自己的三節點想法重現出來，建立可以理解、可以展示、可以逐步擴充的版本。

## 1. 設計目標

我們希望保留剪報中的三個主要節點：

```text
retrieve → rerank → generate
```

但目前先不做完整 RAG，也不急著接向量資料庫。第一版會先使用本機 JSON 紀錄作為簡化版記憶來源。

## 2. Router 的角色

Router 暫時不做成主要節點。

它的概念是：

```text
在進入 retrieve / rerank / generate 前，
先讓小型 AI 根據記憶進行問題重組與分流。
```

例如使用者問：

```text
那它跟 LangChain 差在哪？
```

如果沒有記憶，系統不知道「它」是什麼。

Router 可以先讀取最近 3 到 5 筆對話，將問題重組成：

```text
LangGraph 跟 LangChain 差在哪？
```

之後再交給 retrieve 節點查詢資料。

目前 Router 第一版位於：

```text
src/LangGraph/router.py
```

它會做三件事：

1. 從 `memory/chat_records.json` 讀取同一個 `user_id` 與 `thread_id` 的最近成功對話。
2. 組成 `memory_context`。
3. 用小型 AI 將最新問題重寫成 `rewritten_question`。
4. 判斷這次 generate 是否需要使用記憶，輸出 `use_memory`。

注意：

```text
original_question 永遠保留使用者原始輸入。
rewritten_question 只記錄在 router 的 node_records 裡。
rewritten_question 不是答案，而是給 generate 節點使用的任務化問題。
generate 節點可以同時使用 memory_context 與 rewritten_question 來產生回答。
但只有 `use_memory = true` 時，才會把 memory_context 傳給 generate。
例如「你好」不需要記憶；「我剛剛說什麼」才需要記憶。
```

第一版先固定：

```text
route = retrieve
```

之後才擴充成真正分流。

## 3. 三個主要節點

### node1：retrieve

第一節點負責查詢資料。

目前第一版會先做最基本的能力：將使用者原始問題寫入 JSON 紀錄。

這樣做的目的：

1. 如果系統後面失敗，至少原始問題已經被記錄。
2. Checkpointer 可以保存 graph state。
3. JSON 可以讓人類直接查看紀錄，方便報告展示。

### node2：rerank

第二節點負責整理或排序查詢結果。

目前第一版先建立流程佔位節點：

```text
retrieve_node
↓
rerank_node
↓
generate_node
```

現階段 `rerank_node` 只負責在 JSON 中記錄它已經執行，並保存 `docs` 欄位。
之後和同學的向量排序功能對接時，`docs` 會放排序後的文件結果。

### node3：generate

第三節點才負責產生 AI 最終回答。

之後 generate 會：

1. 讀取原始問題。
2. 使用 router / retrieve / rerank 準備好的資料。
3. 呼叫 LangChain 模型。
4. 將 AI 回答寫回 state。
5. 更新 JSON 紀錄。

## 4. 公版 State

目前公版 State 只保留所有節點都會用到的欄位：

```python
class GraphState(TypedDict):
    id: str
    user_id: str
    thread_id: str
    created_at: str
    original_question: str
    ai_answer: str
    status: str
```

暫時不把所有欄位一次塞進公版 State。

例如：

```text
memory_context
rewritten_question
route
retrieved_docs
reranked_docs
context
```

這些都屬於 router 或特定 node 的專屬欄位，之後實作到對應節點時再新增。

這樣設計比較乾淨，也比較適合初學階段。

## 5. Checkpointer 與 JSON 的分工

目前設計中有兩種紀錄：

| 類型 | 用途 |
| --- | --- |
| Checkpointer | 給 LangGraph 保存流程狀態 |
| `memory/chat_records.json` | 給人類查看、報告展示、後續當簡化記憶來源 |

所以 JSON 不是取代 Checkpointer。

比較正確的理解是：

```text
Checkpointer = LangGraph 的流程存檔
JSON memory = 對話紀錄與展示資料
```

## 5.1 JSON 紀錄格式

JSON 採用「一筆對話主紀錄 + 多筆節點紀錄」的格式。

主紀錄負責保存這一輪對話的最後狀態：

```json
{
  "id": "單次紀錄 ID",
  "user_id": "使用者 ID",
  "thread_id": "對話 ID",
  "created_at": "建立時間",
  "original_question": "使用者原始問題",
  "ai_answer": "AI 最終回答",
  "status": "pending / success / error",
  "node_records": []
}
```

`node_records` 則記錄每個節點寫入過什麼資料：

```json
{
  "node": "router",
  "status": "success",
  "data": {
    "original_question": "使用者原始問題",
    "memory_context": "短期對話記憶",
    "rewritten_question": "router 重寫後的問題",
    "route": "retrieve",
    "use_memory": "False",
    "message": "router 已根據記憶重組問題。"
  }
}
```

```json
{
  "node": "retrieve",
  "status": "pending",
  "data": {
    "docs": [],
    "message": "retrieve 節點已記錄原始查詢。"
  }
}
```

```json
{
  "node": "rerank",
  "status": "pending",
  "data": {
    "docs": [],
    "message": "rerank 節點已執行並儲存 docs，目前尚未接入實際排序。"
  }
}
```

這樣就可以看出資料是由哪個節點產生的，而不是只看到最後一筆結果。

## 6. 第一版流程

第一版先做到：

```text
使用者輸入問題
↓
建立 GraphState
↓
retrieve 節點先將原始問題寫入 memory/chat_records.json
↓
rerank 節點記錄 docs，確保流程順序
↓
generate 節點產生回答
```

這樣可以先確認：

1. State 建立正確。
2. 第一節點可以接收 State。
3. 第一節點可以把紀錄寫成 JSON。
4. 之後其他節點可以用同一個 id 更新同一筆紀錄。

## 7. 目前範例

目前有兩個 LangGraph 相關範例：

```text
examples/02_record_question_node.py
```

用途：

```text
建立 State
→ retrieve_node 寫入原始問題
→ JSON 狀態為 pending
```

```text
examples/03_record_ai_answer.py
```

用途：

```text
建立 State
→ retrieve_node 寫入原始問題
→ generate_node 呼叫 AI
→ 更新同一筆 JSON 的 ai_answer 與 status
```

```text
examples/04_router_memory_chat.py
```

用途：

```text
持續對話
→ Router 讀取 JSON 記憶
→ 重寫問題
→ retrieve_node 記錄
→ generate_node 回覆
→ 下一輪對話可讀到前面記憶
```

## 8. 與向量檢索組對接

向量檢索與 rerank 的對接格式請見：

```text
docs/LANGGRAPH_RAG_INTEGRATION_TEMPLATE.md
```

此文件會用來和同學確認：

1. LangGraph 要傳給檢索組哪些欄位。
2. 檢索組要回傳哪些欄位。
3. `retrieved_docs`、`reranked_docs`、`context` 的格式。
4. JSON 中每個 node 要記錄什麼。

## 9. 正式 LangGraph

正式 `StateGraph` 設計請見：

```text
docs/LANGGRAPH_GRAPH.md
```

目前正式 graph 已建立：

```text
START → retrieve → rerank → generate → END
```

目前先不使用記憶體版 checkpointer；Checkpointer 之後若需要，會另外接 SQLite、資料庫或自訂儲存方式。
