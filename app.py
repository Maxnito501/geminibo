import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import json
from datetime import datetime

# ==========================================
# 🛡️ ส่วนการตั้งค่าถาวร (ใส่ครั้งเดียวใช้ยาว)
# ==========================================
# พี่โบ้เอา Token กับ ID มาใส่ในเครื่องหมายคำพูดได้เลยครับ
DEFAULT_CHANNEL_ACCESS_TOKEN = "XgyfEQh3dozGzEKKXVDUfWVBfBw+gX3yV976yTMnMnwPb+f9pHmytApjipzjXqhz/4IFB+qzMBpXx53NXTwaMMEZ+ctG6touSTIV4dXVEoWxoy5arbYVkkd2sxNCR0bX3GDc4A/XqjhnB38caUjyjQdB04t89/1O/w1cDnyilFU=" 
DEFAULT_USER_ID = "Ua666a6ab22c5871d5cf4dc99d0f5045c"

# ==========================================
# ⚙️ CONFIG & LINE MESSAGING API FUNCTION
# ==========================================
st.set_page_config(page_title="GeminiBo v4.2: Permanent Config", layout="wide", page_icon="🤖")

def send_line_push(message, access_token, user_id):
    """ ส่งข้อความผ่าน LINE Messaging API (Push Message) """
    if not access_token or not user_id:
        st.warning("กรุณาตั้งค่า Token และ User ID ก่อนส่ง")
        return
    
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    payload = {
        'to': user_id,
        'messages': [{'type': 'text', 'text': message}]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            st.toast("ส่งข้อความเรียบร้อย!")
        else:
            st.error(f"Error: {response.status_code}")
    except Exception as e:
        st.error(f"Failed: {e}")

def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty: return None
        price = df['Close'].iloc[-1]
        delta = df['Close'].diff()
        gain, loss = delta.clip(lower=0), -1 * delta.clip(upper=0)
        ma_g, ma_l = gain.rolling(window=14).mean(), loss.rolling(window=14).mean()
        rsi = 100 - (100 / (1 + ma_g/ma_l))
        return {"price": price, "rsi": rsi.iloc[-1]}
    except: return None

# ==========================================
# 🕒 TIME-BASED WORKFLOW LOGIC
# ==========================================
def get_market_phase():
    now = datetime.now().time()
    if now < datetime.strptime("10:00", "%H:%M").time(): return "ก่อนเปิดตลาด"
    if now < datetime.strptime("11:00", "%H:%M").time(): return "10:00 น. - ช่วงเปิดศึก"
    if now < datetime.strptime("12:30", "%H:%M").time(): return "11:00 น. - ช่วงยืนระยะ"
    if now < datetime.strptime("14:30", "%H:%M").time(): return "12:00 น. - พักรบ"
    if now < datetime.strptime("15:30", "%H:%M").time(): return "14:00 น. - เปิดบ่าย"
    if now < datetime.strptime("16:00", "%H:%M").time(): return "15:00 น. - นาทีทอง"
    return "16:00 น. - ปิดประตูตีแมว"

# ==========================================
# 🏹 UI: DASHBOARD
# ==========================================
st.title("🤖 GeminiBo v4.2: Messaging API (Auto-Login)")

# Sidebar: ดึงค่าจาก DEFAULT มาแสดง
st.sidebar.title("🛠️ Setup Autobot")
token = st.sidebar.text_input("Channel Access Token", value=DEFAULT_CHANNEL_ACCESS_TOKEN, type="password")
uid = st.sidebar.text_input("Your User ID", value=DEFAULT_USER_ID)

watchlist = st.sidebar.multiselect("คัดหุ้นเข้า Autobot:", 
                                  ["WHA", "ROJNA", "AMATA", "SIRI", "MTC", "CPALL", "SAWAD", "PLANB", "PTT"],
                                  default=["WHA", "MTC", "SAWAD"])

current_phase = get_market_phase()
st.subheader(f"📍 สถานะปัจจุบัน: {current_phase}")

with st.container(border=True):
    col_msg, col_btn = st.columns([4, 1])
    msg_to_send = "ตลาดปกติ เฝ้าระวัง RSI อย่าให้เกิน 70"
    if "10:00" in current_phase: msg_to_send = "💡 Bot Advice: เช็กราคาเปิด ระวังเจ้ามือลากไปเชือด"
    elif "15:00" in current_phase: msg_to_send = "🔥 Bot Advice: วอลลุ่มพีค! Ratio < 0.3 คือเจ้ามือเอาจริง"
    elif "16:00" in current_phase: msg_to_send = "🆘 Bot Advice: ระวังอ่อยเหยื่อช่วง ATC ลุ้นปิด High"
    
    col_msg.info(f"📢 **Autobot Report:** {msg_to_send}")
    if col_btn.button("🔔 ส่ง LINE"):
        send_line_push(f"🏗️ [GeminiBo]\n{current_phase}\n{msg_to_send}", token, uid)

st.markdown("---")
cols = st.columns(len(watchlist) if len(watchlist) > 0 else 1)
for i, sym in enumerate(watchlist[:3]):
    data = get_stock_data(sym)
    with cols[i]:
        if data:
            with st.container(border=True):
                st.header(f"🛡️ {sym}")
                st.write(f"**ราคา:** {data['price']:.2f} | **RSI:** {data['rsi']:.1f}")
                b1 = st.number_input("Bid 1 (ล้าน)", key=f"b1_{sym}", value=1.0)
                o1 = st.number_input("Offer 1 (ล้าน)", key=f"o1_{sym}", value=2.0)
                ratio = o1 / b1 if b1 > 0 else 0
                st.write(f"📊 **Wall Ratio:** {ratio:.2f}")
                
                status = "⚖️ สมดุล"
                if ratio > 4: status = "🆘 กำแพงลวง"
                elif ratio < 0.4: status = "🚀 ทางสะดวก"
                
                if st.button(f"ส่งสถานะ {sym}", key=f"btn_{sym}"):
                    send_line_push(f"🎯 [Whale]\nหุ้น: {sym}\nราคา: {data['price']}\nRSI: {data['rsi']:.1f}\nสถานะ: {status}", token, uid)

st.sidebar.markdown("---")
st.sidebar.write("🏆 **เป้าหมาย 500 บาท**")
st.sidebar.progress(0.5)
