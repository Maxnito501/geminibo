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
# พี่โบ้ใส่ Token กับ ID ตรงนี้เหมือนเดิมครับ
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
# 🕒 SCHEDULER & MARKET LOGIC
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

def get_advice(phase):
    if "10:00" in phase: return "เช็กราคาเปิด ระวังเจ้ามือลากไปเชือด"
    if "15:00" in phase: return "วอลลุ่มพีค! Ratio < 0.3 คือเจ้ามือเอาจริง Let Profit Run"
    if "16:00" in phase: return "ระวังอ่อยเหยื่อช่วง ATC ลุ้นปิด High"
    return "ตลาดปกติ เฝ้าระวัง RSI อย่าให้เกิน 70"

def run_autobot_scheduler(token, uid):
    schedule_times = ["10:00", "11:00", "12:00", "14:00", "15:00", "16:00"]
    now_str = datetime.now().strftime("%H:%M")
    if "last_sent_hour" not in st.session_state:
        st.session_state.last_sent_hour = ""
    if now_str in schedule_times and st.session_state.last_sent_hour != now_str:
        phase = get_market_phase()
        advice = get_advice(phase)
        full_msg = f"🤖 [Autobot WorkFlow]\nเวลา: {now_str}\nสถานะ: {phase}\nคำแนะนำ: {advice}"
        send_line_push(full_msg, token, uid)
        st.session_state.last_sent_hour = now_str

def get_stock_metrics(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < 15: return 0.0, 50.0
        price = df['Close'].iloc[-1]
        delta = df['Close'].diff()
        gain, loss = delta.clip(lower=0), -1 * delta.clip(upper=0)
        ma_g, ma_l = gain.rolling(window=14).mean(), loss.rolling(window=14).mean()
        rsi = 100 - (100 / (1 + ma_g/ma_l))
        return float(price), float(rsi.iloc[-1])
    except: return 0.0, 50.0

# ==========================================
# 🏹 UI: COMMAND CENTER (REVERTED TO v3.7 STYLE)
# ==========================================
st.title("🏹 Whale Commander v4.3: Autobot Edition")

# Sidebar: Config & Goals
st.sidebar.title("🛠️ Setup Autobot")
token = st.sidebar.text_input("Access Token", value=DEFAULT_CHANNEL_ACCESS_TOKEN, type="password")
uid = st.sidebar.text_input("User ID", value=DEFAULT_USER_ID)
auto_on = st.sidebar.toggle("เปิดระบบส่งอัตโนมัติ (Scheduler)", value=True)

st.sidebar.markdown("---")
st.sidebar.write("🏆 **เป้าหมายค่ากับข้าว 500 บาท**")
st.sidebar.progress(0.5)

# รันระบบ Scheduler ลับหลังบ้าน
if auto_on and token and uid:
    run_autobot_scheduler(token, uid)

# ส่วนแสดงผล Autobot Report ด้านบน
current_phase = get_market_phase()
msg_to_send = get_advice(current_phase)
with st.container(border=True):
    st.info(f"📢 **Autobot Report ({datetime.now().strftime('%H:%M:%S')}):** {msg_to_send}")
    if st.button("🔔 ส่ง LINE ทันที (Manual)"):
        send_line_push(f"🏗️ [GeminiBo Manual]\n{current_phase}\n{msg_to_send}", token, uid)

# ส่วนแสดงหุ้น 3 ตัวเรียงกัน (Layout v3.7 ที่พี่ชอบ)
st.markdown("---")
watchlist = ["WHA", "ROJNA", "AMATA", "SIRI", "MTC", "CPALL", "SAWAD", "PLANB"]
selected_stocks = st.multiselect("เลือกหุ้น 3 ตัวเพื่อเข้าตี:", watchlist, default=["WHA", "ROJNA", "MTC"])

cols = st.columns(3)
for i, sym in enumerate(selected_stocks[:3]):
    price, rsi = get_stock_metrics(sym)
    with cols[i]:
        with st.container(border=True):
            st.header(f"🛡️ {sym}")
            
            # Metrics
            mc1, mc2 = st.columns(2)
            mc1.metric("ราคา", f"{price:.2f}")
            mc2.metric("RSI (14)", f"{rsi:.1f}")

            # Volume Matrix 3 ช่อง (แบบดั้งเดิม)
            st.markdown("---")
            st.write("**🐳 Volume Matrix (ล้านหุ้น)**")
            v_col_b, v_col_o = st.columns(2)
            with v_col_b:
                st.caption("Bid (รับ)")
                b1 = st.number_input("Bid 1", key=f"b1_{sym}", value=1.0)
                b2 = st.number_input("Bid 2", key=f"b2_{sym}", value=1.0)
                b3 = st.number_input("Bid 3", key=f"b3_{sym}", value=1.0)
            with v_col_o:
                st.caption("Offer (ขวาง)")
                o1 = st.number_input("Offer 1", key=f"o1_{sym}", value=2.0)
                o2 = st.number_input("Offer 2", key=f"o2_{sym}", value=2.0)
                o3 = st.number_input("Offer 3", key=f"o3_{sym}", value=2.0)
            
            total_b = b1 + b2 + b3
            total_o = o1 + o2 + o3
            ratio = total_o / total_b if total_b > 0 else 0
            st.write(f"📊 Wall Ratio: **{ratio:.2f}**")
            
            # Whale Logic Analysis
            status = "⚖️ สมดุล/เลือกทาง"
            if ratio > 4: 
                status = "🆘 กำแพงลวง (ห้ามเคาะขวา)"
                st.error(status)
            elif ratio < 0.4: 
                status = "🚀 ทางสะดวก (Let Profit Run)"
                st.warning(status)
            else:
                st.success(status)

            # ปุ่มส่งแจ้งเตือนรายตัวเข้า LINE
            if st.button(f"ส่งสถานะ {sym} เข้า LINE", key=f"btn_{sym}"):
                detail = f"🎯 [Whale Update]\nหุ้น: {sym}\nราคา: {price}\nRSI: {rsi:.1f}\nสถานะ: {status}"
                send_line_push(detail, token, uid)

# ระบบ Auto-Refresh เพื่อให้ Scheduler ทำงานตลอดเวลา
if auto_on:
    time.sleep(1)
    st.rerun()
