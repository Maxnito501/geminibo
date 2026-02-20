# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v6.1 Whale Flow)
# ==========================================
st.set_page_config(page_title="GeminiBo v6.1: Whale Flow", layout="wide", page_icon="🐳")

def get_whale_flow(symbol):
    """ ตรวจจับพฤติกรรมวาฬแอบปล่อยของ """
    try:
        symbol = symbol.strip().upper()
        ticker = yf.Ticker(f"{symbol}.BK")
        # ดึงข้อมูล Intraday ล่าสุด
        df = ticker.history(period="1d", interval="1m")
        df_daily = ticker.history(period="5d", interval="1d")
        
        if df.empty: return None
        
        curr_price = df['Close'].iloc[-1]
        open_price = df['Open'].iloc[0]
        curr_vol = df['Volume'].sum()
        avg_vol = df_daily['Volume'].mean()
        
        # คำนวณความเร็ว (Ticker Speed Simulation)
        rvol = (curr_vol * 10) / avg_vol if avg_vol > 0 else 1.0
        
        # คำนวณความผันผวนล่าสุด (5 นาที)
        recent_volatility = df['Close'].iloc[-5:].std()
        
        # เช็ค RSI ล่าสุด
        delta = df_daily['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        return {
            "price": curr_price,
            "rsi": rsi,
            "rvol": rvol,
            "is_churning": rvol > 2.5 and abs(curr_price - df['Close'].iloc[-5]) < 0.01, # ราคาไม่ไปแต่วอลลุ่มมา
            "is_dumping": curr_price < df['Close'].iloc[-5] and rvol > 1.5, # ราคาเริ่มย้อยลงพร้อมโวลลุ่ม
            "high": df['High'].max(),
            "low": df['Low'].min()
        }
    except: return None

# ==========================================
# 📊 BATTLE STATION
# ==========================================
st.title("🐳 Whale Flow Detector (SIRI Special Scan)")
st.caption(f"อัปเดตข้อมูลล่าสุด: {datetime.now().strftime('%H:%M:%S')}")

# เน้นสแกน SIRI เป็นพิเศษตามที่พี่โบ้กังวล
cols = st.columns([2, 1, 1])

with cols[0]:
    data = get_whale_flow("SIRI")
    with st.container(border=True):
        if data:
            st.header("🛡️ วิเคราะห์ SIRI หน้างาน")
            c1, c2, c3 = st.columns(3)
            c1.metric("ราคาปัจจุบัน", f"{data['price']:.2f}")
            c2.metric("RSI (เตือนภัย)", f"{data['rsi']:.1f}")
            c3.metric("RVOL (ความแรง)", f"{data['rvol']:.2f}")

            st.markdown("---")
            st.subheader("📡 ผลการตรวจจับวาฬ")
            
            if data['rsi'] > 90:
                st.error("🚨 **EXTREME OVERBOUGHT!** (RSI ทะลุ 90)")
                st.write("ราคาเข้าเขต 'ต้องมีของขาย' มากกว่า 'ต้องมีของซื้อ' ระวังแรงทุบฉับพลัน")

            if data['is_churning']:
                st.warning("⚠️ **DETECTED: CHURNING!** (อาการรินของ)")
                st.write("วอลลุ่มมหาศาลแต่ราคาไม่ขยับข้ามต้าน แสดงว่าวาฬแอบส่งของให้รายย่อยที่หน้าต้าน 1.62-1.63")
            
            elif data['is_dumping']:
                st.error("📉 **DETECTED: DUMPING!** (วาฬทิ้งของ)")
                st.write("ราคาเริ่มหลุดแนวรับสั้นๆ พร้อมวอลลุ่มหนา ให้รีบทำตามแผน 'หนีมีเชิง' ทันที")
            
            elif data['rvol'] > 2.0:
                st.success("🚀 **BREAKOUT FORCE!** (วาฬรวบของ)")
                st.write("วอลลุ่มหนาและราคายังดันต่อเนื่อง มีลุ้นทะลุ 1.63 ไปหา 1.66")
            else:
                st.info("📊 สถานะปกติ: วาฬยังดูเชิง")

with cols[1]:
    # ข้อมูล MTC สั้นๆ
    m_data = get_whale_flow("MTC")
    with st.container(border=True):
        st.subheader("🛡️ MTC")
        if m_data:
            st.metric("ราคา", f"{m_data['price']:.2f}")
            st.write(f"RVOL: {m_data['rvol']:.2f}")
            if m_data['price'] < 39.00: st.error("ระวังหลุดแนวรับ")
        else: st.write("รอข้อมูล...")

with cols[2]:
    st.info("💡 **คำแนะนำจอมทัพ:**")
    st.write("1. ถ้า SIRI Match 1.63 แล้วราคา 'หยุดชะงัก' แต่วอลลุ่มยังวิ่งเร็ว... **จงพอใจที่ 1.63**")
    st.write("2. ดูช่อง Bid ใน Streaming ถ้าเริ่มโดนรวบหาย (Bid หาย) ให้ระวังการทิ้งของ")
    if st.button("🔄 สแกนซ้ำวินาทีนี้"):
        st.rerun()

st.markdown("---")
st.caption("v6.1 Whale Flow Detector — พัฒนามาเพื่อดักทาง 'การรินขาย' ของรายใหญ่")
