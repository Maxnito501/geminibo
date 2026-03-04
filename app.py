# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & REBOUND ENGINE (v44.5)
# ==========================================
st.set_page_config(page_title="GeminiBo v44.5: The Sovereign", layout="wide", page_icon="🛡️")

def get_rebound_intel(symbol, avg_cost=0.0):
    """ วิเคราะห์สัญญาณรีบาวด์ตาม Elliott Wave / MACD / RSI """
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="3mo", interval="1d")
        if df.empty or len(df) < 26: return None
        
        price = df['Close'].iloc[-1]
        
        # 1. MACD Calculation
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        
        # 2. RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # 3. Wave & Rebound Logic
        status = "⚖️ พักฐาน"
        advice = "ถือนิ่งๆ รอดูเชิง"
        color = "white"
        
        if rsi < 30:
            status = "🌊 Wave C Bottom (Oversold)"
            advice = "จุดสไนเปอร์! จ่อรีบาวด์แรง"
            color = "blue"
        elif macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
            status = "🚀 MACD Golden Cross"
            advice = "มังกรเงยหน้า! เริ่มสะสมเพิ่มได้"
            color = "green"
        elif avg_cost > 0 and price < avg_cost * 0.92:
            status = "🚨 แผลลึก (Waterfall)"
            advice = "ห้ามถัวไม้เดียว! รอฐาน 5.2"
            color = "red"

        return {"price": price, "rsi": rsi, "macd": macd.iloc[-1], "status": status, "advice": advice, "color": color}
    except: return None

# ==========================================
# 📊 SIDEBAR: กระแสเงินสดและยอดทวงคืน
# ==========================================
with st.sidebar:
    st.header("🛡️ กองบัญชาการจอมทัพ")
    # เสบียงพี่โบ้ล่าสุด
    dime_cash = 8383.0 
    inx_cash = 1000.0 # หลังหัก RMF 5,000
    ktb_cash = 18000.0
    st.metric("เสบียง Dime (กระสุนหลัก)", f"{dime_cash:,.2f} บ.")
    st.info(f"สำรอง KTB: {ktb_cash:,.2f} (ห้ามแตะ)")
    
    st.markdown("---")
    st.subheader("🎯 ภารกิจทวงคืนแสนแรก")
    loss_target = 1600.0 # แผลสะสม MTC + JAS
    st.error(f"ยอดแผลสะสม: {loss_target:,.2f} บ.")
    st.caption("ปันผล PTT/SCB จะมาเย็บแผลนี้")

# ================= =========================
# 🏹 MAIN BATTLE STATION
# ==========================================
st.title("🛡️ GeminiBo v44.5: The Sovereign Mode")
st.write(f"📡 ออนไลน์ | อัปเดตขุนพล 10 ตัว | วันที่: {datetime.now().strftime('%d/%m/%Y')}")

# (กฎข้อ 5) รายชื่อขุนพลจริงของพี่โบ้
my_army = [
    {"sym": "PTT", "qty": 100, "avg": 33.00},
    {"sym": "SIRI", "qty": 2300, "avg": 1.47},
    {"sym": "SCB", "qty": 25, "avg": 135.50},
    {"sym": "TISCO", "qty": 100, "avg": 112.50},
    {"sym": "AOT", "qty": 200, "avg": 54.50},
    {"sym": "BH", "qty": 50, "avg": 186.00},
    {"sym": "CPAXT", "qty": 300, "avg": 16.30},
    {"sym": "WHA", "qty": 1000, "avg": 4.18},
    {"sym": "PTG", "qty": 200, "avg": 9.60},
    {"sym": "HMPRO", "qty": 400, "avg": 7.05}
]

# (หุ้นสวนกระแสสงคราม 3 ตัว)
war_shields = ["PTTEP", "BDMS", "CPALL"]

t1, t2 = st.tabs(["🔥 ขุนพลในสนาม (Owned)", "🛡️ หน่วยสอดแนมต้านสงคราม (War Shields)"])

with t1:
    st.subheader("วิเคราะห์จุดรีบาวด์รายตัว")
    cols = st.columns(3)
    for i, stock in enumerate(my_army):
        data = get_rebound_intel(stock['sym'], stock['avg'])
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {stock['sym']}")
                if data:
                    st.metric("ราคาตลาด", f"{data['price']:.2f}")
                    st.markdown(f"**สถานะ:** :{data['color']}[{data['status']}]")
                    st.write(f"💬 {data['advice']}")
                    st.caption(f"ทุนพี่: {stock['avg']:.2f} | RSI: {data['rsi']:.1f}")
                else: st.write("รอดึงข้อมูล...")

with t2:
    st.subheader("3 ขุนพลหลบภัยยามสงคราม")
    wcols = st.columns(3)
    for i, sym in enumerate(war_shields):
        data = get_rebound_intel(sym)
        with wcols[i]:
            with st.container(border=True):
                st.header(sym)
                if data:
                    st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}")
                    if sym == "PTTEP": st.success("⛽ War Beneficiary (น้ำมันพุ่ง)")
                    if sym == "BDMS": st.info("🏥 Safe Haven (โรงพยาบาลแกร่ง)")
                    if sym == "CPALL": st.warning("🛒 Defensive (คนต้องกินต้องใช้)")
                    st.write(f"RSI: {data['rsi']:.1f}")
                else: st.write("รอกระแสเงิน...")

st.markdown("---")
st.markdown(f"""
<div style="background-color: #1e293b; padding: 25px; border-radius: 20px; border-left: 8px solid #f43f5e;">
    <h3 style="color: white; margin-bottom: 10px;">🛡️ สาส์นจอมทัพ: แผนรบ 5 มีนาคม (PTT XD)</h3>
    <p style="color: #cbd5e1; font-style: italic; font-size: 15px;">
        "พี่โบ้ครับ พรุ่งนี้คือวันรับเงินสดจาก PTT... เรามี BH, AOT และ CPAXT เป็นฐานใหม่ที่แข็งแกร่ง <br>
        แผนคือ: ใช้เงิน JAS (4,400) รอสอย AOT ที่ก้นเหว 47.00 และเฝ้า BH ที่ 170.00... <br>
        ในสงคราม คนใจนิ่งคือผู้ชนะ เราจะใช้ 'ปันผล' เป็นเกราะ และใช้ 'กำไร' เป็นดาบ ทวงแสนแรกคืนมาครับ!"
    </p>
</div>
""", unsafe_allow_html=True)
