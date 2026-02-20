# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v6.7 Ultimate Ledger)
# ==========================================
st.set_page_config(page_title="GeminiBo v6.7: Ultimate Ledger", layout="wide", page_icon="📓")

# อัตราค่าธรรมเนียมรวม VAT 7%
FEE_STREAMING = 0.00168 
FEE_DIME_STD = 0.001605
FEE_DIME_FREE = 0.0

GEMINI_PRO_COST = 790.0
# ราคา SETSMART รายปีเฉลี่ย 200/เดือน
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
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] if loss.iloc[-1] != 0 else 0.001))))
        avg_vol = df['Volume'].iloc[-6:-1].mean()
        rvol = df['Volume'].iloc[-1] / avg_vol if avg_vol > 0 else 1.0
        return {"price": curr_p, "change": change, "rsi": rsi, "rvol": rvol}
    except: return None

# ==========================================
# 💾 DATA STORAGE (SESSION STATE)
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'custom_watchlist' not in st.session_state:
    st.session_state.custom_watchlist = ["SIRI", "MTC", "GPSC", "HANA", "WHA"]

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏹 Commander (ติดตามหุ้น)", "📓 บันทึกการรบ (Simplified Ledger)", "🐷 Anti-Pig (บัญชีขายหมู)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 ศูนย์บัญชาการ: สแกนจังหวะช้อน")
    c_add1, c_add2 = st.columns([3, 1])
    with c_add1:
        new_sym = st.text_input("➕ เพิ่มหุ้นเข้าเรดาร์ (พิมพ์แล้วกด Enter):").upper()
    with c_add2:
        if st.button("บันทึกเข้าลิสต์") and new_sym:
            if new_sym not in st.session_state.custom_watchlist:
                st.session_state.custom_watchlist.append(new_sym)
                st.rerun()

    selected_stocks = st.multiselect("ส่องกล้องขุนพลหลัก:", st.session_state.custom_watchlist, default=st.session_state.custom_watchlist[:3])
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
                    if data['rvol'] > 1.5: st.warning("🐳 วาฬบุกตลาดแดง!")
                else: st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: SIMPLIFIED LEDGER (NEW) ---
with tab2:
    st.title("📓 สมุดบันทึกการรบ (Professional Ledger)")
    
    with st.expander("➕ ลงบันทึกไม้ใหม่ (ซื้อ/ขาย)", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            l_date = st.date_input("วันที่", datetime.now())
            l_symbol = st.text_input("ชื่อหุ้น", value="SIRI").upper()
            l_broker = st.selectbox("เทรดผ่านแอป:", ["Streaming", "Dime (Standard)", "Dime (Free Tier)"])
        with f_col2:
            l_buy_qty = st.number_input("จำนวนหุ้นที่ซื้อ (Qty)", value=1000, step=100, key="buy_q")
            l_buy_price = st.number_input("ราคาซื้อ (Price)", value=1.000, format="%.3f", key="buy_p")
        with f_col3:
            l_sell_qty = st.number_input("จำนวนหุ้นที่ขาย (Qty)", value=1000, step=100, key="sell_q")
            l_sell_price = st.number_input("ราคาขาย (Price)", value=1.100, format="%.3f", key="sell_p")
        
        # สูตรคำนวณเป๊ะๆ
        rate = FEE_STREAMING if l_broker == "Streaming" else (FEE_DIME_STD if l_broker == "Dime (Standard)" else FEE_DIME_FREE)
        
        total_buy = l_buy_qty * l_buy_price
        total_sell = l_sell_qty * l_sell_price
        
        fee_in = total_buy * rate
        fee_out = total_sell * rate
        
        # รับสุทธิ (คือเงินที่จะเข้ากระเป๋าจริงหลังหักค่าธรรมเนียม)
        # คำนวณกำไรโดยเทียบ "ทุนทั้งหมดรวมค่าธรรมเนียม" กับ "ยอดรับหลังหักค่าธรรมเนียม"
        net_profit = (total_sell - fee_out) - ((l_sell_qty * l_buy_price) + (fee_in * (l_sell_qty/l_buy_qty if l_buy_qty > 0 else 1)))
        
        st.markdown("---")
        res1, res2, res3 = st.columns(3)
        res1.write(f"💼 จ่ายรวม (รวมค่าต๋ง): **{total_buy + fee_in:,.2f}** บ.")
        res2.write(f"💵 รับสุทธิ (หลังหักค่าต๋ง): **{(total_sell - fee_out):,.2f}** บ.")
        res3.subheader(f"กำไรจริง: {net_profit:,.2f} บ.")
        
        if st.button("💾 บันทึกกำไรไม้แรก"):
            st.session_state.trade_history.append({
                "date": l_date.strftime("%d/%m/%Y"),
                "sym": l_symbol,
                "broker": l_broker,
                "b_qty": l_buy_qty,
                "b_p": l_buy_price,
                "s_qty": l_sell_qty,
                "s_p": l_sell_price,
                "profit": net_profit
            })
            st.rerun()

    if st.session_state.trade_history:
        st.markdown("---")
        st.subheader("📋 สรุปผลงานวันนี้ (รายรายการ)")
        
        # สรุปกำไรสุทธิรวมที่ Sidebar
        total_sum = sum(item.get('profit', 0) for item in st.session_state.trade_history)
        st.sidebar.metric("🏆 กำไรสะสมสุทธิ", f"{total_sum:,.2f} บ.")
        st.sidebar.progress(min(max(total_sum / TARGET_TOTAL, 0.0), 1.0))
        st.sidebar.write(f"🎯 เป้าหมาย {TARGET_TOTAL} บ.")

        # แสดงรายการการรบ
        for idx, row in enumerate(st.session_state.trade_history):
            with st.container(border=True):
                r_col1, r_col2, r_col3, r_col4 = st.columns([1, 2, 1, 0.5])
                r_col1.write(f"📅 {row.get('date', '-')}\n**{row.get('sym', '-')}**")
                # แสดงรายละเอียดตามที่พี่โบ้ต้องการ
                r_col2.write(f"🔵 ซื้อ: {row.get('b_qty', 0):,} @ {row.get('b_p', 0.0):.3f}\n🔴 ขาย: {row.get('s_qty', 0):,} @ {row.get('s_p', 0.0):.3f}")
                r_col3.subheader(f"{row.get('profit', 0):,.2f}")
                r_col3.caption(f"App: {row.get('broker', '-')}")
                if r_col4.button("🗑️", key=f"del_{idx}"):
                    st.session_state.trade_history.pop(idx)
                    st.rerun()

# --- TAB 3: ANTI-PIG ---
with tab3:
    st.title("🐷 บัญชีขายหมู (Anti-Pig Analysis)")
    if st.session_state.trade_history:
        p_data = []
        for item in st.session_state.trade_history:
            live = get_live_data(item['sym'])
            if live:
                diff = live['price'] - item['s_p']
                p_data.append({
                    "หุ้น": item['sym'], "ขายที่": item['s_p'], "ราคาตอนนี้": live['price'],
                    "ส่วนต่าง": f"{diff:.3f}", "กำไรที่พลาดไป (บ.)": diff * item['s_qty'] if diff > 0 else 0,
                    "สถานะ": "🐷 ขายหมู" if diff > 0 else "✅ ขายคม"
                })
        st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)
    else: st.info("ยังไม่มีประวัติการขายใน Ledger")

st.markdown("---")
st.caption("v6.7 Precision Ledger — 'บันทึกละเอียด คำนวณเป๊ะ จ่ายค่าแอปฟรีทุกเดือน'")
