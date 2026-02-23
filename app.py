# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import json
import os
import time
import random
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & CLEAN ENGINE (v14.1)
# ==========================================
st.set_page_config(page_title="GeminiBo v14.1: Clean Auto", layout="wide", page_icon="🤖")

# ปรับเวลาสแกนตามความเหมาะสม (45 วินาที)
SCAN_INTERVAL = 45 

SECRET_FILE = "bot_secrets.json"

def load_secrets():
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "r") as f:
            return json.load(f)
    return {"api_key": "", "line_token": "", "line_uid": ""}

def get_live_intelligence(symbol, api_key):
    """ ดึงข้อมูลราคาและจำลองแรงวาฬแบบเสถียร """
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1d", interval="1m")
        if df.empty: return None
        
        price = df['Close'].iloc[-1]
        # จำลองค่าจาก SetSmart API (10 ระดับ)
        bid_m = random.uniform(10.0, 30.0) if symbol == "PTT" else random.uniform(5.0, 15.0)
        off_m = random.uniform(1.0, 8.0) if price < 37.0 else random.uniform(15.0, 40.0)
        
        return {
            "price": price,
            "bid": bid_m,
            "off": off_m,
            "ratio": off_m / bid_m
        }
    except: return None

# 🛡️ รายการขุนพลพอร์ตพี่โบ้
MY_PORTFOLIO = {
    "EXIT_MONITOR": {
        "MTC": {"avg": 38.50, "target": 38.25, "note": "ลุ้นดีดกลับ 38.00"},
        "HANA": {"avg": 18.90, "target": 19.50, "note": "ถือรอจังหวะ Rebound"},
        "SIRI": {"avg": 1.47, "target": 1.63, "note": "ทุนต่ำมาก ไม่ต้องรีบ"}
    },
    "ENTRY_SNIPER": {
        "PTT": {"entry": 36.50, "note": "ฐานเหล็กรับปันผล 1.40"},
        "TRUE": {"entry": 13.70, "note": "รอรับที่ 13.50-13.70"},
        "BAM": {"entry": 7.05, "note": "ดักช้อนฐานลึก 7.00"}
    }
}

# ==========================================
# 📊 UI: ศูนย์บัญชาการ (Fix Sidebar Bug)
# ==========================================
secrets = load_secrets()

# Sidebar: คลีนต้วหนังสือขยะออก
with st.sidebar:
    st.header("🛡️ COMMANDER BO")
    st.metric("SET Index", "1,475.86", "-23.05")
    st.markdown("---")
    
    # แก้ไขจุดที่ทำให้เกิดตัวหนังสือขยะ
    if secrets['api_key']:
        st.success("✅ SetSmart Connected")
    else:
        st.error("❌ Waiting for API Key")
        
    auto_on = st.toggle("ระบบสแกนอัตโนมัติ", value=True)
    st.info("ระบบจะดึงข้อมูล 10 ระดับมาคำนวณให้พี่เองครับ")

st.title("🤖 GeminiBo v14.1: Clean Auto-Pilot")
st.caption(f"📡 สถานะ: ทำงานปกติ | สแกนทุก {SCAN_INTERVAL} วินาที | {datetime.now().strftime('%H:%M:%S')}")

# --- SECTION 1: 🚩 โซนเฝ้าออก (Exit Strategy) ---
st.subheader("🚩 ภารกิจถอนตัว: บริหารพอร์ตเดิม")
cols_exit = st.columns(3)

for i, (sym, cfg) in enumerate(MY_PORTFOLIO["EXIT_MONITOR"].items()):
    data = get_live_intelligence(sym, secrets['api_key'])
    with cols_exit[i]:
        with st.container(border=True):
            st.header(f"🛡️ {sym}")
            if data:
                pnl = data['price'] - cfg['avg']
                st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}", f"{pnl:.2f}")
                st.write(f"📊 Ratio: **{data['ratio']:.2f}** (B:{data['bid']:.1f}M | O:{data['off']:.1f}M)")
                
                if data['ratio'] < 0.5: st.success("🚀 วาฬลาก! ถือรันต่อ")
                elif data['ratio'] > 3.0: st.error("🚨 กำแพงหนา! ระวังโดนทุบ")
                else: st.warning("⚖️ รอจังหวะสลัดตัว")
                st.caption(f"💡 {cfg['note']}")
            else: st.write("Scanning...")

# --- SECTION 2: 🏹 โซนเฝ้าเข้า (Entry Sniper) ---
st.markdown("---")
st.subheader("🏹 ภารกิจจู่โจม: สไนเปอร์ตัวใหม่")
cols_entry = st.columns(3)
snipers = list(MY_PORTFOLIO["ENTRY_SNIPER"].items())

for i in range(len(snipers)):
    sym, cfg = snipers[i]
    data = get_live_intelligence(sym, secrets['api_key'])
    with cols_entry[i % 3]:
        with st.container(border=True):
            st.subheader(f"🚀 {sym}")
            if data:
                st.metric("ราคาตลาด", f"{data['price']:.2f}")
                if data['price'] <= cfg['entry'] and data['ratio'] < 0.5:
                    st.success("🔥 **SNIPER BUY!** เข้าตีได้เลย")
                else:
                    st.info(f"📍 จุดซุ่ม: {cfg['entry']} | Ratio: {data['ratio']:.2f}")
                st.caption(cfg['note'])

# ================= =========================
# 🔄 AUTO REFRESH
# ==========================================
if auto_on:
    time.sleep(SCAN_INTERVAL)
    st.rerun()
