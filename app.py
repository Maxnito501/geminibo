# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v7.7 Fix Edition)
# ==========================================
st.set_page_config(page_title="GeminiBo v7.7: Iron-Clad", layout="wide", page_icon="🛡️")

# ค่าธรรมเนียมมาตรฐาน
FEE_STREAMING = 0.00168 
TARGET_TOTAL = 990.0

def get_market_analysis(symbol):
    """ วิเคราะห์ข้อมูลสดเพื่อแยกจริงหรือหลอก """
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
        
        status, color = "⏳ รอสัญญาณ", "gray"
        if curr_p > df_now['Low'].iloc[-15:].min() * 1.002:
            if rvol_active > 1.3: status, color = "✅ รีบาวด์จริง", "green"
            elif rvol_active < 0.8: status, color = "⚠️ รีบาวด์หลอก", "orange"
            else: status, color = "⚖️ เด้งตามตลาด", "blue"
        elif curr_p < df_now['Low'].iloc[-30:].min() * 1.005:
            status, color = "📉 ยังไหลลง", "red"

        return {"price": curr_p, "change": change, "rsi": rsi_1m, "rvol": rvol_active, "status": status, "color": color, "low": df_now['Low'].min()}
    except: return None

# ==========================================
# 💾 DATA STORAGE (FIXED PERSISTENCE)
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'custom_watchlist' not in st.session_state:
    # เพิ่ม ROJNA เข้าลิสต์ตามที่พี่โบ้สั่งครับ
    st.session_state.custom_watchlist = ["HANA", "SIRI", "MTC", "ROJNA", "WHA", "GPSC"]

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏹 Commander (เรดาร์ช้อน)", "📓 Ledger (บันทึกรบ)", "🐷 Anti-Pig (บัญชีขายหมู)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 ศูนย์บัญชาการ (Fixed Version)")
    
    # ส่วนเพิ่มหุ้น (ปรับปรุงให้ทำงานได้จริง)
    with st.container(border=True):
        c_add1, c_add2 = st.columns([3, 1])
        with c_add1:
            stock_input = st.text_input("➕ เพิ่มหุ้นเข้าเรดาร์ (เช่น JMT, EA):", key="new_stock_input").upper()
        with c_add2:
            st.write(" ") # เว้นระยะ
            if st.button("บันทึกหุ้นใหม่") and stock_input:
                if stock_input not in st.session_state.custom_watchlist:
                    st.session_state.custom_watchlist.append(stock_input)
                    st.success(f"เพิ่ม {stock_input} แล้ว!")
                    st.rerun()

    st.markdown("---")
    selected_stocks = st.multiselect("ส่องกล้องขุนพลที่สนใจ:", st.session_state.custom_watchlist, default=st.session_state.custom_watchlist[:4])
    
    cols = st.columns(3)
    for i, sym in enumerate(selected_stocks):
        data = get_market_analysis(sym)
        with cols[i % 3]:
            with st.container(border=True):
                if data:
                    st.header(f"🛡️ {sym}")
                    st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                    st.markdown(f"### สถานะ: :{data['color']}[{data['status']}]")
                    
                    if sym == "SIRI":
                        st.info("💡 ทุน 1.47 ปลอดภัย ถือรันกำไรข้ามอาทิตย์")
                    elif sym == "HANA":
                        st.success("🎯 ทุน 18.90 สวยมาก ถือลุ้นเด้ง")
                    elif sym == "MTC":
                        st.warning("📍 แนวรับ 37.50 คือจุดช้อนไม้ 2")
                    
                    st.write(f"📊 RVOL (15m): {data['rvol']:.2f} | 📡 RSI: {data['rsi']:.1f}")
                else: st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: LEDGER (FIXED) ---
with tab2:
    st.title("📓 บันทึกกำไรรายไม้")
    with st.expander("➕ ลงบันทึกไม้ใหม่ (ซื้อ/ขาย)", expanded=True):
        l1, l2, l3 = st.columns(3)
        with l1:
            l_sym = st.text_input("หุ้น", value="SIRI").upper()
            l_broker = st.selectbox("แอป:", ["Streaming", "Dime (Std)", "Dime (Free)"])
        with l2:
            l_b_q = st.number_input("จำนวนซื้อ", value=1000)
            l_b_p = st.number_input("ราคาซื้อ", value=1.000, format="%.3f")
        with l3:
            l_s_q = st.number_input("จำนวนขาย", value=1000)
            l_s_p = st.number_input("ราคาขาย", value=1.100, format="%.3f")
            if st.button("💾 บันทึกลงสมุด"):
                rate = 0.00168 if l_broker == "Streaming" else (0.001605 if "Std" in l_broker else 0.0)
                fee = ((l_b_q * l_b_p) + (l_s_q * l_s_p)) * rate
                net_p = ((l_s_p - l_b_p) * l_s_q) - fee
                st.session_state.trade_history.append({
                    "date": datetime.now().strftime("%d/%m/%Y"), "sym": l_sym,
                    "b_qty": l_b_q, "b_p": l_b_p, "s_qty": l_s_q, "s_p": l_s_p, "profit": net_p
                })
                st.rerun()

    if st.session_state.trade_history:
        for idx, row in enumerate(st.session_state.trade_history):
            with st.container(border=True):
                r1, r2, r3, r4 = st.columns([1, 2, 1, 0.5])
                r1.write(f"📅 {row.get('date')}\n**{row.get('sym')}**")
                r2.write(f"🔵 {row.get('b_qty', 0):,} @ {row.get('b_p', 0.0):.3f}\n🔴 {row.get('s_qty', 0):,} @ {row.get('s_p', 0.0):.3f}")
                r3.subheader(f"{row.get('profit', 0.0):,.2f}")
                if r4.button("🗑️", key=f"del_{idx}"):
                    st.session_state.trade_history.pop(idx)
                    st.rerun()

# --- TAB 3: ANTI-PIG ---
with tab3:
    st.title("🐷 บัญชีขายหมู")
    if st.session_state.trade_history:
        pig_data = []
        for item in st.session_state.trade_history:
            try:
                live_p = yf.Ticker(f"{item['sym']}.BK").history(period="1d")['Close'].iloc[-1]
                diff = live_p - item['s_p']
                pig_data.append({"หุ้น": item['sym'], "ขายที่": item['s_p'], "ตอนนี้": live_p, "พลาดกำไร": diff * item['s_qty'] if diff > 0 else 0})
            except: continue
        st.dataframe(pd.DataFrame(pig_list := pig_data), use_container_width=True, hide_index=True)

# Sidebar
total_sum = sum((item.get('profit') or 0.0) for item in st.session_state.trade_history)
st.sidebar.metric("🏆 กำไรสะสมสุทธิ", f"{total_sum:,.2f} บ.")
st.sidebar.progress(min(max(total_sum / TARGET_TOTAL, 0.0), 1.0))
st.sidebar.info("HANA 300 หุ้น @ 18.90")
if st.sidebar.button("🚨 ซ่อม Error ล้างข้อมูล"):
    st.session_state.trade_history = []
    st.session_state.custom_watchlist = ["HANA", "SIRI", "MTC", "ROJNA"]
    st.rerun()
