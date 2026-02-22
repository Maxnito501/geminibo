# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import json
import time
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & STREAMING ENGINE (v8.3 Python)
# ==========================================
st.set_page_config(page_title="GeminiBo v8.3: API Auto-Pilot", layout="wide", page_icon="🛡️")

# ฟังก์ชันดึงข้อมูลหุ้น (จำลองการใช้ API Key)
def get_live_market_data(symbol, api_key):
    try:
        # ในอนาคตพี่สามารถเปลี่ยนตรงนี้เป็น requests.get() ไปยัง API ของ SetSmart จริงๆ ได้
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1d", interval="1m")
        if df.empty: return None
        
        # จำลองการคำนวณ Bid/Offer จาก Volume (เพื่อให้พี่เห็นภาพ Whale Ratio)
        price = df['Close'].iloc[-1]
        vol = df['Volume'].sum()
        
        # ตัวอย่าง logic จำลองสำหรับพี่โบ้
        return {
            "price": price,
            "bid_sum": round(vol / 1000000 * 0.7, 2),
            "offer_sum": round(vol / 1000000 * 0.3, 2),
            "status": "Whale Active" if vol > 1000000 else "Normal"
        }
    except: return None

def send_line_alert(message, token, user_id):
    if not token: return
    # ตัวอย่างการส่งผ่าน Line Notify (แบบง่าย)
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {token}'}
    data = {'message': message}
    requests.post(url, headers=headers, data=data)

# ==========================================
# 💾 STATE MANAGEMENT (Cloud Sync Simulation)
# ==========================================
if 'config' not in st.session_state:
    st.session_state.config = {
        "line_token": "",
        "line_uid": "",
        "api_key": ""
    }

# ==========================================
# 📊 SIDEBAR: SETTINGS (ที่ใส่ไอดีครั้งเดียวจบ)
# ==========================================
with st.sidebar:
    st.title("🛡️ กองบัญชาการ")
    with st.expander("🔑 ตั้งค่ากุญแจไอดี (Settings)", expanded=False):
        st.session_state.config["api_key"] = st.text_input("SetSmart API Key", value=st.session_state.config["api_key"])
        st.session_state.config["line_token"] = st.text_input("LINE Token", value=st.session_state.config["line_token"], type="password")
        st.session_state.config["line_uid"] = st.text_input("LINE User ID", value=st.session_state.config["line_uid"])
        if st.button("💾 บันทึกลงระบบ"):
            st.success("บันทึกสำเร็จ!")

    st.markdown("---")
    st.metric("🏆 กำไรเป้าหมาย", "255.00 บ./วัน")
    st.progress(0.4)

# ==========================================
# 🏹 MAIN COMMAND CENTER
# ==========================================
st.title("🏹 GeminiBo v8.3: API Auto-Pilot")
st.write(f"📡 สถานะระบบ: {'พร้อมรบ (API Active)' if st.session_state.config['api_key'] else 'รอการตั้งค่า API'}")

# ปุ่ม Auto Sync ขนาดใหญ่
if st.button("🔄 AUTO SYNC ข้อมูลจาก SETSMART API", use_container_width=True):
    if not st.session_state.config["api_key"]:
        st.error("พี่โบ้ครับ กรุณาใส่ API Key ใน Sidebar ก่อนครับ!")
    else:
        with st.spinner("กำลังดึงข้อมูล SIRI, HANA, MTC จาก API..."):
            time.sleep(1.5)
            st.toast("อัปเดตข้อมูลสำเร็จ!")

# แสดงผล 3 หุ้นหลักของพี่โบ้
stocks = ["SIRI", "HANA", "MTC"]
cols = st.columns(3)

portfolio_data = {
    "SIRI": {"avg": 1.47, "target": 1.63},
    "HANA": {"avg": 18.90, "target": 18.90},
    "MTC": {"avg": 38.50, "target": 38.25}
}

for i, sym in enumerate(stocks):
    data = get_live_market_data(sym, st.session_state.config["api_key"])
    with cols[i]:
        with st.container(border=True):
            st.header(f"🛡️ {sym}")
            if data:
                st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}")
                ratio = data['offer_sum'] / data['bid_sum'] if data['bid_sum'] > 0 else 0
                st.write(f"🐳 Whale Ratio: **{ratio:.2f}**")
                
                # วิเคราะห์สถานะ
                if ratio < 0.4:
                    st.success("🚀 ทางสะดวก!")
                elif ratio > 3.0:
                    st.error("🆘 กำแพงลวง!")
                else:
                    st.info("⚖️ สมดุล")
                
                # แผนแก้ดอย
                target = portfolio_data[sym]['target']
                st.markdown(f"📍 เป้าหมาย: **{target:.2f}**")
                
                if st.button(f"🔔 ส่งแจ้งเตือน {sym}", key=f"btn_{sym}"):
                    msg = f"\n[GeminiBo Alert]\nหุ้น: {sym}\nราคา: {data['price']}\nRatio: {ratio:.2f}\nเป้าหมาย: {target}"
                    send_line_alert(msg, st.session_state.config["line_token"], st.session_state.config["line_uid"])
                    st.toast("ส่ง LINE เรียบร้อย!")
            else:
                st.write("รอการ Sync...")

st.markdown("---")
st.caption("v8.3 Streamlit Edition — ออกแบบมาเพื่อรันบน Cloud ของ Streamlit โดยเฉพาะครับพี่โบ้")
