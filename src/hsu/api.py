"""
FastAPI 接口：把 RAG 包成 HTTP API，讓前端能透過網路呼叫。

提供兩個接口：
  POST /ask          文字問答    body: {"question": "..."}
  POST /ask-image    以圖搜圖    form-data: file=圖片

啟動方式：
  uvicorn api:app --host 0.0.0.0 --port 8000

  --host 0.0.0.0 讓同網路的其他電腦（前端組員）也能連，
  不是只有本機。組員用 http://你的IP:8000 連。
"""
import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
import vectorstore
import bm25_search
import retriever
import generator
import image_processor

app = FastAPI(title="Marine RAG API")

# 允許前端網頁跨來源呼叫（前端和後端不同網址時需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 正式部署可改成前端的網址，安全一點
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 啟動時準備好索引與 BM25（只做一次）──
@app.on_event("startup")
def startup():
    if not vectorstore.index_exists():
        raise RuntimeError("尚未建立索引，請先用 main.py 建立索引再啟動 API")
    bm25_search.build_bm25()
    print("✓ API 已就緒")


# ── 請求/回應格式 ──
class AskRequest(BaseModel):
    question: str


def _format_sources(hits):
    """把檢索結果整理成前端要的來源清單（去重）。"""
    seen = set()
    sources = []
    for h in hits:
        key = (h["source"], h["page"])
        if key not in seen:
            seen.add(key)
            sources.append({"file": h["source"], "page": h["page"]})
    return sources


# ── 接口一：文字問答 ──
@app.post("/ask")
def ask(req: AskRequest):
    hits = retriever.search(req.question)
    answer = generator.generate_answer_text(req.question, hits)
    return {
        "answer": answer,
        "sources": _format_sources(hits),
    }


# ── 接口二：以圖搜圖 ──
@app.post("/ask-image")
async def ask_image(file: UploadFile = File(...)):
    # 把上傳的圖暫存到硬碟
    suffix = os.path.splitext(file.filename)[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # Vision 看圖 → 描述 → 用描述檢索
        desc = image_processor.describe_uploaded_image(tmp_path)
        hits = retriever.search(desc)
        answer = generator.generate_answer_text(desc, hits)
        return {
            "image_description": desc,
            "answer": answer,
            "sources": _format_sources(hits),
        }
    finally:
        os.unlink(tmp_path)   # 用完刪掉暫存圖


# ── 健康檢查（前端可以用這個確認後端有沒有開）──
@app.get("/health")
def health():
    return {"status": "ok"}
