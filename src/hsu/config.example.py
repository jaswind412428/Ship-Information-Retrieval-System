"""
設定範本。複製這個檔案成 config.py，填入你自己的 key 後使用。

  cp config.example.py config.py   （Mac/Linux）
  copy config.example.py config.py （Windows）

config.py 已被 .gitignore 排除，不會上傳，所以你的 key 不會外洩。
"""
import os

# ── API（填你自己的）──
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "在這裡填_OpenAI_API_KEY")

# ── Qdrant Cloud（團隊共用同一個叢集，跟負責人要 URL 和 key）──
QDRANT_URL = os.getenv("QDRANT_URL", "在這裡填_Qdrant_叢集網址")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "在這裡填_Qdrant_API_KEY")

# ── 模型 ──
EMBED_MODEL = "text-embedding-3-large"   # 向量化模型（雙語用 large）
LLM_MODEL = "gpt-5.5"                     # 生成答案模型

# ── 路徑 ──
DATA_DIR = "data"      # PDF 放這裡
DB_DIR = "db"          # 本機向量庫路徑（已改用 Qdrant Cloud，此項保留相容）
COLLECTION_NAME = "marine_docs"

# ── 切割參數 ──
CHUNK_SIZE = 512       # 每塊 token 數
CHUNK_OVERLAP = 64     # 重疊 token 數

# ── 檢索參數 ──
TOP_K = 5              # 最終回傳幾筆
RRF_CANDIDATES = 20    # RRF 粗篩出多少筆，送進重排序
RERANK_TOP_N = 5       # Cross-Encoder 精排後留幾筆
USE_RERANK = True      # 是否開啟 Cross-Encoder 重排序

# ── 開關 ──
GENERATE_ANSWER = True   # True=檢索後生成答案；False=只檢索

# ── 圖片處理 ──
PROCESS_IMAGES = True    # 建索引時是否處理圖片
IMAGE_LIMIT = 20         # 每份 PDF 最多處理幾張圖（None = 不限制）
