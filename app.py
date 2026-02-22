# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import json
import time
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v9.3 Cost Recovery)
# ==========================================
st.set_page_config(page_title="GeminiBo v9.3: Cost Recovery", layout="wide", page_icon="💰")

# ต้นทุนการดำเนินธุรกิจ (990 บาท/เดือน)
MONTHLY_COST = 990.0
DAILY_BREAKEVEN = MONTHLY_COST / 20 # คิด 20 วันทำการ = 49.5 บาท/วัน

STRATEGY_MAP = {
    "SIRI": {"avg": 1.47, "target": 1.63, "qty": 4700, "action": "ขาย 2,000 หุ้นที่เป้า"},
    "HANA": {"avg": 18.90, "target": 18.90, "qty": 300, "action": "เด้งเท่าทุนออก 1/2"},
    "MTC": {"avg": 38.50, "target": 38.25, "qty": 400, "action": "เฉือนเนื้อรักษาทัพ"}
}

def analyze_rhythm(symbol, api_key, bid_ratio):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1d", interval="1m")
        if df.empty: return None
        curr_price = df['Close'].iloc[-1]
        vol_now = df['Volume'].iloc[-1]
        
        status = "⚖️ นิ่ง (Waiting)"
        color = "white"
        if bid_ratio < 0.4 and vol_now > 100000:
            status = "🚀 เริ่มกระชาก (Whale Ride)"; color = "#00ff00"
        elif bid_ratio > 3.0:
            status = "🚨 โดนขวาง (Wall Block)"; color = "#ff4b4b"
            
        return {"price": curr_price, "status": status, "color": color, "vol": vol_now}
    except: return None

# ==========================================
# 📊 SIDEBAR: COST RECOVERY TRACKER
# ==========================================
with st.sidebar:
    st.title("🛡️ กองบัญชาการ v9.3")
    
    # ส่วนติดตามการคืนทุน
    st.subheader("💰 ระบบติดตามการคืนทุน")
    if 'today_profit' not in st.session_state: st.session_state.today_profit = 0.0
    
    profit_input = st.number_input("กำไรปิดไม้สะสมวันนี้ (บ.)", value=st.session_state.today_profit)
    st.session_state.today_profit = profit_input
    
    # คำนวณว่ากำไรวันนี้จ่ายค่าแอปได้กี่วัน
    days_paid = st.session_state.today_profit / DAILY_BREAKEVEN
    st.metric("จ่ายค่าแอปได้แล้ว (วัน)", f"{days_paid:.1f} วัน", f"{st.session_state.today_profit - DAILY_BREAKEVEN:+.2f} บ.")
    
    prog = min(max(st.session_state.today_profit / MONTHLY_COST, 0.0), 1.0)
    st.write(f"🎯 เป้าหมายรายเดือน {MONTHLY_COST} บ.: **{prog*100:.1f}%**")
    st.progress(prog)

    st.markdown("---")
    with st.expander("🔑 คลังกุญแจไอดี"):
        st.session_state.api_key = st.text_input("SetSmart API Key", value=st.session_state.get('api_key', ''))
        st.session_state.line_token = st.text_input("LINE Token", type="password", value=st.session_state.get('line_token', ''))

# ==========================================
# 🏹 MAIN BATTLE STATION
# ==========================================
st.title("🏹 GeminiBo v9.3: Cost Recovery Mode")
st.write(f"📡 สถานะ: {'🟢 พร้อมปั๊มกำไร' if st.session_state.api_key else '🔴 กรุณาใส่ API Key'}")

cols = st.columns(3)
for i, sym in enumerate(["SIRI", "HANA", "MTC"]):
    ratio_val = st.number_input(f"Ratio {sym}", value=1.0, step=0.1, key=f"r_{sym}")
    data = analyze_rhythm(sym, st.session_state.get('api_key', ''), ratio_val)
    
    with cols[i]:
        with st.container(border=True):
            st.header(f"🛡️ {sym}")
            if data:
                st.metric("ราคา", f"{data['price']:.2f}")
                st.markdown(f"<div style='background:{data['color']};padding:5px;border-radius:5px;text-align:center;color:black;'><b>{data['status']}</b></div>", unsafe_allow_html=True)
                
                # คำนวณกำไรคาดการณ์เทียบเป้าหมาย
                info = STRATEGY_MAP[sym]
                pot_profit = (info['target'] - info['avg']) * info['qty']
                st.write(f"🎯 เป้า: {info['target']:.2f} (กำไร: {pot_profit:,.0f} บ.)")
                
                if st.button(f"🔔 แจ้งแผน {sym}", key=f"btn_{sym}"):
                    st.toast("ส่งสัญญาณเข้า LINE แล้ว!")
            else: st.write("รอข้อมูล...")

st.markdown("---")
st.caption("v9.3 — เพราะกำไรคือความจริง ส่วนค่าแอปคือต้นทุนที่เราต้องชนะ!")
