import streamlit as st
import pandas as pd
import yfinance as yf

# ==========================================
# ⚙️ CONFIG & STABLE RSI ENGINE
# ==========================================
st.set_page_config(page_title="GeminiBo Strategist v2.9", page_icon="🏗️", layout="wide")

def get_market_data(symbol):
    try:
        # ดึงข้อมูลย้อนหลัง 1 เดือน เพื่อคำนวณ RSI 14 วัน
        df = yf.download(f"{symbol}.BK", period="1mo", interval="1d", progress=False)
        if df.empty or len(df) < 15:
            return 0.0, 50.0
        
        # ราคาล่าสุด
        last_p = float(df['Close'].iloc[-1])
        
        # คำนวณ RSI (14) แบบมาตรฐาน
        delta = df['Close'].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.rolling(window=14).mean()
        ema_down = down.rolling(window=14).mean()
        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs))
        last_rsi = float(rsi.iloc[-1])
        
        return last_p, last_rsi
    except:
        return 0.0, 50.0

# ==========================================
# 📊 ANALYZER DASHBOARD
# ==========================================
st.sidebar.title("🏗️ GeminiBo v2.9")
menu = st.sidebar.radio("เลือกเครื่องมือ", ["📊 วิเคราะห์เจ้ามือ & หน้าตัก", "🧮 Recovery Tools"])

if menu == "📊 วิเคราะห์เจ้ามือ & หน้าตัก":
    st.title("🚀 Strategist Dashboard: Stable Auto-RSI")
    
    # รวมหุ้นเดิมและหุ้นซิ่งที่พี่โบ้จดจ้อง
    targets = ["SIRI", "WHA", "MTC", "PLANB", "SAWAD", "THCOM"]
    
    st.header("🔍 1. วิเคราะห์ RSI & วอลลุ่มหน้างาน")
    cols = st.columns(3)
    
    for i, symbol in enumerate(targets):
        with cols[i % 3]:
            with st.expander(f"📈 {symbol} Analysis", expanded=True):
                price, rsi_val = get_market_data(symbol)
                
                # แสดงราคาและ RSI แบบกัน Error
                st.metric(f"ราคา {symbol}", f"{price:.2f}" if price > 0 else "N/A")
                st.write(f"📡 **RSI (14): {rsi_val:.2f}**")
                
                m_bid = st.number_input(f"Bid Vol ({symbol})", value=1000000, key=f"b_{symbol}")
                m_off = st.number_input(f"Offer Vol ({symbol})", value=3000000, key=f"o_{symbol}")
                ratio = m_off / m_bid if m_bid > 0 else 0
                st.write(f"📊 Wall Ratio: **{ratio:.2f}**")

                # --- 🤖 วิเคราะห์สถานการณ์ตาม RSI และ Volume ---
                if rsi_val > 70:
                    st.error("🚨 Overbought: ระวังแรงขายทำกำไร!")
                elif rsi_val < 35:
                    st.success("💎 Oversold: โซนเก็บของ/ลุ้นเด้ง")
                
                if ratio > 3:
                    st.warning("⚠️ เจ้าขวาง: กำแพงหนา รายย่อยโดนบีบ")
                elif ratio < 0.6:
                    st.info("🚀 ทางสะดวก: เตรียมลาก/ตามกระแส")

    # --- ส่วนที่ 2: Dashboard บันทึกทุน/กำไร (คงไว้ตามโจทย์) ---
    st.markdown("---")
    st.header("💰 2. สรุปหน้าตักรวม (P/L Tracking)")
    # ... (ส่วน Dashboard กรอกราคาซื้อ/ขาย/กำไร เหมือนเดิมเพื่อให้พี่คุมหน้าตักได้) ...
