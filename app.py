import streamlit as st
import pandas as pd
import yfinance as yf

# ==========================================
# ⚙️ CONFIG & RSI ENGINE
# ==========================================
st.set_page_config(page_title="GeminiBo Strategist v2.6", page_icon="🏗️", layout="wide")

def calculate_rsi(symbol, period=14):
    try:
        # ดึงราคาย้อนหลังเพื่อคำนวณ RSI
        df = yf.download(f"{symbol}.BK", period="1mo", interval="1d", progress=False)
        if len(df) < period: return 50.0
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    except:
        return 50.0

# ==========================================
# 📊 ANALYZER & STRATEGY ADVISOR
# ==========================================
st.sidebar.title("🏗️ GeminiBo v2.6")
menu = st.sidebar.radio("เลือกเครื่องมือ", ["📊 วิเคราะห์เจ้ามือ & หน้าตัก", "🧮 Recovery Tools"])

if menu == "📊 วิเคราะห์เจ้ามือ & หน้าตัก":
    st.title("🚀 Strategist Dashboard: Auto RSI + Volume Analysis")
    targets = ["SIRI", "WHA", "MTC", "PLANB", "SAWAD", "THCOM"]
    
    cols = st.columns(3)
    for i, symbol in enumerate(targets):
        with cols[i % 3]:
            with st.expander(f"📈 วิเคราะห์ {symbol}", expanded=True):
                # ดึงราคาและ RSI อัตโนมัติ
                live_p = yf.Ticker(f"{symbol}.BK").fast_info['last_price']
                auto_rsi = calculate_rsi(symbol)
                
                st.metric(f"ราคา {symbol}", f"{live_p:.2f}")
                st.write(f"📡 Auto RSI (14): **{auto_rsi:.2f}**")
                
                # กรอกวอลลุ่มเจ้ามือเองเพื่ออ่านใจ
                m_bid = st.number_input(f"Bid Vol ({symbol})", value=1000000, key=f"b_{symbol}")
                m_off = st.number_input(f"Offer Vol ({symbol})", value=3000000, key=f"o_{symbol}")
                
                ratio = m_off / m_bid if m_bid > 0 else 0
                
                # --- 🤖 ระบบวิเคราะห์สถานการณ์อัตโนมัติ ---
                if auto_rsi > 70:
                    st.error("🚨 Overbought: ระวังเจ้ามือทุบขายทำกำไร!")
                elif auto_rsi < 30:
                    st.success("💎 Oversold: จุดช้อนซื้อที่ได้เปรียบ!")
                
                if ratio > 3:
                    st.warning("⚠️ เจ้าขวาง: กำแพง Offer หนา บีบให้รายย่อยคายของ")
                elif ratio < 0.5:
                    st.info("🚀 ทางสะดวก: Offer บาง เจ้ามือเตรียมลากกระชาก")

    # --- ส่วน Dashboard บันทึกทุน/กำไร (คงไว้ตามโจทย์) ---
    st.markdown("---")
    st.header("💰 2. สรุปหน้าตัก (Portfolio Tracking)")
    # ... (ส่วน Dashboard กรอกราคาซื้อ/ขาย/กำไร เหมือนเวอร์ชันก่อนหน้า) ...
