# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v6.6 Precision Ledger)
# ==========================================
st.set_page_config(page_title="GeminiBo v6.6: Ultimate Ledger", layout="wide", page_icon="📓")

# ค่าธรรมเนียมมาตรฐาน (รวม VAT 7% แล้ว)
FEE_STREAMING = 0.00168 
FEE_DIME_STD = 0.001605
FEE_DIME_FREE = 0.0

GEMINI_PRO_COST = 790.0
SETSMART_MONTHLY = 200.0 
TARGET_TOTAL = GEMINI_PRO_COST + SETSMART_MONTHLY

def get_tick_size(price):
    if price < 2.0: return 0.01
    if price < 5.0: return 0.02
    if price < 10.0: return 0.05
    if price < 25.0: return 0.10
    if price < 100.0: return 0.25
    return 1.00

def get_live_data(symbol):
    try:
        symbol = symbol.strip().upper()
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < 10: return None
        curr_p = df['Close'].iloc[-1]
        prev_p = df['Close'].iloc[-2]
        change = ((curr_p - prev_p) / prev_p) * 100
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        avg_vol = df['Volume'].iloc[-6:-1].mean()
        rvol = df['Volume'].iloc[-1] / avg_vol if avg_vol > 0 else 1.0
        return {"price": curr_p, "change": change, "rsi": rsi, "rvol": rvol}
    except: return None

# ==========================================
# 💾 DATA STORAGE
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'custom_watchlist' not in st.session_state:
    st.session_state.custom_watchlist = ["SIRI", "MTC", "GPSC", "HANA", "WHA"]

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏹 Commander (ติดตามหุ้น)", "📓 บันทึกการรบ (Trade Ledger)", "🐷 Anti-Pig (บัญชีขายหมู)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 ศูนย์บัญชาการ: สแกนหุ้น & จุดช้อน")
    c_add1, c_add2 = st.columns([3, 1])
    with c_add1:
        new_sym = st.text_input("➕ เพิ่มหุ้นเข้าเรดาร์ (พิมพ์ชื่อหุ้นแล้วกด Enter):").upper()
    with c_add2:
        if st.button("บันทึก") and new_sym:
            if new_sym not in st.session_state.custom_watchlist:
                st.session_state.custom_watchlist.append(new_sym)
                st.rerun()

    selected_stocks = st.multiselect("ส่องกล้องตัวที่น่าสนใจ:", st.session_state.custom_watchlist, default=st.session_state.custom_watchlist[:3])
    cols = st.columns(3)
    for i, sym in enumerate(selected_stocks):
        data = get_live_data(sym)
        with cols[i % 3]:
            with st.container(border=True):
                if data:
                    st.header(f"🛡️ {sym}")
                    tick = get_tick_size(data['price'])
                    st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                    st.markdown(f"📍 **จุดช้อน (-1 ช่อง):** <span style='font-size: 24px; color: #00FF00;'>**{data['price']-tick:.2f}**</span>", unsafe_allow_html=True)
                    st.write(f"📡 RSI: {data['rsi']:.1f} | 🌊 RVOL: {data['rvol']:.2f}")
                else: st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: TRADE LEDGER (Rebuilt) ---
with tab2:
    st.title("📓 สมุดบันทึกการรบ (Professional Ledger)")
    
    with st.expander("➕ ลงบันทึกรายการเทรด (ซื้อ/ขาย)", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            l_date = st.date_input("วันที่", datetime.now())
            l_symbol = st.text_input("ชื่อหุ้น", value="SIRI").upper()
            l_broker = st.selectbox("เทรดผ่านแอป:", ["Streaming", "Dime (Standard)", "Dime (Free Tier)"])
        with f_col2:
            l_buy_qty = st.number_input("จำนวนหุ้นที่ซื้อ (Qty)", value=1000, step=100)
            l_buy_price = st.number_input("ราคาที่ซื้อ (Price)", value=1.000, format="%.3f")
        with f_col3:
            l_sell_qty = st.number_input("จำนวนหุ้นที่ขาย (Qty)", value=1000, step=100)
            l_sell_price = st.number_input("ราคาที่ขาย (Price)", value=1.100, format="%.3f")
        
        # Calculation Logic
        rate = FEE_STREAMING if l_broker == "Streaming" else (FEE_DIME_STD if l_broker == "Dime (Standard)" else FEE_DIME_FREE)
        buy_val = l_buy_qty * l_buy_price
        sell_val = l_sell_qty * l_sell_price
        
        # คิดค่าธรรมเนียมรายขา
        fee_buy = buy_val * rate
        fee_sell = sell_val * rate
        total_fee = fee_buy + fee_sell
        
        # กำไรสุทธิ (คิดจากจำนวนที่ขายจริง)
        # หากขายไม่เท่ากับที่ซื้อ ระบบจะคิดต้นทุนจากสัดส่วนที่ขาย
        real_cost = (l_sell_qty * l_buy_price) + (fee_buy * (l_sell_qty/l_buy_qty if l_buy_qty > 0 else 1))
        real_revenue = sell_val - fee_sell
        net_p = real_revenue - real_cost
        
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.write(f"💰 จ่ายรวม (ซื้อ): **{buy_val + fee_buy:,.2f}**")
        c2.write(f"💵 รับสุทธิ (ขาย): **{real_revenue:,.2f}**")
        c3.subheader(f"กำไร/ขาดทุน: {net_p:,.2f} บ.")
        
        if st.button("💾 บันทึกลงสมุดบัญชี"):
            st.session_state.trade_history.append({
                "วันที่": l_date.strftime("%d/%m/%Y"),
                "หุ้น": l_symbol,
                "แอป": l_broker,
                "ซื้อ Qty": l_buy_qty,
                "ราคาซื้อ": l_buy_price,
                "ขาย Qty": l_sell_qty,
                "ราคาขาย": l_sell_price,
                "กำไรสุทธิ": net_p
            })
            st.rerun()

    if st.session_state.trade_history:
        st.markdown("---")
        st.subheader("📋 สรุปผลการรบรายรายการ")
        df_history = pd.DataFrame(st.session_state.trade_history)
        
        # แสดงผลแบบตารางที่อ่านง่าย
        for idx, row in df_history.iterrows():
            with st.container(border=True):
                r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([1, 1, 2, 1, 0.5])
                r_col1.write(f"📅 {row['วันที่']}")
                r_col2.write(f"**{row['หุ้น']}**\n({row['แอป']})")
                r_col3.write(f"🔵 ซื้อ: {row['ซื้อ Qty']:,} @ {row['ราคาซื้อ']:.3f}\n🔴 ขาย: {row['ขาย Qty']:,} @ {row['ราคาขาย']:.3f}")
                r_col4.subheader(f"{row['กำไรสุทธิ']:,.2f}")
                if r_col5.button("🗑️", key=f"del_{idx}"):
                    st.session_state.trade_history.pop(idx)
                    st.rerun()
        
        total_net = df_history["กำไรสุทธิ"].sum()
        st.sidebar.metric("🏆 กำไรสะสมสุทธิ", f"{total_net:,.2f} บ.")
        st.sidebar.progress(min(max(total_net / TARGET_TOTAL, 0.0), 1.0))
        st.sidebar.write(f"🎯 เป้าหมายแอปฟรี: {TARGET_TOTAL} บ.")

# --- TAB 3: ANTI-PIG ---
with tab3:
    st.title("🐷 บัญชีวิเคราะห์การขายหมู")
    if st.session_state.trade_history:
        p_data = []
        for item in st.session_state.trade_history:
            live = get_live_data(item['หุ้น'])
            if live:
                diff = live['price'] - item['ราคาขาย']
                p_data.append({
                    "หุ้น": item['หุ้น'], "ขายที่": item['ราคาขาย'], "ราคาตอนนี้": live['price'],
                    "กำไรที่พลาดไป": diff * item['ขาย Qty'] if diff > 0 else 0,
                    "สถานะ": "🐷 ขายหมู" if diff > 0 else "✅ ขายคม"
                })
        st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)
    else: st.info("ยังไม่มีประวัติการขาย")

st.markdown("---")
st.caption("v6.6 Precision Ledger — 'บันทึกทุกไม้ คำนวณทุกสตางค์ เพื่อความมั่งคั่งของจอมทัพ'")
