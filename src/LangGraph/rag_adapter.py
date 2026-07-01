"""LangGraph 與 hsu RAG 的連接層。

這個檔案的目的不是修改同學的 RAG，而是把 hsu 的用法包成穩定介面，
讓 LangGraph 節點不用直接依賴太多 hsu 內部細節。
"""

from __future__ import annotations

from typing import Any


Document = dict[str, Any]


def normalize_document(hit: dict[str, Any]) -> Document:
    """把 hsu 回傳的 hit 整理成 LangGraph 使用的 docs 格式。"""

    score = hit.get("rerank_score", hit.get("rrf_score", hit.get("score")))
    return {
        "text": hit.get("text", ""),
        "source": hit.get("source", ""),
        "page": hit.get("page", ""),
        "score": score,
        "rerank_score": hit.get("rerank_score"),
        "rrf_score": hit.get("rrf_score"),
    }


def search_documents(question: str, top_k: int | None = None) -> list[Document]:
    """呼叫 hsu RAG 搜尋，回傳標準化後的 docs。"""

    try:
        from hsu import search

        hits = search(question, top_k=top_k)
        return [normalize_document(hit) for hit in hits]
    except Exception as error:
        raise RuntimeError(f"hsu RAG 檢索失敗：{error}") from error


def generate_answer_from_documents(question: str, docs: list[Document]) -> str:
    """呼叫 hsu generator，根據 docs 產生回答。"""

    try:
        from hsu import generator

        return str(generator.generate_answer_text(question, docs))
    except Exception as error:
        raise RuntimeError(f"hsu RAG 生成失敗：{error}") from error


def build_context_from_documents(
    docs: list[Document],
    max_chars: int = 5000,
) -> str:
    """把 docs 組成可交給 LLM 的 context。"""

    parts: list[str] = []
    current_length = 0

    for index, doc in enumerate(docs, start=1):
        text = str(doc.get("text", "")).strip()
        source = doc.get("source", "未知來源")
        page = doc.get("page", "未知頁碼")
        block = f"[資料{index}，來源 {source} 第 {page} 頁]\n{text}"

        if current_length + len(block) > max_chars:
            break

        parts.append(block)
        current_length += len(block)

    return "\n\n".join(parts)


def format_sources(docs: list[Document]) -> list[dict[str, Any]]:
    """整理來源，方便 main.py 或 API 顯示。"""

    sources: list[dict[str, Any]] = []
    seen: set[tuple[Any, Any]] = set()

    for doc in docs:
        key = (doc.get("source"), doc.get("page"))
        if key in seen:
            continue

        seen.add(key)
        sources.append(
            {
                "file": doc.get("source", ""),
                "page": doc.get("page", ""),
                "score": doc.get("score"),
            }
        )

    return sources
