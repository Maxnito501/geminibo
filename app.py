import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v4.7 Opportunity Sniper)
# ==========================================
st.set_page_config(page_title="GeminiBo v4.7: Opportunity Sniper", layout="wide", page_icon="🏹")

# ค่าธรรมเนียมเฉลี่ย (รวม VAT)
TOTAL_FEE_FACTOR = 0.00168 

def get_advanced_metrics(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < 10: return None
        
        price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        change_pct = ((price - prev_price) / prev_price) * 100
        
        # RSI & RVOL
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
# 📊 SIDEBAR: MTC TACTICAL (100/100 Plan)
# ==========================================
st.sidebar.title("⚔️ ยุทธวิธี MTC 100/100")
st.sidebar.info("แผน: ขาย 100 ที่ 39.75 | รัน 100 สู่ 42.00")

with st.sidebar.expander("🐌 สถานะ MTC รายงานตัว", expanded=True):
    current_mtc = st.number_input("ราคา MTC ปัจจุบัน", value=39.50, step=0.25)
    if current_mtc >= 39.75:
        st.success("🎯 **ถึงเป้าแรก!** ขาย 100 หุ้นทันที")
    elif current_mtc >= 40.00:
        st.error("🔥 **BREAKOUT!** 100 หุ้นที่เหลือรันยาว")

st.sidebar.warning("⚠️ **คำเตือนวันศุกร์:** ระวังหุ้นร้อน (Hot Stocks) เทขายทำกำไรช่วงบ่าย")

# ==========================================
# 🏹 MAIN DASHBOARD
# ==========================================
st.title("🏹 Opportunity Sniper v4.7")

# ส่วนสแกนหาตัวซิ่งแทนที่ MTC (กรองหุ้นร้อนออก)
st.subheader("🔍 สแกนหา 'หุ้นซิ่งเทรนสวย' (เลี่ยงหุ้นร้อนเกินไป)")
watchlist = ["WHA", "ROJNA", "AMATA", "SIRI", "MTC", "CPALL", "SAWAD", "PLANB", "THCOM"]
scan_results = []
for sym in watchlist:
    data = get_advanced_metrics(sym)
    if data:
        status = "รอดูเชิง"
        # เพิ่มเงื่อนไข: หุ้นที่ RSI < 70 เพื่อเลี่ยงตัวที่ร้อนเกินไป (Overbought)
        if data['rvol'] > 1.3 and 45 < data['rsi'] < 65: status = "🚀 พร้อมซิ่ง (เทรนดี)"
        elif data['rsi'] >= 70: status = "🔥 หุ้นร้อน (ระวังโดนเท)"
        elif data['rvol'] < 0.8: status = "🐢 เฉื่อย/พักฐาน"
        
        scan_results.append({
            "หุ้น": sym, "ราคา": f"{data['price']:.2f}",
            "RVOL": round(data['rvol'], 2), "RSI": round(data['rsi'], 1), "สถานะ": status
        })

df_scan = pd.DataFrame(scan_results)
st.dataframe(df_scan, use_container_width=True, hide_index=True)

# ส่วนเจาะลึก MTC และ SIRI
st.markdown("---")
cols = st.columns(3)
selected_stocks = st.multiselect("ส่องกล้อง:", watchlist, default=["MTC", "SIRI", "WHA"])

for i, sym in enumerate(selected_stocks[:3]):
    data = get_advanced_metrics(sym)
    with cols[i]:
        with st.container(border=True):
            if data:
                st.header(f"🛡️ {sym}")
                st.metric("ราคา", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                
                if sym == "MTC":
                    st.write(f"📊 RVOL: **{data['rvol']:.2f}**")
                    if data['price'] < 39.75:
                        st.info("🕒 รอเป้าหมาย 39.75 (หนีมีเชิง)")
                    else:
                        st.success("✅ เป้า 39.75 สำเร็จ!")

                if sym == "SIRI":
                    st.write(f"📈 RSI: **{data['rsi']:.1f}**")
                    if data['price'] >= 1.62:
                        st.warning("🎯 แบ่งทำกำไรตามแผน")
                
                st.write(f"📡 RSI: {data['rsi']:.1f} | 🌊 RVOL: {data['rvol']:.2f}")

st.markdown("---")
st.caption("การถือหุ้นที่มีแต้มต่อ คือหัวใจของการเป็นผู้ชนะในระยะยาว — v4.7 Anti-Pig & Opportunity Sniper")
