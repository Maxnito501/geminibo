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
# ⚙️ CONFIG & HYBRID ENGINE (v11.6)
# ==========================================
st.set_page_config(page_title="GeminiBo v11.6: Hybrid Commander", layout="wide", page_icon="⚔️")

SECRET_FILE = "bot_secrets.json"

def load_secrets():
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "r") as f:
            return json.load(f)
    return {"api_key": "", "line_token": "", "line_uid": ""}

creds = load_secrets()

# 🛡️ ข้อมูลหน่วยแก้ดอย (Recovery Squad)
RECOVERY_CONFIG = {
    "SIRI": {"avg": 1.47, "exit": 1.63, "qty": 4700, "note": "แบ่งขาย 2,000 ที่ 1.63 / รอปันผล"},
    "HANA": {"avg": 18.90, "exit": 18.90, "qty": 300, "note": "ออกหน้าเสมอถอนทุนคืน"},
    "MTC": {"avg": 38.50, "exit": 38.25, "qty": 400, "note": "เฉือน 1/2 ที่ 38.25 ลดความเสี่ยง"}
}

# 🏹 ข้อมูลทัพหลวงชุดใหม่ (New Army Entry)
NEW_ARMY_CONFIG = {
    "PTT": {"entry": 33.50, "target": 38.00, "note": "สไนเปอร์กำไร / รับปันผล"},
    "ROJNA": {"entry": 6.80, "target": "Whale", "note": "ตาม Fund Flow นิคม"},
    "AMATA": {"entry": 24.50, "target": "Whale", "note": "เบรกเอาท์ตามวาฬ"},
    "GULF": {"entry": 52.00, "target": 55.00, "note": "ม้าเร็วพลังงาน"},
    "BBL": {"entry": 147.00, "target": 155.00, "note": "ฐานพอร์ตเกษียณ 10 ปี"},
    "BAM": {"entry": 8.80, "target": 9.50, "note": "ปั๊มปันผลจ่ายค่าแอป"}
}

def fetch_live_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1d", interval="1m")
        price = df['Close'].iloc[-1] if not df.empty else 0.0
        # Simulation Whale Data (ในอนาคตใช้ API SetSmart)
        import random
        return {"price": price, "ratio": random.uniform(0.2, 4.0), "rvol": random.uniform(0.5, 3.0)}
    except: return None

# ==========================================
# 📊 UI & CONTROL
# ==========================================
st.sidebar.title("🛡️ COMMAND CENTER")
auto_scan = st.sidebar.toggle("ระบบสแกน Real-time (30s)", value=True)
st.sidebar.markdown("---")
st.sidebar.metric("🏆 กำไรสะสม (เป้า 990.-)", "639.00 บ.")
st.sidebar.progress(0.65)

st.title("⚔️ Hybrid War Commander v11.6")
st.caption(f"📅 อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}")

# --- SECTION 1: 🚩 ภารกิจสลัดดอย (Exit Monitor) ---
st.header("🚩 ภารกิจสลัดดอย (Recovery Squad)")
cols_old = st.columns(3)
for i, (sym, cfg) in enumerate(RECOVERY_CONFIG.items()):
    data = fetch_live_data(sym)
    with cols_old[i]:
        with st.container(border=True):
            st.subheader(f"🛡️ {sym}")
            if data:
                pnl = (data['price'] - cfg['avg']) * cfg['qty']
                st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}", f"{pnl:,.2f} บ.")
                
                # Logic แจ้งเตือนขาย
                if data['price'] >= cfg['exit']:
                    st.success(f"🎯 **TARGET HIT!** ปล่อยที่ {cfg['exit']} ตามแผน")
                elif data['ratio'] > 3.5:
                    st.error("🚨 **WALL ALERT!** วาฬขวางหนา ชิงขายก่อน")
                else:
                    st.info(f"⏳ {cfg['note']}")
                
                st.caption(f"Whale Ratio: {data['ratio']:.2f}")
            else: st.write("Scanning...")

# --- SECTION 2: 🏹 ภารกิจล่ากำไร (Entry Sniper) ---
st.markdown("---")
st.header("🏹 ภารกิจล่ากำไร (New Army)")
cols_new = st.columns(3)
for i, (sym, cfg) in enumerate(NEW_ARMY_CONFIG.items()):
    data = fetch_live_data(sym)
    with cols_new[i % 3]:
        with st.container(border=True):
            st.markdown(f"### 🚀 {sym}")
            if data:
                st.metric("ราคา", f"{data['price']:.2f}")
                # Logic แจ้งเตือนซื้อ
                if data['price'] <= cfg['entry'] and data['ratio'] < 0.4:
                    st.warning("🔥 **SNIPER BUY!** วาฬรวบในจุดรับ")
                else:
                    st.write(f"📍 จุดซุ่ม: {cfg['entry']} | Ratio: {data['ratio']:.2f}")
                st.caption(cfg['note'])

if auto_scan:
    time.sleep(30)
    st.rerun()
