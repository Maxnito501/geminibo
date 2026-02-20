# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v6.3 Anti-Pig)
# ==========================================
st.set_page_config(page_title="GeminiBo v6.3: Anti-Pig", layout="wide", page_icon="🏹")

FEE_STREAMING = 0.00168 
FEE_DIME_STD = 0.001605
FEE_DIME_FREE = 0.0
GEMINI_PRO_COST = 790.0
SETSMART_MONTHLY = 200.0 
TARGET_TOTAL = GEMINI_PRO_COST + SETSMART_MONTHLY

def get_live_metrics(symbol):
    """ ดึงข้อมูลสดเพื่อวิเคราะห์จังหวะช้อนและรันเทรนด์ """
    try:
        symbol = symbol.strip().upper()
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < 10: return None
        
        curr_p = df['Close'].iloc[-1]
        prev_p = df['Close'].iloc[-2]
        change = ((curr_p - prev_p) / prev_p) * 100
        
        # RSI 
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
# 💾 DATA STORAGE
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'custom_watchlist' not in st.session_state:
    st.session_state.custom_watchlist = ["SIRI", "MTC", "GPSC", "WHA", "ROJNA"]

# ==========================================
# 📊 SIDEBAR: GOAL TRACKER
# ==========================================
st.sidebar.title("🏹 ภารกิจปั้นแสนแรก")
total_p = sum(item.get('กำไรสุทธิ', 0.0) for item in st.session_state.trade_history)
st.sidebar.metric("🏆 กำไรสะสมสุทธิ", f"{total_p:,.2f} บ.")
st.sidebar.progress(min(max(total_p / TARGET_TOTAL, 0.0), 1.0))
st.sidebar.write(f"🎯 เป้าหมายค่าแอป: {TARGET_TOTAL} บ.")

if st.sidebar.button("🔄 ล้างข้อมูลทั้งหมด"):
    st.session_state.trade_history = []
    st.rerun()

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏹 Commander (ติดตาม/ช้อน)", "📓 Master Ledger (บันทึก)", "🐷 Anti-Pig (บัญชีขายหมู)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 ศูนย์บัญชาการ & ตรวจจับวาฬ")
    
    # ส่วนเพิ่มหุ้นที่น่าช้อน
    c_add1, c_add2 = st.columns([3, 1])
    with c_add1:
        new_sym = st.text_input("➕ พิมพ์ชื่อหุ้นที่น่าช้อนเพิ่ม (เช่น JMT, BTS, EA):").upper()
    with c_add2:
        if st.button("บันทึกเข้าลิสต์") and new_sym:
            if new_sym not in st.session_state.custom_watchlist:
                st.session_state.custom_watchlist.append(new_sym)
                st.toast(f"เพิ่ม {new_sym} เข้าเรดาร์แล้ว!")

    st.markdown("---")
    selected_stocks = st.multiselect("ส่องกล้องขุนพลที่เลือก:", st.session_state.custom_watchlist, default=st.session_state.custom_watchlist[:4])
    
    cols = st.columns(3)
    for i, sym in enumerate(selected_stocks):
        data = get_live_metrics(sym)
        with cols[i % 3]:
            with st.container(border=True):
                if data:
                    st.header(f"🛡️ {sym}")
                    st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                    
                    # Panic Sniper Logic
                    if data['rsi'] < 35:
                        st.success("✅ **BUY ZONE (ช้อนด่วน!)**\nราคาลงมาลึก RSI ต่ำมาก ลุ้นเด้ง")
                    elif data['rsi'] > 80:
                        st.error("🆘 **OVERBOUGHT (ระวัง!)**\nราคาพุ่งแรงเกินไป ระวังวาฬทิ้งของ")
                    
                    if data['rvol'] > 1.5:
                        st.warning(f"🐳 **วาฬบุก!** (RVOL: {data['rvol']:.2f})")
                    
                    st.write(f"📡 RSI: {data['rsi']:.1f} | 🌊 RVOL: {data['rvol']:.2f}")
                else: st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: MASTER LEDGER ---
with tab2:
    st.title("📓 สมุดบันทึกการรบมืออาชีพ")
    with st.expander("➕ ลงบันทึกรายการเทรดใหม่", expanded=True):
        l1, l2, l3 = st.columns(3)
        with l1:
            in_sym = st.text_input("ชื่อหุ้นที่ขาย", value="SIRI").upper()
            broker = st.radio("แอปที่ใช้:", ["Streaming", "Dime (Std)", "Dime (Free)"], horizontal=True)
            in_p = st.number_input("ราคาที่ซื้อ (ต้นทุน)", value=1.000, format="%.3f")
        with l2:
            out_q = st.number_input("จำนวนหุ้นที่ขาย", value=1000, step=100)
            out_p = st.number_input("ราคาที่ขายได้", value=1.100, format="%.3f")
            out_d = st.date_input("วันที่ขาย", datetime.now())
        with l3:
            fee_r = FEE_STREAMING if broker == "Streaming" else (FEE_DIME_STD if broker == "Dime (Std)" else FEE_DIME_FREE)
            net_p = ((out_p - in_p) * out_q) - ((out_p + in_p) * out_q * fee_r)
            st.subheader(f"กำไรสุทธิ: {net_p:,.2f} บ.")
            note = st.text_input("หมายเหตุ (เช่น ขายหมูไม้แรก, รันเทรนด์)")
            if st.button("💾 บันทึกลงสมุด"):
                st.session_state.trade_history.append({
                    "วันที่": out_d.strftime("%d/%m/%Y"), "หุ้น": in_sym,
                    "ราคาซื้อ": in_p, "ราคาขาย": out_p, "จำนวน": out_q,
                    "กำไรสุทธิ": net_p, "แอป": broker, "หมายเหตุ": note
                })
                st.rerun()

    if st.session_state.trade_history:
        st.markdown("---")
        for idx, item in enumerate(st.session_state.trade_history):
            r1, r2, r3, r4, r5 = st.columns([1, 1, 1.5, 2, 0.5])
            r1.write(f"{item.get('วันที่', '-')}\n**{item.get('หุ้น', '-')}**")
            r2.write(f"T: {item.get('ราคาซื้อ', 0.0):.3f}\nS: {item.get('ราคาขาย', 0.0):.3f}")
            r3.write(f"**{item.get('กำไรสุทธิ', 0.0):,.2f} บ.**")
            r4.write(f"<small>{item.get('หมายเหตุ', '-')}</small>\n({item.get('แอป', '-')})", unsafe_allow_html=True)
            if r5.button("🗑️", key=f"del_{idx}"):
                st.session_state.trade_history.pop(idx)
                st.rerun()

# --- TAB 3: ANTI-PIG REPORT ---
with tab3:
    st.title("🐷 บัญชีวิเคราะห์การขายหมู (Anti-Pig Analysis)")
    st.info("ระบบจะเทียบ 'ราคาที่พี่ขาย' กับ 'ราคาปัจจุบัน' เพื่อดูว่าเราพลาดกำไรไปเท่าไหร่")
    
    if st.session_state.trade_history:
        pig_data = []
        for item in st.session_state.trade_history:
            live = get_live_metrics(item['หุ้น'])
            if live:
                current_p = live['price']
                sold_p = item['ราคาขาย']
                diff = current_p - sold_p
                missed_profit = diff * item['จำนวน'] if diff > 0 else 0
                
                pig_data.append({
                    "หุ้น": item['หุ้น'],
                    "วันที่ขาย": item['วันที่'],
                    "ราคาที่ขาย": sold_p,
                    "ราคาปัจจุบัน": current_p,
                    "ส่วนต่าง": f"{diff:.3f}",
                    "กำไรที่พลาดไป (บาท)": missed_profit,
                    "สถานะ": "🐷 ขายหมูตัวเบ้อเริ่ม" if diff > 0 else "✅ ขายได้จังหวะดี"
                })
        
        df_pig = pd.DataFrame(pig_data)
        st.dataframe(df_history := df_pig, use_container_width=True, hide_index=True)
        
        total_missed = df_pig["กำไรที่พลาดไป (บาท)"].sum()
        if total_missed > 0:
            st.error(f"😱 รวมกำไรที่ 'ขายหมู' ไปทั้งหมดเดือนนี้: **{total_missed:,.2f} บาท**")
            st.write("คำแนะนำกุนซือ: ไม้หน้าถ้าเห็น RVOL > 1.5 และ RSI < 70 ให้ใจเย็นๆ รันกำไรให้สุดคำครับพี่โบ้!")
        else:
            st.success("🎉 สุดยอดครับพี่โบ้! เดือนนี้ยังไม่มีประวัติการขายหมูแบบมีนัยสำคัญ")
    else:
        st.info("ยังไม่มีประวัติการขาย... บันทึกไม้แรกในหน้า Ledger ก่อนครับ")

st.markdown("---")
st.caption("v6.3 Anti-Pig Commander — 'วินัยของจอมทัพ คือการรันกำไรให้ถึงเป้าหมายแสนแรก'")
