"""
階段 1：讀 PDF + 切 chunk。
負責把 PDF 變成一塊塊帶 metadata 的文字。

切割策略（階段 1-3 升級）：
- 用 RecursiveCharacterTextSplitter：優先在段落、句號等自然邊界切，保留語意完整
- 用 token 計數（tiktoken）：與 embedding 模型的計算單位一致，非單純字元數
"""
import os
import fitz  # PyMuPDF
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from . import config

# 用 OpenAI 的 tokenizer 來算 token 數（cl100k_base 適用於 embedding-3 系列）
_encoder = tiktoken.get_encoding("cl100k_base")


def _token_len(text):
    """計算一段文字的 token 數。"""
    return len(_encoder.encode(text))


# 建立切割器：以 token 為單位，優先在自然邊界（段落→換行→句號→空格）切割
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=config.CHUNK_SIZE,
    chunk_overlap=config.CHUNK_OVERLAP,
    length_function=_token_len,            # 用 token 數而非字元數
    separators=["\n\n", "\n", "。", ". ", " ", ""],  # 優先順序：段落>換行>句號>空格
)


def load_pdf(path):
    """逐頁讀取 PDF 文字，保留頁碼。"""
    doc = fitz.open(path)
    filename = os.path.basename(path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append({"page": i + 1, "text": text, "source": filename})
    doc.close()
    print(f"  ✓ {filename}：{len(pages)} 頁有內容")
    return pages


def split_chunks(pages):
    """用 Recursive + token 切割，保留來源與頁碼。"""
    chunks = []
    for p in pages:
        for piece in _splitter.split_text(p["text"]):
            piece = piece.strip()
            if piece:
                chunks.append({
                    "text": piece,
                    "page": p["page"],
                    "source": p["source"],
                })
    return chunks


def load_all_pdfs():
    """讀取 data/ 資料夾裡所有 PDF，全部切成 chunk。"""
    pdf_files = [f for f in os.listdir(config.DATA_DIR) if f.lower().endswith(".pdf")]
    if not pdf_files:
        raise FileNotFoundError(f"在 {config.DATA_DIR}/ 找不到任何 PDF，請先放入文件")
    return load_pdf_files(pdf_files)


def load_pdf_files(filenames):
    """只讀取指定的幾份 PDF（檔名清單），切成 chunk。"""
    all_chunks = []
    print(f"處理 {len(filenames)} 份 PDF：")
    for fname in filenames:
        path = os.path.join(config.DATA_DIR, fname)
        pages = load_pdf(path)
        all_chunks.extend(split_chunks(pages))
    print(f"✓ 切割完成，共 {len(all_chunks)} 個 chunk\n")
    return all_chunks


def list_pdf_files():
    """列出 data/ 資料夾裡所有 PDF 檔名。data 資料夾不存在時回傳空清單
    （純查詢場景，例如 src/hsu 沒有 data 資料夾，不該報錯）。"""
    if not os.path.isdir(config.DATA_DIR):
        return []
    return [f for f in os.listdir(config.DATA_DIR) if f.lower().endswith(".pdf")]
