import streamlit as st
import pandas as pd
import yfinance as yf

# ==========================================
# ⚙️ UI SETUP & CONFIG
# ==========================================
st.set_page_config(page_title="GeminiBo Strategist v2.5", page_icon="🏗️", layout="wide")
st.sidebar.title("🏗️ GeminiBo v2.5")
st.sidebar.info("Engineering Mindset: Strategist Mode")

menu = st.sidebar.radio("เลือกเครื่องมือ", ["📊 วิเคราะห์เจ้ามือ & หน้าตัก", "🧮 Recovery Tools"])

# ฟังก์ชันดึงราคา (ดีเลย์ 15 นาทีจาก yfinance)
def get_live_price(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        return ticker.fast_info['last_price']
    except: return 0.0

# ==========================================
# 📊 MODE 1: ANALYZER & DASHBOARD
# ==========================================
if menu == "📊 วิเคราะห์เจ้ามือ & หน้าตัก":
    st.title("🚀 Strategist Dashboard: สแกนเจ้ามือ & คุมกำไร")
    
    # หุ้นเป้าหมายของพี่โบ้
    targets = ["SIRI", "WHA", "MTC", "PLANB", "SAWAD", "THCOM"]
    
    # --- ส่วนที่ 1: ระบบวิเคราะห์วอลลุ่ม & RSI (กรอกเองเพื่อความเป๊ะ) ---
    st.header("🔍 1. สแกนสถานการณ์เจ้ามือ (Volume & RSI Analysis)")
    cols = st.columns(3)
    
    for i, symbol in enumerate(targets):
        with cols[i % 3]:
            with st.expander(f"📈 วิเคราะห์ {symbol}", expanded=True):
                live_p = get_live_price(symbol)
                st.metric(f"ราคา {symbol} (Auto)", f"{live_p:.2f}")
                
                # กรอกวอลลุ่มและ RSI
                m_bid = st.number_input(f"Bid Vol ({symbol})", value=1000000, step=100000, key=f"b_{symbol}")
                m_off = st.number_input(f"Offer Vol ({symbol})", value=3000000, step=100000, key=f"o_{symbol}")
                rsi_val = st.slider(f"RSI ({symbol})", 0, 100, 50, key=f"rsi_{symbol}")
                
                ratio = m_off / m_bid if m_bid > 0 else 0
                st.write(f"📊 Wall Ratio: **{ratio:.2f}**")

                # --- 🤖 ระบบวิเคราะห์สถานการณ์ (Strategy Advisor) ---
                if ratio > 3 and rsi_val > 65:
                    st.error("🆘 สถานการณ์: 'เจ้าขวาง/ดักแมงเม่า'")
                    st.write("**คำแนะนำ:** ห้ามซื้อเพิ่ม! ตั้งขายดักหน้ากำแพง (เช่น WHA 4.26)")
                elif ratio < 0.8 and rsi_val < 40:
                    st.success("💎 สถานการณ์: 'เจ้าเก็บของ/ช้อน'")
                    st.write("**คำแนะนำ:** จังหวะช้อน! RSI ต่ำ วอลลุ่มฝั่งขายบาง")
                elif ratio < 0.5 and rsi_val > 55:
                    st.warning("🚀 สถานการณ์: 'กำลังลาก/ตามกระแส'")
                    st.write("**คำแนะนำ:** Let Profit Run! (เหมือน SIRI) รอดูไม้สุดท้าย 1.60")
                else:
                    st.info("⚖️ สถานการณ์: 'ดึงเช็ง/เลือกทาง'")
                    st.write("**คำแนะนำ:** นั่งทับมือ รอกระแสวอลลุ่มเข้า")

    st.markdown("---")

    # --- ส่วนที่ 2: Dashboard คุมราคาได้มา & กำไรขาดทุน ---
    st.header("💰 2. สรุปหน้าตัก (Portfolio Tracking)")
    grand_total = 0
    
    for symbol in targets:
        with st.expander(f"📝 บันทึกรายการ {symbol}"):
            c1, c2, c3, c4 = st.columns(4)
            # ฝั่งซื้อ (ต้นทุน)
            b_vol = c1.number_input(f"หุ้นซื้อ ({symbol})", value=0, key=f"bv_{symbol}")
            b_price = c2.number_input(f"ราคาซื้อ ({symbol})", value=0.0, format="%.2f", key=f"bp_{symbol}")
            # ฝั่งขาย
            s_vol = c3.number_input(f"หุ้นขาย ({symbol})", value=0, key=f"sv_{symbol}")
            s_price = c4.number_input(f"ราคาขาย ({symbol})", value=0.0, format="%.2f", key=f"sp_{symbol}")
            
            # ประเภทรายการ
            st.radio("ประเภท:", ["ไม้แรก/ซิ่ง", "ซื้อถัว (DCA)", "แบ่งขาย"], key=f"type_{symbol}", horizontal=True)
            
            # คำนวณ
            profit = (s_price - b_price) * s_vol if s_vol > 0 else 0
            grand_total += profit
            st.subheader(f"กำไรตัวนี้: {profit:,.2f} บาท")

    st.sidebar.markdown("---")
    st.sidebar.header("🏆 กำไร/ขาดทุนรวมวันนี้")
    st.sidebar.metric("Total P/L (THB)", f"{grand_total:,.2f}")
    if grand_total > 0: st.sidebar.balloons()

# (Recovery Tools คงเดิม)
elif menu == "🧮 Recovery Tools":
    st.title("🧮 Recovery Calculator")
    # ... (ส่วนคำนวณถัวเฉลี่ยเดิม) ...
