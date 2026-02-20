# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v6.8 Rebound Scanner)
# ==========================================
st.set_page_config(page_title="GeminiBo v6.8: Rebound Scanner", layout="wide", page_icon="📈")

# ค่าธรรมเนียม & เป้าหมาย
FEE_STREAMING = 0.00168 
TARGET_TOTAL = 990.0

def get_rebound_analysis(symbol):
    """ วิเคราะห์ว่ารีบาวด์รอบนี้ 'จริง' หรือ 'หลอก' """
    try:
        symbol = symbol.strip().upper()
        ticker = yf.Ticker(f"{symbol}.BK")
        
        # ดึงข้อมูล Intraday 1 นาที (ย้อนหลัง 1 วัน)
        df_now = ticker.history(period="1d", interval="1m")
        # ดึงข้อมูล Daily (ย้อนหลัง 1 เดือน)
        df_daily = ticker.history(period="1mo", interval="1d")
        
        if df_now.empty or df_daily.empty: return None
        
        curr_p = df_now['Close'].iloc[-1]
        prev_p = df_daily['Close'].iloc[-2]
        change = ((curr_p - prev_p) / prev_p) * 100
        
        # 1. เช็ค RSI (1m) เพื่อดูแรงเด้งสั้นๆ
        delta = df_now['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi_1m = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] if loss.iloc[-1] != 0 else 0.001))))
        
        # 2. เช็ค RVOL (เทียบวอลลุ่มช่วง 15 นาทีล่าสุด กับค่าเฉลี่ย)
        vol_recent = df_now['Volume'].iloc[-15:].sum()
        avg_vol_5d = df_daily['Volume'].iloc[-6:-1].mean() / 26 # เฉลี่ยต่อ 15 นาที (ตลาดเปิด 6.5 ชม.)
        rvol_active = vol_recent / avg_vol_5d if avg_vol_5d > 0 else 1.0
        
        # 3. ตรรกะวิเคราะห์ จริง vs หลอก
        # จริง = ราคาบวก + วอลลุ่มสนับสนุน (RVOL > 1.2) + RSI ฟื้นตัว (> 40)
        # หลอก = ราคาบวกจิ๊บๆ + วอลลุ่มบาง (RVOL < 0.8) + RSI ยังกองข้างล่าง
        status = "⏳ รอสัญญาณ"
        status_color = "gray"
        
        if curr_p > df_now['Close'].iloc[-10]: # ราคา 10 นาทีล่าสุดเป็นขาขึ้น
            if rvol_active > 1.3:
                status = "✅ รีบาวด์จริง (วาฬเข้าสวน)"
                status_color = "green"
            elif rvol_active < 0.8:
                status = "⚠️ รีบาวด์หลอก (วอลลุ่มบาง)"
                status_color = "orange"
            else:
                status = "⚖️ เด้งตามตลาด (ยังไม่ชัด)"
                status_color = "blue"
        elif curr_p < df_now['Low'].iloc[-30:].min() * 1.005:
            status = "📉 ยังไหลลง (ทับมือไว้!)"
            status_color = "red"

        return {
            "price": curr_p, "change": change, "rsi": rsi_1m, 
            "rvol": rvol_active, "status": status, "color": status_color
        }
    except: return None

# ==========================================
# 💾 DATA STORAGE
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'custom_watchlist' not in st.session_state:
    st.session_state.custom_watchlist = ["SIRI", "MTC", "GPSC", "HANA", "WHA", "JMT"]

# ==========================================
# 📊 SIDEBAR: GOAL TRACKER
# ==========================================
st.sidebar.title("🏹 ภารกิจปั้นแสนแรก")
total_sum = sum(item.get('profit', 0) for item in st.session_state.trade_history)
st.sidebar.metric("🏆 กำไรสะสมสุทธิ", f"{total_sum:,.2f} บ.")
st.sidebar.progress(min(max(total_sum / TARGET_TOTAL, 0.0), 1.0))

if st.sidebar.button("🔄 Refresh วิเคราะห์สด"):
    st.rerun()

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏹 Commander (เช็ครีบาวด์)", "📓 บันทึกการรบ (Ledger)", "🐷 Anti-Pig (บัญชีขายหมู)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 ระบบตรวจจับ 'รีบาวด์จริง หรือ หลอก'")
    
    c_add1, c_add2 = st.columns([3, 1])
    with c_add1:
        new_sym = st.text_input("➕ เพิ่มหุ้นเข้าเรดาร์ (เช่น EA, BTS):").upper()
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
                    
                    # แสดงผลวิเคราะห์ Real vs Fake
                    st.markdown(f"### สถานะ: :{data['color']}[{data['status']}]")
                    st.write(f"📊 RVOL (15m): **{data['rvol']:.2f}**")
                    st.write(f"📡 RSI (1m): **{data['rsi']:.1f}**")
                    
                    if data['status'] == "✅ รีบาวด์จริง (วาฬเข้าสวน)":
                        st.success("🎯 จังหวะช้อน! วอลลุ่มสนับสนุนการขึ้น")
                    elif data['status'] == "📉 ยังไหลลง (ทับมือไว้!)":
                        st.error("🚫 อย่าเพิ่งรับ! มีดกำลังบิน")
                else: st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: DETAILED LEDGER ---
with tab2:
    st.title("📓 สมุดบันทึกกำไรจริง")
    with st.expander("➕ ลงบันทึกไม้ใหม่ (ซื้อ/ขาย)", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            l_date = st.date_input("วันที่", datetime.now())
            l_symbol = st.text_input("หุ้น", value="SIRI").upper()
            l_broker = st.selectbox("แอป:", ["Streaming", "Dime (Standard)", "Dime (Free Tier)"])
        with f_col2:
            l_buy_qty = st.number_input("ซื้อ Qty", value=1000, step=100)
            l_buy_price = st.number_input("ราคาซื้อ", value=1.000, format="%.3f")
        with f_col3:
            l_sell_qty = st.number_input("ขาย Qty", value=1000, step=100)
            l_sell_price = st.number_input("ราคาขาย", value=1.100, format="%.3f")
        
        if st.button("💾 บันทึกกำไรลงบัญชี"):
            # คิดค่าธรรมเนียมตามแอป
            rate = 0.00168 if l_broker == "Streaming" else (0.001605 if "Std" in l_broker else 0.0)
            buy_val, sell_val = l_buy_qty * l_buy_price, l_sell_qty * l_sell_price
            fee = (buy_val + sell_val) * rate
            net_profit = (sell_val - (l_sell_qty * l_buy_price)) - fee
            
            st.session_state.trade_history.append({
                "date": l_date.strftime("%d/%m/%Y"), "sym": l_symbol, "broker": l_broker,
                "b_qty": l_buy_qty, "b_p": l_buy_price, "s_qty": l_sell_qty, "s_p": l_sell_price,
                "profit": net_profit
            })
            st.rerun()

    if st.session_state.trade_history:
        for idx, row in enumerate(st.session_state.trade_history):
            with st.container(border=True):
                r1, r2, r3, r4 = st.columns([1, 2, 1, 0.5])
                r1.write(f"📅 {row.get('date')}\n**{row.get('sym')}**")
                r2.write(f"🔵 {row.get('b_qty'):,} @ {row.get('b_p'):.3f}\n🔴 {row.get('s_qty'):,} @ {row.get('s_p'):.3f}")
                r3.subheader(f"{row.get('profit'):,.2f}")
                if r4.button("🗑️", key=f"del_{idx}"):
                    st.session_state.trade_history.pop(idx)
                    st.rerun()

# --- TAB 3: ANTI-PIG ---
with tab3:
    st.title("🐷 บัญชีขายหมู")
    if st.session_state.trade_history:
        p_data = []
        for item in st.session_state.trade_history:
            live = yf.Ticker(f"{item['sym']}.BK").history(period="1d")['Close'].iloc[-1]
            diff = live - item['s_p']
            p_data.append({
                "หุ้น": item['sym'], "ขายที่": item['s_p'], "ราคาตอนนี้": live,
                "ส่วนต่าง": f"{diff:.3f}", "กำไรที่พลาด": diff * item['s_qty'] if diff > 0 else 0
            })
        st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("v6.8 Rebound Scanner — 'วอลลุ่มคือหัวใจ ราคาคือภาพลวงตา'")
