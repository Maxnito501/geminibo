import streamlit as st
import pandas as pd
import yfinance as yf

# ==========================================
# ⚙️ CONFIG & STABLE RSI ENGINE
# ==========================================
st.set_page_config(page_title="GeminiBo Strategist v2.7", page_icon="🏗️", layout="wide")

def get_safe_rsi(symbol):
    try:
        data = yf.download(f"{symbol}.BK", period="1mo", interval="1d", progress=False)
        if len(data) < 15: return 50.0  # ถ้าข้อมูลไม่พอให้คืนค่ากลาง
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        val = rsi.iloc[-1]
        return float(val) if not pd.isna(val) else 50.0
    except: return 50.0

# ==========================================
# 📊 ANALYZER & STRATEGY ADVISOR
# ==========================================
st.sidebar.title("🏗️ GeminiBo v2.7")
menu = st.sidebar.radio("เลือกเครื่องมือ", ["📊 วิเคราะห์เจ้ามือ & หน้าตัก", "🧮 Recovery Tools"])

if menu == "📊 วิเคราะห์เจ้ามือ & หน้าตัก":
    st.title("🚀 Strategist Dashboard: Multi-Portfolio Control")
    
    # แยกกลุ่มหุ้นชัดเจน
    main_stocks = ["SIRI", "WHA", "MTC"]
    trending_stocks = ["PLANB", "SAWAD", "THCOM"]
    all_stocks = main_stocks + trending_stocks
    
    # --- ส่วนที่ 1: วิเคราะห์สถานการณ์ (ราคาออโต้ วอลลุ่มคุมเอง) ---
    st.header("🔍 1. อ่านใจเจ้ามือ (Auto RSI & Manual Volume)")
    cols = st.columns(3)
    
    for i, symbol in enumerate(all_stocks):
        with cols[i % 3]:
            with st.expander(f"📈 วิเคราะห์ {symbol}", expanded=True):
                price = yf.Ticker(f"{symbol}.BK").fast_info['last_price']
                rsi = get_safe_rsi(symbol)
                
                st.write(f"**ราคาล่าสุด:** {price:.2f} | **RSI (14):** {rsi:.2f}")
                
                m_bid = st.number_input(f"Bid Vol ({symbol})", value=1000000, key=f"b_{symbol}")
                m_off = st.number_input(f"Offer Vol ({symbol})", value=3000000, key=f"o_{symbol}")
                ratio = m_off / m_bid if m_bid > 0 else 0
                
                # --- 🤖 วิเคราะห์สถานการณ์ ---
                if rsi > 65 and ratio > 2:
                    st.error("🆘 สถานการณ์: 'เจ้าขวาง/ดักแมงเม่า'")
                elif rsi < 40 and ratio < 0.8:
                    st.success("💎 สถานการณ์: 'เจ้าเก็บของ/ช้อน'")
                elif ratio < 0.5:
                    st.warning("🚀 สถานการณ์: 'ทางสะดวก/เตรียมลาก'")
                else:
                    st.info("⚖️ สถานการณ์: 'ดึงเช็ง/รอเลือกทาง'")

    st.markdown("---")

    # --- ส่วนที่ 2: Dashboard คุมราคาได้มา & กำไรขาดทุน ---
    st.header("💰 2. สรุปหน้าตักรวม (Profit & Loss Dashboard)")
    grand_total = 0.0
    
    for symbol in all_stocks:
        with st.expander(f"📝 รายการ {symbol}"):
            c1, c2, c3, c4 = st.columns(4)
            # ข้อมูลต้นทุน
            vol_in = c1.number_input(f"จำนวนหุ้นที่ได้มา ({symbol})", value=0, key=f"vi_{symbol}")
            price_in = c2.number_input(f"ราคาต้นทุน ({symbol})", value=0.0, format="%.2f", key=f"pi_{symbol}")
            # ข้อมูลขาย
            vol_out = c3.number_input(f"จำนวนหุ้นที่ขาย ({symbol})", value=0, key=f"vo_{symbol}")
            price_out = c4.number_input(f"ราคาที่ขายได้ ({symbol})", value=0.0, format="%.2f", key=f"po_{symbol}")
            
            # คำนวณกำไร/ขาดทุน
            p_l = (price_out - price_in) * vol_out if vol_out > 0 else 0.0
            grand_total += p_l
            
            st.radio("ประเภท:", ["ไม้แรก/ซิ่ง", "ซื้อถัว (DCA)", "แบ่งขาย"], key=f"t_{symbol}", horizontal=True)
            st.subheader(f"กำไร {symbol}: {p_l:,.2f} บาท")

    st.sidebar.markdown("---")
    st.sidebar.header("🏆 สรุปผลงานวันนี้")
    st.sidebar.metric("กำไร/ขาดทุนรวม (บาท)", f"{grand_total:,.2f}")
    if grand_total > 0: st.sidebar.balloons()
