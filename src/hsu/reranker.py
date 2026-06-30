"""
階段 3：Cross-Encoder 重排序（Reranking）。
RRF 粗篩出 Top-20 後，用 BGE Reranker 對每筆做真實相關度評分，精排出 Top-5。

跟 RRF 的差別：
- RRF 只看排名（快，但分不出真實相關度，相關和不相關可能同分）
- Cross-Encoder 把 (問題, 段落) 一起丟進模型做交叉比對，給出真實相關分數

模型 BAAI/bge-reranker-v2-m3 支援多語言，中英文跨語言都能評分，
所以就算 BM25 撈進不相關內容，這層也能把它降下去。
"""
from sentence_transformers import CrossEncoder
import config

# 全域載入一次（第一次會下載模型，約 600MB，之後快取在本機）
_model = None


def _get_model():
    global _model
    if _model is None:
        print("  載入 Reranker 模型（首次會下載，約 600MB）...")
        _model = CrossEncoder("BAAI/bge-reranker-v2-m3")
        print("  ✓ Reranker 模型載入完成")
    return _model


def rerank(question, hits, top_n=None):
    """對 hits（RRF 粗篩結果）做 Cross-Encoder 精排，回傳 Top-N。

    在每筆 hit 加上 rerank_score 欄位，依此分數由高到低排序。
    """
    if top_n is None:
        top_n = config.RERANK_TOP_N
    if not hits:
        return []

    model = _get_model()

    # 組成 (問題, 段落) 配對，讓模型逐筆打分
    pairs = [[question, h["text"]] for h in hits]
    scores = model.predict(pairs)

    # 把分數寫回每筆，依分數排序取 Top-N
    for h, s in zip(hits, scores):
        h["rerank_score"] = float(s)

    ranked = sorted(hits, key=lambda h: h["rerank_score"], reverse=True)
    return ranked[:top_n]
