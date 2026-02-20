# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import json
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v7.8 Persistent Edition)
# ==========================================
st.set_page_config(page_title="GeminiBo v7.8: Persistent", layout="wide", page_icon="🛡️")

# ค่าธรรมเนียม (รวม VAT 7%)
FEES = {
    "Streaming": 0.00168,
    "Dime (Standard)": 0.001605,
    "Dime (Free Tier)": 0.0
}
TARGET_TOTAL = 990.0

def get_market_data(symbol):
    try:
        symbol = symbol.strip().upper()
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty: return None
        curr_p = df['Close'].iloc[-1]
        prev_p = df['Close'].iloc[-2]
        change = ((curr_p - prev_p) / prev_p) * 100
        # Simple RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] if loss.iloc[-1] != 0 else 0.001))))
        return {"price": curr_p, "change": change, "rsi": rsi}
    except: return None

# ==========================================
# 💾 DATA STORAGE & PERSISTENCE
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'custom_watchlist' not in st.session_state:
    st.session_state.custom_watchlist = ["HANA", "SIRI", "MTC", "ROJNA"]

# ฟังก์ชันสำหรับ Save/Load ข้อมูล ป้องกันการหายเมื่อ Refresh
def export_data():
    data = {
        "history": st.session_state.trade_history,
        "watchlist": st.session_state.custom_watchlist
    }
    return json.dumps(data)

def import_data(uploaded_file):
    if uploaded_file is not None:
        data = json.load(uploaded_file)
        st.session_state.trade_history = data.get("history", [])
        st.session_state.custom_watchlist = data.get("watchlist", ["HANA", "SIRI", "MTC", "ROJNA"])
        st.success("📂 ดึงข้อมูลกลับมาเรียบร้อย!")

# ==========================================
# 📊 SIDEBAR & TOOLS
# ==========================================
st.sidebar.title("🛡️ กองบัญชาการจอมทัพ")
total_sum = sum((item.get('profit') or 0.0) for item in st.session_state.trade_history)
st.sidebar.metric("🏆 กำไรสะสมสุทธิ", f"{total_sum:,.2f} บ.")
st.sidebar.progress(min(max(total_sum / TARGET_TOTAL, 0.0), 1.0))

st.sidebar.markdown("---")
st.sidebar.subheader("💾 ป้องกันข้อมูลหาย")
st.sidebar.download_button(
    label="📥 เซฟบัญชีลงเครื่อง (Backup)",
    data=export_data(),
    file_name=f"geminibo_backup_{datetime.now().strftime('%d%m%y')}.json",
    mime="application/json"
)
uploaded_file = st.sidebar.file_uploader("📂 ดึงข้อมูลที่เซฟไว้กลับมา", type="json")
if uploaded_file:
    import_data(uploaded_file)

if st.sidebar.button("🚨 ล้างข้อมูลทั้งหมด"):
    st.session_state.trade_history = []
    st.session_state.custom_watchlist = ["HANA", "SIRI", "MTC", "ROJNA"]
    st.rerun()

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏹 Commander (เรดาร์)", "📓 Ledger (บันทึกรบ)", "🐷 Anti-Pig (ขายหมู)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 เรดาร์ติดตามขุนพล")
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        new_stk = c1.text_input("➕ เพิ่มหุ้นเข้าเรดาร์ (เช่น JMT, EA):").upper()
        if c2.button("บันทึกหุ้น") and new_stk:
            if new_stk not in st.session_state.custom_watchlist:
                st.session_state.custom_watchlist.append(new_stk)
                st.rerun()

    st.markdown("---")
    selected = st.multiselect("เลือกตัวที่จะสแกน:", st.session_state.custom_watchlist, default=st.session_state.custom_watchlist[:4])
    cols = st.columns(3)
    for i, sym in enumerate(selected):
        data = get_market_data(sym)
        with cols[i % 3]:
            with st.container(border=True):
                if data:
                    st.header(f"🛡️ {sym}")
                    st.metric("ราคา", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                    st.write(f"📡 RSI: {data['rsi']:.1f}")
                    if sym == "SIRI": st.info("💡 ทุน 1.47 ถือรันข้ามอาทิตย์")
                    elif sym == "HANA": st.success("🎯 ทุน 18.90 สวยมาก")
                else: st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: DETAILED LEDGER ---
with tab2:
    st.title("📓 สมุดบันทึกการรบแบบละเอียด")
    with st.expander("➕ ลงบันทึกไม้ใหม่ (ระบุวันซื้อ-วันขาย)", expanded=True):
        l1, l2, l3 = st.columns(3)
        with l1:
            buy_date = st.date_input("วันที่ซื้อ", datetime.now(), key="b_date")
            sell_date = st.date_input("วันที่ขาย", datetime.now(), key="s_date")
            sym = st.text_input("ชื่อหุ้น", value="HANA").upper()
        with l2:
            broker = st.selectbox("แอป:", list(FEES.keys()))
            b_q = st.number_input("จำนวนหุ้นที่ซื้อ", value=300)
            b_p = st.number_input("ราคาซื้อ", value=18.90, format="%.3f")
        with l3:
            s_q = st.number_input("จำนวนหุ้นที่ขาย", value=300)
            s_p = st.number_input("ราคาขาย", value=19.50, format="%.3f")
            
            # คำนวณเงินจริง
            rate = FEES[broker]
            buy_val, sell_val = b_q * b_p, s_q * s_p
            fee = (buy_val + sell_val) * rate
            # กำไรสุทธิคิดจากสัดส่วนที่ขายจริง
            profit = ((s_p - b_p) * s_q) - fee
            
            st.write(f"ค่าธรรมเนียมรวม: {fee:.2f} บ.")
            st.subheader(f"กำไรจริง: {profit:,.2f} บ.")
            
            if st.button("💾 บันทึกลงสมุด"):
                st.session_state.trade_history.append({
                    "b_date": buy_date.strftime("%d/%m/%y"),
                    "s_date": sell_date.strftime("%d/%m/%y"),
                    "sym": sym, "broker": broker,
                    "b_q": b_q, "b_p": b_p,
                    "s_q": s_q, "s_p": s_p,
                    "profit": profit
                })
                st.rerun()

    if st.session_state.trade_history:
        st.markdown("---")
        for idx, row in enumerate(st.session_state.trade_history):
            with st.container(border=True):
                r1, r2, r3, r4 = st.columns([1.2, 2, 1, 0.5])
                r1.write(f"📅 {row.get('b_date')} → {row.get('s_date')}\n**{row.get('sym')}**")
                r2.write(f"🔵 ซื้อ: {row.get('b_q',0):,} @ {row.get('b_p',0.0):.3f}\n🔴 ขาย: {row.get('s_q',0):,} @ {row.get('s_p',0.0):.3f}")
                r3.subheader(f"{row.get('profit', 0.0):,.2f}")
                r3.caption(f"แอป: {row.get('broker')}")
                if r4.button("🗑️", key=f"del_{idx}"):
                    st.session_state.trade_history.pop(idx)
                    st.rerun()

# --- TAB 3: ANTI-PIG ---
with tab3:
    st.title("🐷 บัญชีวิเคราะห์การขายหมู")
    if st.session_state.trade_history:
        p_data = []
        for item in st.session_state.trade_history:
            try:
                live = yf.Ticker(f"{item['sym']}.BK").history(period="1d")['Close'].iloc[-1]
                diff = live - item['s_p']
                p_data.append({
                    "หุ้น": item['sym'], "วันที่ขาย": item['s_date'], "ราคาที่ขาย": item['s_p'],
                    "ราคาตอนนี้": live, "กำไรที่พลาด": diff * item['s_q'] if diff > 0 else 0
                })
            except: continue
        st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)
    else: st.info("ยังไม่มีข้อมูลการขาย")
