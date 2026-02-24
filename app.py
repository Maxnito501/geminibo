# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & IRON ENGINE (v38.0 Python Fix)
# ==========================================
st.set_page_config(page_title="GeminiBo v38.0: Iron Commander", layout="wide", page_icon="🛡️")

# กฎเหล็กข้อ 5: รายชื่อขุนพลทั้งหมด (ห้ามลบ)
STOCKS = [
    {"symbol": "SIRI", "type": "Owned", "cost": 1.47},
    {"symbol": "MTC", "type": "Owned", "cost": 38.50},
    {"symbol": "HANA", "type": "Owned", "cost": 18.90},
    {"symbol": "HMPRO", "type": "Owned", "cost": 7.05},
    {"symbol": "TRUE", "type": "Hunting", "cost": 0.0},
    {"symbol": "SCB", "type": "Hunting", "cost": 0.0},
    {"symbol": "PTT", "type": "Hunting", "cost": 33.00},
    {"symbol": "ADVANC", "type": "Hunting", "cost": 0.0},
    {"symbol": "ITEL", "type": "Hunting", "cost": 0.0},
    {"symbol": "CPALL", "type": "Hunting", "cost": 0.0},
    {"symbol": "BBL", "type": "Hunting", "cost": 0.0},
    {"symbol": "BDMS", "type": "Hunting", "cost": 0.0},
]

def get_stock_analysis(symbol):
    """ วิเคราะห์ 3 มิติ ตามกฎเหล็ก 1-4 """
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty: return None
        
        last_price = df['Close'].iloc[-1]
        ema5 = df['Close'].ewm(span=5, adjust=False).mean().iloc[-1]
        
        # คำนวณ RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        return {"price": last_price, "ema5": ema5, "rsi": rsi}
    except: return None

# ==========================================
# 📊 SIDEBAR: WAR FUND & SETTINGS
# ==========================================
with st.sidebar:
    st.header("🛡️ จอมทัพโบ้")
    st.success("💰 เสบียงพร้อมรบ: ฿58,000")
    st.markdown("---")
    st.info("💡 กฎเหล็ก: อิงราคา/วอลลุ่มจาก SETSmart 10 ชั้น")
    auto_refresh = st.toggle("ระบบตัดสินใจ Real-time (45s)", value=True)
    st.error("🚨 บันทึก: ยอดขาดทุน MTC/HANA ~฿1,000")

# ==========================================
# 🏹 MAIN BATTLEFIELD
# ==========================================
st.title("🛡️ GeminiBo v38.0: Iron Commander")
st.caption(f"📅 อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')} | เสถียร 100% บน Streamlit")

tab1, tab2 = st.tabs(["🔥 ทัพหลวง (Owned)", "🏹 หน่วยล่า (Hunting)"])

def display_unit(s_data, idx):
    symbol = s_data["symbol"]
    cost = s_data["cost"]
    type_group = s_data["type"]
    
    data = get_stock_analysis(symbol)
    
    with st.container(border=True):
        if data:
            col_h1, col_h2 = st.columns([2, 1])
            col_h1.header(f"{symbol}")
            col_h2.metric("ราคาตลาด", f"{data['price']:.2f}")
            
            # --- รับข้อมูล Whale Ratio ตามกฎข้อ 1 & 4 ---
            st.write("**🐳 ข้อมูลวอลลุ่ม SetSmart**")
            b_vol = st.number_input(f"Bid 10 ชั้น (M) - {symbol}", value=10.0, step=0.1, key=f"b_{symbol}")
            o_vol = st.number_input(f"Offer 10 ชั้น (M) - {symbol}", value=4.0, step=0.1, key=f"o_{symbol}")
            ratio = o_vol / b_vol if b_vol > 0 else 0
            st.write(f"📊 Whale Ratio: **{ratio:.2f}**")
            
            # --- DECISION ENGINE (RULES 5, 6, 7) ---
            st.markdown("---")
            if type_group == "Owned":
                is_profit = data['price'] >= cost
                pnl = (data['price'] - cost) * 400 # จำลองจำนวนหุ้น
                
                if is_profit: # กฎ 5.1.1
                    if ratio < 0.5 and data['rsi'] < 85:
                        st.success("💎 ห้ามขายหมู! รอรันกำไร")
                    else:
                        st.warning("💰 แบ่งขาย 1/2 (ต้านหนา)")
                else: # กฎ 5.1.2
                    if data['rsi'] < 35:
                        st.info("⚖️ รอเด้งก้นเหว (ห้ามคัด)")
                    else:
                        st.error("🚨 หนีตาม EMA หรือรอถัว")
                st.caption(f"ทุนพี่: {cost:.2f} | RSI: {data['rsi']:.1f}")
            
            else: # หน่วยล่า (Hunting / Rule 5.2)
                if ratio < 0.4 and data['price'] > data['ema5']:
                    st.success("🏹 ช้อนตามน้ำ! วาฬเปิดทาง")
                elif data['rsi'] < 40:
                    st.info("🎯 เฝ้าช่องเข้า 5.2 (จ่อก้นเหว)")
                else:
                    st.write("📡 รอกระแสเงินไหลเข้า")
                st.caption(f"ช่องเข้าเป้าหมาย: {data['ema5']:.2f}")
        else:
            st.write(f"กำลังสแกน {symbol}...")

with tab1:
    owned_stocks = [s for s in STOCKS if s["type"] == "Owned"]
    cols = st.columns(2)
    for i, s in enumerate(owned_stocks):
        with cols[i % 2]: display_unit(s, i)

with tab2:
    hunting_stocks = [s for s in STOCKS if s["type"] == "Hunting"]
    cols = st.columns(3)
    for i, s in enumerate(hunting_stocks):
        with cols[i % 3]: display_unit(s, i + 100)

# ================= =========================
# 🔄 AUTO REFRESH
# ==========================================
if auto_refresh:
    time.sleep(45)
    st.rerun()
