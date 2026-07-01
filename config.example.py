"""專案共用設定範本。

使用方式：

1. 複製根目錄的 `.env.example` 成 `.env`，並填入 API Key / Token。
2. 如果要使用 hsu 的檢索模組，請把此檔案複製成：

   src/hsu/config.py

   Windows PowerShell：

       Copy-Item config.example.py src/hsu/config.py

3. `src/hsu/config.py` 已被 `.gitignore` 排除，不要上傳自己的本機設定。

設計原則：

- API Key、Token、URL 這類每個人不同且不該上傳的資料，放在 `.env`。
- 模型名稱、資料夾、檢索數量、chunk 大小等公開參數，放在這個 config 範本。
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


CONFIG_FILE = Path(__file__).resolve()

if CONFIG_FILE.parent.name == "hsu":
    PROJECT_ROOT = CONFIG_FILE.parents[2]
else:
    PROJECT_ROOT = CONFIG_FILE.parent

load_dotenv(PROJECT_ROOT / ".env")


# ── API / Token 類設定：實際值請放在根目錄 .env ──
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")


# ── hsu RAG 模型設定 ──
EMBED_MODEL = "text-embedding-3-large"
LLM_MODEL = "gpt-4o-mini"


# ── hsu RAG 路徑設定 ──
DATA_DIR = str(PROJECT_ROOT / "src" / "hsu" / "data")
DB_DIR = str(PROJECT_ROOT / "src" / "hsu" / "db")
COLLECTION_NAME = "marine_docs"


# ── hsu RAG 切割參數 ──
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


# ── hsu RAG 檢索與排序參數 ──
TOP_K = 5
RRF_CANDIDATES = 20
RERANK_TOP_N = 5
USE_RERANK = True


# ── hsu RAG 開關 ──
GENERATE_ANSWER = True


# ── hsu 圖片處理設定 ──
PROCESS_IMAGES = True
IMAGE_LIMIT = 20
