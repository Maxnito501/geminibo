import streamlit as st
import pandas as pd
import yfinance as yf

# ==========================================
# ⚙️ CONFIG & RSI ENGINE
# ==========================================
st.set_page_config(page_title="GeminiBo Strategist v2.8", page_icon="🏗️", layout="wide")

def get_live_data(symbol):
    try:
        # ดึงข้อมูลย้อนหลัง 1 เดือนเพื่อคำนวณ RSI 14 วัน
        df = yf.download(f"{symbol}.BK", period="1mo", interval="1d", progress=False)
        if len(df) < 15: return 0.0, 50.0
        
        # คำนวณ RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return df['Close'].iloc[-1], rsi.iloc[-1]
    except:
        return 0.0, 50.0

# ==========================================
# 📊 MAIN ANALYZER
# ==========================================
st.sidebar.title("🏗️ GeminiBo v2.8")
menu = st.sidebar.radio("เลือกเครื่องมือ", ["📊 วิเคราะห์เจ้ามือ & หน้าตัก", "🧮 Recovery Tools"])

if menu == "📊 วิเคราะห์เจ้ามือ & หน้าตัก":
    st.title("🚀 Strategist Dashboard: Auto RSI & Situation Analysis")
    
    # หุ้นเดิม + หุ้นใหม่ที่พี่ให้สแกน
    targets = ["SIRI", "WHA", "MTC", "PLANB", "SAWAD", "THCOM"]
    
    # --- ส่วนที่ 1: วิเคราะห์ RSI และ วอลลุ่ม ---
    st.header("🔍 1. วิเคราะห์สถานการณ์ (RSI ออโต้ / วอลลุ่มกรอกเอง)")
    cols = st.columns(3)
    
    for i, symbol in enumerate(targets):
        with cols[i % 3]:
            with st.expander(f"📈 {symbol} Strategy", expanded=True):
                price, rsi_val = get_live_data(symbol)
                
                st.metric(f"ราคา {symbol}", f"{price:.2f}")
                st.write(f"📡 **RSI (14): {rsi_val:.2f}**")
                
                m_bid = st.number_input(f"Bid Vol ({symbol})", value=1000000, key=f"b_{symbol}")
                m_off = st.number_input(f"Offer Vol ({symbol})", value=3000000, key=f"o_{symbol}")
                
                ratio = m_off / m_bid if m_bid > 0 else 0
                st.write(f"📊 Wall Ratio: **{ratio:.2f}**")

                # --- 🤖 ระบบวิเคราะห์สถานการณ์ (Decision Logic) ---
                if rsi_val > 70:
                    st.error("🚨 Overbought: ตึงมาก! เจ้ามืออาจทุบขาย")
                elif rsi_val < 30:
                    st.success("💎 Oversold: ถูกมาก! จังหวะช้อนเก็บของ")
                
                if ratio > 3:
                    st.warning("⚠️ เจ้าขวาง: กำแพงหนา บีบให้รายย่อยคายของ")
                elif ratio < 0.5:
                    st.info("🚀 ทางสะดวก: Offer บาง เจ้ามือเตรียมลาก")

    st.markdown("---")

    # --- ส่วนที่ 2: Dashboard คุมราคาได้มา & กำไรขาดทุน ---
    st.header("💰 2. สรุปหน้าตัก (Portfolio Dashboard)")
    grand_total = 0.0
    
    for symbol in targets:
        with st.expander(f"📝 บันทึกรายการ {symbol}"):
            c1, c2, c3, c4 = st.columns(4)
            v_in = c1.number_input(f"หุ้นที่ได้มา ({symbol})", value=0, key=f"vi_{symbol}")
            p_in = c2.number_input(f"ราคาต้นทุน ({symbol})", value=0.0, format="%.2f", key=f"pi_{symbol}")
            v_out = c3.number_input(f"หุ้นที่ขาย ({symbol})", value=0, key=f"vo_{symbol}")
            p_out = c4.number_input(f"ราคาที่ขาย ({symbol})", value=0.0, format="%.2f", key=f"po_{symbol}")
            
            p_l = (p_out - p_in) * v_out if v_out > 0 else 0.0
            grand_total += p_l
            st.subheader(f"กำไร {symbol}: {p_l:,.2f} บาท")

    st.sidebar.markdown("---")
    st.sidebar.header("🏆 กำไร/ขาดทุนรวมวันนี้")
    st.sidebar.metric("Total P/L (THB)", f"{grand_total:,.2f}")
