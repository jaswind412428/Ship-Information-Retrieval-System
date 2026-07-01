"""
階段 4：圖片處理（多模態）。

兩個用途：
1. 建索引時：抽出 PDF 裡的圖片，用 GPT-5.5 Vision 生成文字描述，存進向量庫
   （描述當成可搜尋的文字，標 content_type='image'）
2. 查詢時：使用者上傳圖片 → Vision 轉描述 → 用描述跑檢索（以圖搜圖）

本質：圖片不能直接做語意搜尋，但「圖片的文字描述」可以。
所以把圖轉成描述，就能沿用現有的文字檢索流程。
"""
import os
import base64
import fitz  # PyMuPDF
from openai import OpenAI
from . import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

# 圖片過濾門檻：太小的（裝飾、logo）不處理
MIN_IMG_SIZE = 100


def _describe_image_bytes(img_bytes, media_type="image/png"):
    """用 GPT-5.5 Vision 看圖，生成文字描述。"""
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    resp = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text":
                    "這是一份工程力學教科書中的圖片。請用繁體中文簡潔描述這張圖的內容，"
                    "包含：圖的類型（如自由體圖、運動軌跡圖、機構圖等）、出現的物理量與符號、"
                    "以及它在說明什麼概念。控制在 100 字內。"},
                {"type": "image_url",
                 "image_url": {"url": f"data:{media_type};base64,{b64}"}},
            ],
        }],
    )
    return resp.choices[0].message.content.strip()


def extract_image_chunks(pdf_path, limit=None):
    """抽出 PDF 圖片並生成描述，回傳可存入向量庫的 chunk 清單。

    limit：最多處理幾張（測試階段先設 20，避免費用爆掉）。
    """
    doc = fitz.open(pdf_path)
    filename = os.path.basename(pdf_path)
    chunks = []
    count = 0

    for page_idx in range(doc.page_count):
        if limit and count >= limit:
            break
        for img in doc[page_idx].get_images():
            if limit and count >= limit:
                break
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                # 過濾太小的圖
                if pix.width < MIN_IMG_SIZE or pix.height < MIN_IMG_SIZE:
                    pix = None
                    continue
                # 轉成 PNG bytes
                if pix.n >= 5:  # CMYK 等，先轉 RGB
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                img_bytes = pix.tobytes("png")
                pix = None

                desc = _describe_image_bytes(img_bytes)
                count += 1
                print(f"  [{count}] {filename} 第 {page_idx+1} 頁的圖 → {desc[:40]}...")

                # 描述存成一個 chunk，標明這是圖片
                chunks.append({
                    "text": f"[圖片描述] {desc}",
                    "page": page_idx + 1,
                    "source": filename,
                    "content_type": "image",
                })
            except Exception as e:
                print(f"  ⚠ 第 {page_idx+1} 頁有張圖處理失敗：{e}")
                continue

    doc.close()
    print(f"✓ {filename}：處理了 {count} 張圖\n")
    return chunks


def describe_uploaded_image(image_path):
    """查詢用：把使用者上傳的圖片轉成文字描述（之後拿去檢索）。"""
    ext = os.path.splitext(image_path)[1].lower()
    media = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    return _describe_image_bytes(img_bytes, media_type=media)
