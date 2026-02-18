import streamlit as st
import pandas as pd
import yfinance as yf

# ==========================================
# ⚙️ CONFIG & ENGINE (หักค่าต๋ง + RSI แม่นยำ)
# ==========================================
st.set_page_config(page_title="GeminiBo v3.5: Whale Rider", page_icon="🏗️", layout="wide")
FEE_RATE, VAT_RATE = 0.00157, 0.07

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
# 📊 STRATEGIST COMMAND CENTER
# ==========================================
st.sidebar.title("🏗️ GeminiBo v3.5")
menu = st.sidebar.radio("เลือกโหมด", ["🔥 กลยุทธ์สู้เจ้ามือ & บัญชี", "🎯 สรุปเป้าหมาย 500 บาท"])

targets = ["SIRI", "WHA", "MTC", "PLANB", "SAWAD", "THCOM"]

if menu == "🔥 กลยุทธ์สู้เจ้ามือ & บัญชี":
    st.title("🚀 Command Center: วิเคราะห์ & บันทึกกำไร")
    
    total_net_profit = 0.0 # ตัวแปรเก็บกำไรสุทธิรวม
    
    for sym in targets:
        with st.expander(f"📦 จัดการหุ้น {sym}", expanded=True):
            # --- ส่วนที่ 1: วิเคราะห์ RSI & กลยุทธ์ ---
            p, r = get_accurate_rsi(sym)
            c1, c2, c3 = st.columns([1, 1, 2])
            
            with c1:
                st.metric(f"ราคา {sym}", f"{p:.2f}")
                st.write(f"📡 RSI: **{r:.2f}**")
            
            with c2:
                b = st.number_input(f"Bid Vol", value=1000000, key=f"b_{sym}")
                o = st.number_input(f"Offer Vol", value=3000000, key=f"o_{sym}")
                ratio = o / b if b > 0 else 0
                st.write(f"📊 Ratio: **{ratio:.2f}**")
            
            with c3:
                st.markdown("**🛡️ กลยุทธ์สู้เจ้า:**")
                if ratio > 4 and r > 60:
                    st.error(f"🆘 'กำแพงลวง': เจ้าขวางบีบคายของ ตั้งขายดักหน้า!")
                elif ratio < 0.7 and r < 40:
                    st.success(f"💎 'ซุ่มเก็บของ': RSI ต่ำ วอลลุ่มบาง จังหวะช้อน")
                elif ratio < 0.4 and r > 50:
                    st.warning(f"🚀 'ลากกระชาก': ทางสะดวก Let Profit Run!")
                else:
                    st.info(f"⚖️ 'ดึงเช็ง': รอไม้ใหญ่ฝั่ง Buy ค่อยตาม")

            # --- ส่วนที่ 2: กระดานบัญชี (หักค่าต๋ง) ---
            st.markdown("---")
            st.markdown("**💰 บัญชีคุมหน้าตัก (หักค่าต๋ง 0.168%):**")
            bc1, bc2, bc3 = st.columns(3)
            
            v_in = bc1.number_input(f"จำนวนหุ้นต้นทุน ({sym})", value=0, key=f"vi_{sym}")
            p_in = bc1.number_input(f"ราคาต้นทุน ({sym})", value=0.0, format="%.2f", key=f"pi_{sym}")
            
            v_out = bc2.number_input(f"จำนวนที่ขาย ({sym})", value=0, key=f"vo_{sym}")
            p_out = bc2.number_input(f"ราคาที่ขาย ({sym})", value=0.0, format="%.2f", key=f"po_{sym}")
            
            # คำนวณกำไรสุทธิแบบหักค่าต๋งจริง
            buy_val = v_in * p_in
            sell_val = v_out * p_out
            fee_buy = buy_val * FEE_RATE * (1 + VAT_RATE)
            fee_sell = sell_val * FEE_RATE * (1 + VAT_RATE)
            
            # กำไรสุทธิ = (ส่วนต่างราคา) - (ค่าต๋งขาซื้อ+ขาขาย)
            raw_p = (p_out - p_in) * v_out if v_out > 0 else 0.0
            net_p = raw_p - (fee_buy * (v_out/v_in if v_in > 0 else 0) + fee_sell)
            
            total_net_profit += net_p if v_out > 0 else 0
            
            with bc3:
                st.write(f"📉 ค่าต๋งรวม: **{ (fee_buy * (v_out/v_in if v_in > 0 else 0) + fee_sell):.2f}** บาท")
                st.subheader(f"✅ สุทธิ: {net_p:,.2f}")

    # แสดงผลรวมที่ Sidebar
    st.sidebar.markdown("---")
    st.sidebar.metric("🏆 กำไรสุทธิรวม (บาท)", f"{total_net_profit:,.2f}")
    prog = min(max(total_net_profit / 500.0, 0.0), 1.0)
    st.sidebar.write(f"🎯 เป้าหมาย 500 บาท: **{prog*100:.1f}%**")
    st.sidebar.progress(prog)

elif menu == "🎯 สรุปเป้าหมาย 500 บาท":
    st.title("🎯 Weekly Profit Goal Tracker")
    st.write("เป้าหมาย 0.8% ต่อสัปดาห์ (ค่ากับข้าว 500 บาท)")
    # ส่วนสรุปกราฟกำไรสะสม (ถ้าพี่ต้องการเพิ่มภายหลัง)
