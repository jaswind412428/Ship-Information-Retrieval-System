import base64
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

# 1. 強制尋找並讀取旁邊的 .env 檔案
load_dotenv()

# 2. 偷偷印出來檢查系統現在抓到什麼引擎
print("\n" + "="*40)
print(f"🔍 系統目前抓到的引擎是：{os.getenv('LLM_PROVIDER')}")
print("="*40 + "\n")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, File, UploadFile, Form

# ==========================================
# 確保 Python 能正確讀取 src 目錄下的模組 (比照同學的寫法)
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# 匯入同學寫好的 LangGraph 核心流程
from LangGraph.flow import run_chat_flow

# 初始化 API 伺服器
app = FastAPI(title="造船工程 LangGraph API")

# ==========================================
# 定義前端傳遞過來的資料格式
# ==========================================
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "demo-user"
    # 支援傳遞 thread_id，讓不同的對話視窗擁有獨立的記憶體
    thread_id: Optional[str] = "demo-thread" 

class ChatResponse(BaseModel):
    reply: str
    sources: List[str]
    status: str
    record_id: Optional[str] = None

# ==========================================
# API 端點：文字對話與檢索
# ==========================================
@app.post("/api/chat", response_model=ChatResponse)
async def api_chat(request: ChatRequest):
    try:
        # 將前端傳來的問題交給 LangGraph 大腦處理
        state = run_chat_flow(
            question=request.message,
            user_id=request.user_id,
            thread_id=request.thread_id,
        )
        
        # 提取 AI 的回答內容
        ai_answer = state.get("ai_answer", "API 內部錯誤：未收到 AI 回覆。")
        
        print(f"\n🕵️ [後端準備送出的答案]：\n{ai_answer}\n")
        
        # 提取狀態與這筆對話的 JSON 紀錄 ID
        status = state.get("status", "unknown")
        record_id = state.get("id")
        
        # ==========================================
        # 🛠️ 提取參考文獻：從大腦狀態中找出實際的課本與頁數
        # ==========================================
        sources = state.get("sources", [])
        
        # 如果組員的寫法是把文獻存在 "documents" 裡面 (這是 RAG 最常見的寫法)
        if not sources and "documents" in state:
            for i, doc in enumerate(state["documents"]):
                # 嘗試取得 Document 物件裡面的 metadata (詮釋資料)
                meta = doc.metadata if hasattr(doc, "metadata") else (doc.get("metadata", {}) if isinstance(doc, dict) else {})
                
                # 抓取檔名 (通常叫 source 或 file_name) 與頁數 (page)
                # 使用 split("/")[-1] 來去掉冗長的路徑，只留檔名
                raw_source = str(meta.get("source", meta.get("file_name", "未知課本")))
                file_name = raw_source.split("/")[-1].split("\\")[-1] 
                page_num = meta.get("page", "未知")
                
                # 組合出漂亮的來源標籤，例如：[資料1] Engineering_Mechanics_Dynamics.pdf (第 582 頁)
                sources.append(f"[資料{i+1}] {file_name} (第 {page_num} 頁)")
            
            # 去除可能重複的文獻
            sources = list(dict.fromkeys(sources))
        
        return ChatResponse(
            reply=ai_answer,
            sources=sources,
            status=status,
            record_id=record_id
        )
        
    except Exception as e:
        # 如果 LangGraph 執行過程報錯，回傳 500 錯誤給前端
        raise HTTPException(status_code=500, detail=str(e))
    
# ... (上面是你原本的 api_chat 程式碼，完全不用動) ...

@app.post("/api/analyze-image")
async def analyze_image(
    prompt: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # 1. 讀取前端傳來的圖片，並轉換為 Base64 格式
        image_bytes = await file.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # 取得圖片的副檔名類型 (例如 image/jpeg, image/png)
        mime_type = file.content_type or "image/png"
        
        # 2. 強制設定「繁體中文」與「LaTeX 格式」的系統指令
        system_instruction = "請務必全程使用「繁體中文」詳細解答這道題目，並給出完整的計算過程，相關的公式請使用 LaTeX 格式輸出。"
        
        # 將使用者的問題與系統指令結合起來
        if prompt and prompt.strip():
            final_prompt = f"{system_instruction}\n\n使用者的補充說明：{prompt}"
        else:
            final_prompt = f"{system_instruction}\n\n請直接幫我解圖中的題目。"
        
        # 3. 召喚具備視覺能力的 OpenAI 模型
        # gpt-4o-mini 本身就具備強大的視覺辨識能力
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # 4. 把文字與圖片一起打包成 HumanMessage 格式送出
        message = HumanMessage(
            content=[
                {"type": "text", "text": final_prompt}, # 👈 改成 final_prompt
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                },
            ]
        )
        
        # 5. 執行分析並取得解答
        response = llm.invoke([message])
        ai_answer = response.content
        
        print(f"\n🕵️ [後端視覺模型解出的答案]：\n{ai_answer}\n")
        
        return {
            "reply": ai_answer,
            "sources": [],
            "status": "success",
            "record_id": "image-solved"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))