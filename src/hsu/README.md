# Marine RAG 後端

造船工程知識助理的 RAG 檢索後端。提供文字問答與以圖搜圖的 API。

## 功能

- 混合檢索：向量搜尋 + BM25 + RRF 合併
- Multi-Query 查詢改寫（支援中英文跨語言檢索）
- Cross-Encoder 重排序（BGE）
- LLM 生成答案（標來源頁碼、查無資料時 Fallback）
- 圖片多模態（文件抽圖描述 + 以圖搜圖）
- 向量庫：Qdrant Cloud（團隊共用）

## 安裝

```bash
pip install -r requirements.txt
```

## 設定（重要）

1. 複製設定範本：
   ```bash
   copy config.example.py config.py    # Windows
   # cp config.example.py config.py    # Mac/Linux
   ```
2. 打開 `config.py`，填入：
   - `OPENAI_API_KEY`：你的 OpenAI key
   - `QDRANT_URL` / `QDRANT_API_KEY`：跟負責人要（團隊共用同一個 Qdrant 叢集）

> `config.py` 已被 `.gitignore` 排除，不會上傳，所以 key 不會外洩。

## 建索引（第一次 / 加新文件）

把 PDF 放進 `data/` 資料夾，然後：

```bash
python main.py
```

- 第一次：讀 PDF → embedding → 存進 Qdrant Cloud
- 加新 PDF：丟進 data/ 再跑一次，會自動只處理新檔
- 索引存在 Qdrant Cloud，團隊共用，建一次大家都能用

## 啟動 API

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

測試頁：http://localhost:8000/docs

## API 接口

| 方法 | 路徑 | 送什麼 | 回什麼 |
|------|------|--------|--------|
| POST | /ask | `{"question": "..."}` | `{"answer", "sources"}` |
| POST | /ask-image | form-data: `file=圖片` | `{"image_description", "answer", "sources"}` |
| GET | /health | — | `{"status": "ok"}` |

## 檔案結構

```
你的 RAG 部分：
  pdf_loader.py      讀 PDF + 切 chunk
  vectorstore.py     embedding + Qdrant 存取
  bm25_search.py     BM25 關鍵字搜尋
  query_rewriter.py  Multi-Query 查詢改寫
  reranker.py        Cross-Encoder 重排序
  retriever.py       混合檢索（串起上面幾個）
  generator.py       LLM 生成答案
  image_processor.py 圖片抽取 + Vision 描述

共用：
  config.py          設定（不上傳，各自填 key）
  api.py             FastAPI 入口
  main.py            建索引 + 命令列查詢
```

## 給整合 Database 的組員

對話歷史(Checkpointer)、檔案儲存、日誌等模組可新增獨立檔案
（如 memory.py、storage.py、logger.py），在 `api.py` 串接。
盡量各自管各自的檔案，只有 config.py / api.py / main.py 需要協調，減少衝突。
