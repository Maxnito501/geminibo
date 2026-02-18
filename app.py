import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import json
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & LINE MESSAGING API FUNCTION
# ==========================================
st.set_page_config(page_title="GeminiBo v4.1: Autobot Messaging API", layout="wide", page_icon="🤖")

def send_line_push(message, access_token, user_id):
    """ ส่งข้อความผ่าน LINE Messaging API (Push Message) """
    if not access_token or not user_id:
        return
    
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    payload = {
        'to': user_id,
        'messages': [
            {
                'type': 'text',
                'text': message
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            st.toast("ส่งข้อความผ่าน Messaging API เรียบร้อย!")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Failed to send message: {e}")

def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty: return None
        price = df['Close'].iloc[-1]
        delta = df['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        ma_g = gain.rolling(window=14).mean()
        ma_l = loss.rolling(window=14).mean()
        rsi = 100 - (100 / (1 + ma_g/ma_l))
        return {"price": price, "rsi": rsi.iloc[-1], "volume": df['Volume'].iloc[-1]}
    except:
        return None

# ==========================================
# 🕒 TIME-BASED WORKFLOW LOGIC
# ==========================================
def get_market_phase():
    now = datetime.now().time()
    if now < datetime.strptime("10:00", "%H:%M").time(): return "ก่อนเปิดตลาด (เตรียมแผน)"
    if now < datetime.strptime("11:00", "%H:%M").time(): return "10:00 น. - ช่วงเปิดศึก (Check ATO/Gap)"
    if now < datetime.strptime("12:30", "%H:%M").time(): return "11:00 น. - ช่วงยืนระยะ (Check Momentum)"
    if now < datetime.strptime("14:30", "%H:%M").time(): return "12:00 น. - พักรบ (สรุปครึ่งเช้า)"
    if now < datetime.strptime("15:30", "%H:%M").time(): return "14:00 น. - เปิดบ่าย (Check Baiting)"
    if now < datetime.strptime("16:00", "%H:%M").time(): return "15:00 น. - นาทีทอง (Whale Activity)"
    return "16:00 น. - ปิดประตูตีแมว (ATC Analysis)"

# ==========================================
# 🏹 UI: DASHBOARD
# ==========================================
st.title("🤖 GeminiBo v4.1: Messaging API Autobot")

# Sidebar: LINE Messaging API Setup
st.sidebar.title("🛠️ Setup Messaging API")
channel_access_token = st.sidebar.text_input("Channel Access Token", type="password", help="จาก LINE Developers Console")
line_user_id = st.sidebar.text_input("Your User ID", help="เลข UID ของพี่ (ดูได้จากหน้า Console)")

watchlist = st.sidebar.multiselect("คัดหุ้นเข้า Autobot:", 
                                  ["WHA", "ROJNA", "AMATA", "SIRI", "MTC", "CPALL", "SAWAD", "PLANB", "PTT"],
                                  default=["WHA", "MTC", "SAWAD"])

current_phase = get_market_phase()
st.subheader(f"📍 สถานะปัจจุบัน: {current_phase}")

# ส่วนแสดงการแจ้งเตือน Autobot
with st.container(border=True):
    col_msg, col_btn = st.columns([4, 1])
    msg_to_send = ""
    
    with col_msg:
        st.markdown(f"### 📢 Autobot Battle Report ({datetime.now().strftime('%H:%M')})")
        if "10:00" in current_phase:
            msg_to_send = "💡 Bot Advice: เช็กวอลลุ่มเปิด ถ้าเปิดโดดเกิน 3% และ Bid หนา ให้ระวังเจ้ามือ 'ลากไปเชือด'"
            st.info(msg_to_send)
        elif "15:00" in current_phase:
            msg_to_send = "🔥 Bot Advice: วอลลุ่มพีค! สแกน Wall Ratio ด่วน ถ้า Ratio < 0.3 คือเจ้ามือเอาจริง Let Profit Run!"
            st.warning(msg_to_send)
        elif "16:00" in current_phase:
            msg_to_send = "🆘 Bot Advice: ระวัง 'อ่อยเหยื่อ' ช่วง ATC ถ้า Offer โดนรวบทีเดียว ให้ถือลุ้นปิด High"
            st.error(msg_to_send)
        else:
            msg_to_send = "✅ Bot Advice: ตลาดปกติ เฝ้าระวัง RSI อย่าให้เกิน 70"
            st.success(msg_to_send)

    with col_btn:
        if st.button("🔔 ส่ง Push Message"):
            if channel_access_token and line_user_id:
                full_msg = f"🏗️ [GeminiBo v4.1]\nสถานะ: {current_phase}\nคำแนะนำ: {msg_to_send}"
                send_line_push(full_msg, channel_access_token, line_user_id)
            else:
                st.error("กรุณาใส่ Token และ User ID")

# ส่วนแสดงหุ้น 3 ตัวเรียงกัน
st.markdown("---")
cols = st.columns(len(watchlist) if len(watchlist) > 0 else 1)

for i, sym in enumerate(watchlist[:3]):
    data = get_stock_data(sym)
    with cols[i]:
        if data:
            with st.container(border=True):
                st.header(f"🛡️ {sym}")
                st.write(f"**ราคา:** {data['price']:.2f} | **RSI:** {data['rsi']:.1f}")
                
                c_bid, c_off = st.columns(2)
                with c_bid:
                    b1 = st.number_input("Bid 1 (ล้าน)", key=f"b1_{sym}", value=1.0)
                with c_off:
                    o1 = st.number_input("Offer 1 (ล้าน)", key=f"o1_{sym}", value=2.0)
                
                ratio = o1 / b1 if b1 > 0 else 0
                st.write(f"📊 **Wall Ratio:** {ratio:.2f}")
                
                whale_status = ""
                if ratio > 4:
                    whale_status = "🆘 กำแพงลวง: เจ้าขวางหนา บีบคายของ"
                    st.error(whale_status)
                elif ratio < 0.4:
                    whale_status = "🚀 ทางสะดวก: เตรียมกระชากราคา"
                    st.warning(whale_status)
                else:
                    whale_status = "⚖️ สมดุล: เจ้ามือดูเชิง"
                    st.info(whale_status)
                
                # ปุ่มแจ้งเตือนรายตัวผ่าน Messaging API
                if st.button(f"ส่งสถานะ {sym}", key=f"btn_{sym}"):
                    if channel_access_token and line_user_id:
                        detail = (f"🎯 [Whale Update]\n"
                                 f"หุ้น: {sym}\n"
                                 f"ราคา: {data['price']}\n"
                                 f"RSI: {data['rsi']:.1f}\n"
                                 f"สถานะ: {whale_status}")
                        send_line_push(detail, channel_access_token, line_user_id)

st.sidebar.markdown("---")
st.sidebar.write("🏆 **เป้าหมายค่ากับข้าว 500 บาท**")
st.sidebar.progress(0.5)
