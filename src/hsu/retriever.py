"""
階段 2-3：混合檢索（Hybrid Search）+ Multi-Query 查詢改寫。

流程：
  原始問句 → 改寫成多個子查詢
           → 每個子查詢各跑「向量 + BM25」兩路
           → 全部結果用 RRF 統一合併 → Top-K

RRF（Reciprocal Rank Fusion）：不看絕對分數，只看每筆在各路排第幾名，
把排名的倒數加起來。避免不同來源分數尺度不同互相干擾。
"""
from . import config
from . import bm25_search
from . import query_rewriter
from . import reranker
from .vectorstore import get_collection, embed_texts

RRF_K = 60   # RRF 常數（業界慣用 60）


def vector_search(question, top_k=20):
    """向量搜尋，回傳 Top-K（含排名）。"""
    coll = get_collection()
    q_vec = embed_texts([question])[0]
    res = coll.query(query_embeddings=[q_vec], n_results=top_k)

    hits = []
    for rank, (doc, meta, dist) in enumerate(
        zip(res["documents"][0], res["metadatas"][0], res["distances"][0]), 1
    ):
        hits.append({
            "text": doc,
            "source": meta["source"],
            "page": meta["page"],
            "rank": rank,
        })
    return hits


def _key(hit):
    """判斷是不是同一個 chunk（用 source+page+前40字辨識）。"""
    return (hit["source"], hit["page"], hit["text"][:40])


def fuse(rank_lists, top_k):
    """RRF 合併『多路』排名清單。

    rank_lists：list of list，每個內層 list 是一路的檢索結果（已含 rank）。
    每筆 chunk 的分數 = 在所有路 1/(K+排名) 的總和。
    """
    scores = {}
    store = {}
    for hits in rank_lists:
        for h in hits:
            k = _key(h)
            scores[k] = scores.get(k, 0) + 1 / (RRF_K + h["rank"])
            if k not in store:
                store[k] = h

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    results = []
    for k, rrf_score in ranked:
        h = store[k]
        results.append({
            "text": h["text"],
            "source": h["source"],
            "page": h["page"],
            "rrf_score": rrf_score,
        })
    return results


def search(question, top_k=None, use_multi_query=True):
    """檢索主入口：（改寫）→ 多子查詢 →（向量+BM25）→ RRF 粗篩 → 重排序精排。"""
    if top_k is None:
        top_k = config.TOP_K

    # 1. 查詢改寫成多個子查詢（關掉則只用原句）
    if use_multi_query:
        queries = query_rewriter.rewrite(question)
    else:
        queries = [question]

    # 2. 每個子查詢各跑向量 + BM25，全部收集成多路
    rank_lists = []
    for q in queries:
        rank_lists.append(vector_search(q, top_k=20))
        rank_lists.append(bm25_search.search(q, top_k=20))

    # 3. RRF 統一合併，粗篩出候選（預設 Top-20）
    candidates = fuse(rank_lists, config.RRF_CANDIDATES)

    # 4. Cross-Encoder 重排序，精排出最終 Top-K（用原始問句評分）
    if config.USE_RERANK:
        return reranker.rerank(question, candidates, top_n=top_k)
    else:
        return candidates[:top_k]


def print_hits(question, hits):
    """把檢索結果印出來。"""
    print("=" * 60)
    print(f"❓ 查詢：{question}")
    print("=" * 60)
    for rank, h in enumerate(hits, 1):
        preview = h["text"].replace("\n", " ")[:180]
        if "rerank_score" in h:
            score_str = f"重排分數：{h['rerank_score']:.4f}"
        else:
            score_str = f"RRF分數：{h.get('rrf_score', 0):.4f}"
        print(f"\n【第 {rank} 相關】　{h['source']} 第 {h['page']} 頁　{score_str}")
        print(f"  {preview}...")
