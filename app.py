import streamlit as st
import pandas as pd
import yfinance as yf

# ==========================================
# ⚙️ CONFIG & ENGINE (หักค่าต๋ง 0.157% + VAT 7%)
# ==========================================
st.set_page_config(page_title="GeminiBo Strategist v3.2", page_icon="🏗️", layout="wide")

# ค่าธรรมเนียมมาตรฐาน (ประมาณ 0.168% รวม VAT ต่อขา)
FEE_RATE = 0.00157 
VAT_RATE = 0.07    

def get_accurate_rsi(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="2mo", interval="1d")
        if df.empty or len(df) < 20: return 0.0, 50.0
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(df['Close'].iloc[-1]), float(rsi.iloc[-1])
    except: return 0.0, 50.0

# ==========================================
# 📊 STRATEGIST DASHBOARD
# ==========================================
st.sidebar.title("🏗️ GeminiBo v3.2")
menu = st.sidebar.radio("เลือกโหมด", ["📊 วิเคราะห์สถานการณ์", "💰 กระดานบัญชี (หักค่าต๋ง)", "🎯 สรุปเป้าหมายรายสัปดาห์"])

targets = ["SIRI", "WHA", "MTC", "PLANB", "SAWAD", "THCOM"]

if menu == "📊 วิเคราะห์สถานการณ์":
    st.title("🚀 Situation Room: Accurate Technicals")
    cols = st.columns(3)
    for i, symbol in enumerate(targets):
        with cols[i % 3]:
            with st.expander(f"📈 วิเคราะห์ {symbol}", expanded=True):
                price, rsi_val = get_accurate_rsi(symbol)
                st.metric(f"ราคา {symbol}", f"{price:.2f}")
                st.write(f"📡 RSI (14): **{rsi_val:.2f}**")
                m_bid = st.number_input(f"Bid Vol ({symbol})", value=1000000, key=f"b_{symbol}")
                m_off = st.number_input(f"Offer Vol ({symbol})", value=3000000, key=f"o_{symbol}")
                ratio = m_off / m_bid if m_bid > 0 else 0
                st.write(f"📊 Wall Ratio: **{ratio:.2f}**")

# ==========================================
# 💰 กระดานบัญชี (หักค่าต๋งจริง)
# ==========================================
elif menu == "💰 กระดานบัญชี (หักค่าต๋ง)":
    st.title("💰 Portfolio & Net Profit Tracker")
    st.info("💡 ระบบหักค่าธรรมเนียมรวมประมาณ 0.168% ต่อขา เพื่อให้พี่เห็นกำไรสุทธิจริง")
    grand_net_profit = 0.0
    
    for symbol in targets:
        with st.expander(f"📝 บันทึก {symbol}", expanded=True):
            c1, c2, c3 = st.columns(3)
            # ขาซื้อ
            v_old = c1.number_input(f"หุ้นเดิม ({symbol})", value=0, key=f"vo_{symbol}")
            p_old = c1.number_input(f"ราคาทุน ({symbol})", value=0.0, format="%.2f", key=f"po_{symbol}")
            v_new = c2.number_input(f"หุ้นเพิ่ม ({symbol})", value=0, key=f"vn_{symbol}")
            p_new = c2.number_input(f"ราคาถัว ({symbol})", value=0.0, format="%.2f", key=f"pn_{symbol}")
            # ขาขาย
            v_out = c3.number_input(f"จำนวนขาย ({symbol})", value=0, key=f"vs_{symbol}")
            p_out = c3.number_input(f"ราคาขาย ({symbol})", value=0.0, format="%.2f", key=f"ps_{symbol}")
            
            # คำนวณต้นทุนรวมและค่าต๋งขาซื้อ
            total_v = v_old + v_new
            buy_val = (v_old * p_old) + (v_new * p_new)
            fee_buy = buy_val * FEE_RATE * (1 + VAT_RATE)
            
            # คำนวณยอดขายและค่าต๋งขาขาย
            sell_val = v_out * p_out
            fee_sell = sell_val * FEE_RATE * (1 + VAT_RATE)
            
            # กำไรสุทธิ = (ยอดขาย - ทุนส่วนที่ขาย) - ค่าต๋งรวม
            avg_p = buy_val / total_v if total_v > 0 else 0.0
            net_profit = (sell_val - (avg_p * v_out)) - (fee_buy * (v_out/total_v if total_v>0 else 0) + fee_sell)
            
            grand_net_profit += net_profit if v_out > 0 else 0
            
            st.write(f"📊 ทุนเฉลี่ย: **{avg_p:.2f}** | ค่าต๋งรวมไม้นี้: **{ (fee_buy * (v_out/total_v if total_v>0 else 0) + fee_sell):.2f}** บาท")
            st.subheader(f"✅ กำไรสุทธิ {symbol}: {net_profit:,.2f} บาท")

    st.sidebar.markdown("---")
    st.sidebar.metric("🏆 กำไรสุทธิรวมวันนี้", f"{grand_net_profit:,.2f}")
    
    # ระบบ Progress Bar เป้าหมาย 500 บาท
    progress = min(max(grand_net_profit / 500.0, 0.0), 1.0)
    st.sidebar.write(f"🎯 เป้าหมายค่ากับข้าว 500 บาท: **{progress*100:.1f}%**")
    st.sidebar.progress(progress)
    if grand_net_profit >= 500:
        st.sidebar.success("🎉 ครบค่ากับข้าวอาทิตย์นี้แล้วครับพี่โบ้!")
