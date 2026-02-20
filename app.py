# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v6.4 Ultimate)
# ==========================================
st.set_page_config(page_title="GeminiBo v6.4: Ultimate", layout="wide", page_icon="🏹")

FEE_STREAMING = 0.00168 
FEE_DIME_STD = 0.001605
GEMINI_PRO_COST = 790.0
SETSMART_MONTHLY = 200.0 
TARGET_TOTAL = GEMINI_PRO_COST + SETSMART_MONTHLY

def get_live_data(symbol):
    """ ดึงข้อมูลสดเพื่อวิเคราะห์ Whale Flow และ RSI """
    try:
        symbol = symbol.strip().upper()
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < 10: return None
        
        curr_p = df['Close'].iloc[-1]
        prev_p = df['Close'].iloc[-2]
        change = ((curr_p - prev_p) / prev_p) * 100
        
        # RSI 14
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # RVOL
        avg_vol = df['Volume'].iloc[-6:-1].mean()
        rvol = df['Volume'].iloc[-1] / avg_vol if avg_vol > 0 else 1.0
        
        return {"price": curr_p, "change": change, "rsi": rsi, "rvol": rvol}
    except: return None

# ==========================================
# 💾 DATA STORAGE (KeyError Protected)
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'custom_watchlist' not in st.session_state:
    st.session_state.custom_watchlist = ["SIRI", "MTC", "GPSC", "HANA", "WHA"]

# ==========================================
# 📊 SIDEBAR: PORTFOLIO HEALTH
# ==========================================
st.sidebar.title("🏹 กองบัญชาการจอมทัพ")
total_p = sum(item.get('กำไรสุทธิ', 0.0) for item in st.session_state.trade_history)
st.sidebar.metric("🏆 กำไรสะสมสุทธิ", f"{total_p:,.2f} บ.")
st.sidebar.progress(min(max(total_p / TARGET_TOTAL, 0.0), 1.0))
st.sidebar.write(f"🎯 เป้าหมายแอปฟรี: {TARGET_TOTAL} บ.")

if st.sidebar.button("🚨 ล้างข้อมูลทั้งหมด"):
    st.session_state.trade_history = []
    st.rerun()

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏹 Commander (เฝ้าช้อน)", "📓 Ledger (บันทึกรบ)", "🐷 Anti-Pig (บัญชีขายหมู)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 เรดาร์ตรวจจับ 'วาฬสวนตลาด'")
    
    # ส่วนเพิ่มหุ้นที่น่าช้อน
    c_add1, c_add2 = st.columns([3, 1])
    with c_add1:
        new_sym = st.text_input("➕ เพิ่มหุ้นที่น่าช้อน (เช่น HANA, JMT, EA):").upper()
    with c_add2:
        if st.button("บันทึกเข้าเรดาร์") and new_sym:
            if new_sym not in st.session_state.custom_watchlist:
                st.session_state.custom_watchlist.append(new_sym)
                st.toast(f"เพิ่ม {new_sym} เรียบร้อย!")

    st.markdown("---")
    selected_stocks = st.multiselect("ส่องกล้องตัวที่น่าสนใจ:", st.session_state.custom_watchlist, default=st.session_state.custom_watchlist[:4])
    
    cols = st.columns(3)
    for i, sym in enumerate(selected_stocks):
        data = get_live_data(sym)
        with cols[i % 3]:
            with st.container(border=True):
                if data:
                    st.header(f"🛡️ {sym}")
                    st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                    
                    # ช้อน Advisor
                    if data['rsi'] < 35:
                        st.success("✅ **BUY ZONE!** (ช้อนจังหวะ Panic)")
                    elif data['rvol'] > 1.5 and data['change'] < 0:
                        st.warning("🐳 **Whale Accumulating!** (วาฬแอบเก็บของสวนตลาด)")
                    
                    if sym == "HANA" and data['rvol'] > 1.5:
                        st.info("💡 **HANA Note:** วอลลุ่มเข้าผิดปกติแม้ตลาดแดง ระวังตกรถตอนเด้ง")

                    st.write(f"📡 RSI: {data['rsi']:.1f} | 🌊 RVOL: {data['rvol']:.2f}")
                else: st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: MASTER LEDGER ---
with tab2:
    st.title("📓 บันทึกการปิดรอบ")
    with st.expander("➕ ลงบันทึกรายการเทรดใหม่", expanded=True):
        l1, l2, l3 = st.columns(3)
        with l1:
            in_sym = st.text_input("หุ้น", value="SIRI").upper()
            broker = st.radio("แอป:", ["Streaming", "Dime (Std)", "Dime (Free)"], horizontal=True)
            in_p = st.number_input("ราคาซื้อ (ต้นทุน)", value=1.000, format="%.3f")
        with l2:
            out_q = st.number_input("จำนวนหุ้น", value=2000, step=100)
            out_p = st.number_input("ราคาขาย", value=1.630, format="%.3f")
        with l3:
            fee_r = FEE_STREAMING if broker == "Streaming" else (0.001605 if "Std" in broker else 0.0)
            net_p = ((out_p - in_p) * out_q) - ((out_p + in_p) * out_q * fee_r)
            st.subheader(f"กำไรสุทธิ: {net_p:,.2f} บ.")
            note = st.text_input("หมายเหตุ", value="ปิดไม้แรก")
            if st.button("💾 บันทึกลงสมุด"):
                st.session_state.trade_history.append({
                    "วันที่": datetime.now().strftime("%d/%m/%Y"), "หุ้น": in_sym,
                    "ราคาซื้อ": in_p, "ราคาขาย": out_p, "จำนวน": out_q,
                    "กำไรสุทธิ": net_p, "แอป": broker, "หมายเหตุ": note
                })
                st.rerun()

    if st.session_state.trade_history:
        for idx, item in enumerate(st.session_state.trade_history):
            r1, r2, r3, r4 = st.columns([1, 2, 2, 0.5])
            r1.write(f"**{item.get('หุ้น', '-')}**")
            r2.write(f"{item.get('จำนวน', 0):,} หุ้น | กำไร: {item.get('กำไรสุทธิ', 0):,.2f}")
            r3.write(f"<small>{item.get('หมายเหตุ', '-')}</small>", unsafe_allow_html=True)
            if r4.button("🗑️", key=f"del_{idx}"):
                st.session_state.trade_history.pop(idx)
                st.rerun()

# --- TAB 3: ANTI-PIG ---
with tab3:
    st.title("🐷 บัญชีขายหมู (Anti-Pig Analysis)")
    if st.session_state.trade_history:
        p_data = []
        for item in st.session_state.trade_history:
            live = get_live_data(item['หุ้น'])
            if live:
                diff = live['price'] - item['ราคาขาย']
                missed = diff * item['จำนวน'] if diff > 0 else 0
                p_data.append({
                    "หุ้น": item['หุ้น'], "ขายที่": item['ราคาขาย'], "ราคาตอนนี้": live['price'],
                    "ส่วนต่าง": f"{diff:.3f}", "กำไรที่พลาด (บ.)": missed,
                    "สถานะ": "🐷 ขายหมู" if diff > 0 else "✅ ขายคม"
                })
        st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)
    else: st.info("ยังไม่มีประวัติการขายใน Ledger")

st.markdown("---")
st.caption("v6.4 Ultimate — 'ช้อนในวันที่คนกลัว รันกำไรในวันที่คนกล้า'")
