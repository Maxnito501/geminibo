import streamlit as st
import pandas as pd
import yfinance as yf

# ==========================================
# ⚙️ CONFIG & STABLE RSI ENGINE
# ==========================================
st.set_page_config(page_title="GeminiBo Strategist v3.0", page_icon="🏗️", layout="wide")

def get_market_data(symbol):
    try:
        df = yf.download(f"{symbol}.BK", period="1mo", interval="1d", progress=False)
        if df.empty or len(df) < 15: return 0.0, 50.0
        last_p = float(df['Close'].iloc[-1])
        delta = df['Close'].diff()
        up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
        ma_up, ma_down = up.rolling(window=14).mean(), down.rolling(window=14).mean()
        rs = ma_up / ma_down
        rsi = 100 - (100 / (1 + rs))
        return last_p, float(rsi.iloc[-1])
    except: return 0.0, 50.0

# ==========================================
# 📊 MAIN DASHBOARD
# ==========================================
st.sidebar.title("🏗️ GeminiBo v3.0")
menu = st.sidebar.radio("เลือกโหมดใช้งาน", ["📊 วิเคราะห์เจ้ามือ & หน้าตัก", "🧮 Recovery Tools"])

if menu == "📊 วิเคราะห์เจ้ามือ & หน้าตัก":
    st.title("🚀 Strategist Dashboard: Full Control")
    targets = ["SIRI", "WHA", "MTC", "PLANB", "SAWAD", "THCOM"]
    
    # --- ส่วนที่ 1: วิเคราะห์สถานการณ์ (Strategy Advisor) ---
    st.header("🔍 1. อ่านใจเจ้ามือ (RSI + Volume Matrix)")
    cols = st.columns(3)
    for i, symbol in enumerate(targets):
        with cols[i % 3]:
            with st.expander(f"📈 วิเคราะห์ {symbol}", expanded=True):
                price, rsi_val = get_market_data(symbol)
                st.metric(f"ราคา {symbol}", f"{price:.2f}")
                st.write(f"📡 **RSI (14): {rsi_val:.2f}**")
                
                m_bid = st.number_input(f"Bid Vol ({symbol})", value=1000000, key=f"b_{symbol}")
                m_off = st.number_input(f"Offer Vol ({symbol})", value=3000000, key=f"o_{symbol}")
                ratio = m_off / m_bid if m_bid > 0 else 0
                
                # --- 🤖 🤖 ระบบวิเคราะห์สถานการณ์ (กลับมาแล้ว!) ---
                st.markdown("**💡 คำแนะนำจาก AI:**")
                if rsi_val > 65 and ratio > 3:
                    st.error("🆘 สถานการณ์: 'เจ้าขวาง/ล่อแมงเม่า' \n\n **ทำอย่างไร:** ห้ามถัว! ตั้งขายดักหน้ากำแพง (เช่น 4.26)")
                elif rsi_val < 40 and ratio < 0.8:
                    st.success("💎 สถานการณ์: 'เจ้าเก็บของ/ช้อน' \n\n **ทำอย่างไร:** จังหวะเบิ้ลไม้ถัวล่างสุดตามกราฟ")
                elif ratio < 0.5 and rsi_val > 50:
                    st.warning("🚀 สถานการณ์: 'ทางสะดวก/ลากจริง' \n\n **ทำอย่างไร:** Let Profit Run ดักไม้สุดท้าย 1.60")
                else:
                    st.info("⚖️ สถานการณ์: 'ดึงเช็ง/เลือกทาง' \n\n **ทำอย่างไร:** นั่งทับมือ รอตามกระแสราคาปิด")

    st.markdown("---")

    # --- ส่วนที่ 2: กระดานคิดราคา & สรุปกำไร (กลับมาแล้ว!) ---
    st.header("💰 2. บัญชีคุมหน้าตัก (Portfolio Dashboard)")
    grand_total_profit = 0.0
    
    for symbol in targets:
        with st.expander(f"📝 บันทึกบัญชี {symbol}"):
            c1, c2, c3 = st.columns(3)
            
            # ข้อมูลต้นทุน (ทุนเดิม + ซื้อเพิ่ม)
            vol_old = c1.number_input(f"จำนวนหุ้นเดิม ({symbol})", value=0, key=f"vo_{symbol}")
            price_old = c1.number_input(f"ราคาที่ได้มา ({symbol})", value=0.0, format="%.2f", key=f"po_{symbol}")
            
            vol_new = c2.number_input(f"จำนวนซื้อเพิ่ม/ถัว ({symbol})", value=0, key=f"vn_{symbol}")
            price_new = c2.number_input(f"ราคาที่ซื้อเพิ่ม ({symbol})", value=0.0, format="%.2f", key=f"pn_{symbol}")
            
            # ข้อมูลการขาย
            vol_sell = c3.number_input(f"จำนวนที่ขาย ({symbol})", value=0, key=f"vs_{symbol}")
            price_sell = c3.number_input(f"ราคาที่ขาย ({symbol})", value=0.0, format="%.2f", key=f"ps_{symbol}")
            
            # คำนวณต้นทุนเฉลี่ย
            total_vol = vol_old + vol_new
            avg_cost = ((vol_old * price_old) + (vol_new * price_new)) / total_vol if total_vol > 0 else 0.0
            
            # คำนวณกำไร/ขาดทุน
            p_l = (price_sell - avg_cost) * vol_sell if vol_sell > 0 else 0.0
            grand_total_profit += p_l
            
            st.write(f"📊 ทุนเฉลี่ย: **{avg_cost:.2f}** | จำนวนหุ้นรวม: **{total_vol:,}**")
            st.subheader(f"💵 กำไร/ขาดทุน {symbol}: {p_l:,.2f} บาท")

    st.sidebar.markdown("---")
    st.sidebar.header("🏆 สรุปผลงานวันนี้")
    st.sidebar.metric("กำไร/ขาดทุนรวม (บาท)", f"{grand_total_profit:,.2f}")
    if grand_total_profit > 0: st.sidebar.balloons()
