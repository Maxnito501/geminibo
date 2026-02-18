import streamlit as st
import pandas as pd
from settrade_v2.user import Investor

# ==========================================
# ⚙️ CONFIGURATION & UI SETUP
# ==========================================
st.set_page_config(page_title="GeminiBo Engineer v2.1", page_icon="🏗️", layout="wide")

# ส่วนกรอก ID (พี่โบ้กรอกตรงนี้ หรือใส่ใน Secrets ของ Streamlit Cloud)
APP_ID = "A6ci0gEXKmkRPwRY"
APP_SECRET = "AMZcHrk9Ytvyj+UPO7BDgvpZ5Cjy8h0H8ocZoNQ6aQPK"

# ==========================================
# 📡 CONNECTION HELPER
# ==========================================
@st.cache_resource
def connect_market():
    try:
        investor = Investor(
            app_id=APP_ID, app_secret=APP_SECRET,
            broker_id="SANDBOX", app_code="SANDBOX", is_auto_queue=False
        )
        return investor.MarketData()
    except Exception as e:
        st.error(f"❌ เชื่อมต่อ API ไม่สำเร็จ: {e}")
        return None

market = connect_market()

# ==========================================
# 🎨 SIDEBAR MENU
# ==========================================
st.sidebar.title("🏗️ GeminiBo v2.1")
st.sidebar.info("Engineering Mindset for Trading")
menu = st.sidebar.radio("เลือกโหมดใช้งาน", ["📊 Dashboard 3 หุ้นเทพ", "🔍 สแกนหุ้นรายตัว", "🧮 เครื่องมือแก้เกม (Recovery)"])

# ==========================================
# 📊 MODE 1: DASHBOARD (SIRI, WHA, MTC)
# ==========================================
if menu == "📊 Dashboard 3 หุ้นเทพ":
    st.title("🚀 Real-time Dashboard: SIRI | WHA | MTC")
    targets = ["SIRI", "WHA", "MTC"]
    
    if st.button("🔄 อัปเดตข้อมูลด่วน"):
        st.rerun()

    if market:
        cols = st.columns(3)
        for i, symbol in enumerate(targets):
            quote = market.get_quote_symbol(symbol)
            with cols[i]:
                st.subheader(f"📈 {symbol}")
                if quote and quote.get('last') is not None:
                    last = quote.get('last', 0)
                    chg = quote.get('percent_change', 0)
                    
                    # วิเคราะห์ Wall Ratio (Offer / Bid 3 ช่องแรก)
                    sum_bid = sum([quote.get(f'bid_volume{j}', 0) for j in range(1, 4)])
                    sum_off = sum([quote.get(f'offer_volume{j}', 0) for j in range(1, 4)])
                    ratio = sum_off / sum_bid if sum_bid > 0 else 0
                    
                    st.metric("ราคา", f"{last:.2f}", f"{chg}%")
                    st.write(f"📊 Wall Ratio: **{ratio:.2f}**")
                    
                    if ratio > 3: st.warning("⚠️ เจ้ามือวางกำแพงขวาง")
                    elif ratio < 0.5: st.success("🚀 ทางสะดวก/เจ้าเก็บของ")
                    else: st.info("⚖️ บีบกรอบแคบ/เลือกทาง")
                else:
                    st.write("❌ ไม่พบข้อมูล (Sandbox)")
    else:
        st.error("🔌 กรุณาตรวจสอบ API Connection")

# ==========================================
# 🔍 MODE 2: สแกนหุ้นรายตัว (กัน Error 100%)
# ==========================================
elif menu == "🔍 สแกนหุ้นรายตัว":
    st.title("🛡️ Market Sentinel: เจาะลึก Bid/Offer")
    symbol = st.text_input("ระบุชื่อหุ้น", "WHA").upper()
    
    if st.button("🔍 สแกนเดี๋ยวนี้"):
        if market:
            quote = market.get_quote_symbol(symbol)
            if quote and quote.get('last') is not None:
                # แก้ Error 'total_volume' ด้วย .get()
                last = quote.get('last', 0) or 0
                pct = quote.get('percent_change', 0) or 0
                vol = quote.get('total_volume', 0) or 0
                
                c1, c2, c3 = st.columns(3)
                c1.metric("ราคาล่าสุด", f"{last:.2f}", f"{pct}%")
                c2.metric("Volume รวม", f"{vol:,}")
                c3.metric("เวลา", quote.get('time', '--:--'))

                st.markdown("---")
                col_b, col_o = st.columns(2)
                with col_b:
                    st.subheader("BIDS (รอซื้อ)")
                    bid_df = pd.DataFrame({
                        "Price": [quote.get(f'bid_price{i}', 0) for i in range(1, 6)],
                        "Volume": [quote.get(f'bid_volume{i}', 0) for i in range(1, 6)]
                    })
                    st.table(bid_df.style.format({"Price": "{:.2f}", "Volume": "{:,}"}))
                with col_o:
                    st.subheader("OFFERS (รอขาย)")
                    off_df = pd.DataFrame({
                        "Price": [quote.get(f'offer_price{i}', 0) for i in range(1, 6)],
                        "Volume": [quote.get(f'offer_volume{i}', 0) for i in range(1, 6)]
                    })
                    st.table(off_df.style.format({"Price": "{:.2f}", "Volume": "{:,}"}))
            else:
                st.error("⚠️ ไม่พบข้อมูลหุ้นตัวนี้")

# ==========================================
# 🧮 MODE 3: เครื่องมือแก้เกม (DCA & Free Seed)
# ==========================================
elif menu == "🧮 เครื่องมือแก้เกม (Recovery)":
    st.title("🧮 Recovery Calculator")
    
    tab1, tab2 = st.tabs(["📉 คำนวณถัวเฉลี่ย (WHA/MTC)", "💰 คำนวณถอนทุนคืน (SIRI)"])
    
    with tab1:
        st.subheader("จุดถัวเฉลี่ยเพื่อตีตื้น")
        c1, c2 = st.columns(2)
        old_v = c1.number_input("จำนวนหุ้นเดิม", value=1000)
        old_p = c2.number_input("ต้นทุนเดิม", value=4.22)
        new_v = c1.number_input("จำนวนหุ้นที่จะถัว", value=1000)
        new_p = c2.number_input("ราคาที่ถัว", value=4.14)
        
        avg = ((old_v * old_p) + (new_v * new_p)) / (old_v + new_v)
        st.success(f"🎯 ทุนเฉลี่ยใหม่ของคุณคือ: {avg:.2f}")

    with tab2:
        st.subheader("ขายกี่หุ้นให้ได้เงินต้นคืน? (Free Seed)")
        total_s = st.number_input("จำนวนหุ้นทั้งหมดที่มี", value=8700)
        cost_p = st.number_input("ทุนเฉลี่ย (1.47)", value=1.47)
        target_s = st.number_input("ราคาที่จะแบ่งขาย", value=1.65)
        
        money_back = (total_s * cost_p) / target_s
        st.warning(f"💡 พี่โบ้ต้องขาย {int(money_back):,} หุ้น เพื่อเอาทุนคืนทั้งหมด")
        st.info(f"🚀 จะเหลือหุ้นฟรีไว้รันกำไร: {int(total_s - money_back):,} หุ้น")
