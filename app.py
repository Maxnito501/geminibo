import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v5.2 Precision Broker)
# ==========================================
st.set_page_config(page_title="GeminiBo v5.2: Precision Broker", layout="wide", page_icon="📓")

# ค่าธรรมเนียมมาตรฐาน (รวม VAT 7% แล้ว)
FEE_STREAMING = 0.00168  # 0.157% + VAT = ~0.168%
FEE_DIME_STD = 0.001605  # 0.15% + VAT = ~0.1605% (Dime มักถูกกว่าเล็กน้อย)
FEE_DIME_FREE = 0.0      # สำหรับไม้แรกๆ ของเดือน

GEMINI_PRO_COST = 790.0

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
        
        return {
            "price": price, "change": change_pct, "rsi": rsi.iloc[-1], "rvol": rvol
        }
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
tab1, tab2 = st.tabs(["🏹 ศูนย์บัญชาการ (Commander)", "📓 สมุดบัญชีเป๊ะ (Precision Ledger)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 GeminiBo v5.2: Commander")
    
    c_add1, c_add2 = st.columns([3, 1])
    with c_add1:
        new_sym = st.text_input("➕ เพิ่มหุ้นเข้าลิสต์ (เช่น GPSC, JMT, BTS):").upper()
    with c_add2:
        if st.button("บันทึกเข้าลิสต์") and new_sym:
            if new_sym not in st.session_state.custom_watchlist:
                st.session_state.custom_watchlist.append(new_sym)
                st.toast(f"เพิ่ม {new_sym} เรียบร้อย!")
    
    st.markdown("---")
    selected_stocks = st.multiselect("เลือกขุนพลที่จะเข้าตี:", st.session_state.custom_watchlist, default=st.session_state.custom_watchlist[:3])
    
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
                        elif 1.62 <= data['price'] <= 1.63: st.warning("🎯 **Target:** แบ่งขายไม้แรก")
                    elif sym == "MTC":
                        st.info("🕒 **MTC:** ตั้งขาย 100 หุ้นที่ 39.75")
                    elif sym == "GPSC":
                        if data['rsi'] < 65 and data['rvol'] > 1.2: st.success("💎 **ทรงสวย!** ระวังขายหมู")
                    
                    st.write(f"📡 RSI: {data['rsi']:.1f} | 🌊 RVOL: {data['rvol']:.2f}")
                else: st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: PRECISION LEDGER ---
with tab2:
    st.title("📓 สมุดบัญชีจอมทัพ (Precision Ledger)")
    
    with st.expander("➕ ลงบันทึกรายการเทรด (หักค่าธรรมเนียมตามค่าย)", expanded=True):
        l_col1, l_col2, l_col3 = st.columns(3)
        
        with l_col1:
            st.caption("🟢 ภาคการซื้อ (Entry)")
            in_symbol = st.text_input("ชื่อหุ้น", value="SIRI").upper()
            broker_type = st.radio("เลือกแอปที่ใช้เทรด:", ["Dime (Free Tier)", "Dime (Standard)", "Streaming (Standard)"], horizontal=True)
            in_price = st.number_input("ราคาที่ซื้อ (ทุน)", value=1.000, step=0.001, format="%.3f")
            in_qty = st.number_input("จำนวนหุ้นที่ซื้อมา", value=1000, step=100)
            in_lot = st.selectbox("ซื้อไม้ที่", ["ไม้ 1", "ไม้ 2", "ไม้ 3", "ถัวเฉลี่ย"])

        with l_col2:
            st.caption("🔴 ภาคการขาย (Exit)")
            out_price = st.number_input("ราคาที่ขายได้", value=1.100, step=0.001, format="%.3f")
            out_qty = st.number_input("จำนวนหุ้นที่ขายออก", value=1000, step=100)
            out_lot = st.selectbox("ขายไม้ที่", ["ไม้ 1", "ไม้ 2", "ปิดรอบ"])

        with l_col3:
            st.caption("💰 คำนวณกำไรสุทธิแบบเป๊ะๆ")
            
            # เลือกค่าธรรมเนียมตามแอป
            if broker_type == "Dime (Free Tier)": fee_rate = FEE_DIME_FREE
            elif broker_type == "Dime (Standard)": fee_rate = FEE_DIME_STD
            else: fee_rate = FEE_STREAMING
            
            buy_val = in_price * out_qty
            sell_val = out_price * out_qty
            
            # คำนวณค่าธรรมเนียมรายขา
            fee_in = buy_val * fee_rate
            fee_out = sell_val * fee_rate
            total_fee = fee_in + fee_out
            
            net_profit = (sell_val - buy_val) - total_fee
            
            st.write(f"โบรกเกอร์: **{broker_type}**")
            st.write(f"ยอดซื้อ: {buy_val:,.2f} บ.")
            st.write(f"ยอดขาย: {sell_val:,.2f} บ.")
            st.write(f"หักค่าธรรมเนียมรวม: {total_fee:,.2f} บ.")
            st.subheader(f"กำไรสุทธิ: {net_profit:,.2f} บ.")
            
            if st.button("💾 บันทึกลงสมุดบัญชี"):
                new_trade = {
                    "หุ้น": in_symbol, "แอป": broker_type,
                    "ทุน": in_price, "ซื้อไม้": in_lot,
                    "ราคาขาย": out_price, "ขายไม้": out_lot,
                    "จำนวน": out_qty, "กำไรสุทธิ": net_profit, 
                    "วันที่": datetime.now().strftime("%d/%m/%Y")
                }
                st.session_state.trade_history.append(new_trade)
                st.toast("บันทึกสำเร็จ!")

    if st.session_state.trade_history:
        df_history = pd.DataFrame(st.session_state.trade_history)
        st.markdown("---")
        st.subheader("📋 ประวัติการทำกำไรรายไม้")
        st.dataframe(df_history, use_container_width=True, hide_index=True)
        
        total_p = df_history["กำไรสุทธิ"].sum()
        r1, r2 = st.columns(2)
        r1.metric("💰 กำไรสะสมสุทธิทั้งหมด", f"{total_p:,.2f} บ.")
        
        gemini_status = total_p - GEMINI_PRO_COST
        if gemini_status >= 0:
            r2.success(f"🎉 คืนค่า Gemini Pro แล้ว! (ส่วนเกิน {gemini_status:,.2f})")
        else:
            r2.warning(f"🕒 อีก {abs(gemini_status):,.2f} บาท จะถึงเป้าค่าแอป")

        if st.button("🗑️ ล้างข้อมูลทั้งหมด"):
            st.session_state.trade_history = []
            st.rerun()
