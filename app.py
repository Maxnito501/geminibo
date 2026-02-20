# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import json
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v8.0 The Heart of the Whale)
# ==========================================
st.set_page_config(page_title="GeminiBo v8.0: The Heart of the Whale", layout="wide", page_icon="🐳")

FEES = {
    "Streaming": 0.00168,
    "Dime (Standard)": 0.001605,
    "Dime (Free Tier)": 0.0
}
TARGET_TOTAL = 990.0

def get_whale_heart_analysis(symbol):
    """ 
    ระบบอ่านใจรายใหญ่ (The Core Engine) 
    วิเคราะห์พฤติกรรมจาก Price Action + RSI + RVOL + Tick Flow
    """
    try:
        symbol = symbol.strip().upper()
        ticker = yf.Ticker(f"{symbol}.BK")
        # ดึงข้อมูล Intraday 1 นาที
        df_now = ticker.history(period="1d", interval="1m")
        # ดึงข้อมูล Daily 1 เดือน
        df_daily = ticker.history(period="1mo", interval="1d")
        
        if df_now.empty or df_daily.empty: return None
        
        curr_p = df_now['Close'].iloc[-1]
        prev_p = df_daily['Close'].iloc[-2]
        change = ((curr_p - prev_p) / prev_p) * 100
        low_today = df_now['Low'].min()
        high_today = df_now['High'].max()
        
        # RSI 1m (คำนวณแบบแม่นยำ)
        delta = df_now['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] if loss.iloc[-1] != 0 else 0.001))))
        
        # RVOL (15m Active vs 5-Day Avg)
        vol_recent = df_now['Volume'].iloc[-15:].sum()
        avg_vol_5d = df_daily['Volume'].iloc[-6:-1].mean() / 26 # เฉลี่ยต่อ 15 นาที
        rvol = vol_recent / avg_vol_5d if avg_vol_5d > 0 else 1.0

        # --- ตรรกะอ่านใจเจ้ามือ (หัวใจของแอป) ---
        status = "⚖️ ตลาดรอเลือกทาง"
        color = "gray"
        whale_action = "ดูเชิง"
        
        # กรณี 1: เจ้ามือแอบเก็บ (ห้ามขาย)
        if rsi < 35 and rvol > 1.2:
            status = "💎 เจ้ามือแอบเก็บ (ห้ามขาย!)"
            color = "green"
            whale_action = "สะสมของ"
        # กรณี 2: เจ้ามือไล่ราคา
        elif rvol > 2.0 and curr_p > df_now['Close'].iloc[-5]:
            status = "🚀 เจ้ามือไล่ราคา (รันเทรนด์)"
            color = "blue"
            whale_action = "ดันราคา"
        # กรณี 3: เจ้ามือรินขาย
        elif rsi > 80 and rvol > 1.5:
            status = "⚠️ เจ้ามือรินขาย (ระวัง!)"
            color = "red"
            whale_action = "ส่งของ"
        # กรณี 4: เจ้ามือพักรบ
        elif rvol < 0.4:
            status = "🐌 เจ้ามือพักรบ (วอลลุ่มหาย)"
            color = "orange"
            whale_action = "รอจังหวะ"

        return {
            "price": curr_p, "change": change, "rsi": rsi, "rvol": rvol,
            "low": low_today, "high": high_today, 
            "status": status, "color": color, "whale_action": whale_action
        }
    except: return None

# ==========================================
# 💾 DATA STORAGE & PERSISTENCE
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'custom_watchlist' not in st.session_state:
    st.session_state.custom_watchlist = ["HANA", "SIRI", "MTC", "ROJNA", "WHA"]

def export_data():
    return json.dumps({"history": st.session_state.trade_history, "watchlist": st.session_state.custom_watchlist})

def import_data(uploaded_file):
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            st.session_state.trade_history = data.get("history", [])
            st.session_state.custom_watchlist = data.get("watchlist", ["HANA", "SIRI", "MTC", "ROJNA"])
            st.success("📂 ดึงข้อมูลกลับมาเรียบร้อย!")
            st.rerun()
        except: st.error("ไฟล์ไม่ถูกต้อง")

# ==========================================
# 📊 SIDEBAR
# ==========================================
st.sidebar.title("🛡️ กองบัญชาการจอมทัพ")
total_sum = sum((item.get('profit') or 0.0) for item in st.session_state.trade_history)
st.sidebar.metric("🏆 กำไรสะสมสุทธิ", f"{total_sum:,.2f} บ.")
st.sidebar.progress(min(max(total_sum / TARGET_TOTAL, 0.0), 1.0))

st.sidebar.markdown("---")
st.sidebar.subheader("💾 ระบบกันข้อมูลหาย")
st.sidebar.download_button("📥 เซฟบัญชีลงเครื่อง", data=export_data(), file_name=f"geminibo_backup_{datetime.now().strftime('%d%m')}.json")
up_f = st.sidebar.file_uploader("📂 ดึงข้อมูลกลับมา", type="json")
if up_f: import_data(up_f)

if st.sidebar.button("🚨 ล้างข้อมูลและเริ่มใหม่"):
    st.session_state.trade_history = []
    st.rerun()

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏹 Commander (อ่านใจเจ้ามือ)", "📓 Ledger (บันทึกรบ)", "🐷 Anti-Pig (ขายหมู)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 เรดาร์อ่านใจเจ้ามือ (Whale Insight)")
    st.caption("ดึงข้อมูลจริงจากตลาดแบบนาทีต่อนาที เพื่อดูร่องรอยรายใหญ่")
    
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        new_stk = c1.text_input("➕ เพิ่มหุ้นเข้าเรดาร์ (พิมพ์ชื่อหุ้นแล้วกด Enter):").upper()
        if c2.button("บันทึกหุ้น") and new_stk:
            if new_stk not in st.session_state.custom_watchlist:
                st.session_state.custom_watchlist.append(new_stk)
                st.rerun()

    st.markdown("---")
    selected = st.multiselect("สแกนขุนพลที่สนใจ:", st.session_state.custom_watchlist, default=st.session_state.custom_watchlist[:4])
    
    for sym in selected:
        data = get_whale_heart_analysis(sym)
        with st.container(border=True):
            if data:
                # Layout: Header | Metrics | Strategy Matrix
                m_header, m_metrics, m_matrix = st.columns([1, 1.2, 3])
                
                with m_header:
                    st.header(f"🛡️ {sym}")
                    st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                    st.write(f"📊 RVOL: **{data['rvol']:.2f}**")
                    st.write(f"📡 RSI (1m): **{data['rsi']:.1f}**")
                
                with m_metrics:
                    st.subheader(f":{data['color']}[{data['status']}]")
                    st.info(f"📍 **Low วันนี้: {data['low']:.2f}**")
                    st.write(f"Whale Action: **{data['whale_action']}**")
                    if data['color'] == "green":
                        st.success("💎 **ห้ามขาย!** เจ้าสะสม")
                    elif data['color'] == "red":
                        st.error("🆘 **ควรปล่อย!** เจ้าทิ้งของ")

                with m_matrix:
                    p_have, p_none = st.columns(2)
                    with p_have:
                        st.markdown("💰 **กรณีมีของ (ควรทำอย่างไร?)**")
                        if data['color'] == "green":
                            st.success("💎 **ห้ามขาย/ถือต่อ:** เจ้ามือรับของสวนตลาด ห้ามคายของเด็ดขาด รอลุ้นเด้ง")
                        elif data['color'] == "red":
                            st.error("🚨 **จุดขาย/ถอย:** เจ้ามือรินของออก ทยอยขายทำกำไรหรือคัดเพื่อรักษากระสุน")
                        elif data['color'] == "blue":
                            st.warning("🚀 **Let Profit Run:** เจ้ามือไล่ราคา ถือรันกำไรไปเรื่อยๆ อย่ารีบลง")
                        else:
                            st.info("⚖️ **รอ:** ถือดูอาการตามแนวรับ-แนวต้านเดิม")
                    
                    with p_none:
                        st.markdown("🆕 **กรณีไม่มีของ (ควรทำอย่างไร?)**")
                        if data['rsi'] < 35 and data['color'] == "green":
                            st.success(f"🎯 **ช้อนเพิ่ม:** จุดได้เปรียบ {data['low']:.2f} วาฬแบกทุนเป็นเพื่อน")
                        elif data['rsi'] > 75:
                            st.error("🚫 **หยุด/ทับมือ:** อันตราย! ราคาพุ่งเกินพื้นฐาน อย่าไล่ราคาเจ้า")
                        elif data['color'] == "red":
                            st.error("🚫 **ทับมือ:** อันตราย! มีดกำลังบิน รอให้เจ้าทิ้งจบก่อน")
                        else:
                            st.warning("⏳ **รอ:** ทับมือไว้ รอวอลลุ่มวาฬกระตุกเข้า (RVOL > 1.2)")
            else: st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: DETAILED LEDGER ---
with tab2:
    st.title("📓 สมุดบันทึกการรบ (Detailed Ledger)")
    with st.expander("➕ ลงบันทึกรายการเทรด (ซื้อ/ขาย)", expanded=True):
        l1, l2, l3 = st.columns(3)
        with l1:
            b_date = st.date_input("วันที่ซื้อ", datetime.now(), key="entry_d")
            s_date = st.date_input("วันที่ขาย", datetime.now(), key="exit_d")
            sym_in = st.text_input("ชื่อหุ้น", value="SIRI").upper()
        with l2:
            broker = st.selectbox("แอปที่ใช้:", list(FEES.keys()))
            b_q = st.number_input("จำนวนที่ซื้อ (Qty)", value=1000)
            b_p = st.number_input("ราคาที่ซื้อ (Price)", value=1.000, format="%.3f")
        with l3:
            s_q = st.number_input("จำนวนที่ขาย (Qty)", value=1000)
            s_p = st.number_input("ราคาที่ขาย (Price)", value=1.100, format="%.3f")
            
            # การคำนวณเงินจริง (Net Profit)
            rate = FEES[broker]
            buy_val, sell_val = b_q * b_p, s_q * s_p
            fee = (buy_val + sell_val) * rate
            profit = ((s_p - b_p) * s_q) - fee
            
            st.write(f"ค่าต๋งรวม: {fee:.2f} บ.")
            st.subheader(f"กำไรรับจริง: {profit:,.2f} บ.")
            
            if st.button("💾 บันทึกลงสมุด"):
                st.session_state.trade_history.append({
                    "b_date": b_date.strftime("%d/%m/%y"), "s_date": s_date.strftime("%d/%m/%y"),
                    "sym": sym_in, "broker": broker, "b_q": b_q, "b_p": b_p, "s_q": s_q, "s_p": s_p, "profit": profit
                })
                st.rerun()

    if st.session_state.trade_history:
        st.markdown("---")
        for idx, row in enumerate(st.session_state.trade_history):
            with st.container(border=True):
                r1, r2, r3, r4 = st.columns([1.5, 2, 1, 0.5])
                r1.write(f"📅 {row.get('b_date')} → {row.get('s_date')}\n**{row.get('sym')}** ({row.get('broker')})")
                r2.write(f"🔵 {row.get('b_q',0):,} @ {row.get('b_p',0.0):.3f}\n🔴 {row.get('s_q',0):,} @ {row.get('s_p',0.0):.3f}")
                r3.subheader(f"{row.get('profit', 0.0):,.2f}")
                if r4.button("🗑️", key=f"del_{idx}"):
                    st.session_state.trade_history.pop(idx)
                    st.rerun()

# --- TAB 3: ANTI-PIG ---
with tab3:
    st.title("🐷 บัญชีขายหมู (Anti-Pig Analysis)")
    if st.session_state.trade_history:
        pig_list = []
        for item in st.session_state.trade_history:
            try:
                live = yf.Ticker(f"{item['sym']}.BK").history(period="1d")['Close'].iloc[-1]
                diff = live - item.get('s_p', 0.0)
                pig_list.append({
                    "หุ้น": item['sym'], "วันที่ขาย": item['s_date'], "ขายที่": item['s_p'],
                    "ตอนนี้": live, "กำไรที่พลาด": diff * item['s_q'] if diff > 0 else 0
                })
            except: continue
        st.dataframe(pd.DataFrame(pig_list), use_container_width=True, hide_index=True)
    else: st.info("ยังไม่มีประวัติการขายใน Ledger")

st.markdown("---")
st.caption("v8.0 Iron-Clad — 'จอมทัพต้องนิ่งพอที่จะไม่รับมีด และเป๊ะพอที่จะไม่พลาดกำไร'")
