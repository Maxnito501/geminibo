# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import json
import os
import time
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & STORAGE (v10.1 Eternal Memory)
# ==========================================
st.set_page_config(page_title="GeminiBo v10.1: Eternal Memory", layout="wide", page_icon="♾️")

SECRET_FILE = "bot_secrets.json"

def save_secrets(api_key, line_token, line_uid):
    """ บันทึกข้อมูลไอดีลงไฟล์ถาวร (ห้ามลบ) """
    data = {
        "api_key": api_key,
        "line_token": line_token,
        "line_uid": line_uid
    }
    with open(SECRET_FILE, "w") as f:
        json.dump(data, f)

def load_secrets():
    """ ดึงข้อมูลไอดีจากไฟล์ถาวร """
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "r") as f:
            return json.load(f)
    return {"api_key": "", "line_token": "", "line_uid": ""}

# โหลดข้อมูลทันทีที่เปิดแอป
saved_data = load_secrets()

# ==========================================
# 🏹 STRATEGY & DECISION ENGINE
# ==========================================
STRATEGY_MAP = {
    "SIRI": {"avg": 1.47, "target": 1.63, "qty": 4700, "action": "รันกำไรไปเป้า 1.63 / รอปันผล"},
    "HANA": {"avg": 18.90, "target": 18.90, "qty": 300, "action": "เด้งเท่าทุนออก 1/2 ทันที"},
    "MTC": {"avg": 38.50, "target": 38.25, "qty": 400, "action": "เฉือนเนื้อรักษาทัพ (Cut Loss)"}
}

def send_line_push(message, access_token, user_id):
    """ ส่งสัญญาณรบผ่าน Messaging API """
    if not access_token or not user_id: return "ERROR: ขาดกุญแจ"
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
    payload = {'to': user_id, 'messages': [{'type': 'text', 'text': message}]}
    try:
        res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=5)
        return "SUCCESS" if res.status_code == 200 else f"ERROR: {res.status_code}"
    except: return "ERROR: Connection"

def analyze_whale_rhythm(symbol, bid_ratio):
    """ วิเคราะห์จังหวะการทำราคาของเจ้ามือ """
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1d", interval="1m")
        if df.empty: return None
        curr_price = df['Close'].iloc[-1]
        vol_now = df['Volume'].iloc[-1]
        
        # วิเคราะห์จังหวะ (Rhythm)
        status = "⚖️ ช่วงดูเชิง (Watching)"
        color = "#334155" # Slate
        
        if bid_ratio < 0.4 and vol_now > 100000:
            status = "🚀 วาฬลาก! (Whale Riding)"
            color = "#059669" # Green
        elif bid_ratio > 3.0:
            status = "🚨 กำแพงขวาง (Wall Block)"
            color = "#dc2626" # Red
        elif vol_now > 500000:
            status = "🌪️ เขย่าของ (Shake-off)"
            color = "#d97706" # Orange

        return {"price": curr_price, "status": status, "color": color, "vol": vol_now}
    except: return None

# ==========================================
# 📊 SIDEBAR: THE SECRET VAULT
# ==========================================
with st.sidebar:
    st.title("🛡️ คลังกุญแจฝังใจ v10.1")
    st.warning("ข้อมูลส่วนนี้ถูกบันทึกถาวรในเครื่องพี่โบ้")
    
    with st.expander("🔑 จัดการไอดี (ID Vault)", expanded=not saved_data["api_key"]):
        api_key = st.text_input("SetSmart API Key", value=saved_data["api_key"])
        line_token = st.text_input("Channel Access Token", type="password", value=saved_data["line_token"])
        line_uid = st.text_input("User ID (UID)", value=saved_data["line_uid"])
        
        if st.button("💾 บันทึกและจำฝังใจ (Save Forever)"):
            save_secrets(api_key, line_token, line_uid)
            st.success("บันทึกข้อมูลถาวรเรียบร้อย!")
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    if 'today_p' not in st.session_state: st.session_state.today_p = 0.0
    st.metric("🏆 กำไรสะสมวันนี้", f"{st.session_state.today_p:,.2f} บ.")
    # จ่ายค่าแอป 990 บาท/เดือน
    prog = min(max(st.session_state.today_p / 990, 0.0), 1.0)
    st.progress(prog)
    st.write(f"ความคืบหน้าค่าแอป: **{prog*100:.1f}%**")

# ==========================================
# 🏹 MAIN BATTLE STATION
# ==========================================
st.title("🏹 GeminiBo v10.1: Eternal Memory")
st.write(f"📡 สถานะระบบ: {'🟢 กุญแจพร้อมรบ' if saved_data['api_key'] and saved_data['line_token'] else '🔴 รอกรอกไอดีใน Sidebar'}")

if st.button("🔄 AUTO SYNC (อัปเดตราคาและจังหวะวาฬ)", use_container_width=True):
    st.rerun()

# วิเคราะห์ 3 ขุนพลของพี่โบ้
cols = st.columns(3)
for i, sym in enumerate(["SIRI", "HANA", "MTC"]):
    ratio_val = st.number_input(f"SetSmart Ratio ({sym})", value=1.0, step=0.1, key=f"r_{sym}")
    data = analyze_whale_rhythm(sym, ratio_val)
    
    with cols[i]:
        with st.container(border=True):
            st.header(f"🛡️ {sym}")
            if data:
                st.metric("ราคา", f"{data['price']:.2f}")
                st.markdown(f"""
                    <div style="background:{data['color']}; padding:10px; border-radius:12px; text-align:center; color:white; font-weight:bold; margin-bottom:12px;">
                        {data['status']}
                    </div>
                """, unsafe_allow_html=True)
                
                info = STRATEGY_MAP[sym]
                st.write(f"🎯 เป้าหมาย: **{info['target']:.2f}**")
                st.caption(f"💡 แผนรบ: {info['action']}")
                
                # ปุ่มส่งสัญญาณที่ฉลาดขึ้น
                if st.button(f"🔔 ส่งสัญญาณ {sym} เข้า LINE", key=f"btn_{sym}"):
                    msg = f"\n[Whale Report]\nหุ้น: {sym}\nราคา: {data['price']:.2f}\nสถานะ: {data['status']}\nคำแนะนำ: {info['action']}"
                    res = send_line_push(msg, saved_data['line_token'], saved_data['line_uid'])
                    st.toast(res)
            else:
                st.write("กำลังสแกนสัญญาณ...")

st.markdown("---")
st.info("💡 **กลยุทธ์ตามน้ำ:** หากเห็นสถานะ 'วาฬลาก!' (สีเขียว) ให้พี่โบ้เตรียมรันกำไรให้สุดเทรนด์ แต่ถ้าเห็น 'กำแพงขวาง' (สีแดง) ให้พิจารณาแบ่งขายเพื่อถือเงินสดรอปันผลครับ")
