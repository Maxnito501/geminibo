import streamlit as st
import pandas as pd
import yfinance as yf

# ==========================================
# ⚙️ UI SETUP
# ==========================================
st.set_page_config(page_title="GeminiBo Hybrid v2.4", page_icon="🏗️", layout="wide")

st.sidebar.title("🏗️ GeminiBo v2.4")
st.sidebar.info("Hybrid Control: Auto Price + Manual Volume")
menu = st.sidebar.radio("เลือกโหมด", ["📊 วิเคราะห์เจ้ามือ & Dashboard", "🧮 เครื่องมือแก้เกม (Recovery)"])

# ฟังก์ชันดึงราคาหุ้นอัตโนมัติ (SET)
def get_live_price(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        return ticker.fast_info['last_price']
    except:
        return 0.0

# ==========================================
# 📊 MODE 1: ANALYSIS & PROFIT DASHBOARD
# ==========================================
if menu == "📊 วิเคราะห์เจ้ามือ & Dashboard":
    st.title("🚀 Real-time Analysis & Portfolio Dashboard")
    
    targets = ["SIRI", "WHA", "MTC"]
    portfolio_data = []

    # --- ส่วนที่ 1: วิเคราะห์ Wall Ratio (ราคาออโต้ วอลลุ่มกรอกเอง) ---
    st.header("🔍 ส่วนที่ 1: อ่านใจเจ้ามือ (Wall Ratio)")
    cols = st.columns(3)
    for i, symbol in enumerate(targets):
        with cols[i]:
            live_p = get_live_price(symbol)
            st.subheader(f"📈 {symbol}")
            st.metric("ราคาปัจจุบัน (Auto)", f"{live_p:.2f}")
            
            m_bid = st.number_input(f"Bid Vol (3 ช่องแรก)", value=1000000, step=100000, key=f"b_{symbol}")
            m_off = st.number_input(f"Offer Vol (3 ช่องแรก)", value=3000000, step=100000, key=f"o_{symbol}")
            
            ratio = m_off / m_bid if m_bid > 0 else 0
            st.write(f"📊 Wall Ratio: **{ratio:.2f}**")
            if ratio > 3: st.warning("⚠️ เจ้ามือวางกำแพงขวาง")
            elif ratio < 0.5: st.success("🚀 ทางสะดวก/เจ้าเก็บของ")

    st.markdown("---")

    # --- ส่วนที่ 2: Dashboard คำนวณต้นทุน/กำไร (กรอกละเอียด) ---
    st.header("💰 ส่วนที่ 2: สรุปผลการเทรด (Profit/Loss Dashboard)")
    
    grand_total_profit = 0
    
    for symbol in targets:
        with st.expander(f"📝 บันทึกรายการ {symbol}", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            
            # ฝั่งซื้อ/ต้นทุน
            buy_vol = c1.number_input(f"จำนวนที่ซื้อ ({symbol})", value=0, key=f"bv_{symbol}")
            buy_price = c2.number_input(f"ราคาที่ได้มา ({symbol})", value=0.0, format="%.2f", key=f"bp_{symbol}")
            buy_total = buy_vol * buy_price
            c1.write(f"เป็นเงิน: **{buy_total:,.2f}**")
            
            # ฝั่งขาย
            sell_vol = c3.number_input(f"จำนวนที่ขาย ({symbol})", value=0, key=f"sv_{symbol}")
            sell_price = c4.number_input(f"ราคาขาย ({symbol})", value=0.0, format="%.2f", key=f"sp_{symbol}")
            sell_total = sell_vol * sell_price
            c3.write(f"เป็นเงิน: **{sell_total:,.2f}**")
            
            # สถานะเพิ่มเติม
            trade_type = st.radio("ประเภทรายการ:", ["ซื้อปกติ/ดักไม้แรก", "ซื้อถัวเพิ่ม (DCA)", "แบ่งขายทำกำไร"], key=f"type_{symbol}", horizontal=True)
            
            # คำนวณกำไร/ขาดทุน ของตัวนั้นๆ
            # คิดกำไรจากจำนวนหุ้นที่ขายไป เทียบกับทุนเดิม
            realized_profit = (sell_price - buy_price) * sell_vol if sell_vol > 0 else 0
            grand_total_profit += realized_profit
            
            st.subheader(f"📊 สรุป {symbol}: กำไร/ขาดทุนสุทธิ: {realized_profit:,.2f} บาท")
            st.markdown("---")

    # สรุปยอดรวมทั้งหมด
    st.sidebar.markdown("---")
    st.sidebar.header("🏆 สรุปภาพรวมพอร์ต")
    st.sidebar.metric("กำไร/ขาดทุนรวม (บาท)", f"{grand_total_profit:,.2f}")
    if grand_total_profit > 0: st.sidebar.balloons()

# ==========================================
# (MODE 2: RECOVERY ยังคงอยู่เหมือนเดิม)
# ==========================================
elif menu == "🧮 เครื่องมือแก้เกม (Recovery)":
    st.title("🧮 Recovery Tools")
    # ... โค้ดส่วน Recovery เดิม ...
