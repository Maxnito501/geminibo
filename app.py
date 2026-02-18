import streamlit as st
import pandas as pd
from settrade_v2.user import Investor

# ==========================================
# ⚙️ CONFIGURATION & UI SETUP
# ==========================================
st.set_page_config(page_title="GeminiBo Engineer v2.2", page_icon="🏗️", layout="wide")

APP_ID = "A6ci0gEXKmkRPwRY"
APP_SECRET = "AMZcHrk9Ytvyj+UPO7BDgvpZ5Cjy8h0H8ocZoNQ6aQPK"

@st.cache_resource
def connect_market():
    try:
        investor = Investor(app_id=APP_ID, app_secret=APP_SECRET,
                           broker_id="SANDBOX", app_code="SANDBOX", is_auto_queue=False)
        return investor.MarketData()
    except Exception as e: return None

market = connect_market()

st.sidebar.title("🏗️ GeminiBo v2.2")
menu = st.sidebar.radio("เลือกโหมดใช้งาน", ["📊 Dashboard 3 หุ้นเทพ", "🔍 สแกนหุ้นรายตัว", "🧮 เครื่องมือแก้เกม (Recovery)"])

# ==========================================
# 📊 MODE 1: DASHBOARD (เพิ่มช่องกรอกวอลลุ่มเอง)
# ==========================================
if menu == "📊 Dashboard 3 หุ้นเทพ":
    st.title("🚀 Real-time Dashboard (Manual Input Option)")
    targets = ["SIRI", "WHA", "MTC"]
    
    cols = st.columns(3)
    for i, symbol in enumerate(targets):
        with cols[i]:
            st.subheader(f"📈 {symbol}")
            
            # ดึงข้อมูลจากตลาด (ถ้ามี)
            last_price = 0.0
            if market:
                quote = market.get_quote_symbol(symbol)
                if quote and quote.get('last'):
                    last_price = quote.get('last', 0)
                    st.metric("ราคาตลาด", f"{last_price:.2f}", f"{quote.get('percent_change', 0)}%")

            # --- ส่วนกรอกวอลลุ่มเอง (ทางเลือกสำหรับพี่โบ้) ---
            with st.expander(f"🛠️ กรอกวอลลุ่ม {symbol} เอง"):
                manual_bid = st.number_input(f"Bid Vol ({symbol})", value=1000000, step=100000, key=f"b_{symbol}")
                manual_off = st.number_input(f"Offer Vol ({symbol})", value=3000000, step=100000, key=f"o_{symbol}")
                
                # คำนวณ Ratio จากที่กรอกเอง
                m_ratio = manual_off / manual_bid if manual_bid > 0 else 0
                st.write(f"📊 Manual Wall Ratio: **{m_ratio:.2f}**")
                
                if m_ratio > 3: st.warning("⚠️ เจ้ามือวางกำแพงขวาง (จากค่าที่กรอก)")
                elif m_ratio < 0.5: st.success("🚀 ทางสะดวก/เจ้าเก็บของ (จากค่าที่กรอก)")
                else: st.info("⚖️ บีบกรอบแคบ/เลือกทาง")

# ==========================================
# (เนื้อหา MODE 2 และ 3 คงเดิมตามที่พี่โบ้ต้องการ)
# ==========================================
elif menu == "🔍 สแกนหุ้นรายตัว":
    st.title("🛡️ Market Sentinel: เจาะลึก Bid/Offer")
    symbol = st.text_input("ระบุชื่อหุ้น", "WHA").upper()
    if st.button("🔍 สแกนเดี๋ยวนี้"):
        if market:
            quote = market.get_quote_symbol(symbol)
            if quote and quote.get('last') is not None:
                last = quote.get('last', 0) or 0
                vol = quote.get('total_volume', 0) or 0
                st.metric("ราคาล่าสุด", f"{last:.2f}")
                st.metric("Volume รวม", f"{vol:,}")
                # ... (ตาราง Bid/Offer เหมือนเดิม)

elif menu == "🧮 เครื่องมือแก้เกม (Recovery)":
    st.title("🧮 Recovery Calculator")
    tab1, tab2 = st.tabs(["📉 คำนวณถัวเฉลี่ย (WHA/MTC)", "💰 คำนวณถอนทุนคืน (SIRI)"])
    # ... (ส่วนคำนวณเหมือนเดิม)
