import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime as dt

# ==========================================
# ⚙️ CONFIGURATION & UI SETUP
# ==========================================
st.set_page_config(page_title="Geminibo Commander v2.3", page_icon="🏗️", layout="wide")

# ระบบจำสถานะพอร์ตและเงินสด (Session State)
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 20172.03
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"หุ้น": "SIRI", "จำนวน": 8700, "ทุน": 1.47, "เป้าหมาย": 1.50, "กลยุทธ์": "ขายที่ราคาเป้าหมาย"},
        {"หุ้น": "MTC", "จำนวน": 200, "ทุน": 39.50, "เป้าหมาย": 42.00, "กลยุทธ์": "สะสมเพิ่ม"},
        {"หุ้น": "WHA", "จำนวน": 1000, "ทุน": 4.22, "เป้าหมาย": 4.30, "กลยุทธ์": "รอจังหวะขายคืนทุน"}
    ]

# --- Custom CSS (Premium Light Theme) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    /* Metrics & Cards */
    div[data-testid="stMetric"] {
        background-color: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
    }
    .status-card {
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 10px solid #3b82f6; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .strategy-badge {
        padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold;
    }
    .badge-dividend { background-color: #dcfce7; color: #166534; }
    .badge-sell { background-color: #dbeafe; color: #1e40af; }
    .badge-acc { background-color: #fee2e2; color: #991b1b; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📡 DATA ENGINE (Fixing ValueError)
# ==========================================
def get_clean_price(symbol):
    try:
        if not symbol.endswith(".BK"): symbol += ".BK"
        data = yf.download(symbol, period="1d", interval="1m", progress=False)
        if data.empty: return None
        # แก้ไขการดึงค่าให้เป็น float เพื่อกัน Error ในรูป 6b09a6
        val = data['Close'].iloc[-1]
        if isinstance(val, pd.Series): val = val.iloc[0]
        return round(float(val), 2)
    except:
        return None

# ==========================================
# 🎨 SIDEBAR COMMANDER
# ==========================================
st.sidebar.title("🏗️ GeminiBo v2.3")
st.sidebar.metric("เงินสดคงเหลือ (Dime!)", f"฿{st.session_state.cash_balance:,.2f}")

total_invested = sum([s['จำนวน'] * s['ทุน'] for s in st.session_state.portfolio])
st.sidebar.write(f"งบลงทุนที่ใช้ไป: ฿{total_invested:,.2f}")
st.sidebar.progress(min(total_invested / 40000, 1.0), text=f"พอร์ต 40K ({total_invested/400:,.1f}%)")

menu = st.sidebar.radio("ห้องบัญชาการ", ["🛡️ พอร์ตแม่ทัพ & กลยุทธ์", "🎯 Sniper & Manual Wall", "🚀 สแกนหุ้นซิ่ง (App 7)"])

# ==========================================
# 🛡️ MODE 1: PORTFOLIO & STRATEGY DASHBOARD
# ==========================================
if menu == "🛡️ พอร์ตแม่ทัพ & กลยุทธ์":
    st.title("🛡️ Strategic Portfolio Dashboard")
    
    df = pd.DataFrame(st.session_state.portfolio)
    if not df.empty:
        # วิเคราะห์แบบ Real-time
        with st.spinner("กำลังดึงราคาตลาด..."):
            df['ราคาล่าสุด'] = df['หุ้น'].apply(lambda x: get_clean_price(x) or 0.0)
        
        df['มูลค่าปัจจุบัน'] = df['จำนวน'] * df['ราคาล่าสุด']
        df['กำไร/ขาดทุน'] = (df['ราคาล่าสุด'] - df['ทุน']) * df['จำนวน']
        df['% P/L'] = ((df['ราคาล่าสุด'] / df['ทุน']) - 1) * 100
        
        # แสดงตารางแบบสรุป
        st.dataframe(df.style.format({
            "ทุน": "{:.2f}", "ราคาล่าสุด": "{:.2f}", "เป้าหมาย": "{:.2f}",
            "มูลค่าปัจจุบัน": "{:,.2f}", "กำไร/ขาดทุน": "{:,.2f}", "% P/L": "{:+.2f}%"
        }), use_container_width=True, hide_index=True)

        st.divider()
        
        # สรุปภาพรวม
        c1, c2, c3 = st.columns(3)
        total_mkt = df['มูลค่าปัจจุบัน'].sum()
        total_pl = df['กำไร/ขาดทุน'].sum()
        c1.metric("มูลค่าพอร์ตรวม", f"฿{total_mkt:,.2f}")
        c2.metric("กำไรสะสมสุทธิ", f"฿{total_pl:,.2f}", f"{total_pl/total_invested*100:+.2f}%")
        c3.metric("สถานะ", "BULLISH" if total_pl > 0 else "DEFENSIVE")
        
    else:
        st.info("ยังไม่มีหุ้นในพอร์ตครับพี่โบ้")

# ==========================================
# 🎯 MODE 2: SNIPER & MANUAL WALL
# ==========================================
elif menu == "🎯 Sniper & Manual Wall":
    st.title("🎯 Momentum Sniper (Precision Control)")
    
    col_sel, col_mode = st.columns([1, 1])
    target = col_sel.selectbox("เลือกหุ้นปฏิบัติการ", [s['หุ้น'] for s in st.session_state.portfolio] + ["PLANB", "THCOM", "JTS", "ERW"])
    use_manual = col_mode.toggle("เปิดโหมดกรอกเอง (Manual Override)", value=True)

    curr_mkt_p = get_clean_price(target) or 0.0
    
    with st.container():
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        
        with c1:
            price_active = st.number_input("ราคาลั่นไก (Active Price)", value=float(curr_mkt_p), format="%.2f")
            st.caption(f"ราคาตลาด: {curr_mkt_p}")
            
        if use_manual:
            with c2:
                bid_v = st.number_input("Bid Volume (3 แถวแรก)", value=1000000)
            with c3:
                off_v = st.number_input("Offer Volume (3 แถวแรก)", value=5000000)
            
            # Geminibo Wall Logic
            ratio = off_v / bid_v if bid_v > 0 else 0
            st.write(f"📊 **Wall Ratio:** {ratio:.2f}x")
            if ratio > 3: st.warning("⚠️ เจ้ามือวางกั้น (รอรวบ)")
            elif ratio < 0.6: st.success("🚀 ทางสะดวก (เจ้าเก็บของ)")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # --- บัญชาการการรบ (Action) ---
    st.subheader("🛠️ คำสั่งซื้อขายและสถานะพอร์ต")
    act_col1, act_col2 = st.columns(2)
    
    holding = next((s for s in st.session_state.portfolio if s['หุ้น'] == target), None)

    with act_col1:
        st.markdown("**➕ เพิ่มไม้/ซื้อใหม่**")
        qty_buy = st.number_input("จำนวนที่ต้องการซื้อ", value=100, step=100, key="b")
        if st.button("ยืนยันการซื้อ (หักเงินสด)"):
            cost = qty_buy * price_active
            if cost <= st.session_state.cash_balance:
                st.session_state.cash_balance -= cost
                if holding:
                    holding['ทุน'] = ((holding['ทุน'] * holding['จำนวน']) + cost) / (holding['จำนวน'] + qty_buy)
                    holding['จำนวน'] += qty_buy
                else:
                    st.session_state.portfolio.append({"หุ้น": target, "จำนวน": qty_buy, "ทุน": price_active, "เป้าหมาย": price_active*1.05, "กลยุทธ์": "สะสมเพิ่ม"})
                st.success(f"บันทึกซื้อ {target} เรียบร้อย!")
                st.rerun()
            else:
                st.error("กระสุนเงินสดไม่พอครับ!")

    with act_col2:
        st.markdown("**➖ ปิดจ๊อบ/ขายออก**")
        qty_sell = st.number_input("จำนวนที่ต้องการขาย", value=holding['จำนวน'] if holding else 0, step=100, key="s")
        if st.button("ยืนยันการขาย (คืนเงินสด)"):
            if holding and holding['จำนวน'] >= qty_sell:
                gain = qty_sell * price_active
                st.session_state.cash_balance += gain
                holding['จำนวน'] -= qty_sell
                if holding['จำนวน'] == 0:
                    st.session_state.portfolio = [s for s in st.session_state.portfolio if s['หุ้น'] != target]
                st.success(f"ขาย {target} คืนทุน ฿{gain:,.2f}")
                st.rerun()

# ==========================================
# 🚀 MODE 3: ZING 20 SCANNER (APP 7 STYLE)
# ==========================================
elif menu == "🚀 สแกนหุ้นซิ่ง (App 7)":
    st.title("🚀 Zing 20 Strategic Scanner")
    pool = ["THCOM", "JTS", "PLANB", "SIRI", "WHA", "MTC", "DELTA", "HANA", "KCE", "CPALL", "TRUE", "ADVANC", "ERW", "CENTEL", "SPA", "TASCO", "DOHOME", "GLOBAL", "AMATA", "ROJNA"]
    
    if st.button("🔄 RE-SCAN MARKET"): st.rerun()
    
    results = []
    with st.spinner("AI กำลังกวาดรอยเท้าเจ้ามือ 20 ตัว..."):
        for sym in pool:
            p = get_clean_price(sym)
            if p:
                results.append({"หุ้น": sym, "ราคา": p, "Signal": "🔥 น่าจับตา" if p < 10 else "⚖️ ถือรอ"})
    
    st.table(pd.DataFrame(results))

st.sidebar.divider()
st.sidebar.caption(f"Last Updated: {dt.now().strftime('%H:%M:%S')}")
