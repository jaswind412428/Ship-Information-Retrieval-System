# Marine RAG 後端

這是組員製作的船舶工程 RAG 檢索後端，主要負責：

- PDF 讀取與切 chunk
- embedding 與 Qdrant 向量資料庫
- BM25 關鍵字搜尋
- hybrid search / rerank
- 使用 LLM 根據檢索結果生成回答
- FastAPI 檢索 API

## 安裝套件

請回到專案根目錄安裝統一套件：

```powershell
pip install -r requirements.txt
```

`src/hsu` 已不再維護獨立的 `requirements.txt`，避免組員環境不一致。

## 設定方式

目前設定分成兩個檔案：

| 檔案 | 用途 | 是否上傳 |
| --- | --- | --- |
| 根目錄 `config.example.py` | 公開參數，例如模型名稱、TOP_K、chunk size | 會上傳 |
| 根目錄 `.env` | API Key、Token、Qdrant URL 等秘密資料 | 不上傳 |

第一次使用前，請在專案根目錄執行：

```powershell
Copy-Item .env.example .env
Copy-Item config.example.py src/hsu/config.py
```

接著打開根目錄 `.env`，填入：

```env
OPENAI_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
```

注意：

- `src/hsu/config.py` 是每個人自己的本機設定，已被 `.gitignore` 排除。
- 不要把自己的 API Key 或 Qdrant Key 上傳到 GitHub。

## 放置 PDF

PDF 請放在：

```text
src/hsu/data/
```

## 建立索引

在 `src/hsu` 內執行：

```powershell
python main.py
```

## 啟動 hsu API

在 `src/hsu` 內執行：

```powershell
uvicorn api:app --host 0.0.0.0 --port 8000
```

測試頁：

```text
http://localhost:8000/docs
```

## 主要 API

| 方法 | 路徑 | 用途 |
| --- | --- | --- |
| GET | `/health` | 確認 API 是否啟動 |
| POST | `/ask` | 文字問題檢索與回答 |
| POST | `/ask-image` | 上傳圖片後檢索與回答 |

## 檔案簡介

```text
pdf_loader.py      讀 PDF + 切 chunk
vectorstore.py     embedding + Qdrant 存取
bm25_search.py     BM25 關鍵字搜尋
query_rewriter.py  查詢改寫
reranker.py        Cross-Encoder 重排序
retriever.py       混合檢索
generator.py       LLM 生成答案
image_processor.py 圖片抽取 + Vision 描述
api.py             FastAPI 入口
main.py            建索引與命令列查詢
config.py          本機設定，從根目錄 config.example.py 複製而來，不上傳
```
