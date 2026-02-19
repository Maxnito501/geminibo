import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v5.4 Correction Ledger)
# ==========================================
st.set_page_config(page_title="GeminiBo v5.4: Precision Ledger", layout="wide", page_icon="📓")

# ค่าธรรมเนียมมาตรฐาน (รวม VAT 7% แล้ว)
FEE_STREAMING = 0.00168  # 0.157% + VAT = ~0.168%
FEE_DIME_STD = 0.001605  # 0.15% + VAT = ~0.1605%
FEE_DIME_FREE = 0.0      # สำหรับไม้แรกๆ ของเดือน

GEMINI_PRO_COST = 790.0
SETSMART_COST = 1000.0
TARGET_TOTAL = GEMINI_PRO_COST + SETSMART_COST

def get_advanced_metrics(symbol):
    try:
        symbol = symbol.strip().upper()
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < 10: return None
        
        price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        change_pct = ((price - prev_price) / prev_price) * 100
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        avg_vol_5d = df['Volume'].iloc[-6:-1].mean()
        curr_vol = df['Volume'].iloc[-1]
        rvol = curr_vol / avg_vol_5d if avg_vol_5d > 0 else 1.0
        
        return {"price": price, "change": change_pct, "rsi": rsi.iloc[-1], "rvol": rvol}
    except: return None

# ==========================================
# 💾 DATA STORAGE
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'custom_watchlist' not in st.session_state:
    st.session_state.custom_watchlist = ["WHA", "ROJNA", "SIRI", "MTC", "GPSC"]

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2 = st.tabs(["🏹 ศูนย์บัญชาการ (Commander)", "📓 สมุดบัญชีจอมทัพ (Detailed Ledger)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 GeminiBo v5.4: Commander")
    
    # ส่วนเพิ่มหุ้นด้วยตนเอง
    c_add1, c_add2 = st.columns([3, 1])
    with c_add1:
        new_sym = st.text_input("➕ เพิ่มหุ้นเข้าลิสต์สแกน (เช่น GPSC, JMT, BTS):").upper()
    with c_add2:
        if st.button("บันทึกเข้าลิสต์") and new_sym:
            if new_sym not in st.session_state.custom_watchlist:
                st.session_state.custom_watchlist.append(new_sym)
                st.toast(f"เพิ่ม {new_sym} เรียบร้อย!")

    # สรุป ROI รายเดือนที่ Sidebar
    st.sidebar.title("💰 สถานะหาเงินจ่ายแอป")
    total_p_accum = sum(item['กำไรสุทธิ'] for item in st.session_state.trade_history)
    st.sidebar.metric("🏆 กำไรสะสมสุทธิ", f"{total_p_accum:,.2f} บ.")
    
    prog_val = min(max(total_p_accum / TARGET_TOTAL, 0.0), 1.0)
    st.sidebar.progress(prog_val)
    st.sidebar.write(f"🎯 เป้าหมาย 1,790: **{prog_val*100:.1f}%**")
    
    if total_p_accum >= GEMINI_PRO_COST:
        st.sidebar.success("✅ คืนทุนค่า Gemini Pro แล้ว!")

    # วิเคราะห์หุ้น
    st.markdown("---")
    selected_stocks = st.multiselect("เลือกขุนพลวันนี้:", st.session_state.custom_watchlist, default=st.session_state.custom_watchlist[:3])
    
    cols = st.columns(3)
    for i, sym in enumerate(selected_stocks[:3]):
        data = get_advanced_metrics(sym)
        with cols[i]:
            with st.container(border=True):
                if data:
                    st.header(f"🛡️ {sym}")
                    st.metric("ราคาล่าสุด", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                    
                    if sym == "SIRI":
                        if data['price'] >= 1.66: st.error("🔥 **ห้ามขายหมู!** ทะลุต้านใหญ่แล้ว")
                        elif 1.62 <= data['price'] <= 1.63: st.warning("🎯 **เป้าไม้แรก:** แบ่งขายเก็บกำไร")
                    elif sym == "MTC":
                        st.info("🕒 **MTC:** ตั้งขาย 100 หุ้นที่ 39.75 (หนีมีเชิง)")
                    elif sym == "GPSC":
                        if data['rsi'] < 65 and data['rvol'] > 1.2: st.success("💎 **ทรงสวย!** ระวังขายหมูซ้ำรอย")
                    
                    st.write(f"📡 RSI: {data['rsi']:.1f} | 🌊 RVOL: {data['rvol']:.2f}")
                else: st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: DETAILED LEDGER ---
with tab2:
    st.title("📓 สมุดบัญชีการรบ (Detailed Trade Journal)")
    
    with st.expander("➕ ลงบันทึกรายการเทรดใหม่", expanded=True):
        l1, l2, l3 = st.columns(3)
        
        with l1:
            st.caption("🟢 ภาคการซื้อ (Entry)")
            in_symbol = st.text_input("ชื่อหุ้น (พิมพ์เองได้เลย)", value="SIRI").upper()
            broker_type = st.radio("เทรดผ่านแอป:", ["Streaming", "Dime (Standard)", "Dime (Free Tier)"], horizontal=True)
            in_price = st.number_input("ราคาซื้อ (ต้นทุน)", value=1.000, step=0.001, format="%.3f")
            in_qty_total = st.number_input("จำนวนหุ้นที่ซื้อมา (ล็อตนี้)", value=1000, step=100)
            in_lot_name = st.text_input("ซื้อไม้ที่ (เช่น ไม้ 1)", value="ไม้ 1")

        with l2:
            st.caption("🔴 ภาคการขาย (Exit)")
            out_qty = st.number_input("จำนวนหุ้นที่ขายครั้งนี้", value=1000, step=100)
            out_price = st.number_input("ราคาที่ขายได้จริง", value=1.100, step=0.001, format="%.3f")
            out_lot_name = st.text_input("ขายไม้ที่ (เช่น ปิดไม้ 1)", value="ปิดรอบ")
            out_date = st.date_input("วันที่ขาย", datetime.now())

        with l3:
            st.caption("💰 สรุปผลกำไรสุทธิ")
            fee_rate = FEE_STREAMING if broker_type == "Streaming" else (FEE_DIME_STD if broker_type == "Dime (Standard)" else FEE_DIME_FREE)
            
            buy_val = in_price * out_qty
            sell_val = out_price * out_qty
            total_fee = (buy_val + sell_val) * fee_rate
            net_profit = (sell_val - buy_val) - total_fee
            
            st.write(f"โบรกเกอร์: **{broker_type}**")
            st.write(f"ค่าธรรมเนียมรวม: {total_fee:,.2f} บ.")
            st.subheader(f"กำไรสุทธิ: {net_profit:,.2f} บ.")
            
            l_note = st.text_input("หมายเหตุ", placeholder="เช่น ขายหมู, รันเทรนด์สำเร็จ")
            
            if st.button("💾 บันทึกลงสมุดบัญชี"):
                new_entry = {
                    "วันที่": out_date.strftime("%d/%m/%Y"),
                    "หุ้น": in_symbol,
                    "แอป": broker_type,
                    "จำนวน": out_qty,
                    "ราคาซื้อ": in_price,
                    "ราคาขาย": out_price,
                    "กำไรสุทธิ": net_profit,
                    "หมายเหตุ": f"{in_lot_name} -> {out_lot_name} | {l_note}"
                }
                st.session_state.trade_history.append(new_entry)
                st.toast("บันทึกสำเร็จ!")
                st.rerun()

    # --- ส่วนแสดงรายการและปุ่มลบรายแถว ---
    if st.session_state.trade_history:
        st.markdown("---")
        st.subheader("📋 ประวัติการทำกำไร (ลบรายการที่ผิดได้ท้ายแถว)")
        
        # ส่วนหัวของรายการ
        h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([1, 1, 1.5, 1, 2, 0.5])
        h_col1.write("**วันที่**")
        h_col2.write("**หุ้น**")
        h_col3.write("**จำนวน/ราคา**")
        h_col4.write("**กำไรสุทธิ**")
        h_col5.write("**หมายเหตุ**")
        h_col6.write("**ลบ**")
        
        # รายละเอียดแต่ละบรรทัด
        for idx, item in enumerate(st.session_state.trade_history):
            r_col1, r_col2, r_col3, r_col4, r_col5, r_col6 = st.columns([1, 1, 1.5, 1, 2, 0.5])
            r_col1.write(item['วันที่'])
            r_col2.write(f"**{item['หุ้น']}**")
            r_col3.write(f"{item['จำนวน']:,} @ {item['ราคาขาย']:.3f}")
            r_col4.write(f"{item['กำไรสุทธิ']:,.2f}")
            r_col5.write(f"<small>{item['หมายเหตุ']}</small>", unsafe_allow_html=True)
            
            # ปุ่มลบรายช่อง
            if r_col6.button("🗑️", key=f"del_{idx}"):
                st.session_state.trade_history.pop(idx)
                st.toast(f"ลบรายการ {item['หุ้น']} เรียบร้อย!")
                st.rerun()

        st.markdown("---")
        st.metric("💰 กำไรสะสมสุทธิรวม", f"{total_p_accum:,.2f} บ.")
        
        if st.button("🚨 ล้างข้อมูลทั้งหมด (เริ่มเดือนใหม่)"):
            st.session_state.trade_history = []
            st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลการขาย... บันทึกไม้แรกเพื่อเริ่มภารกิจหาเงินจ่ายค่าแอปครับพี่โบ้!")

st.markdown("---")
st.caption("v5.4 Precision & Correction Ledger — เพราะทุกความผิดพลาด แก้ไขได้เสมอ")
