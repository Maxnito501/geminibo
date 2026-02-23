# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & HYBRID ENGINE (v11.9)
# ==========================================
st.set_page_config(page_title="GeminiBo v11.9: Recovery & Target", layout="wide", page_icon="⚔️")

# หน่วงเวลา 45 วินาทีตามพี่โบ้สั่ง
SCAN_INTERVAL = 45 

# 🛡️ ภารกิจหลัก: เฝ้าขาย (Exit Strategy)
EXIT_MISSION = {
    "MTC": {"avg": 38.50, "target": 38.75, "qty": 400, "note": "รอคืนทุน 38.50 หรือกำไร 38.75"},
    "HANA": {"avg": 18.90, "target": 19.50, "qty": 300, "note": "เป้าปล่อย 19.50 (ต้านบ่าย)"},
    "SIRI": {"avg": 1.47, "target": 1.63, "qty": 4700, "note": "เป้า 1.63 ล็อกกำไร / 2,700 รอปันผล"}
}

# 🏹 ภารกิจรอง: เฝ้าซื้อ (Entry Sniper)
ENTRY_MISSION = {
    "PTT": {"entry": 36.50, "info": "รอช้อนหลัง XD 5 มี.ค."},
    "ROJNA": {"entry": 6.80, "info": "รอวอลลุ่มเข้า > 10M"},
    "AMATA": {"entry": 24.50, "info": "นิคมเบรกเอาท์ตามวาฬ"},
    "GULF": {"entry": 60.00, "info": "พลังงาน High Growth"},
    "BBL": {"entry": 175.0, "info": "สะสมทัพหลวง"},
    "BAM": {"entry": 7.55, "info": "ปันผลจ่ายค่าแอป"}
}

def fetch_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1d", interval="1m")
        if df.empty: return None
        return {"price": df['Close'].iloc[-1], "change": ((df['Close'].iloc[-1]-df['Open'].iloc[0])/df['Open'].iloc[0])*100}
    except: return None

# ==========================================
# 📊 MAIN DASHBOARD
# ==========================================
st.title("⚔️ GeminiBo v11.9: Recovery & Target Pro")
st.caption(f"📅 รอบสแกน: {SCAN_INTERVAL} วินาที | อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}")

with st.sidebar:
    st.header("🛡️ สถานะกองทัพ")
    st.metric("SET Index", "1,501.73", "+22.02")
    st.markdown("---")
    st.write("🎯 **ภารกิจวันนี้:**")
    st.write("1. ปล่อย MTC ที่ทุน 38.50")
    st.write("2. ดักขาย HANA 19.50")
    st.write("3. รวบกำไร SIRI 1.63")

# --- SECTION 1: 🚩 โซนเฝ้าขาย (RECOVERY ZONE) ---
st.subheader("🚩 ภารกิจสลัดดอย & ล็อกกำไร (SIRI, HANA, MTC)")
cols_exit = st.columns(3)
for i, (sym, cfg) in enumerate(EXIT_MISSION.items()):
    data = fetch_data(sym)
    with cols_exit[i]:
        with st.container(border=True):
            st.header(f"🛡️ {sym}")
            if data:
                pnl = (data['price'] - cfg['avg']) * cfg['qty']
                color = "green" if pnl >= 0 else "red"
                st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}", f"{pnl:,.2f} บ.")
                
                if data['price'] >= cfg['target']:
                    st.success(f"🎯 **TARGET HIT!** ปล่อยของที่ {cfg['target']}")
                elif data['price'] >= cfg['avg']:
                    st.warning("⚖️ **BREAKEVEN:** เท่าทุนแล้ว พิจารณาถอนทัพ")
                else:
                    st.info(f"⏳ {cfg['note']}")
            else: st.write("Scanning...")

# --- SECTION 2: 🏹 โซนเฝ้าซื้อ (ENTRY RADAR) ---
st.markdown("---")
st.subheader("🏹 หน่วยสอดแนมหุ้นใหม่ (Entry Sniper)")
cols_entry = st.columns(3)
items = list(ENTRY_MISSION.items())
for i in range(len(items)):
    sym, cfg = items[i]
    data = fetch_data(sym)
    with cols_entry[i % 3]:
        with st.container(border=True):
            if data:
                st.write(f"**{sym}**")
                st.metric("Price", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                st.caption(f"📍 จุดรับ: {cfg['entry']} | {cfg['info']}")

# ================= =========================
# 🔄 REFRESH
# ==========================================
time.sleep(SCAN_INTERVAL)
st.rerun()
