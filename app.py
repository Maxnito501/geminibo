import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from settrade_v2.user import Investor

# ==========================================
# ⚙️ CONFIGURATION & UI SETUP
# ==========================================
st.set_page_config(
    page_title="GeminiBo Engineer",
    page_icon="🤖",
    layout="wide"
)

# --- ระบบกุญแจลับ (Streamlit Secrets) ---
# วิธีใช้: ใส่ใน Advanced Settings ของ Streamlit Cloud
try:
    APP_ID = st.secrets["SETTRADE_APP_ID"]
    APP_SECRET = st.secrets["SETTRADE_APP_SECRET"]
except:
    # สำหรับรันในเครื่องตัวเอง (Local) ให้แก้รหัสตรงนี้ครับ
    APP_ID = "A6ci0gEXKmkRPwRY"
    APP_SECRET = "AMZcHrk9Ytvyj+UPO7BDgvpZ5Cjy8h0H8ocZoNQ6aQPK"

DB_FILE = 'data.json'

# --- ฟังก์ชันโหลด/บันทึกข้อมูล ---
def load_data():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==========================================
# 📡 SETTRADE API CONNECTION
# ==========================================
@st.cache_resource # ช่วยให้ไม่ต้องต่อเน็ตใหม่ทุกครั้งที่กดปุ่ม
def connect_settrade():
    try:
        investor = Investor(
            app_id=APP_ID,
            app_secret=APP_SECRET,
            broker_id="SANDBOX",
            app_code="SANDBOX",
            is_auto_queue=False
        )
        return investor.MarketData()
    except Exception as e:
        st.error(f"❌ เชื่อมต่อ API ไม่สำเร็จ: {e}")
        return None

market = connect_settrade()

# ==========================================
# 🎨 SIDEBAR & MENU
# ==========================================
st.sidebar.title("🏗️ GeminiBo v2.0")
st.sidebar.caption("Engineering Trading System")
menu = st.sidebar.radio("Main Menu", ["🛡️ Market Sentinel", "📝 Trade Planner", "⚠️ Risk Manager"])

# ==========================================
# 🛡️ MODULE 1: MARKET SENTINEL (Auto Real-time)
# ==========================================
if menu == "🛡️ Market Sentinel":
    st.title("🛡️ Market Sentinel: อ่านใจเจ้ามือ (Real-time)")
    
    symbol = st.text_input("ระบุชื่อหุ้นที่ต้องการเจาะลึก", "PTT").upper()
    
    if st.button("🔍 สแกน Bid/Offer เดี๋ยวนี้", type="primary"):
        if market:
            quote = market.get_quote_symbol(symbol)
            if quote and quote.get('last'):
                # ส่วนหัวข้อราคา
                c1, c2, c3 = st.columns(3)
                c1.metric("ราคาล่าสุด", f"{quote['last']:.2f}", f"{quote.get('percent_change', 0)}%")
                c2.metric("Volume รวม", f"{quote['total_volume']:,}")
                c3.metric("เวลาอัปเดต", quote.get('time', '--:--'))

                st.markdown("---")
                
                # ส่วนตาราง Bid/Offer
                col_bid, col_off = st.columns(2)
                
                with col_bid:
                    st.subheader("BIDS (รอซื้อ)")
                    bid_df = pd.DataFrame({
                        "Volume": [quote[f'bid_volume{i}'] for i in range(1,6)],
                        "Price": [quote[f'bid_price{i}'] for i in range(1,6)]
                    })
                    st.table(bid_df.style.format({"Volume": "{:,.0f}", "Price": "{:.2f}"}))

                with col_off:
                    st.subheader("OFFERS (รอขาย)")
                    off_df = pd.DataFrame({
                        "Price": [quote[f'offer_price{i}'] for i in range(1,6)],
                        "Volume": [quote[f'offer_volume{i}'] for i in range(1,6)]
                    })
                    st.table(off_df.style.format({"Volume": "{:,.0f}", "Price": "{:.2f}"}))

                # วิเคราะห์ Wall Ratio
                top_bid = quote['bid_volume1']
                top_offer = quote['offer_volume1']
                ratio = top_offer / top_bid if top_bid > 0 else 0
                
                st.markdown("### 📊 วิเคราะห์เชิงวิศวกรรม")
                st.write(f"**Wall Ratio (Offer/Bid):** {ratio:.2f} เท่า")
                if ratio > 5:
                    st.error("🚨 STATUS: SQUEEZE! (โดนขวางหนัก -> เจ้าเก็บของ/กดราคา)")
                elif ratio < 0.2:
                    st.warning("🩸 STATUS: PANIC/DUMP! (ระวังแรงเทขาย)")
                else:
                    st.success("ℹ️ STATUS: NORMAL (ตลาดปกติ)")
            else:
                st.warning("❌ ไม่พบข้อมูลหุ้นตัวนี้")

# ==========================================
# 📝 MODULE 2: TRADE PLANNER
# ==========================================
elif menu == "📝 Trade Planner":
    st.title("📝 Trade Planner: วางแผนเทรด")
    
    with st.form("plan_form"):
        c1, c2 = st.columns(2)
        sym = c1.text_input("ชื่อหุ้น").upper()
        vol = c2.number_input("จำนวนหุ้น", 100)
        ent = c1.number_input("ทุน", format="%.2f")
        target = c2.number_input("เป้าขาย", format="%.2f")
        sl = c1.number_input("Stop Loss", format="%.2f")
        
        if st.form_submit_button("💾 บันทึกแผน"):
            data = load_data()
            data.append({
                "symbol": sym, "date": datetime.now().strftime("%Y-%m-%d"),
                "shares": vol, "entry_price": ent, 
                "target_price": target, "stop_loss": sl, "status": "Active"
            })
            save_data(data)
            st.toast(f"บันทึก {sym} สำเร็จ!")

# ==========================================
# ⚠️ MODULE 3: RISK MANAGER
# ==========================================
elif menu == "⚠️ Risk Manager":
    st.title("⚠️ Risk Manager: เช็กสุขภาพพอร์ต")
    data = load_data()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        if st.button("🔄 อัปเดตราคาพอร์ตทั้งหมด (Real-time)"):
            if market:
                updated_prices = []
                for s in df['symbol']:
                    q = market.get_quote_symbol(s)
                    updated_prices.append(q['last'] if q else 0)
                df['Current'] = updated_prices
                df['P/L'] = (df['Current'] - df['entry_price']) * df['shares']
                st.dataframe(df[['symbol', 'shares', 'entry_price', 'Current', 'P/L']])
    else:
        st.info("ยังไม่มีข้อมูลพอร์ต")
