import streamlit as st
import pandas as pd
import yfinance as yf

# ==========================================
# ⚙️ CONFIG & BUG FIX: RSI ENGINE
# ==========================================
st.set_page_config(page_title="GeminiBo Strategist v3.1", page_icon="🏗️", layout="wide")

def get_accurate_rsi(symbol):
    try:
        # ดึงข้อมูลย้อนหลัง 2 เดือนเพื่อให้คำนวณ RSI 14 วันได้แม่นยำ
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="2mo", interval="1d")
        
        if df.empty or len(df) < 20: return 0.0, 50.0
        
        # คำนวณ RSI แบบ Wilder's Smoothing (มาตรฐานกราฟเทคนิค)
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        # ป้องกันการหารด้วยศูนย์
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(df['Close'].iloc[-1]), float(rsi.iloc[-1])
    except:
        return 0.0, 50.0

# ==========================================
# 📊 STRATEGIST DASHBOARD
# ==========================================
st.sidebar.title("🏗️ GeminiBo v3.1")
menu = st.sidebar.radio("เลือกโหมด", ["📊 วิเคราะห์สถานการณ์", "💰 กระดานบัญชี"])

targets = ["SIRI", "WHA", "MTC", "PLANB", "SAWAD", "THCOM"]

if menu == "📊 วิเคราะห์สถานการณ์":
    st.title("🚀 Situation Room: Accurate Technicals")
    cols = st.columns(3)
    
    for i, symbol in enumerate(targets):
        with cols[i % 3]:
            with st.expander(f"📈 วิเคราะห์ {symbol}", expanded=True):
                price, rsi_val = get_accurate_rsi(symbol)
                
                # แสดงค่าที่แยกจากกันชัดเจน
                st.metric(f"ราคา {symbol}", f"{price:.2f}")
                st.write(f"📡 RSI (14): **{rsi_val:.2f}**")
                
                m_bid = st.number_input(f"Bid Vol ({symbol})", value=1000000, key=f"b_{symbol}")
                m_off = st.number_input(f"Offer Vol ({symbol})", value=3000000, key=f"o_{symbol}")
                ratio = m_off / m_bid if m_bid > 0 else 0
                
                # --- 🤖 ระบบแนะนำ (AI Strategy Advisor) ---
                st.markdown("---")
                if rsi_val > 70:
                    st.error(f"🚨 {symbol}: 'ตึงมาก' (Overbought)\nห้ามเคาะขวา! รอจังหวะขาย")
                elif rsi_val < 35:
                    st.success(f"💎 {symbol}: 'ถูกมาก' (Oversold)\nจังหวะช้อน/ถัวไม้ล่าง")
                elif ratio < 0.6:
                    st.warning(f"🚀 {symbol}: 'ทางสะดวก'\nเจ้ามือเตรียมลาก ตามกระแส!")
                else:
                    st.info(f"⚖️ {symbol}: 'ดึงเช็ง'\nรอเลือกทาง นั่งทับมือก่อน")

# ==========================================
# 💰 กระดานบัญชี (สรุปกำไร/ขาดทุน)
# ==========================================
elif menu == "💰 กระดานบัญชี":
    st.title("💰 Portfolio Summary")
    grand_profit = 0.0
    for symbol in targets:
        with st.expander(f"📝 บันทึก {symbol}", expanded=True):
            c1, c2, c3 = st.columns(3)
            # กรอกหุ้นเดิม
            v_old = c1.number_input(f"หุ้นเดิม ({symbol})", value=0, key=f"vo_{symbol}")
            p_old = c1.number_input(f"ราคาทุน ({symbol})", value=0.0, format="%.2f", key=f"po_{symbol}")
            # กรอกหุ้นถัว/ซื้อเพิ่ม
            v_new = c2.number_input(f"หุ้นเพิ่ม ({symbol})", value=0, key=f"vn_{symbol}")
            p_new = c2.number_input(f"ราคาถัว ({symbol})", value=0.0, format="%.2f", key=f"pn_{symbol}")
            # กรอกการขาย
            v_out = c3.number_input(f"จำนวนขาย ({symbol})", value=0, key=f"vs_{symbol}")
            p_out = c3.number_input(f"ราคาขาย ({symbol})", value=0.0, format="%.2f", key=f"ps_{symbol}")
            
            # คำนวณ
            total_v = v_old + v_new
            avg_p = ((v_old * p_old) + (v_new * p_new)) / total_v if total_v > 0 else 0.0
            profit = (p_out - avg_p) * v_out if v_out > 0 else 0.0
            grand_profit += profit
            st.write(f"📊 ทุนเฉลี่ยใหม่: **{avg_p:.2f}** | กำไรตัวนี้: **{profit:,.2f}**")
            
    st.sidebar.metric("🏆 กำไร/ขาดทุนรวม", f"{grand_profit:,.2f}")
