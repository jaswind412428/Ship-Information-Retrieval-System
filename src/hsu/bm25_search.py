"""
階段 2：BM25 關鍵字搜尋。
跟向量搜尋互補：BM25 做精確詞彙匹配，適合法規條號、專有名詞。

中文用 jieba 斷詞，英文用空格分詞。BM25 需要在記憶體持有全部文件，
所以啟動時從向量庫撈出所有 chunk 文字，建一個 BM25 索引。
"""
import re
import jieba
from rank_bm25 import BM25Okapi
from vectorstore import get_collection

# 全域 BM25 索引（啟動時建一次，之後查詢重複用）
_bm25 = None
_docs = None       # 每個 chunk 的原始文字
_metas = None      # 每個 chunk 的 metadata（source, page）


def _tokenize(text):
    """中英混合斷詞：中文用 jieba，英文/數字保留為詞。"""
    text = text.lower()
    tokens = []
    for tok in jieba.cut(text):
        tok = tok.strip()
        # 過濾純空白與標點
        if tok and not re.fullmatch(r"[\s\W]+", tok):
            tokens.append(tok)
    return tokens


def build_bm25():
    """從向量庫撈出所有 chunk，建立 BM25 索引（記憶體）。"""
    global _bm25, _docs, _metas
    coll = get_collection()
    data = coll.get(include=["documents", "metadatas"])
    _docs = data["documents"]
    _metas = data["metadatas"]

    tokenized = [_tokenize(d) for d in _docs]
    _bm25 = BM25Okapi(tokenized)
    print(f"✓ BM25 索引建立完成，{len(_docs)} 筆\n")


def search(question, top_k=20):
    """BM25 關鍵字搜尋，回傳 Top-K 結果（含分數與排名）。"""
    if _bm25 is None:
        build_bm25()

    q_tokens = _tokenize(question)
    scores = _bm25.get_scores(q_tokens)

    # 取分數最高的 top_k 筆
    ranked_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    hits = []
    for rank, idx in enumerate(ranked_idx, 1):
        hits.append({
            "text": _docs[idx],
            "source": _metas[idx]["source"],
            "page": _metas[idx]["page"],
            "bm25_score": float(scores[idx]),
            "rank": rank,
        })
    return hits
