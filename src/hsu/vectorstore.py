"""
向量庫（Qdrant Cloud 版）。
從 Chroma 換成 Qdrant Cloud：索引存在雲端，你和組員的後端都連同一個，索引共用。

為了不動其他檔案（retriever、bm25_search 都靠 get_collection()），
這裡用一個 wrapper 模擬 Chroma 的 query()/get()/count() 介面，對外行為一致。
"""
import uuid
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from . import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

# 延遲連線：用到時才連 Qdrant Cloud（避免 import 時就連、也方便測試替換）
_qdrant = None


def _get_qdrant():
    global _qdrant
    if _qdrant is None:
        _qdrant = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY, timeout=120)
    return _qdrant


# text-embedding-3-large 的維度
VECTOR_SIZE = 3072


def embed_texts(texts):
    """把文字批次轉成向量。"""
    all_vecs = []
    batch = 100
    for i in range(0, len(texts), batch):
        resp = client.embeddings.create(model=config.EMBED_MODEL, input=texts[i:i + batch])
        all_vecs.extend([d.embedding for d in resp.data])
        print(f"  embedding 進度：{min(i + batch, len(texts))}/{len(texts)}")
    return all_vecs


class _QdrantCollection:
    """包一層，讓 Qdrant 用起來像 Chroma 的 collection（query/get/count）。"""

    def __init__(self, qdrant, name):
        self.q = qdrant
        self.name = name

    def count(self):
        return self.q.count(self.name, exact=True).count

    def query(self, query_embeddings, n_results):
        """模擬 Chroma 的 query：回傳 {documents, metadatas, distances}（都包一層 list）。"""
        res = self.q.query_points(
            self.name,
            query=query_embeddings[0],
            limit=n_results,
            with_payload=True,
        ).points
        docs, metas, dists = [], [], []
        for p in res:
            docs.append(p.payload["text"])
            metas.append({"source": p.payload["source"],
                          "page": p.payload["page"],
                          "content_type": p.payload.get("content_type", "text")})
            # Qdrant 回傳相似度分數（越高越像）；轉成 Chroma 風格的「距離」（越小越像）
            dists.append(1 - p.score)
        return {"documents": [docs], "metadatas": [metas], "distances": [dists]}

    def get(self, include=None):
        """模擬 Chroma 的 get：撈出全部，回傳 {documents, metadatas}。"""
        docs, metas = [], []
        offset = None
        while True:
            points, offset = self.q.scroll(
                self.name, limit=1000, offset=offset, with_payload=True,
            )
            for p in points:
                docs.append(p.payload["text"])
                metas.append({"source": p.payload["source"],
                              "page": p.payload["page"],
                              "content_type": p.payload.get("content_type", "text")})
            if offset is None:
                break
        return {"documents": docs, "metadatas": metas}


def _ensure_collection():
    """確保 collection 存在（不存在就建）。"""
    existing = [c.name for c in _get_qdrant().get_collections().collections]
    if config.COLLECTION_NAME not in existing:
        _get_qdrant().create_collection(
            config.COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def get_collection():
    """取得向量庫 collection（Qdrant 版，介面相容 Chroma）。"""
    _ensure_collection()
    return _QdrantCollection(_get_qdrant(), config.COLLECTION_NAME)


def _write_points(chunks, vecs):
    """把 chunk + 向量寫進 Qdrant，分批上傳。"""
    points = []
    for c, v in zip(chunks, vecs):
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=v,
            payload={
                "text": c["text"],
                "source": c["source"],
                "page": c["page"],
                "content_type": c.get("content_type", "text"),
            },
        ))
    batch = 100   # 每批小一點，避免單次傳太多導致雲端逾時
    for i in range(0, len(points), batch):
        _get_qdrant().upsert(config.COLLECTION_NAME, points=points[i:i + batch], wait=True)
        print(f"  寫入進度：{min(i + batch, len(points))}/{len(points)}")


def build_index(chunks):
    """把 chunk 向量化並存入 Qdrant（重建：先刪 collection 再建）。"""
    try:
        _get_qdrant().delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass
    _ensure_collection()

    vecs = embed_texts([c["text"] for c in chunks])
    _write_points(chunks, vecs)
    print(f"✓ 索引建立完成，{len(chunks)} 筆已存到 Qdrant Cloud\n")


def index_exists():
    """檢查 Qdrant 裡是否已經有資料。"""
    try:
        return get_collection().count() > 0
    except Exception:
        return False


def get_indexed_sources():
    """回傳已經建過索引的文件名稱集合。"""
    try:
        coll = get_collection()
        if coll.count() == 0:
            return set()
        data = coll.get()
        return {m["source"] for m in data["metadatas"]}
    except Exception:
        return set()


def add_chunks(chunks, start_id=None):
    """把一批新 chunk 向量化後加進 Qdrant（不刪舊的）。start_id 在 Qdrant 版用不到（用 uuid）。"""
    _ensure_collection()
    vecs = embed_texts([c["text"] for c in chunks])
    _write_points(chunks, vecs)
    print(f"✓ 已新增 {len(chunks)} 筆到 Qdrant Cloud\n")


def next_id():
    """Qdrant 用 uuid 當 id，不需要編號，回傳 0 即可（相容舊呼叫）。"""
    return 0
