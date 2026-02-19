import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v4.9 Professional Ledger)
# ==========================================
st.set_page_config(page_title="GeminiBo v4.9: Professional Ledger", layout="wide", page_icon="📓")

# ค่าธรรมเนียมเฉลี่ย (รวม VAT) ประมาณ 0.168% ต่อขา
TOTAL_FEE_FACTOR = 0.00168 
GEMINI_PRO_COST = 790.0
SETSMART_COST = 1000.0

def get_advanced_metrics(symbol):
    try:
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
# 💾 DATA STORAGE (Session State)
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2 = st.tabs(["🏹 ศูนย์บัญชาการ (Commander)", "📓 บัญชีรายเดือน (Trade Ledger)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 GeminiBo v4.9: Commander")
    
    # ส่วนวิเคราะห์เฉพาะหน้า (SIRI / MTC / ตัวเลือกเสริม)
    cols = st.columns(3)
    watchlist = ["WHA", "ROJNA", "AMATA", "SIRI", "MTC", "CPALL", "SAWAD", "PLANB", "THCOM"]
    selected_stocks = st.multiselect("เจาะลึกสมรภูมิ:", watchlist, default=["SIRI", "MTC", "WHA"])

    for i, sym in enumerate(selected_stocks[:3]):
        data = get_advanced_metrics(sym)
        with cols[i]:
            with st.container(border=True):
                if data:
                    st.header(f"🛡️ {sym}")
                    st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                    
                    if sym == "SIRI":
                        if data['price'] >= 1.66:
                            st.error("💎 **ห้ามขายหมู!** ทะลุต้านใหญ่แล้ว รันต่อ")
                        elif 1.62 <= data['price'] <= 1.63:
                            st.warning("🎯 **Target Hit:** แบ่งขาย 2,000 หุ้น")
                    
                    if sym == "MTC":
                        st.info("🕒 **MTC Strategy:** ตั้งขาย 100 หุ้นที่ 39.75 (หนีมีเชิง)")

                    st.write(f"📡 RSI: {data['rsi']:.1f} | 🌊 RVOL: {data['rvol']:.2f}")

# --- TAB 2: TRADE LEDGER ---
with tab2:
    st.title("📓 สมุดบันทึกการรบ (Monthly Ledger)")
    
    # แบบฟอร์มกรอกข้อมูลการเทรด
    with st.expander("➕ เพิ่มบันทึกการเทรดใหม่", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            t_date_buy = st.date_input("วันที่ซื้อ", datetime.now())
            t_symbol = st.selectbox("หุ้น", watchlist)
            t_buy_price = st.number_input("ราคาที่ได้ (ซื้อ)", value=1.000, step=0.001, format="%.3f")
        with c2:
            t_date_sell = st.date_input("วันที่ขาย", datetime.now())
            t_qty = st.number_input("จำนวนหุ้น", value=100, step=100)
            t_sell_price = st.number_input("ราคาที่ขาย", value=1.000, step=0.001, format="%.3f")
        with c3:
            st.write("📌 **การคำนวณเบื้องต้น**")
            gross_buy = t_buy_price * t_qty
            gross_sell = t_sell_price * t_qty
            fee_buy = gross_buy * TOTAL_FEE_FACTOR
            fee_sell = gross_sell * TOTAL_FEE_FACTOR
            total_fee = fee_buy + fee_sell
            net_profit = (gross_sell - gross_buy) - total_fee
            
            st.write(f"ค่าธรรมเนียม+VAT: {total_fee:,.2f} บ.")
            st.subheader(f"กำไรสุทธิ: {net_profit:,.2f} บ.")
            
            if st.button("💾 บันทึกลงสมุดบัญชี"):
                new_record = {
                    "วันที่ซื้อ": t_date_buy,
                    "วันที่ขาย": t_date_sell,
                    "หุ้น": t_symbol,
                    "ราคาซื้อ": t_buy_price,
                    "ราคาขาย": t_sell_price,
                    "จำนวน": t_qty,
                    "ค่าธรรมเนียม": total_fee,
                    "กำไรสุทธิ": net_profit
                }
                st.session_state.trade_history.append(new_record)
                st.toast("บันทึกเรียบร้อย!")

    # ตารางแสดงประวัติการเทรด
    if st.session_state.trade_history:
        df_history = pd.DataFrame(st.session_state.trade_history)
        st.markdown("---")
        st.subheader("📋 ประวัติการปิดรอบเดือนนี้")
        st.dataframe(df_history, use_container_width=True, hide_index=True)
        
        # ส่วนสรุป ROI
        total_net_profit = df_history["กำไรสุทธิ"].sum()
        remaining_after_ai = total_net_profit - GEMINI_PRO_COST
        
        c_res1, c_res2, c_res3 = st.columns(3)
        c_res1.metric("💰 กำไรสุทธิรวม (หลังหักค่าต๋ง)", f"{total_net_profit:,.2f} บ.")
        c_res2.metric("🤖 หลังหักค่า Gemini Pro", f"{remaining_after_ai:,.2f} บ.", delta_color="normal")
        
        if remaining_after_ai >= SETSMART_COST:
            c_res3.success(f"✅ พร้อมสมัคร SetSmart! (เหลือเงิน {remaining_after_ai-SETSMART_COST:,.2f} บ.)")
        else:
            c_res3.warning(f"🕒 ขาดอีก {SETSMART_COST-remaining_after_ai:,.2f} บ. เพื่อค่า SetSmart")
            
        if st.button("🗑️ ล้างข้อมูลทั้งหมด (เริ่มเดือนใหม่)"):
            st.session_state.trade_history = []
            st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลการรบ... เริ่มบันทึกไม้แรกเพื่อดูผลงานรายเดือนครับพี่โบ้!")

st.markdown("---")
st.caption("v4.9 Professional Ledger — รบอย่างจอมทัพ บริหารอย่างนักธุรกิจ เพื่อเป้าหมายแสนแรก")
