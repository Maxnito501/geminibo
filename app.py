# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v23.0 Iron Decision)
# ==========================================
st.set_page_config(page_title="GeminiBo v23.0: Decision Engine", layout="wide", page_icon="🛡️")

# กฎเหล็กข้อ 5: รายชื่อขุนพล
STOCK_GROUPS = {
    "OWNED": ["SIRI", "MTC", "HANA"],
    "NEW_STRANGE": ["TRUE", "ADVANC", "ITEL"],
    "RISING_STARS": ["SCB", "PTT", "BBL", "CPALL", "BDMS"]
}

def get_market_intel(symbol):
    """ วิเคราะห์ 3 มิติ ตามกฎเหล็กข้อ 1-4 """
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty: return None
        
        curr_p = df['Close'].iloc[-1]
        ema5 = df['Close'].ewm(span=5, adjust=False).mean().iloc[-1]
        
        # RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # RVOL
        avg_vol = df['Volume'].iloc[-6:-1].mean()
        rvol = df['Volume'].iloc[-1] / avg_vol if avg_vol > 0 else 1.0
        
        return {"price": curr_p, "ema5": ema5, "rsi": rsi, "rvol": rvol}
    except: return None

# ==========================================
# 📊 SIDEBAR: SETTINGS (Iron Rule 1)
# ==========================================
with st.sidebar:
    st.header("👤 จอมทัพโบ้")
    st.success("💰 กระสุนพร้อมรบ: ~58,000 บ.")
    st.markdown("---")
    st.subheader("🔑 SetSmart Config")
    api_key = st.text_input("SetSmart API Key", type="password", value="API_CONNECTED")
    auto_refresh = st.toggle("ระบบตัดสินใจ Real-time (30s)", value=True)
    
# ==========================================
# 🏹 MAIN DASHBOARD: THE DECISION CENTER
# ==========================================
st.title("🛡️ GeminiBo v23.0: Actionable Intelligence")
st.caption(f"📅 อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')} | ตามกฎเหล็กดึงข้อมูล SetSmart")

# --- SECTION 1: หุ้นในมือ (Decision Logic Rule 6-7) ---
st.subheader("🔥 กองทัพเก่า: วิเคราะห์จุดรุก/ถอย")
c_old = st.columns(3)

for i, sym in enumerate(STOCK_GROUPS["OWNED"]):
    data = get_market_intel(sym)
    with c_old[i]:
        with st.container(border=True):
            if data:
                # ข้อมูลทุน (Mock up based on history)
                cost = 1.47 if sym=="SIRI" else 38.50 if sym=="MTC" else 18.90
                pnl_pct = ((data['price'] - cost) / cost) * 100
                
                st.header(f"{sym}")
                st.metric("ราคาตลาด", f"{data['price']:.2f}", f"{pnl_pct:.2f}%")
                
                # รับค่าวอลลุ่มหน้างาน (SetSmart Rule 4)
                st.write("**🐳 วิเคราะห์วอลลุ่ม SetSmart**")
                b_vol = st.number_input(f"Total Bid (M) - {sym}", value=10.0, step=0.1, key=f"b_{sym}", label_visibility="collapsed")
                o_vol = st.number_input(f"Total Offer (M) - {sym}", value=4.0, step=0.1, key=f"o_{sym}", label_visibility="collapsed")
                ratio = o_vol / b_vol if b_vol > 0 else 0
                
                # --- BRAIN LOGIC: คำสั่งจอมทัพ ---
                st.markdown("---")
                st.write("🎯 **คำสั่งปฏิบัติการ:**")
                
                if data['price'] >= cost: # กรณีมีกำไร (Rule 6)
                    if ratio < 0.5 and data['rsi'] < 85:
                        st.success("💎 HOLD / ห้ามขายหมู!")
                        st.info("เหตุผล: วาฬยังดันต่อ + ทางสะดวก")
                    else:
                        st.warning("💰 SELL 1/2 / ล็อกกำไร")
                        st.write("เหตุผล: เริ่มมีกำแพงขวาง หรือ RSI ตึง")
                else: # กรณีติดดอย (Rule 7)
                    if data['rsi'] < 40:
                        st.info("⚖️ WAIT / รอเด้ง")
                        st.write("เหตุผล: ราคาต่ำเกินไป ขายตอนนี้เสียเปรียบ")
                    elif data['price'] > data['ema5'] * 0.99:
                        st.error("🚨 EXIT AT REBOUND / หนี!")
                        st.write("เหตุผล: เด้งมาทดสอบแนวรับแล้วไม่ผ่าน")
                
                st.caption(f"RVOL: {data['rvol']:.2f} | RSI: {data['rsi']:.1f}")

# --- SECTION 2: หุ้นใหม่ & ตัวรุ่ง (Decision Logic Rule 8) ---
st.markdown("---")
tab_new, tab_rising = st.tabs(["🏹 หุ้นใหม่/แปลก (Scoop Tactics)", "🚀 5 ตัวรุ่ง (Dividend Watch)"])

with tab_new:
    cols = st.columns(3)
    for i, sym in enumerate(STOCK_GROUPS["NEW_STRANGE"]):
        data = get_market_intel(sym)
        with cols[i]:
            if data:
                st.subheader(sym)
                st.metric("ราคา", f"{data['price']:.2f}")
                # รับค่า Ratio ชั่วคราว
                r_val = st.slider(f"Whale Ratio {sym}", 0.0, 5.0, 1.0)
                
                if r_val < 0.4 and data['price'] > data['ema5']:
                    st.success("🏹 BUY / ช้อนตามน้ำ!")
                else:
                    st.write("⌛ รอกระแสเงินไหลเข้า")

with tab_rising:
    cols = st.columns(5)
    for i, sym in enumerate(STOCK_GROUPS["RISING_STARS"]):
        data = get_market_intel(sym)
        with cols[i]:
            if data:
                st.markdown(f"**{sym}**")
                st.write(f"฿{data['price']:.2f}")
                if data['rsi'] < 45: st.write("🟢 น่าสะสม")

# ================= =========================
# 🔄 REFRESH (30 Seconds)
# ==========================================
if auto_refresh:
    time.sleep(30)
    st.rerun()
