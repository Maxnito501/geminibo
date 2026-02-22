# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import numpy as np

# ==========================================
# ⚙️ CONFIG & PREDICTIVE ENGINE (v9.0 Whale Rider)
# ==========================================
st.set_page_config(page_title="GeminiBo v9.0: Whale Rider", layout="wide", page_icon="🐳")

def analyze_whale_behavior(symbol, api_key, bid_ratio):
    """ 
    ระบบวิเคราะห์พฤติกรรมวาฬขั้นสูง 
    วิเคราะห์การ 'เทขาย', 'เขย่า', และ 'ตามน้ำ'
    """
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1d", interval="1m")
        df_daily = ticker.history(period="5d", interval="1d")
        
        if df.empty: return None
        
        curr_price = df['Close'].iloc[-1]
        vol_1m = df['Volume'].iloc[-5:].sum() # โวลลุ่ม 5 นาทีล่าสุด
        avg_vol_5d = df_daily['Volume'].mean() / 240 # เฉลี่ยรายนาที
        rvol_live = vol_1m / (avg_vol_5d * 5)
        
        # --- WHALE LOGIC MODULE ---
        behavior = "⚖️ ช่วงดูเชิง"
        action = "เฝ้าระวัง"
        confidence = "Normal"

        # 1. เทขาย (Dumping)
        if rvol_live > 2.0 and bid_ratio > 3.0:
            behavior = "🚨 วาฬกำลังรินขาย (Dumping)"
            action = "ถอนตัว/ลดพอร์ต"
            confidence = "High"
        
        # 2. เขย่าไล่เม่า (Shake-off)
        elif curr_price < df['Close'].iloc[-10] and bid_ratio < 0.6 and rvol_live < 1.5:
            behavior = "🌪️ การเขย่าเล่าเม่า (Shake-off)"
            action = "นิ่งสงบ/รอช้อน"
            confidence = "Medium"
            
        # 3. ตามน้ำ/ขี่วาฬ (Whale Riding)
        elif curr_price > df['Open'].iloc[0] and bid_ratio < 0.4 and rvol_live > 1.8:
            behavior = "🚀 วาฬเริ่มลาก (Whale Riding)"
            action = "ตามน้ำ/ถือรัน"
            confidence = "High"

        return {
            "price": curr_price,
            "rvol": rvol_live,
            "behavior": behavior,
            "action": action,
            "confidence": confidence,
            "rsi": 50.0 # Placeholder
        }
    except: return None

# ==========================================
# 📊 BATTLE STATION UI
# ==========================================
st.sidebar.title("🐳 Whale Rider HQ")
st.sidebar.info("ยุทธศาสตร์: 'ตามวาฬ ได้เนื้อ... ตามเม่า ได้ดอย'")

# เป้าหมายสะสม
if 'net_profit' not in st.session_state: st.session_state.net_profit = 80.0
st.sidebar.metric("🏆 กำไรสะสมสุทธิ", f"{st.session_state.net_profit:,.2f} บ.")

st.title("🏹 GeminiBo v9.0: Whale Rider Edition")
st.caption(f"Real-time Analysis for SIRI, HANA, MTC | {datetime.now().strftime('%H:%M:%S')}")

# เลือกหุ้นขุนพล
stocks = ["SIRI", "HANA", "MTC"]
cols = st.columns(3)

for i, sym in enumerate(stocks):
    # จำลองการรับค่า Ratio จาก SetSmart ในอนาคต
    ratio_val = st.number_input(f"Ratio {sym} (จาก SetSmart)", value=1.0, step=0.1, key=f"in_{sym}")
    data = analyze_whale_behavior(sym, "", ratio_val)
    
    with cols[i]:
        with st.container(border=True):
            st.header(f"🛡️ {sym}")
            if data:
                st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}")
                st.write(f"📊 RVOL (5m): **{data['rvol']:.2f}**")
                
                # แสดงผลวิเคราะห์พฤติกรรม
                st.markdown("---")
                st.subheader(data['behavior'])
                
                if "Riding" in data['behavior']:
                    st.success(f"🔥 คำสั่ง: {data['action']}")
                elif "Dumping" in data['behavior']:
                    st.error(f"🔥 คำสั่ง: {data['action']}")
                elif "Shake-off" in data['behavior']:
                    st.warning(f"🔥 คำสั่ง: {data['action']}")
                else:
                    st.info(f"🔥 คำสั่ง: {data['action']}")
                
                st.caption(f"Confidence: {data['confidence']}")
            else:
                st.write("รอสัญญาณ...")

st.markdown("---")
st.caption("v9.0 Whale Rider — พัฒนามาเพื่อเปลี่ยนพี่โบ้ให้เป็น 'เหาฉลาม' ที่เกาะติดกำไรไปกับเจ้ามือครับ")
