# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v7.4 Strategy Matrix)
# ==========================================
st.set_page_config(page_title="GeminiBo v7.4: Strategy Matrix", layout="wide", page_icon="🛡️")

FEE_STREAMING = 0.00168 
TARGET_TOTAL = 990.0

def get_tick_size(price):
    if price < 2.0: return 0.01
    if price < 5.0: return 0.02
    if price < 10.0: return 0.05
    if price < 25.0: return 0.10
    if price < 100.0: return 0.25
    return 1.00

def get_market_analysis(symbol):
    """ วิเคราะห์ข้อมูลเชิงลึกรายตัวสำหรับแผน 2 กรณี """
    try:
        symbol = symbol.strip().upper()
        ticker = yf.Ticker(f"{symbol}.BK")
        df_now = ticker.history(period="1d", interval="1m")
        df_daily = ticker.history(period="1mo", interval="1d")
        
        if df_now.empty or df_daily.empty: return None
        
        curr_p = df_now['Close'].iloc[-1]
        low_today = df_now['Low'].min()
        high_today = df_now['High'].max()
        
        # RSI 1m
        delta = df_now['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi_1m = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] if loss.iloc[-1] != 0 else 0.001))))
        
        # RVOL (15m Active)
        vol_recent = df_now['Volume'].iloc[-15:].sum()
        avg_vol_5d = df_daily['Volume'].iloc[-6:-1].mean() / 26
        rvol_active = vol_recent / avg_vol_5d if avg_vol_5d > 0 else 1.0
        
        tick = get_tick_size(curr_p)
        
        return {
            "price": curr_p, "rsi": rsi_1m, "rvol": rvol_active, 
            "low": low_today, "high": high_today, "tick": tick
        }
    except: return None

# ==========================================
# 💾 DATA STORAGE
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'custom_watchlist' not in st.session_state:
    st.session_state.custom_watchlist = ["HANA", "SIRI", "MTC", "GPSC", "WHA"]

# ==========================================
# 📊 SIDEBAR: BATTLE STATUS
# ==========================================
st.sidebar.title("🛡️ กองบัญชาการจอมทัพ")
total_sum = sum((item.get('profit') or 0.0) for item in st.session_state.trade_history)
st.sidebar.metric("🏆 กำไรสะสมสุทธิ", f"{total_sum:,.2f} บ.")
st.sidebar.progress(min(max(total_sum / TARGET_TOTAL, 0.0), 1.0))

if st.sidebar.button("🚨 ซ่อม Error และล้างข้อมูล"):
    st.session_state.trade_history = []
    st.rerun()

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏹 Commander (แผนรบรายตัว)", "📓 Ledger (บันทึกรบ)", "🐷 Anti-Pig (บัญชีขายหมู)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 ยุทธวิธี 'มีของ' vs 'ไม่มีของ' (Strategy Matrix)")
    st.info("💡 ในสภาวะ Panic Sell การตัดสินใจที่เร็วและแม่นยำคือหัวใจของการรักษาพอร์ต")
    
    selected_stocks = st.multiselect("ส่องกล้องขุนพลหลัก:", st.session_state.custom_watchlist, default=st.session_state.custom_watchlist[:3])
    
    for sym in selected_stocks:
        data = get_market_analysis(sym)
        with st.container(border=True):
            if data:
                c_title, c_metrics, c_plan = st.columns([1, 1, 3])
                
                with c_title:
                    st.header(f"🛡️ {sym}")
                    st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}")
                    st.write(f"📊 RVOL: {data['rvol']:.2f}")
                    st.write(f"📡 RSI (1m): {data['rsi']:.1f}")

                with c_metrics:
                    st.write("📍 **ข้อมูลหน้างาน**")
                    st.write(f"Low วันนี้: **{data['low']:.2f}**")
                    st.write(f"High วันนี้: **{data['high']:.2f}**")
                    st.write(f"Tick Size: **{data['tick']:.2f}**")

                with c_plan:
                    p1, p2 = st.columns(2)
                    with p1:
                        st.subheader("✅ กรณีมีของ (Hold/Exit)")
                        if data['price'] <= data['low']:
                            st.error(f"🚨 **Stop Loss:** หลุด {data['low']:.2f} ถอยด่วน!")
                        elif data['rsi'] > 80:
                            st.warning("💰 **Take Profit:** แบ่งขายทำกำไร")
                        else:
                            st.info("⚖️ **Hold:** ถือลุ้นเด้งตามตลาด")
                    
                    with p2:
                        st.subheader("🆕 กรณีไม่มีของ (Entry)")
                        buy_p = data['low'] if data['price'] > data['low'] else data['price'] - data['tick']
                        if data['rsi'] < 35 and data['rvol'] > 1.2:
                            st.success(f"🎯 **Buy Now:** ช้อนได้เปรียบที่ {buy_p:.2f}")
                        elif data['rvol'] < 0.6:
                            st.error("🚫 **Wait:** วอลลุ่มหาย ห้ามรับมีด")
                        else:
                            st.warning(f"🕒 **Limit Buy:** ดักที่ {data['low'] - data['tick']:.2f}")
            else:
                st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: DETAILED LEDGER ---
with tab2:
    st.title("📓 สมุดบันทึกการรบ")
    with st.expander("➕ ลงบันทึกรายการเทรดใหม่"):
        l1, l2, l3 = st.columns(3)
        with l1:
            l_date = st.date_input("วันที่", datetime.now())
            l_sym = st.text_input("หุ้น", value="SIRI").upper()
        with l2:
            l_b_q = st.number_input("จำนวนซื้อ", value=1000)
            l_b_p = st.number_input("ราคาซื้อ", value=1.00, format="%.3f")
        with l3:
            l_s_q = st.number_input("จำนวนขาย", value=1000)
            l_s_p = st.number_input("ราคาขาย", value=1.00, format="%.3f")
            if st.button("💾 บันทึกลงสมุด"):
                fee = ((l_b_q * l_b_p) + (l_s_q * l_s_p)) * FEE_STREAMING
                net_p = ((l_s_p - l_b_p) * l_s_q) - fee if l_s_q > 0 else 0.0
                st.session_state.trade_history.append({
                    "date": l_date.strftime("%d/%m/%Y"), "sym": l_sym,
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
    # ... (โค้ดดึงราคาปัจจุบันเหมือนเดิม)
