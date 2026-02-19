import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v5.0 Master Ledger)
# ==========================================
st.set_page_config(page_title="GeminiBo v5.0: Master Ledger", layout="wide", page_icon="📓")

# ค่าธรรมเนียมเฉลี่ย (รวม VAT) ประมาณ 0.168% ต่อขา
TOTAL_FEE_FACTOR = 0.00168 
GEMINI_PRO_COST = 790.0

def get_advanced_metrics(symbol):
    """ ดึงข้อมูลวิเคราะห์จาก Yahoo Finance """
    try:
        # ล้างช่องว่างและแปลงเป็นตัวใหญ่
        symbol = symbol.strip().upper()
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < 10: return None
        
        price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        change_pct = ((price - prev_price) / prev_price) * 100
        
        # RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # RVOL (Relative Volume)
        avg_vol_5d = df['Volume'].iloc[-6:-1].mean()
        curr_vol = df['Volume'].iloc[-1]
        rvol = curr_vol / avg_vol_5d if avg_vol_5d > 0 else 1.0
        
        return {
            "price": price, 
            "change": change_pct, 
            "rsi": rsi.iloc[-1], 
            "rvol": rvol,
            "high": df['High'].iloc[-1],
            "low": df['Low'].iloc[-1]
        }
    except: return None

# ==========================================
# 💾 DATA STORAGE (Session State)
# ==========================================
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'custom_watchlist' not in st.session_state:
    st.session_state.custom_watchlist = ["WHA", "ROJNA", "SIRI", "MTC", "GPSC"]

# ==========================================
# 📊 NAVIGATION TABS
# ==========================================
tab1, tab2 = st.tabs(["🏹 ศูนย์บัญชาการ (Commander)", "📓 สมุดบัญชีจอมทัพ (Master Ledger)"])

# --- TAB 1: COMMANDER ---
with tab1:
    st.title("🏹 GeminiBo v5.0: Master Commander")
    
    # ส่วนเพิ่มหุ้นด้วยตนเอง
    c_add1, c_add2 = st.columns([3, 1])
    with c_add1:
        new_sym = st.text_input("➕ เพิ่มหุ้นตัวใหม่เข้าลิสต์สแกน (เช่น GPSC, JMT, BTS):").upper()
    with c_add2:
        if st.button("บันทึกเข้าลิสต์") and new_sym:
            if new_sym not in st.session_state.custom_watchlist:
                st.session_state.custom_watchlist.append(new_sym)
                st.toast(f"เพิ่ม {new_sym} เข้าลิสต์แล้ว!")
    
    st.markdown("---")
    
    # วิเคราะห์หุ้นที่เลือก
    selected_stocks = st.multiselect("เลือกขุนพลที่จะเข้าตีวันนี้:", st.session_state.custom_watchlist, default=st.session_state.custom_watchlist[:3])
    
    cols = st.columns(3)
    for i, sym in enumerate(selected_stocks[:3]):
        data = get_advanced_metrics(sym)
        with cols[i]:
            with st.container(border=True):
                if data:
                    st.header(f"🛡️ {sym}")
                    st.metric("ราคาล่าสุด", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                    
                    # --- ยุทธศาสตร์รายตัว ---
                    if sym == "SIRI":
                        if data['price'] >= 1.66: st.error("🔥 **ห้ามขายหมู!** ทะลุต้านใหญ่แล้ว รันยาว")
                        elif 1.62 <= data['price'] <= 1.63: st.warning("🎯 **Target Hit:** แบ่งขายไม้แรก (2,000 หุ้น)")
                    
                    if sym == "MTC":
                        st.info("🕒 **MTC Strategy:** ตั้งขาย 100 หุ้นที่ 39.75 (หนีมีเชิง)")
                        
                    if sym == "GPSC":
                        if data['rsi'] < 65 and data['rvol'] > 1.2: 
                            st.success("💎 **อย่าเพิ่งรีบขาย!** ทรงยังสวย วาฬยังอยู่ ระวังขายหมูซ้ำรอย")
                    
                    st.write(f"📡 **RSI:** {data['rsi']:.1f} | 🌊 **RVOL:** {data['rvol']:.2f}")
                    if data['rvol'] > 1.5: st.warning("🐳 วาฬบุก! วอลลุ่มเข้าผิดปกติ")
                else:
                    st.error(f"ไม่พบข้อมูล {sym}")

# --- TAB 2: MASTER LEDGER ---
with tab2:
    st.title("📓 สมุดบัญชีการรบ (Professional Ledger)")
    
    with st.expander("➕ ลงบันทึกการปิดไม้ (ขาย)", expanded=True):
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            l_date_buy = st.date_input("วันที่ซื้อ", datetime.now())
            l_symbol = st.selectbox("หุ้นที่ขาย", st.session_state.custom_watchlist)
            l_lot_no = st.selectbox("ขายไม้ที่", ["ไม้ 1", "ไม้ 2", "ไม้ 3", "ปิดรอบ (All Out)"])
        with lc2:
            l_date_sell = st.date_input("วันที่ขาย", datetime.now())
            l_buy_price = st.number_input("ราคาต้นทุน (เฉลี่ย)", value=1.000, step=0.001, format="%.3f")
            l_sell_price = st.number_input("ราคาที่ขายได้", value=1.000, step=0.001, format="%.3f")
        with lc3:
            l_qty = st.number_input("จำนวนหุ้นที่ขาย", value=100, step=100)
            l_note = st.text_input("หมายเหตุ (เช่น ขายหมู, ตามแผน, ถอนทุน)")
            
            # คำนวณเงินและค่าธรรมเนียม
            g_buy = l_buy_price * l_qty
            g_sell = l_sell_price * l_qty
            total_fee = (g_buy + g_sell) * TOTAL_FEE_FACTOR
            n_profit = (g_sell - g_buy) - total_fee
            
            st.write(f"💼 ค่าธรรมเนียม+VAT: {total_fee:,.2f} บ.")
            st.subheader(f"กำไรสุทธิ: {n_profit:,.2f} บ.")
            
            if st.button("💾 บันทึกลงสมุดบัญชี"):
                new_entry = {
                    "วันที่ซื้อ": l_date_buy,
                    "วันที่ขาย": l_date_sell,
                    "หุ้น": l_symbol,
                    "ไม้ที่": l_lot_no,
                    "จำนวน": l_qty,
                    "ต้นทุน": l_buy_price,
                    "ราคาขาย": l_sell_price,
                    "ค่าต๋ง": total_fee,
                    "กำไรสุทธิ": n_profit,
                    "หมายเหตุ": l_note
                }
                st.session_state.trade_history.append(new_entry)
                st.toast("บันทึกสำเร็จ!")

    # สรุปตาราง Ledger
    if st.session_state.trade_history:
        df_ledg = pd.DataFrame(st.session_state.trade_history)
        st.markdown("---")
        st.subheader("📋 รายงานสรุปผลงานรายไม้")
        st.dataframe(df_ledg, use_container_width=True, hide_index=True)
        
        # สรุปภาพรวม
        total_p = df_ledg["กำไรสุทธิ"].sum()
        after_gemini = total_p - GEMINI_PRO_COST
        
        r1, r2, r3 = st.columns(3)
        r1.metric("💰 กำไรสุทธิสะสม", f"{total_p:,.2f} บ.")
        r2.metric("🤖 กำไรหลังหักค่า Gemini", f"{after_gemini:,.2f} บ.")
        
        if after_gemini > 0:
            r3.success(f"🎉 ตอนนี้พี่โบ้ได้ใช้ Gemini Pro ฟรีแล้ว! (กำไรเหลือ {after_gemini:,.2f})")
        else:
            r3.warning(f"🕒 อีก {abs(after_gemini):,.2f} บาท จะได้ค่าแอปคืน")

        if st.button("🗑️ ล้างข้อมูล Ledger ทั้งหมด"):
            st.session_state.trade_history = []
            st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลการขาย... เริ่มบันทึกเพื่อดูความแม่นยำรายไม้ครับพี่โบ้!")

st.markdown("---")
st.caption("v5.0 Master Ledger — ต่อยอดเป้าหมายแสนแรกด้วยระบบบัญชีมืออาชีพ")
