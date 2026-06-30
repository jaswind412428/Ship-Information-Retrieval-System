import streamlit as st
import requests
from datetime import datetime

# 設定後端 API 網址 (本地開發預設為 8000 port)
BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="造船工程知識代理系統", page_icon="🚢", layout="wide")

# ==========================================
# 1. 狀態初始化與處理邏輯
# ==========================================
# 初始化歷史紀錄清單 (存放過去的所有對話)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 初始化當前對話
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "您好！請問今天想查詢哪方面的造船規範或工程知識？"}
    ]

def start_new_chat():
    """處理建立新對話的邏輯：將當前對話存檔後清空"""
    # 如果當前對話有內容（超過一句初始問候語），則將其存入歷史紀錄
    if len(st.session_state.messages) > 1:
        # 擷取使用者的第一個問題作為標題，若太長則截斷
        first_user_msg = next((msg["content"] for msg in st.session_state.messages if msg["role"] == "user"), "未命名對話")
        title = first_user_msg[:15] + "..." if len(first_user_msg) > 15 else first_user_msg
        
        st.session_state.chat_history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": title,
            "messages": st.session_state.messages.copy()
        })
    
    # 重置當前對話畫面
    st.session_state.messages = [
        {"role": "assistant", "content": "您好！請問今天想查詢哪方面的造船規範或工程知識？"}
    ]

# ==========================================
# 2. 側邊欄設定 (加入新對話按鈕與歷史紀錄)
# ==========================================
with st.sidebar:
    # 建立新對話按鈕，點擊時會觸發 start_new_chat 函數
    st.button("➕ 建立新對話", on_click=start_new_chat, use_container_width=True, type="primary")
    
    st.markdown("---")
    st.header("⚙️ 系統狀態")
    st.success("API 連線正常")
    
    uploaded_image = st.file_uploader("上傳圖片或公式截圖", type=['png', 'jpg', 'jpeg'])
    
    st.markdown("---")
    st.header("📝 歷史對話紀錄")
    # 顯示歷史紀錄 (最新的在最上面)
    if not st.session_state.chat_history:
        st.caption("尚無歷史紀錄")
    else:
        for idx, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"{chat['time']} - {chat['title']}"):
                # 在側邊欄簡單預覽過去的問答
                for msg in chat['messages']:
                    if msg['role'] == 'user':
                        st.write(f"**🧑‍💻 User:** {msg['content']}")
                    elif msg['role'] == 'assistant':
                        st.caption(f"🤖 Agent: {msg['content'][:30]}...")

# ==========================================
# 3. 主畫面與當前對話介面
# ==========================================
st.title("🚢 造船工程助理")

# 渲染當前歷史對話
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📄 檢視參考資料來源"):
                for src in msg["sources"]:
                    st.markdown(f"- {src}")

# ==========================================
# 4. 處理使用者輸入並呼叫後端 API
# ==========================================
if prompt := st.chat_input("請輸入您的問題..."):
    # 顯示使用者問題
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("後端 Agent 處理中..."):
            try:
                if uploaded_image:
                    files = {"file": (uploaded_image.name, uploaded_image.getvalue(), uploaded_image.type)}
                    data = {"prompt": prompt}
                    res = requests.post(f"{BACKEND_URL}/api/analyze-image", files=files, data=data)
                else:
                    res = requests.post(f"{BACKEND_URL}/api/chat", json={"message": prompt})
                
                res.raise_for_status()
                response_data = res.json()
                
                reply = response_data.get("reply", "發生錯誤，無回傳內容")
                sources = response_data.get("sources", [])

                # 顯示回覆與來源
                st.markdown(reply)
                if sources:
                    with st.expander("📄 檢視參考資料來源"):
                        for src in sources:
                            st.markdown(f"- {src}")
                
                # 儲存對話
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply,
                    "sources": sources
                })
                
            except requests.exceptions.RequestException as e:
                st.error(f"無法連線至後端 API，請確認 FastAPI 伺服器是否已啟動。錯誤訊息：{e}")