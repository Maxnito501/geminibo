# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v22.0 Iron Rules Only)
# ==========================================
st.set_page_config(page_title="GeminiBo v22.0: Iron Commander", layout="wide", page_icon="🛡️")

# กฎเหล็กข้อ 5.1 & 5.2: รายชื่อขุนพลที่ต้องติดตาม
STOCK_LIST = {
    "OWNED": ["SIRI", "MTC", "HANA"],
    "NEW_STRANGE": ["TRUE", "ADVANC", "ITEL"],
    "RISING_STARS": ["SCB", "PTT", "BBL", "CPALL", "BDMS"]
}

def get_iron_metrics(symbol):
    """ วิเคราะห์ 3 มิติ (กราฟ, ดัชนี, วอลลุ่ม) ตามกฎเหล็กข้อ 1-4 """
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty: return None
        
        curr_p = df['Close'].iloc[-1]
        prev_p = df['Close'].iloc[-2]
        
        # กฎข้อ 2: กราฟ & เทรนด์ (EMA 5)
        ema5 = df['Close'].ewm(span=5, adjust=False).mean().iloc[-1]
        trend = "UP" if curr_p > ema5 else "DOWN"
        
        # กฎข้อ 3: RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # กฎข้อ 4: วอลลุ่มเจ้ามือ (RVOL)
        avg_vol = df['Volume'].iloc[-6:-1].mean()
        rvol = df['Volume'].iloc[-1] / avg_vol if avg_vol > 0 else 1.0
        
        return {"price": curr_p, "trend": trend, "rsi": rsi, "rvol": rvol, "ema5": ema5}
    except: return None

# ==========================================
# 📊 BATTLE STATION UI
# ==========================================
st.title("🛡️ GeminiBo v22.0: Iron Commander")
st.caption(f"📅 อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')} | ตามกฎเหล็ก SetSmart")

# Sidebar (กฎข้อ 1: ตั้งค่าดึงข้อมูล)
with st.sidebar:
    st.header("👤 จอมทัพโบ้")
    st.success("💰 กระสุนพร้อมรบ: ~58,000 บ.")
    st.markdown("---")
    auto_refresh = st.toggle("ระบบสแกน Real-time (45s)", value=True)
    st.warning("🚨 ตรวจพบ Syntax Error เดิม -> แก้ไขแล้ว")

# --- SECTION 1: หุ้นในมือ (OWNED - กฎข้อ 6-7) ---
st.subheader("🔥 กองทัพเก่า (SIRI, MTC, HANA)")
c_old = st.columns(3)
for i, sym in enumerate(STOCK_LIST["OWNED"]):
    data = get_iron_metrics(sym)
    with c_old[i]:
        with st.container(border=True):
            if data:
                # กำหนดทุน (Manual อิงจากไฟล์ประวัติ)
                cost = 1.47 if sym=="SIRI" else 38.50 if sym=="MTC" else 18.90
                is_profit = data['price'] > cost
                
                st.header(f"{sym}")
                st.metric("ราคาตลาด", f"{data['price']:.2f}", f"{data['price']-cost:.2f}")
                
                # ตรรกะตามกฎเหล็กข้อ 6-7
                if is_profit:
                    st.success("💎 กฎข้อ 6: ห้ามขายหมู!")
                    st.caption("แผน: ถือรันปันผล หรือแบ่งขาย 1.63")
                else:
                    st.error("🚨 กฎข้อ 7: ติดดอย!")
                    st.caption("แผน: รอเด้งขายตัด หรือถัวเมื่อหยุดไหล")
                
                st.write(f"📈 เทรนด์: {data['trend']} | 📡 RSI: {data['rsi']:.1f}")
                st.progress(min(data['rsi']/100, 1.0))

# --- SECTION 2: หุ้นใหม่ & ตัวรุ่ง (กฎข้อ 8) ---
st.markdown("---")
tab_new, tab_rising = st.tabs(["🏹 หุ้นใหม่ที่แปลก (Tech)", "🚀 5 ตัวรุ่ง (Top Picks)"])

with tab_new:
    cols = st.columns(3)
    for i, sym in enumerate(STOCK_LIST["NEW_STRANGE"]):
        data = get_iron_metrics(sym)
        with cols[i]:
            if data:
                st.subheader(sym)
                st.metric("ราคา", f"{data['price']:.2f}")
                if data['rvol'] > 1.5: st.warning("🐳 วาฬเข้า! (RVOL สูง)")
                st.info("🏹 แผน: รอช้อนตามน้ำ")

with tab_rising:
    cols = st.columns(5)
    for i, sym in enumerate(STOCK_LIST["RISING_STARS"]):
        data = get_iron_metrics(sym)
        with cols[i]:
            if data:
                st.write(f"**{sym}**")
                st.write(f"{data['price']:.2f}")
                if data['trend'] == "UP": st.success("🚀")

# ================= =========================
# 🔄 REFRESH (กฎข้อ 5)
# ==========================================
if auto_refresh:
    time.sleep(45)
    st.rerun()
