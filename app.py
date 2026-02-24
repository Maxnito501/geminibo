# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & HYBRID ENGINE (v26.0 ตามกฎเหล็ก)
# ==========================================
st.set_page_config(page_title="GeminiBo v26.0: Iron Guard", layout="wide", page_icon="🛡️")

# รายชื่อขุนพลทั้งหมด
OWNED_STOCKS = ["SIRI", "MTC", "HANA"]
SPY_STOCKS = ["TRUE", "ADVANC", "ITEL", "SCB", "PTT", "BBL", "CPALL", "BDMS"]

def get_detailed_intel(symbol):
    """ วิเคราะห์ 3 มิติ (ราคา, เทรนด์, อินดิเคเตอร์) ตามกฎข้อ 1-4 """
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty: return None
        
        curr_p = df['Close'].iloc[-1]
        ema5 = df['Close'].ewm(span=5, adjust=False).mean().iloc[-1]
        low_3d = df['Low'].iloc[-3:].min()
        
        # RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # วอลลุ่มเฉลี่ย (Rule 4)
        rvol = df['Volume'].iloc[-1] / df['Volume'].iloc[-6:-1].mean()
        
        return {
            "price": curr_p, "ema5": ema5, "rsi": rsi, 
            "rvol": rvol, "entry_zone": f"{min(low_3d, ema5):.2f} - {max(low_3d, ema5):.2f}"
        }
    except: return None

# ==========================================
# 📊 SIDEBAR: PORTFOLIO STATUS (Rule 5)
# ==========================================
with st.sidebar:
    st.header("👤 จอมทัพโบ้")
    st.success("💰 เสบียงพร้อมรบ: ~58,000 บ.")
    st.markdown("---")
    st.subheader("📝 จัดการหุ้นในมือ (Old Guard)")
    # รับค่าจำนวนหุ้นและทุนตามกฎข้อ 5
    my_shares = {}
    my_costs = {}
    for sym in OWNED_STOCKS:
        col1, col2 = st.columns(2)
        with col1:
            q = st.number_input(f"จำนวน {sym}", value=4700 if sym=="SIRI" else 400 if sym=="MTC" else 300, key=f"q_{sym}")
            my_shares[sym] = q
        with col2:
            c = st.number_input(f"ทุน {sym}", value=1.47 if sym=="SIRI" else 38.50 if sym=="MTC" else 18.90, key=f"c_{sym}")
            my_costs[sym] = c
    
    st.markdown("---")
    auto_refresh = st.toggle("ระบบตัดสินใจ Real-time (45s)", value=True)

# ================= =========================
# 🏹 MAIN DASHBOARD: THE TWO FORTRESSES
# ==========================================
st.title("🛡️ GeminiBo v26.0: The Two Fortresses")
st.caption(f"📅 แยกโซนหุ้นเก่าและหุ้นใหม่ตามกฎเหล็ก | อัปเดต: {datetime.now().strftime('%H:%M:%S')}")

tab1, tab2 = st.tabs(["🔥 กองทัพเก่า (Owned Management)", "🏹 หน่วยสอดแนม (Entry Hunter)"])

# --- TAB 1: หุ้นในมือ (บริหารตามกฎข้อ 6-7) ---
with tab1:
    st.subheader("📍 โซนบริหารจัดการหุ้นเดิม (Manage & Recovery)")
    cols = st.columns(3)
    for i, sym in enumerate(OWNED_STOCKS):
        data = get_detailed_intel(sym)
        cost = my_costs[sym]
        with cols[i]:
            with st.container(border=True):
                if data:
                    st.header(sym)
                    pnl = ((data['price'] - cost) / cost) * 100
                    st.metric("ราคาตลาด", f"{data['price']:.2f}", f"{pnl:.2f}%")
                    
                    # วิเคราะห์วอลลุ่มหน้างาน (SetSmart Rule 1)
                    ratio = st.slider(f"Whale Ratio - {sym}", 0.0, 5.0, 1.0, step=0.1, key=f"r_owned_{sym}")
                    
                    # --- DECISION BRAIN (RULE 6-7) ---
                    st.markdown("---")
                    if data['price'] >= cost: # กฎข้อ 6
                        if ratio < 0.5:
                            st.success("💎 HOLD / ห้ามขายหมู!")
                            st.info("เหตุผล: วาฬยังค้ำ และได้เปรียบต้นทุน")
                        else:
                            st.warning("💰 SELL 1/2 / แบ่งกำไร")
                            st.write("เหตุผล: เริ่มมีกำแพงขวางหน้าต้าน")
                    else: # กฎข้อ 7
                        if data['rsi'] < 35:
                            st.info("⚖️ WAIT / รอเด้งก้นเหว")
                        elif ratio > 3.0:
                            st.error("🚨 EXIT AT REBOUND / หนี!")
                            st.write("เหตุผล: เจ้ามือรินของใส่เขื่อน")
                    
                    st.caption(f"RSI: {data['rsi']:.1f} | RVOL: {data['rvol']:.2f}")

# --- TAB 2: หุ้นใหม่ (สอดแนมตามกฎข้อ 5.2) ---
with tab2:
    st.subheader("📍 โซนสอดแนมหาช่องเข้า (Spying & Hunting)")
    spy_cols = st.columns(4)
    for i, sym in enumerate(SPY_STOCKS):
        data = get_detailed_intel(sym)
        with spy_cols[i % 4]:
            with st.container(border=True):
                if data:
                    st.subheader(sym)
                    st.metric("ราคา", f"{data['price']:.2f}")
                    st.write(f"🎯 **ช่องเข้า (Entry):**")
                    st.code(data['entry_zone'])
                    
                    # สัญญาณตามกฎ 5.2
                    ratio_spy = st.slider(f"Ratio - {sym}", 0.0, 5.0, 1.0, step=0.1, key=f"r_spy_{sym}")
                    if ratio_spy < 0.4 and data['price'] > data['ema5']:
                        st.success("🏹 BUY / ช้อนตามน้ำ")
                    else:
                        st.write("⌛ รอกระแสเงินไหลเข้า")

# ================= =========================
# 🔄 REFRESH
# ==========================================
if auto_refresh:
    time.sleep(45)
    st.rerun()
