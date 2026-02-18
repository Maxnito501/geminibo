import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime as dt

# ==========================================
# ⚙️ CONFIGURATION & UI SETUP
# ==========================================
st.set_page_config(page_title="Geminibo Engineer v2.2", page_icon="🏗️", layout="wide")

# ระบบจำสถานะพอร์ตและเงินสด (Session State)
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 20172.03 # เงินสดพร้อมรบใน Dime!
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"หุ้น": "SIRI", "จำนวน": 8700, "ทุน": 1.47},
        {"หุ้น": "MTC", "จำนวน": 200, "ทุน": 39.50},
        {"หุ้น": "WHA", "จำนวน": 1000, "ทุน": 4.22}
    ]

# --- Custom CSS สำหรับสีโทนสว่างอ่านง่าย ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .stApp { background-color: #f8fafc; }
    div[data-testid="stMetric"] {
        background-color: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
    }
    .manual-box {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border: 2px solid #3b82f6; margin-bottom: 20px;
    }
    .action-buy { color: #16a34a; font-weight: bold; }
    .action-sell { color: #dc2626; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📡 DATA ENGINE
# ==========================================
def get_price(symbol):
    try:
        data = yf.download(symbol + ".BK", period="1d", interval="1m", progress=False)
        return round(data['Close'].iloc[-1], 2)
    except:
        return None

# ==========================================
# 🎨 SIDEBAR: กองบัญชาการเงินสด
# ==========================================
st.sidebar.title("🏗️ GeminiBo v2.2")
st.sidebar.markdown(f"**เงินสด Dime!:** ฿{st.session_state.cash_balance:,.2f}")

invested_val = sum([s['จำนวน'] * s['ทุน'] for s in st.session_state.portfolio])
st.sidebar.write(f"งบลงทุนปัจจุบัน: ฿{invested_val:,.2f}")
st.sidebar.progress(min(invested_val / 40000, 1.0), text="Capacity 40K")

menu = st.sidebar.radio("เมนูหลัก", ["🎯 Sniper & Manual Wall", "🛡️ Portfolio Manager", "🧮 Recovery Tools"])

# ==========================================
# 🎯 MODE 1: SNIPER & MANUAL WALL
# ==========================================
if menu == "🎯 Sniper & Manual Wall":
    st.title("🎯 Momentum Sniper (Manual Override)")
    
    col_sel, col_mode = st.columns([1, 1])
    target = col_sel.selectbox("เลือกหุ้นเป้าหมาย", [s['หุ้น'] for s in st.session_state.portfolio] + ["PLANB", "ERW", "THCOM"])
    use_manual = col_mode.toggle("เปิดโหมดกรอกวอลุ่มเอง (Manual)", value=True)

    # ดึงราคาตลาดมาเป็นฐาน
    market_p = get_price(target) or 0.0
    
    with st.container():
        st.markdown('<div class="manual-box">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        
        with c1:
            price_input = st.number_input("ราคาปัจจุบัน (Price)", value=market_p if market_p > 0 else 0.0, format="%.2f")
            st.caption(f"ดึงจากตลาด: {market_p}")
            
        if use_manual:
            with c2:
                bid_v = st.number_input("รวม Bid Volume (3 ช่องแรก)", value=1000000, step=10000)
            with c3:
                off_v = st.number_input("รวม Offer Volume (3 ช่องแรก)", value=5000000, step=10000)
            
            # คำนวณ Wall Ratio
            ratio = off_v / bid_v if bid_v > 0 else 0
            
            st.divider()
            res1, res2 = st.columns(2)
            with res1:
                st.metric("Wall Ratio", f"{ratio:.2f}x")
            with res2:
                if ratio > 3:
                    st.warning("⚠️ เจ้ามือวางกำแพงขวาง (รอรวบ)")
                elif ratio < 0.6:
                    st.success("🚀 ทางสะดวก/เจ้าเก็บของ (น่าเข้า)")
                else:
                    st.info("⚖️ ตลาดลังเล/เลือกทาง")
        else:
            st.info("💡 โหมด Auto: ระบบจะวิเคราะห์จากข้อมูล Market Data (หากเชื่อมต่อ API)")

        st.markdown('</div>', unsafe_allow_html=True)

    # --- ส่วนการตัดสินใจ: ซื้อเพิ่ม หรือ ขายออก ---
    st.subheader("🛠️ แผนปฏิบัติการ (Action Plan)")
    act1, act2, act3 = st.columns(3)
    
    with act1:
        st.markdown("<p class='action-buy'>➕ ซื้อเพิ่ม (Buy More)</p>", unsafe_allow_html=True)
        buy_shares = st.number_input("จำนวนหุ้นที่ซื้อ", value=100, step=100, key="buy_sh")
        if st.button("ยืนยันการซื้อ"):
            total_cost = buy_shares * price_input
            if total_cost <= st.session_state.cash_balance:
                st.session_state.cash_balance -= total_cost
                # อัปเดตพอร์ต
                found = False
                for s in st.session_state.portfolio:
                    if s['หุ้น'] == target:
                        s['ทุน'] = ((s['ทุน'] * s['จำนวน']) + total_cost) / (s['จำนวน'] + buy_shares)
                        s['จำนวน'] += buy_shares
                        found = True
                if not found:
                    st.session_state.portfolio.append({"หุ้น": target, "จำนวน": buy_shares, "ทุน": price_input})
                st.success(f"ซื้อ {target} สำเร็จ! ใช้เงิน ฿{total_cost:,.2f}")
                st.rerun()
            else:
                st.error("เงินสดไม่พอครับพี่โบ้!")

    with act2:
        st.markdown("<p class='action-sell'>➖ ขายออก (Sell/Take Profit)</p>", unsafe_allow_html=True)
        sell_shares = st.number_input("จำนวนหุ้นที่ขาย", value=100, step=100, key="sell_sh")
        if st.button("ยืนยันการขาย"):
            for s in st.session_state.portfolio:
                if s['หุ้น'] == target and s['จำนวน'] >= sell_shares:
                    gain = sell_shares * price_input
                    st.session_state.cash_balance += gain
                    s['จำนวน'] -= sell_shares
                    st.success(f"ขาย {target} สำเร็จ! ได้เงินคืน ฿{gain:,.2f}")
                    st.rerun()

    with act3:
        st.markdown("<p style='font-weight:bold;'>📉 สถานะปัจจุบัน</p>", unsafe_allow_html=True)
        current_holding = next((s for s in st.session_state.portfolio if s['หุ้น'] == target), None)
        if current_holding:
            st.write(f"มีอยู่: {current_holding['จำนวน']:,} หุ้น")
            st.write(f"ทุนเดิม: ฿{current_holding['ทุน']:.2f}")
            pl = (price_input - current_holding['ทุน']) * current_holding['จำนวน']
            st.write(f"กำไร/ขาดทุน: :{'green' if pl>=0 else 'red'}[฿{pl:,.2f}]")
        else:
            st.write("ไม่มีหุ้นตัวนี้ในพอร์ต")

# ==========================================
# 🛡️ MODE 2: PORTFOLIO MANAGER
# ==========================================
elif menu == "🛡️ Portfolio Manager":
    st.title("🛡️ แดชบอร์ดคุมงานพอร์ต")
    
    df = pd.DataFrame(st.session_state.portfolio)
    if not df.empty:
        # ดึงราคาตลาดปัจจุบันมาโชว์
        df['ราคาปัจจุบัน'] = df['หุ้น'].apply(lambda x: get_price(x) or 0.0)
        df['มูลค่าตลาด'] = df['จำนวน'] * df['ราคาปัจจุบัน']
        df['กำไร/ขาดทุน (฿)'] = (df['ราคาปัจจุบัน'] - df['ทุน']) * df['จำนวน']
        df['%'] = ((df['ราคาปัจจุบัน'] / df['ทุน']) - 1) * 100
        
        st.dataframe(df.style.format({
            "ทุน": "{:.2f}", 
            "ราคาปัจจุบัน": "{:.2f}", 
            "มูลค่าตลาด": "{:,.2f}",
            "กำไร/ขาดทุน (฿)": "{:,.2f}",
            "%": "{:.2f}%"
        }), use_container_width=True, hide_index=True)
        
        total_val = df['มูลค่าตลาด'].sum()
        st.metric("มูลค่าพอร์ตรวม", f"฿{total_val:,.2f}", f"{total_val - invested_val:,.2f}")
    else:
        st.write("พอร์ตว่างเปล่าครับ")
    
    if st.button("ล้างข้อมูลพอร์ต (Reset)"):
        st.session_state.portfolio = []
        st.session_state.cash_balance = 20172.03
        st.rerun()

# ==========================================
# 🧮 MODE 3: RECOVERY TOOLS
# ==========================================
elif menu == "🧮 เครื่องมือแก้เกม (Recovery)":
    st.title("🧮 Recovery & Planning")
    tab1, tab2 = st.tabs(["📉 จุดถัวเฉลี่ย", "💰 ถอนทุน (Free Seed)"])
    
    with tab1:
        st.subheader("คำนวณจุดตีตื้น")
        cx1, cx2 = st.columns(2)
        sym_rec = cx1.selectbox("เลือกหุ้นในมือ", [s['หุ้น'] for s in st.session_state.portfolio])
        curr_s = next(s for s in st.session_state.portfolio if s['หุ้น'] == sym_rec)
        
        add_shares = cx2.number_input("จะซื้อเพิ่มอีกกี่หุ้น", value=curr_s['จำนวน'])
        add_price = cx1.number_input("ราคาที่จะเข้าถัว", value=curr_s['ทุน'] * 0.95)
        
        new_avg = ((curr_s['จำนวน'] * curr_s['ทุน']) + (add_shares * add_price)) / (curr_s['จำนวน'] + add_shares)
        st.markdown(f"""
        ### 🎯 ผลลัพธ์
        - ทุนเดิม: **{curr_s['ทุน']:.2f}**
        - ทุนใหม่หลังถัว: **{new_avg:.2f}**
        - ต้องใช้เงินเพิ่ม: **฿{(add_shares * add_price):,.2f}**
        """)
        
    with tab2:
        st.subheader("กลยุทธ์ถอนทุนคืน (SIRI Free Seed)")
        total_s = st.number_input("หุ้นทั้งหมด", value=8700)
        cost_p = st.number_input("ราคาต้นทุน", value=1.47)
        target_p = st.number_input("ราคาเป้าหมายที่จะขายคืนทุน", value=1.65)
        
        shares_to_sell = (total_s * cost_p) / target_p
        st.warning(f"ขายออกแค่ **{int(shares_to_sell):,}** หุ้น พี่จะได้ทุนคืนครบ!")
        st.info(f"จะเหลือหุ้นฟรี (Free Seed) ไว้รันกำไร: **{int(total_s - shares_to_sell):,}** หุ้น")

st.sidebar.divider()
st.sidebar.caption(f"Update: {dt.now().strftime('%H:%M:%S')}")
