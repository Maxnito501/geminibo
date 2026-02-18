import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import json
import time
from datetime import datetime

# ==========================================
# 🛡️ ส่วนการตั้งค่าถาวร (ใส่ครั้งเดียวใช้ยาว)
# ==========================================
DEFAULT_CHANNEL_ACCESS_TOKEN = "XgyfEQh3dozGzEKKXVDUfWVBfBw+gX3yV976yTMnMnwPb+f9pHmytApjipzjXqhz/4IFB+qzMBpXx53NXTwaMMEZ+ctG6touSTIV4dXVEoWxoy5arbYVkkd2sxNCR0bX3GDc4A/XqjhnB38caUjyjQdB04t89/1O/w1cDnyilFU=" 
DEFAULT_USER_ID = "Ua666a6ab22c5871d5cf4dc99d0f5045c"

# ==========================================
# ⚙️ CONFIG & LINE MESSAGING API FUNCTION
# ==========================================
st.set_page_config(page_title="GeminiBo v4.3: Scheduled Autobot", layout="wide", page_icon="🤖")

def send_line_push(message, access_token, user_id):
    if not access_token or not user_id:
        return
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
    payload = {'to': user_id, 'messages': [{'type': 'text', 'text': message}]}
    try:
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        if res.status_code == 200: st.toast("Autobot ส่งข้อความเรียบร้อย!")
    except: pass

# ==========================================
# 🕒 SCHEDULER LOGIC (ระบบส่งอัตโนมัติตามเวลา)
# ==========================================
def run_autobot_scheduler(token, uid):
    # กำหนดเวลาที่ต้องการให้บอทส่ง (HH:MM)
    schedule_times = ["10:00", "11:00", "12:00", "14:00", "15:00", "16:00"]
    now_str = datetime.now().strftime("%H:%M")
    
    # ใช้ Session State เพื่อจำว่าชั่วโมงนี้ส่งไปหรือยัง (ป้องกันการส่งซ้ำทุกวินาที)
    if "last_sent_hour" not in st.session_state:
        st.session_state.last_sent_hour = ""

    if now_str in schedule_times and st.session_state.last_sent_hour != now_str:
        phase = get_market_phase()
        advice = get_advice(phase)
        full_msg = f"🤖 [Autobot WorkFlow]\nเวลา: {now_str}\nสถานะ: {phase}\nคำแนะนำ: {advice}"
        send_line_push(full_msg, token, uid)
        st.session_state.last_sent_hour = now_str

def get_market_phase():
    now = datetime.now().time()
    if now < datetime.strptime("10:00", "%H:%M").time(): return "ก่อนเปิดตลาด"
    if now < datetime.strptime("11:00", "%H:%M").time(): return "10:00 น. - ช่วงเปิดศึก"
    if now < datetime.strptime("12:30", "%H:%M").time(): return "11:00 น. - ช่วงยืนระยะ"
    if now < datetime.strptime("14:30", "%H:%M").time(): return "12:00 น. - พักรบ"
    if now < datetime.strptime("15:30", "%H:%M").time(): return "14:00 น. - เปิดบ่าย"
    if now < datetime.strptime("16:00", "%H:%M").time(): return "15:00 น. - นาทีทอง"
    return "16:00 น. - ปิดประตูตีแมว"

def get_advice(phase):
    if "10:00" in phase: return "เช็กราคาเปิด ระวังเจ้ามือลากไปเชือด"
    if "15:00" in phase: return "วอลลุ่มพีค! Ratio < 0.3 คือเจ้ามือเอาจริง Let Profit Run"
    if "16:00" in phase: return "ระวังอ่อยเหยื่อช่วง ATC ลุ้นปิด High"
    return "ตลาดปกติ เฝ้าระวัง RSI อย่าให้เกิน 70"

# ==========================================
# 🏹 UI: DASHBOARD
# ==========================================
st.title("🤖 GeminiBo v4.3: Scheduled Autobot")

# Sidebar: Config
st.sidebar.title("🛠️ Setup Autobot")
token = st.sidebar.text_input("Access Token", value=DEFAULT_CHANNEL_ACCESS_TOKEN, type="password")
uid = st.sidebar.text_input("User ID", value=DEFAULT_USER_ID)
auto_on = st.sidebar.toggle("เปิดระบบส่งอัตโนมัติ (Scheduler)", value=True)

watchlist = st.sidebar.multiselect("คัดหุ้นเข้า Autobot:", 
                                  ["WHA", "ROJNA", "AMATA", "SIRI", "MTC", "CPALL", "SAWAD", "PLANB"],
                                  default=["WHA", "MTC"])

# รันระบบ Scheduler
if auto_on and token and uid:
    run_autobot_scheduler(token, uid)

current_phase = get_market_phase()
msg_to_send = get_advice(current_phase)

with st.container(border=True):
    st.info(f"📢 **Autobot Report ({datetime.now().strftime('%H:%M:%S')}):** {msg_to_send}")
    if st.button("🔔 ส่ง LINE ทันที (Manual)"):
        send_line_push(f"🏗️ [GeminiBo Manual]\n{current_phase}\n{msg_to_send}", token, uid)

# ส่วนวิเคราะห์หุ้น (Whale Rider Logic)
st.markdown("---")
cols = st.columns(len(watchlist) if len(watchlist) > 0 else 1)
for i, sym in enumerate(watchlist[:3]):
    # จำลองดึงข้อมูล (ในแอปจริงจะดึงจาก yfinance)
    with cols[i]:
        with st.container(border=True):
            st.header(f"🛡️ {sym}")
            b1 = st.number_input("Bid 1 (ล้าน)", key=f"b1_{sym}", value=1.0)
            o1 = st.number_input("Offer 1 (ล้าน)", key=f"o1_{sym}", value=2.0)
            ratio = o1 / b1 if b1 > 0 else 0
            st.write(f"📊 Wall Ratio: {ratio:.2f}")
            
            if st.button(f"ส่งสถานะ {sym} เข้า LINE", key=f"btn_{sym}"):
                send_line_push(f"🎯 [Whale]\nหุ้น: {sym}\nสถานะ: {'🚀 ทางสะดวก' if ratio < 0.4 else '🆘 กำแพงลวง' if ratio > 4 else '⚖️ สมดุล'}", token, uid)

# ระบบ Refresh หน้าจออัตโนมัติเพื่อให้ Scheduler ทำงาน
st.sidebar.markdown("---")
st.sidebar.write("⏱️ แอปจะรีเฟรชตัวเองเพื่อเช็กเวลาทุกๆ 1 นาที")
time.sleep(1) # เล็กน้อยเพื่อไม่ให้รันหนักเกินไป
if auto_on:
    st.rerun()
