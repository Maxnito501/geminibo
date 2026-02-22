# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import json
import time
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v9.1 Strategic Autobot)
# ==========================================
st.set_page_config(page_title="GeminiBo v9.1: Strategic Autobot", layout="wide", page_icon="🤖")

# ข้อมูลยุทธศาสตร์ของพี่โบ้ (Strategy Map)
STRATEGY_MAP = {
    "SIRI": {"avg": 1.47, "target": 1.63, "qty_sell": 2000, "action": "ขายล็อกกำไรส่วนหนึ่ง"},
    "HANA": {"avg": 18.90, "target": 18.90, "qty_sell": 300, "action": "ถอนทัพหน้าเสมอ (เท่าทุน)"},
    "MTC": {"avg": 38.50, "target": 38.25, "qty_sell": 200, "action": "เฉือนเนื้อรักษาทัพ (Cut loss บางส่วน)"}
}

def send_line_alert(message, token, user_id):
    """ ส่งแจ้งเตือนผ่าน LINE (รองรับทั้ง Bot และ Notify) """
    if not token: return False
    
    # 1. ลองส่งผ่าน Messaging API (Bot)
    if user_id and len(user_id) > 10:
        url = 'https://api.line.me/v2/bot/message/push'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
        payload = {'to': user_id, 'messages': [{'type': 'text', 'text': message}]}
        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=5)
            if res.status_code == 200: return True
        except: pass

    # 2. Fallback ไป LINE Notify
    url_n = 'https://notify-api.line.me/api/notify'
    headers_n = {'Authorization': f'Bearer {token}'}
    try:
        res = requests.post(url_n, headers=headers_n, data={'message': message}, timeout=5)
        return res.status_code == 200
    except: return False

def analyze_whale_behavior(symbol, bid_ratio):
    """ วิเคราะห์พฤติกรรมวาฬและออกคำแนะนำตามแผนพี่โบ้ """
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1d", interval="1m")
        df_daily = ticker.history(period="5d", interval="1d")
        
        if df.empty: return None
        
        curr_price = df['Close'].iloc[-1]
        vol_5m = df['Volume'].iloc[-5:].sum()
        avg_vol_5d = df_daily['Volume'].mean() / 240
        rvol = vol_5m / (avg_vol_5d * 5) if avg_vol_5d > 0 else 1.0
        
        # ดึงแผนของหุ้นตัวนี้
        plan = STRATEGY_MAP.get(symbol, {})
        target = plan.get("target", 0)
        
        # ประเมินสถานะการซื้อขาย (Decision Logic)
        signal = "HOLD"
        reason = "รอจังหวะ"
        
        if curr_price >= target:
            if bid_ratio < 0.5:
                signal = "SELL_LIMIT"
                reason = "ราคาถึงเป้า + เจ้าถอนขวาง (ทางสะดวก) : เคาะขายได้เลย!"
            else:
                signal = "SELL_NOW"
                reason = "ราคาถึงเป้า แต่ออฟเฟอร์ขวางหนา : ชิงขายก่อนโดนทุบ"
        elif curr_price < target * 0.97: # กรณีหลุดแนวรับ
            signal = "STOP_LOSS"
            reason = "ราคาหลุดแนวรับสำคัญ : ถอยทัพรักษาชีวิต"

        return {
            "price": curr_price,
            "rvol": rvol,
            "ratio": bid_ratio,
            "signal": signal,
            "reason": reason,
            "target": target,
            "action_text": plan.get("action", "")
        }
    except: return None

# ==========================================
# 💾 SESSION STATE & SIDEBAR
# ==========================================
if 'last_alert' not in st.session_state: st.session_state.last_alert = {}

with st.sidebar:
    st.title("🤖 Autobot Settings")
    token = st.text_input("LINE Token", type="password")
    uid = st.text_input("LINE User ID (Optional)")
    auto_send = st.toggle("ส่งแจ้งเตือนอัตโนมัติเมื่อถึงเป้า", value=False)
    
    st.markdown("---")
    st.write("📈 **เป้าหมาย: แสนแรก (10 ปี)**")
    st.progress(0.48)

# ==========================================
# 🏹 MAIN COMMAND CENTER
# ==========================================
st.title("🏹 GeminiBo v9.1: Strategic Autobot")
st.caption(f"ระบบวิเคราะห์และแจ้งเตือนตามแผนแก้ดอย | {datetime.now().strftime('%H:%M:%S')}")

stocks = ["SIRI", "HANA", "MTC"]
cols = st.columns(3)

for i, sym in enumerate(stocks):
    # รับค่า Ratio จาก SetSmart
    ratio_val = st.number_input(f"SetSmart Ratio ({sym})", value=1.0, step=0.1, key=f"r_{sym}")
    data = analyze_whale_behavior(sym, ratio_val)
    
    with cols[i]:
        with st.container(border=True):
            st.header(f"🛡️ {sym}")
            if data:
                st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}")
                
                # แสดงสัญญาณเทรด (Signal)
                if data['signal'] in ["SELL_LIMIT", "SELL_NOW"]:
                    st.success(f"🎯 สัญญาณ: {data['signal']}")
                elif data['signal'] == "STOP_LOSS":
                    st.error(f"🚨 สัญญาณ: {data['signal']}")
                else:
                    st.info(f"⚖️ สัญญาณ: {data['signal']}")
                
                st.write(f"💬 {data['reason']}")
                st.markdown(f"📍 **แผน:** {data['action_text']}")
                
                # ระบบแจ้งเตือน
                alert_msg = f"\n[GeminiBo SIGNAL]\nหุ้น: {sym}\nราคา: {data['price']:.2f}\nสัญญาณ: {data['signal']}\nคำแนะนำ: {data['reason']}"
                
                if st.button(f"🔔 ส่งสัญญาณ {sym} เข้า LINE", key=f"btn_{sym}"):
                    if send_line_alert(alert_msg, token, uid):
                        st.toast("ส่งสัญญาณเข้ามือถือแล้ว!")
                    else:
                        st.error("ส่งไม่สำเร็จ เช็ค Token ครับ")
                
                # Auto Alert Logic (ส่งเมื่อถึงเป้าและยังไม่ได้ส่งในรอบนี้)
                if auto_send and data['signal'] != "HOLD":
                    now_hour = datetime.now().hour
                    if st.session_state.last_alert.get(sym) != now_hour:
                        send_line_alert(alert_msg, token, uid)
                        st.session_state.last_alert[sym] = now_hour
            else:
                st.write("รอข้อมูลสัญญาณ...")

st.markdown("---")
st.info("💡 **กลยุทธ์จอมทัพ:** ระบบจะเปรียบเทียบราคาจาก SetSmart กับเป้าหมาย 1.63, 18.90 และ 38.25 โดยอัตโนมัติ พร้อมวิเคราะห์ Whale Ratio เพื่อบอกว่าควร 'เคาะขวา' หรือ 'ตั้งรอ' ครับ")
