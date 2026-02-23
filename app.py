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
# ⚙️ CONFIG & ENTRY ENGINE (v11.5)
# ==========================================
st.set_page_config(page_title="GeminiBo v11.5: Entry Sniper", layout="wide", page_icon="🎯")

SECRET_FILE = "bot_secrets.json"

def load_secrets():
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "r") as f:
            return json.load(f)
    return {"api_key": "", "line_token": "", "line_uid": ""}

creds = load_secrets()

# 🏹 ข้อมูลทัพหลวงชุดใหม่ (จุดดักซุ่ม & เงื่อนไขเข้าตี)
NEW_ARMY_CONFIG = {
    "PTT": {"entry": 33.50, "target": 38.00, "type": "Dividend", "note": "ช้อนหลัง XD หรือเมื่อ Ratio < 0.5"},
    "ROJNA": {"entry": 6.80, "target": "Whale", "type": "Growth", "note": "เข้าเมื่อ Ratio < 0.4 + RVOL > 1.5"},
    "AMATA": {"entry": 24.50, "target": "Whale", "type": "Growth", "note": "นิคมเบรกเอาท์ตาม Fund Flow"},
    "GULF": {"entry": 52.00, "target": 58.00, "type": "Tech/Power", "note": "ม้าเร็วข้ามต้าน 55.00"},
    "BBL": {"entry": 147.00, "target": 155.00, "type": "Value", "note": "ทัพหลวงเกษียณ 10 ปี (NVDR ชอบ)"},
    "BAM": {"entry": 8.80, "target": 9.50, "type": "CashFlow", "note": "เครื่องผลิตปันผลจ่ายค่าแอป"}
}

# ==========================================
# 🐳 AUTO-WHALE MONITOR (Simulation Ready)
# ==========================================
def fetch_whale_status(symbol):
    try:
        # จำลองสถานะวาฬอิงจากข้อมูลตลาด (ในอนาคตใช้ API SetSmart จริง)
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1d", interval="1m")
        price = df['Close'].iloc[-1] if not df.empty else 0.0
        
        # Simulation Logic: สุ่ม Ratio เพื่อดูการแจ้งเตือน
        import random
        sim_ratio = random.uniform(0.2, 4.0)
        sim_rvol = random.uniform(0.5, 3.0)
        
        return {"price": price, "ratio": sim_ratio, "rvol": sim_rvol}
    except: return None

# ==========================================
# 📊 MAIN DASHBOARD
# ==========================================
st.sidebar.title("🛡️ ENTRY COMMANDER")
auto_scan = st.sidebar.toggle("เปิดระบบสแกนจุดเข้าออโต้", value=True)

st.title("🎯 New Army Entry Sniper v11.5")
st.caption(f"📅 สมรภูมิวันที่: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# --- SECTION: 🏹 จังหวะเข้าทำ (Entry Alerts) ---
st.subheader("🚩 เรดาร์ดักซุ่ม (Entry Radar)")
cols = st.columns(3)

for i, (sym, cfg) in enumerate(NEW_ARMY_CONFIG.items()):
    data = fetch_whale_status(sym)
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"### 🛡️ {sym}")
            st.caption(f"ประเภท: {cfg['type']}")
            
            if data:
                st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}")
                
                # Logic วิเคราะห์จุดเข้า
                is_entry_price = data['price'] <= cfg['entry']
                is_whale_in = data['ratio'] < 0.4
                
                if is_entry_price and is_whale_in:
                    st.success("🚀 **SNIPER BUY!** วาฬลากในจุดรับ")
                elif is_entry_price:
                    st.warning("⚖️ **WAITING:** ราคาได้ แต่ Ratio ยังไม่สวย")
                elif is_whale_in:
                    st.info("🌊 **WHALE ACTIVE:** วาฬมาแต่ราคาสูงไปนิด")
                else:
                    st.write("⌛ **PATIENCE:** รอชัยภูมิที่ได้เปรียบ")
                
                st.markdown("---")
                st.write(f"📊 Ratio: **{data['ratio']:.2f}** | RVOL: **{data['rvol']:.2f}**")
                st.write(f"📍 จุดดักซุ่ม: **{cfg['entry']:.2f}**")
                st.info(f"💡 {cfg['note']}")
            else:
                st.write("กำลังเชื่อมต่อตาทิพย์...")

# ================= =========================
# 🔄 AUTO REFRESH
# ==========================================
if auto_scan:
    time.sleep(10)
    st.rerun()
