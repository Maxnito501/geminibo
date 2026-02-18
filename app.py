import streamlit as st
import pandas as pd
import yfinance as yf

# ==========================================
# ⚙️ ENGINE: RSI คำนวณแยกอิสระ (ไม่พัง)
# ==========================================
st.set_page_config(page_title="GeminiBo v3.4: Whale Rider", page_icon="🏗️", layout="wide")

def get_accurate_rsi(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < 15: return 0.0, 50.0
        
        delta = df['Close'].diff()
        gain, loss = delta.clip(lower=0), -1 * delta.clip(upper=0)
        ma_g, ma_l = gain.rolling(window=14).mean(), loss.rolling(window=14).mean()
        rs = ma_g / ma_l
        rsi = 100 - (100 / (1 + rs))
        return float(df['Close'].iloc[-1]), float(rsi.iloc[-1])
    except: return 0.0, 50.0

# ==========================================
# 📊 STRATEGIST DASHBOARD (กลยุทธสู้เจ้า)
# ==========================================
st.sidebar.title("🏗️ GeminiBo v3.4")
menu = st.sidebar.radio("เลือกโหมด", ["🔥 กลยุทธ์สู้เจ้ามือ (Whale Rider)", "💰 กระดานบัญชี (หักค่าต๋ง)"])

targets = ["SIRI", "WHA", "MTC", "PLANB", "SAWAD", "THCOM"]

if menu == "🔥 กลยุทธ์สู้เจ้ามือ (Whale Rider)":
    st.title("🏹 Whale Rider: อ่านใจรายใหญ่ (Fixed Logic)")
    cols = st.columns(3)
    
    for i, sym in enumerate(targets):
        with cols[i % 3]:
            # บังคับให้ Streamlit สร้าง Key แยกกันด้วย f"{sym}"
            with st.expander(f"🐳 {sym} Strategy", expanded=True):
                # 1. ดึงข้อมูลแยกรายตัว
                p, r = get_accurate_rsi(sym)
                st.write(f"**ราคาล่าสุด:** {p:.2f} | **RSI (14):** {r:.2f}")
                
                # 2. กรอกวอลลุ่มแยกรายตัว
                b = st.number_input(f"Bid Vol ({sym})", value=1000000, key=f"b_{sym}")
                o = st.number_input(f"Offer Vol ({sym})", value=3000000, key=f"o_{sym}")
                ratio = o / b if b > 0 else 0
                
                # --- ❤️ หัวใจ: กลยุทธ์คำนวณแยกตามตัวแปร b, o, r ของแต่ละหุ้น ---
                st.markdown("---")
                if ratio > 4 and r > 60:
                    st.error(f"🆘 **{sym}: 'กำแพงลวง'**")
                    st.caption("เจ้าขวางหนักบีบคายของ ตั้งขายดักหน้ากำแพง!")
                elif ratio < 0.7 and r < 40:
                    st.success(f"💎 **{sym}: 'ซุ่มเก็บของ'**")
                    st.caption("วอลลุ่มขายบาง RSI ต่ำ จังหวะช้อนไม้แรก")
                elif ratio < 0.4 and r > 50:
                    st.warning(f"🚀 **{sym}: 'ลากกระชาก'**")
                    st.caption("ทางสะดวก เจ้าถอน Offer ออก Let Profit Run!")
                else:
                    st.info(f"⚖️ **{sym}: 'ดึงเช็ง/เลือกทาง'**")
                    st.caption("นั่งทับมือ รอดู Ticker ไม้ใหญ่ฝั่ง Buy")

# ... (ส่วนกระดานบัญชีหักค่าต๋ง 0.168% และเป้าหมาย 500 บาท คงเดิม) ...
