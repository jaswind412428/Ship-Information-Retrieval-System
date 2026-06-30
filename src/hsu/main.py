"""
主程式：把各模組串起來。
第一次跑會建索引；之後跑會直接讀已存的索引（持久化，不用重 embedding）。

支援兩種查詢：
- 文字查詢：直接輸入問題
- 以圖搜圖：輸入  img:圖片路徑   例如  img:test.png
"""
import config
import pdf_loader
import vectorstore
import retriever
import generator
import bm25_search
import image_processor


def build():
    """全部重建：讀 data/ 所有 PDF → 切 chunk →（可選）處理圖片 → 建索引。"""
    chunks = pdf_loader.load_all_pdfs()

    # 處理圖片：抽圖 + Vision 描述，當成 chunk 一起存（測試階段限 IMAGE_LIMIT 張）
    if config.PROCESS_IMAGES:
        print("開始處理圖片（Vision 生成描述）...\n")
        for fname in pdf_loader.list_pdf_files():
            path = f"{config.DATA_DIR}/{fname}"
            img_chunks = image_processor.extract_image_chunks(path, limit=config.IMAGE_LIMIT)
            chunks.extend(img_chunks)

    vectorstore.build_index(chunks)


def sync_new_pdfs():
    """自動偵測 data/ 裡的新 PDF，只對新檔做 embedding 並加進現有索引。"""
    on_disk = set(pdf_loader.list_pdf_files())
    indexed = vectorstore.get_indexed_sources()
    new_files = sorted(on_disk - indexed)

    if not new_files:
        print("✓ 沒有新 PDF，索引已是最新\n")
        return

    print(f"偵測到 {len(new_files)} 份新 PDF：{', '.join(new_files)}\n")
    chunks = pdf_loader.load_pdf_files(new_files)
    if config.PROCESS_IMAGES:
        for fname in new_files:
            path = f"{config.DATA_DIR}/{fname}"
            chunks.extend(image_processor.extract_image_chunks(path, limit=config.IMAGE_LIMIT))
    start_id = vectorstore.next_id()
    vectorstore.add_chunks(chunks, start_id)


def ask(question):
    """文字查詢：檢索 +（可選）生成。"""
    hits = retriever.search(question)
    retriever.print_hits(question, hits)
    if config.GENERATE_ANSWER:
        generator.generate_answer(question, hits)
    print("\n")


def ask_by_image(image_path):
    """以圖搜圖：上傳圖 → Vision 轉描述 → 用描述跑檢索。"""
    import os
    if not os.path.exists(image_path):
        print(f"⚠ 找不到圖片：{image_path}\n")
        return
    print("  分析上傳的圖片中...")
    desc = image_processor.describe_uploaded_image(image_path)
    print(f"  圖片描述：{desc}\n")
    # 用描述當查詢跑檢索
    hits = retriever.search(desc)
    retriever.print_hits(f"[以圖搜圖] {desc[:30]}...", hits)
    if config.GENERATE_ANSWER:
        generator.generate_answer(desc, hits)
    print("\n")


def main():
    print("\n========== Marine RAG 系統 ==========\n")

    if not vectorstore.index_exists():
        print("尚未建立索引，開始建立...\n")
        build()
    else:
        print("✓ 已有索引，檢查是否有新 PDF...\n")
        sync_new_pdfs()

    bm25_search.build_bm25()

    # 互動查詢
    print("（輸入問題進行文字查詢；輸入 img:圖片路徑 進行以圖搜圖；直接 Enter 離開）")
    while True:
        q = input("\n請輸入問題 > ").strip()
        if not q:
            break
        if q.startswith("img:"):
            ask_by_image(q[4:].strip())
        else:
            ask(q)


if __name__ == "__main__":
    main()
