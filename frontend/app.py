import streamlit as st
import requests
from datetime import datetime

# 設定後端 API 網址 (本地開發預設為 8000 port)
BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="造船工程知識代理系統", page_icon="🚢", layout="wide")

# ==========================================
# 1. 狀態初始化與處理邏輯
# ==========================================
# 初始化歷史紀錄清單
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 初始化當前對話 ID (給這串對話一個專屬的身份證)
if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = datetime.now().strftime("thread_%Y%m%d_%H%M%S")

# 初始化當前對話
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "您好！請問今天想查詢哪方面的造船規範或工程知識？"}
    ]

# ==========================================
# 2. 側邊欄：功能按鈕與歷史紀錄
# ==========================================
with st.sidebar:
    # 1. 建立新對話按鈕
    if st.button("➕ 建立新對話", use_container_width=True, type="primary"):
        # 換一個全新的對話 ID
        st.session_state.current_thread_id = datetime.now().strftime("thread_%Y%m%d_%H%M%S")
        # 清空畫面，回到初始問候語
        st.session_state.messages = [{"role": "assistant", "content": "您好！請問今天想查詢哪方面的造船規範或工程知識？"}]
        st.rerun()

    st.markdown("---")

    # 2. 圖片與公式上傳區塊
    st.markdown("### 📸 上傳圖片或公式截圖")
    uploaded_image = st.file_uploader("支援 JPG, PNG 格式", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

    st.markdown("---")

    # 3. 歷史對話紀錄區塊
    st.header("📝 歷史對話紀錄")
    
    if not st.session_state.chat_history:
        st.caption("尚無歷史紀錄")
    else:
        # 使用 enumerate 與 reversed 來反轉順序並取得索引 (最新的在最上面)
        for idx, chat in enumerate(reversed(st.session_state.chat_history)):
            
            button_label = f"💬 {chat.get('time', '')} - {chat.get('title', '對話')}"
            
            # 每個按鈕必須有獨一無二的 key
            if st.button(button_label, key=f"history_btn_{chat.get('thread_id', idx)}_{idx}"):
                
                # 當按鈕被點擊時，切換 ID 並把歷史對話覆寫到主畫面的變數中
                st.session_state.current_thread_id = chat.get('thread_id')
                st.session_state.messages = list(chat['messages'])
                
                # 強制重新整理網頁，讓主畫面立刻顯示舊對話
                st.rerun()

# ==========================================
# 3. 主畫面與當前對話介面
# ==========================================
st.title("🚢 造船工程助理")

# 渲染當前歷史對話
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # 🛠️ 新增：把 OpenAI 的公式符號替換成 Streamlit 支援的 $$ 與 $
        safe_content = msg["content"].replace("\\[", "$$").replace("\\]", "$$").replace("\\(", "$").replace("\\)", "$")
        
        # 🛠️ 修改：明確使用 st.markdown 來渲染
        st.markdown(safe_content)
        
        # 如果有參考文獻，用折疊面板顯示
        if "sources" in msg and msg["sources"]:
            with st.expander("參考文獻"):
                for src in msg["sources"]:
                    st.write(f"- {src}")

# 接收使用者輸入
if prompt := st.chat_input("請輸入您的問題..."):
    # 將使用者訊息加入狀態並立刻顯示在畫面上
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 處理 AI 回應
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                reply = ""
                sources = []
                
                # 判斷是否有上傳圖片
                if uploaded_image is not None:
                    # 呼叫圖片分析 API
                    files = {"file": (uploaded_image.name, uploaded_image.getvalue(), uploaded_image.type)}
                    data = {"prompt": prompt}
                    response = requests.post(f"{BACKEND_URL}/api/analyze-image", files=files, data=data)
                else:
                    # ==========================================
                    # 🛠️ 偷偷在問題背後加上強制排版的「隱藏指令」
                    # ==========================================
                    hidden_instruction = "\n\n[系統隱藏指令：請務必使用 $ 或 $$ 來包覆所有數學公式與變數符號，絕對不要使用反引號 ( ` ) 來呈現數學式。]"
                    
                    # 呼叫一般文字對話 API
                    payload = {
                        "message": prompt + hidden_instruction, # 將指令和問題綁在一起送給後端
                        "user_id": "demo-user",
                        "thread_id": st.session_state.current_thread_id
                    }
                    response = requests.post(f"{BACKEND_URL}/api/chat", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    reply = result.get("reply", "未收到回應")
                    
                    # 🛠️ 新增：接收到新回答時，也立刻替換公式符號
                    reply = reply.replace("\\[", "$$").replace("\\]", "$$").replace("\\(", "$").replace("\\)", "$")
                    
                    sources = result.get("sources", [])
                else:
                    reply = f"API 錯誤：{response.status_code} - {response.text}"
                
                # 🛠️ 修改：顯示 AI 回覆時明確使用 st.markdown
                st.markdown(reply)
                
                
                            
                # 儲存對話到 messages
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply,
                    "sources": sources
                })
                
                # ==========================================
                # 同步將這筆對話更新到左側的歷史紀錄中
                # ==========================================
                # 1. 抓取使用者的第一句話當作這筆紀錄的「標題」
                user_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
                title = user_msgs[0][:15] + "..." if user_msgs else "新對話"
                
                # 2. 找找看歷史紀錄裡有沒有這張「身份證 (thread_id)」
                record_exists = False
                for chat in st.session_state.chat_history:
                    if chat.get("thread_id") == st.session_state.current_thread_id:
                        # 如果有，就直接更新它的對話內容
                        chat["messages"] = list(st.session_state.messages)
                        record_exists = True
                        break
                        
                # 3. 如果是全新的對話，就新增一筆完整的紀錄進去
                if not record_exists:
                    st.session_state.chat_history.append({
                        "thread_id": st.session_state.current_thread_id,
                        "title": title,
                        "time": datetime.now().strftime("%H:%M"),
                        "messages": list(st.session_state.messages)
                    })

            except Exception as e:
                st.error(f"連線失敗：{e}")