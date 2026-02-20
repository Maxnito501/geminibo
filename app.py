# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v7.0 Iron-Clad Edition)
# ==========================================
st.set_page_config(page_title="GeminiBo v7.0: Iron-Clad", layout="wide", page_icon="🛡️")

# ค่าธรรมเนียมมาตรฐาน (รวม VAT 7% แล้ว)
FEE_STREAMING = 0.00168 
FEE_DIME_STD = 0.001605
FEE_DIME_FREE = 0.0
TARGET_TOTAL = 990.0

def get_rebound_analysis(symbol):
    """ วิเคราะห์จังหวะช้อน: รีบาวด์จริง หรือ หลอก """
    try:
        symbol = symbol.strip().upper()
        ticker = yf.Ticker(f"{symbol}.BK")
        df_now = ticker.history(period="1d", interval="1m")
        df_daily = ticker.history(period="1mo", interval="1d")
        
        if df_now.empty or df_daily.empty: return None
        
        curr_p = df_now['Close'].iloc[-1]
        prev_p = df_daily['Close'].iloc[-2]
        change = ((curr_p - prev_p) / prev_p) * 100
        
        # RSI 1m
        delta = df_now['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi_1m = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] if loss.iloc[-1] != 0 else 0.001))))
        
        # RVOL (15m Active)
        vol_recent = df_now['Volume'].iloc[-15:].sum()
        avg_vol_5d = df_daily['Volume'].iloc[-6:-1].mean() / 26
        rvol_active = vol_recent / avg_vol_5d if avg_vol_5d > 0 else 1.0
        
        status, color, advice = "⏳ รอสัญญาณ", "gray", "รอดูเชิง"
        if curr_p > df_now['Low'].iloc[-15:].min() * 1.002:
            if rvol_active > 1.3:
                status, color, advice = "✅ รีบาวด์จริง", "green", "จังหวะช้อน! วาฬเข้าสวน"
            elif rvol_active < 0.8:
                status, color, advice = "⚠️ รีบาวด์หลอก", "orange", "ระวัง Bull Trap! ทับมือไว้"
            else:
                status, color, advice = "⚖️ เด้งตามตลาด", "blue", "แบ่งไม้ช้อนจิ๋วๆ"
        elif curr_p < df_now['Low'].iloc[-30:].min() * 1.005:
            status, color, advice = "📉 ยังไหลลง", "red", "อย่าเพิ่งรับ! มีดกำลังบิน"

        return {"price": curr_p, "change": change, "rsi": rsi_1m, "rvol": rvol_active, "status": status, "color": color, "advice": advice}
    except: return None

# ==========================================
# 💾 DATA STORAGE (Iron-Clad Protection)
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'custom_watchlist' not in st.session_state:
    st.session_state.custom_watchlist = ["SIRI", "MTC", "GPSC", "HANA", "WHA", "JMT", "BTS", "EA"]

# ==========================================
# 📊 SIDEBAR: GOAL TRACKER
# ==========================================
st.sidebar.title("🏹 ภารกิจปั้นแสนแรก")
# ป้องกัน TypeError ในการคำนวณผลรวม
total_sum = sum((item.get('profit') or 0.0) for item in st.session_state.trade_history)
st.sidebar.metric("🏆 กำไรสะสมสุทธิ", f"{total_sum:,.2f} บ.")
st.sidebar.progress(min(max(total_sum / TARGET_TOTAL, 0.0), 1.0))

if st.sidebar.button("🚨 ล้างข้อมูลและซ่อม Error"):
    st.session_state.trade_history = []
    st.rerun()

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏹 Commander (เรดาร์ช้อน)", "📓 Ledger (บันทึกรบ)", "🐷 Anti-Pig (บัญชีขายหมู)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 ระบบตรวจจับ 'รีบาวด์จริง หรือ หลอก'")
    c_add1, c_add2 = st.columns([3, 1])
    with c_add1:
        new_sym = st.text_input("➕ เพิ่มหุ้นน่าช้อนเพิ่ม (เช่น HANA, JMT):").upper()
    with c_add2:
        if st.button("บันทึก") and new_sym:
            if new_sym not in st.session_state.custom_watchlist:
                st.session_state.custom_watchlist.append(new_sym)
                st.rerun()

    st.markdown("---")
    selected_stocks = st.multiselect("ส่องกล้องตัวที่น่าสนใจ:", st.session_state.custom_watchlist, default=st.session_state.custom_watchlist[:4])
    cols = st.columns(3)
    for i, sym in enumerate(selected_stocks):
        data = get_rebound_analysis(sym)
        with cols[i % 3]:
            with st.container(border=True):
                if data:
                    st.header(f"🛡️ {sym}")
                    st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                    st.markdown(f"### สถานะ: :{data['color']}[{data['status']}]")
                    st.write(f"📢 **คำแนะนำ:** {data['advice']}")
                    st.write(f"📊 RVOL (15m): {data['rvol']:.2f} | 📡 RSI (1m): {data['rsi']:.1f}")
                    if data['color'] == "green": st.success("🎯 วาฬเข้าสวน! พิจารณาช้อนไม้แรก")
                else: st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: DETAILED LEDGER (FIXED ERROR) ---
with tab2:
    st.title("📓 สมุดบันทึกกำไรจริง")
    with st.expander("➕ ลงบันทึกไม้ใหม่ (ซื้อ/ขาย)", expanded=True):
        l1, l2, l3 = st.columns(3)
        with l1:
            l_date = st.date_input("วันที่", datetime.now())
            l_sym = st.text_input("หุ้น", value="SIRI").upper()
            l_broker = st.selectbox("แอปที่ใช้:", ["Streaming", "Dime (Standard)", "Dime (Free Tier)"])
        with l2:
            l_b_q = st.number_input("จำนวนซื้อ (Qty)", value=1000, step=100)
            l_b_p = st.number_input("ราคาซื้อ (Price)", value=1.000, format="%.3f")
        with l3:
            l_s_q = st.number_input("จำนวนขาย (Qty)", value=1000, step=100)
            l_s_p = st.number_input("ราคาขาย (Price)", value=1.100, format="%.3f")
        
        if st.button("💾 บันทึกลงสมุด"):
            rate = FEE_STREAMING if l_broker == "Streaming" else (FEE_DIME_STD if "Std" in l_broker else 0.0)
            fee = ((l_b_q * l_b_p) + (l_s_q * l_s_p)) * rate
            net_p = ((l_s_p - l_b_p) * l_s_q) - fee
            st.session_state.trade_history.append({
                "date": l_date.strftime("%d/%m/%Y"), "sym": l_sym, "broker": l_broker,
                "b_qty": l_b_q, "b_p": l_b_p, "s_qty": l_s_q, "s_p": l_s_p, "profit": net_p
            })
            st.rerun()

    if st.session_state.trade_history:
        st.markdown("---")
        for idx, row in enumerate(st.session_state.trade_history):
            with st.container(border=True):
                r1, r2, r3, r4 = st.columns([1, 2, 1, 0.5])
                # --- จุดสำคัญ: ป้องกัน KeyError และ TypeError หายขาด ---
                b_q = row.get('b_qty') or 0
                b_p = row.get('b_p') or 0.0
                s_q = row.get('s_qty') or 0
                s_p = row.get('s_p') or 0.0
                profit = row.get('profit') or 0.0
                
                r1.write(f"📅 {row.get('date', '-')}\n**{row.get('sym', 'Unknown')}**")
                r2.write(f"🔵 {b_q:,} @ {b_p:.3f}\n🔴 {s_q:,} @ {s_p:.3f}")
                r3.subheader(f"{profit:,.2f}")
                r3.caption(f"App: {row.get('broker', '-')}")
                if r4.button("🗑️", key=f"del_{idx}"):
                    st.session_state.trade_history.pop(idx)
                    st.rerun()

# --- TAB 3: ANTI-PIG ---
with tab3:
    st.title("🐷 บัญชีวิเคราะห์การขายหมู")
    if st.session_state.trade_history:
        pig_list = []
        for item in st.session_state.trade_history:
            try:
                live = yf.Ticker(f"{item['sym']}.BK").history(period="1d")['Close'].iloc[-1]
                diff = live - (item.get('s_p') or 0.0)
                pig_list.append({
                    "หุ้น": item['sym'], "ขายที่": item.get('s_p') or 0.0, "ราคาตอนนี้": live,
                    "ส่วนต่าง": f"{diff:.3f}", "กำไรที่พลาด": diff * (item.get('s_qty') or 0) if diff > 0 else 0
                })
            except: continue
        st.dataframe(pd.DataFrame(pig_list), use_container_width=True, hide_index=True)
    else: st.info("ยังไม่มีประวัติการขาย")

st.markdown("---")
st.caption("v7.0 Iron-Clad — 'จอมทัพต้องนิ่งพอที่จะไม่รับมีด และเป๊ะพอที่จะไม่พลาดกำไร'")
