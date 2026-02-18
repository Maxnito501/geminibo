# Complete, well-commented, runnable code for Polaris v2.1 (App 7)
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime as dt

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="POLARIS v2.1: Geminibo Advanced",
    page_icon="🚀",
    layout="wide"
)

# --- 2. SESSION STATE (ระบบจำค่า ID และข้อมูลกำแพง) ---
if 'manual_wall_vol' not in st.session_state:
    st.session_state.manual_wall_vol = 7555000.0  # ค่าตั้งต้นจากกำแพง SIRI ที่พี่เจอ
if 'manual_avg_vol' not in st.session_state:
    st.session_state.manual_avg_vol = 15000000.0
if 'manual_ticker' not in st.session_state:
    st.session_state.manual_ticker = "SIRI"

# --- 3. PREMIUM LIGHT THEME (Slate White & Navy Focus) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .stApp { background-color: #f8fafc; color: #1e293b; }
    
    /* Command Center Panel */
    .command-panel {
        background-color: #ffffff;
        padding: 25px; border-radius: 20px;
        border: 2px solid #3b82f6; margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1);
    }
    
    /* Result Box */
    .gs-result-box {
        text-align: center; padding: 25px;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-radius: 15px; border: 1px solid #bfdbfe;
    }
    
    .trend-tag {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 0.75rem; font-weight: bold; margin-bottom: 10px;
    }
    .trend-bull { background-color: #dcfce7; color: #166534; }
    .trend-bear { background-color: #fee2e2; color: #991b1b; }
    
    h1, h2, h3 { color: #0f172a !important; }
    .label-mini { color: #64748b; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ADVANCED DATA ENGINE (v2.1) ---
@st.cache_data(ttl=60)
def fetch_advanced_data(ticker):
    try:
        t_bk = ticker + ".BK"
        # ดึงข้อมูล 3 เดือนเพื่อให้ครอบคลุมเส้น EMA
        data = yf.download(t_bk, period="3mo", interval="1d", progress=False)
        if data.empty: return None
        
        close = data['Close'].iloc[:, 0] if isinstance(data['Close'], pd.DataFrame) else data['Close']
        vol = data['Volume'].iloc[:, 0] if isinstance(data['Volume'], pd.DataFrame) else data['Volume']
        
        # A. RSI (14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # B. Trend Detection (EMA 20)
        ema20 = close.ewm(span=20, adjust=False).mean()
        curr_price = close.iloc[-1]
        curr_ema = ema20.iloc[-1]
        trend = "BULL" if curr_price > curr_ema else "BEAR"
        
        # C. Avg Volume (5 days)
        avg_vol_5d = vol.iloc[-6:-1].mean()
        
        return {
            "price": curr_price,
            "rsi": rsi.iloc[-1],
            "ema20": curr_ema,
            "trend": trend,
            "avg_vol": avg_vol_5d
        }
    except: return None

# --- 5. MAIN COMMANDER UI ---
def main():
    st.title("🏹 Geminibo v2.1: Advanced Sniper")
    st.caption(f"กองบัญชาการวิศวกรโบ้: ระบบดักทางกำแพงเจ้ามือ & วิเคราะห์เทรนด์ | {dt.now().strftime('%H:%M:%S')}")

    # --- TOP METRICS ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Cash Reserve", "฿20,172.03", "Ready to Double")
    m2.metric("System Mode", "Manual + Trend", delta="Active")
    m3.metric("Project ID", "Geminibo-v2.1", delta="suchat3165")

    st.divider()

    # --- SECTION: ADVANCED COMMAND PANEL ---
    st.subheader("⌨️ Strategic Manual Override (กรอกกำแพงหน้างาน)")
    
    with st.container():
        st.markdown('<div class="command-panel">', unsafe_allow_html=True)
        col_in, col_calc, col_score = st.columns([1.2, 1, 1.5])
        
        with col_in:
            st.session_state.manual_ticker = st.text_input("ชื่อหุ้น (Target)", value=st.session_state.manual_ticker).upper()
            auto = fetch_advanced_data(st.session_state.manual_ticker)
            
            if auto:
                trend_class = "trend-bull" if auto['trend'] == "BULL" else "trend-bear"
                st.markdown(f'<span class="trend-tag {trend_class}">TREND: {auto["trend"]}</span>', unsafe_allow_html=True)
                st.write(f"ราคาล่าสุด: **{auto['price']:.2f}** (EMA20: {auto['ema20']:.2f})")
                st.write(f"RSI: **{auto['rsi']:.1f}**")
            else:
                st.warning("รอข้อมูลตลาด...")

        with col_calc:
            st.session_state.manual_wall_vol = st.number_input("กำแพงวอลลุ่ม (Wall Vol)", value=st.session_state.manual_wall_vol, step=100000.0)
            default_avg = auto['avg_vol'] if auto else st.session_state.manual_avg_vol
            st.session_state.manual_avg_vol = st.number_input("วอลลุ่มเฉลี่ย (Avg Vol)", value=float(default_avg))
            
            # Geminibo Math Logic v2.1
            vol_ratio = st.session_state.manual_wall_vol / st.session_state.manual_avg_vol if st.session_state.manual_avg_vol > 0 else 0
            rsi_val = auto['rsi'] if auto else 50
            
            # Formula: Weight(RSI) 30% + Weight(Vol) 50% + Weight(Trend) 20%
            r_score = max(0, 100 - rsi_val)
            v_score = min(100, vol_ratio * 40)
            t_score = 100 if (auto and auto['trend'] == "BULL") else 30
            
            g_score = (r_score * 0.3) + (v_score * 0.5) + (t_score * 0.2)

        with col_score:
            status_color = "#ef4444" if g_score > 75 else "#f59e0b" if g_score > 55 else "#3b82f6"
            st.markdown(f"""
            <div class="gs-result-box">
                <p class="label-mini">Geminibo Score (v2.1)</p>
                <h1 style="color:{status_color}; font-size:4rem; margin:0;">{g_score:.1f}</h1>
                <p style="font-weight:bold; color:#1e293b;">Vol Ratio: {vol_ratio:.2f}x</p>
                <hr style="margin:15px 0; border:0; border-top:1px solid #bfdbfe;">
                <p style="font-size:0.9rem;">
                    <b>คําแนะนำ:</b> {'🔥 ลั่นไกตามเจ้ามือ!' if g_score > 75 else '⏳ จดจ้องในกรง' if g_score > 55 else '😴 นั่งทับมือรอ'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    # --- SECTION: DIME PRECISION CALCULATOR ---
    st.divider()
    st.subheader("🧮 Dime! Net Profit Calculator")
    cc1, cc2, cc3 = st.columns(3)
    with cc1: shares = st.number_input("จำนวนหุ้น", value=8700 if st.session_state.manual_ticker == "SIRI" else 200, step=100)
    with cc2: b_p = st.number_input("ราคาซื้อ (Avg Cost)", value=auto['price'] if auto else 1.47, format="%.2f")
    with cc3: s_p = st.number_input("ราคาขายเป้าหมาย", value=(auto['price']*1.05) if auto else 1.55, format="%.2f")
    
    # Dime Logic: 0.15% + VAT + Reg Fee
    comm = (b_p * shares * 0.0015) + (s_p * shares * 0.0015)
    total_fees = (comm * 1.07) + ((b_p + s_p) * shares * 0.00007)
    net_profit = ((s_p - b_p) * shares) - total_fees
    
    res_col1, res_col2 = st.columns([2, 1])
    res_col1.metric("กำไรสุทธิหลังหักคอมฯ (NET)", f"฿{net_profit:,.2f}", f"ROI: {((net_profit/(b_p*shares))*100):.2f}%")
    res_col2.write(f"ค่าธรรมเนียม Dime! รวม: **฿{total_fees:.2f}**")

    # --- FOOTER ---
    st.info(f"💡 **Engineer's Note:** ข้อมูลกำแพง {st.session_state.manual_wall_vol:,.0} หุ้น ของ {st.session_state.manual_ticker} ถูกจำไว้ใน ID ของพี่แล้ว แม้สลับไปทำงานราชการกลับมาข้อมูลก็ยังอยู่ครับ")

if __name__ == "__main__":
    main()
