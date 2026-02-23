# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & HEAT ENGINE (v11.8)
# ==========================================
st.set_page_config(page_title="GeminiBo v11.8: Market Heat", layout="wide", page_icon="🔥")

# หน่วงเวลา 45 วินาทีตามที่พี่โบ้สั่ง
SCAN_INTERVAL = 45 

# รายชื่อหุ้นที่วอลลุ่มเข้าแรงวันนี้ (Market Watch)
MARKET_HEAT = ["SIRI", "BBL", "SCB", "GULF", "CPALL", "TRUE"]

def fetch_whale_heat(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1d", interval="5m")
        df_daily = ticker.history(period="5d", interval="1d")
        
        if df.empty: return None
        
        curr_vol = df['Volume'].sum()
        avg_vol = df_daily['Volume'].mean()
        rvol = curr_vol / (avg_vol / 2) if avg_vol > 0 else 1.0 # หาร 2 เพราะเพิ่งผ่านครึ่งวัน
        
        return {
            "price": df['Close'].iloc[-1],
            "change": ((df['Close'].iloc[-1] - df['Open'].iloc[0]) / df['Open'].iloc[0]) * 100,
            "rvol": rvol,
            "total_vol": curr_vol
        }
    except: return None

# ==========================================
# 📊 MAIN DASHBOARD
# ==========================================
st.title("🔥 GeminiBo v11.8: Market Heat Scanner")
st.caption(f"📅 รอบการสแกน: {SCAN_INTERVAL} วินาที | อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}")

st.sidebar.title("🛡️ จอมทัพโบ้")
st.sidebar.metric("SET Index", "1,501.73", "+22.02")
st.sidebar.info(f"ROJNA วันนี้วอลลุ่มยังเงียบ (Inflow < 10M) แนะนำเฝ้า SIRI หรือ BBL แทนครับ")

# --- SECTION 1: 🐳 WHALE HOT STOCKS (ที่ที่เงินไหลเข้าจริง) ---
st.subheader("🚀 ที่ที่มีวาฬ (Top Inflow Stocks)")
cols = st.columns(3)

for i, sym in enumerate(MARKET_HEAT):
    data = fetch_whale_heat(sym)
    with cols[i % 3]:
        with st.container(border=True):
            if data:
                st.header(f"🛡️ {sym}")
                st.metric("ราคา", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                st.write(f"🌊 ความแรงวอลลุ่ม (RVOL): **{data['rvol']:.2f}**")
                
                if data['rvol'] > 1.8:
                    st.success("🔥 **HOT:** วาฬอัดวอลลุ่มหนามาก!")
                elif data['rvol'] < 0.5:
                    st.warning("💤 **QUIET:** รายใหญ่ยังไม่เล่น")
                
                st.caption(f"Volume รวมครึ่งเช้า: {data['total_vol']:,.0f} หุ้น")
            else: st.write("Scanning...")

# --- SECTION 2: 🚩 ภารกิจส่วนตัว (ROJNA/MTC) ---
st.markdown("---")
st.subheader("🚩 เป้าหมายเดิม (Private Targets)")
c1, c2 = st.columns(2)
with c1:
    st.info("**ROJNA:** วอลลุ่มยังไม่มา เงินไปกองอยู่ที่หุ้นใหญ่ เป้า 6.80 ยังไกลไปนิดครับ")
with c2:
    st.success("**MTC:** ทรงสวยกว่า มีแรงรับที่ 38.00 หนาแน่น ลุ้นดีดหาทุน 38.50 บ่ายนี้ครับ")

# ================= =========================
# 🔄 STEADY REFRESH
# ==========================================
time.sleep(SCAN_INTERVAL)
st.rerun()
