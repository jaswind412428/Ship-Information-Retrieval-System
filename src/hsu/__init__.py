"""
hsu — RAG 檢索後端 package。

給團隊整合用。主程式可以這樣 import：

    from hsu import retriever, generator

    hits = retriever.search("什麼是功能原理")
    answer = generator.generate_answer_text("什麼是功能原理", hits)

或直接用便捷函式：

    from hsu import search, answer

    result = answer("什麼是功能原理")   # 一步到位：檢索 + 生成
    # result = {"answer": "...", "sources": [{"file","page"}, ...]}

也可以呼叫建索引（加新 PDF 時）：

    from hsu import build_index_from_data
    build_index_from_data()
"""
from . import retriever
from . import generator
from . import image_processor


def search(question, top_k=None):
    """檢索：回傳相關段落清單（已混合檢索 + 重排序）。"""
    return retriever.search(question, top_k=top_k)


def answer(question):
    """一步到位：檢索 + 生成。回傳 {answer, sources}。"""
    hits = retriever.search(question)
    text = generator.generate_answer_text(question, hits)
    seen, sources = set(), []
    for h in hits:
        key = (h["source"], h["page"])
        if key not in seen:
            seen.add(key)
            sources.append({"file": h["source"], "page": h["page"]})
    return {"answer": text, "sources": sources}


def answer_by_image(image_path):
    """以圖搜圖：上傳圖片路徑，回傳 {image_description, answer, sources}。"""
    desc = image_processor.describe_uploaded_image(image_path)
    hits = retriever.search(desc)
    text = generator.generate_answer_text(desc, hits)
    seen, sources = set(), []
    for h in hits:
        key = (h["source"], h["page"])
        if key not in seen:
            seen.add(key)
            sources.append({"file": h["source"], "page": h["page"]})
    return {"image_description": desc, "answer": text, "sources": sources}


def build_index_from_data():
    """建索引：讀 data/ 裡尚未進雲端的 PDF，embedding 後存到 Qdrant。"""
    from . import main as _main
    _main.sync_new_pdfs()


__all__ = [
    "retriever", "generator", "image_processor",
    "search", "answer", "answer_by_image", "build_index_from_data",
]
