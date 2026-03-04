# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE
# ==========================================
st.set_page_config(page_title="GeminiBo v44.5: The Sovereign", layout="wide", page_icon="🛡️")

# ค่าธรรมเนียมเฉลี่ย
FEE_RATE = 0.00168 

def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty: return None
        
        price = df['Close'].iloc[-1]
        ema5 = df['Close'].ewm(span=5, adjust=False).mean().iloc[-1]
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        return {"price": price, "rsi": rsi, "ema5": ema5}
    except: return None

# ==========================================
# 📊 SIDEBAR: เสบียงและยอดทวงคืน
# ==========================================
with st.sidebar:
    st.header("🛡️ กองบัญชาการจอมทัพ")
    # ข้อมูลกระแสเงินสดที่พี่โบ้แจ้งล่าสุด
    dime_cash = 12783.0 # รวมจากการขาย JAS
    ktb_cash = 18000.0
    total_cash = dime_cash + ktb_cash
    
    st.metric("เสบียงรวม (Dime + KTB)", f"{total_cash:,.2f} บ.")
    st.info(f"Dime: {dime_cash:,.2f} | KTB: {ktb_cash:,.2f}")
    
    st.markdown("---")
    # ยอดแผล MTC 1,000 + JAS 600
    loss_target = 1600.0
    st.subheader("🎯 ภารกิจทวงคืน")
    st.error(f"ยอดติดลบสะสม: {loss_target:,.2f} บ.")
    
    # คำนวณความคืบหน้า (สมมติจากกำไร Unrealized)
    st.caption("วินัย: ไม่จำเป็นไม่ถัว คัตได้คัต")

# ================= =========================
# 🏹 MAIN BATTLE STATION
# ==========================================
st.title("🛡️ GeminiBo v44.5: The Sovereign Mode")
st.write(f"📡 สถานะ: {'🟢 ออนไลน์'} | อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}")

# รายชื่อหุ้นในมือและหุ้นเป้าหมาย
owned_list = ["PTT", "SIRI", "SCB", "TISCO", "HMPRO", "PTG"]
hunting_list = ["LH", "BH", "TRUE", "CPF"]

tab1, tab2 = st.tabs(["🔥 ขุนพลในสนาม (Owned)", "🏹 หน่วยล่าเป้าหมาย (Hunting)"])

with tab1:
    cols = st.columns(3)
    for i, sym in enumerate(owned_list):
        data = get_stock_data(sym)
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(sym)
                if data:
                    st.metric("ราคาตลาด", f"{data['price']:.2f}")
                    st.write(f"RSI: {data['rsi']:.1f}")
                    
                    # คำสั่งยุทธการ
                    if sym == "PTT":
                        st.info("⌛ พรุ่งนี้ XD: ถือรับปันผล 1.40 บ.")
                    elif sym == "SIRI":
                        st.success("💎 ทุน 1.47 แกร่งมาก ถือรับทรัพย์")
                    elif data['rsi'] < 30:
                        st.warning("⚖️ ก้นเหว: รอปลาบยอดรีบาวด์")
                    else:
                        st.write("📡 เฝ้าตามวินัย")
                else:
                    st.write("กำลังดึงข้อมูล...")

with tab2:
    st.subheader("เป้าหมายใหม่: LH และขุนพลต้านสงคราม")
    hcols = st.columns(2)
    for i, sym in enumerate(hunting_list):
        data = get_stock_data(sym)
        with hcols[i % 2]:
            with st.container(border=True):
                st.header(sym)
                if data:
                    st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}")
                    if sym == "LH":
                        st.success("🎯 เป้าช้อน: 3.98 - 4.00 (Yield 7.5%)")
                    elif sym == "BH":
                        st.info("🏥 จุดรับสะสม: 168.0 - 170.0")
                    
                    if data['rsi'] < 35:
                        st.warning("🏹 สัญญาณสไนเปอร์: ราคาโดนกดขี่!")
                else:
                    st.write("รอกระแสเงิน...")

st.markdown("---")
st.markdown("""
<div style="background-color: #1e293b; padding: 20px; border-radius: 15px; border-left: 5px solid #3b82f6;">
    <h4 style="color: white; margin-bottom: 10px;">สาส์นจอมทัพ: แผนกู้เสบียง</h4>
    <p style="color: #cbd5e1; font-style: italic; font-size: 14px;">
        "พี่โบ้ครับ เราล้างพอร์ต MTC และ JAS เพื่อเอาเงินสด 12,000+ ใน Dime กลับมา... <br>
        พรุ่งนี้เรามีหน้าที่แค่ 'ถือนิ่งๆ' รับปันผล PTT และตั้งเบ็ดตกมังกร LH ที่ราคา 4.00 ครับ... <br>
        ยอดเสีย 1,600 บาท จะหายไปเมื่อปันผลและกำไรจาก LH ไหลเข้าพอร์ตครับ!"
    </p>
</div>
""", unsafe_allow_html=True)
