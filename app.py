# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v6.2 Panic Sniper)
# ==========================================
st.set_page_config(page_title="GeminiBo v6.2: Panic Sniper", layout="wide", page_icon="🏹")

def get_panic_metrics(symbol):
    """ วิเคราะห์จังหวะ 'ช้อน' ในภาวะตลาดตกใจ """
    try:
        symbol = symbol.strip().upper()
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1d", interval="1m")
        df_daily = ticker.history(period="1mo", interval="1d")
        
        if df.empty: return None
        
        curr_p = df['Close'].iloc[-1]
        change = ((curr_p - df_daily['Close'].iloc[-1]) / df_daily['Close'].iloc[-1]) * 100
        
        # คำนวณ RSI รายนาทีเพื่อดูจุดกลับตัว
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi_m = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if not loss.empty and loss.iloc[-1] != 0 else 50
        
        # แนวรับสำคัญจาก Low ในรอบเดือน
        support_lv = df_daily['Low'].min()
        
        return {
            "price": curr_p,
            "change": change,
            "rsi_m": rsi_m,
            "support": support_lv,
            "vol_surge": df['Volume'].iloc[-5:].sum() > df['Volume'].mean() * 2 # วอลลุ่มเข้าที่แนวรับหรือไม่
        }
    except: return None

# ==========================================
# 📊 PANIC COMMAND CENTER
# ==========================================
st.title("🏹 GeminiBo v6.2: Panic Sniper Edition")
st.subheader("🚨 ตรวจจับจังหวะ 'ช้อน' (Bottom Fishing)")

# สรุปภาวะตลาดจากรูปที่พี่โบ้ส่งมา
st.sidebar.error("🚩 ตลาดติดลบแรง (-18.61)")
st.sidebar.write("กลยุทธ์: 'นิ่งสงบ สยบแรงเทขาย' ดักช้อนที่แนวรับสำคัญ")

watchlist = ["MTC", "SIRI", "WHA", "GPSC"]
cols = st.columns(len(watchlist))

for i, sym in enumerate(watchlist):
    data = get_panic_metrics(sym)
    with cols[i]:
        with st.container(border=True):
            if data:
                st.header(f"🛡️ {sym}")
                st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                
                # --- ยุทธศาสตร์การช้อน ---
                if sym == "MTC":
                    st.write("📍 **โซนช้อน:** 38.00 - 38.25")
                    if data['price'] <= 38.25:
                        st.success("✅ **BUY ZONE!**\nลงมาลึกตามแผนพี่โบ้ เตรียมไม้ 1 ได้เลย")
                    if data['rsi_m'] < 30:
                        st.warning("🌊 **Oversold:** แรงขายใกล้หมด ลุ้นเด้งกลับ")
                
                if sym == "SIRI":
                    st.write("📍 **โซนช้อน:** 1.50 - 1.54")
                    if data['price'] <= 1.55:
                        st.info("🕒 **รอดูเชิง:** RSI กำลังคลายความร้อนจาก 91")
                
                # สัญญาณวอลลุ่มกระตุก (Whale Re-entry)
                if data['vol_surge']:
                    st.warning("🐳 **วาฬเริ่มช้อน!**\nมีแรงซื้อสวนที่แนวรับ")
                
                st.write(f"📡 RSI (1m): {data['rsi_m']:.1f}")
                st.progress(min(data['rsi_m']/100, 1.0))
            else:
                st.error(f"ไม่พบข้อมูล {sym}")

# ==========================================
# 📓 บันทึกแผนการช้อน
# ==========================================
st.markdown("---")
with st.expander("📓 บันทึกแผนการรบ (ช้อนหุ้นแดง)"):
    col1, col2 = st.columns(2)
    with col1:
        st.write("**แผน MTC:** ดัก 38.00 ถือลุ้นเด้งกลับไป 40.00")
        st.write("**แผน SIRI:** รอรับที่ 1.52-1.54 เพื่อรันรอบใหม่")
    with col2:
        if st.button("🔄 อัปเดตราคา Real-time"):
            st.rerun()

st.caption("v6.2 Panic Sniper — 'ในวิกฤตมีโอกาส จอมทัพที่นิ่งที่สุดคือผู้ชนะ'")
