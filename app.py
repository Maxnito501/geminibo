import streamlit as st
import yfinance as yf
import pandas as pd

# ==========================================
# ⚙️ CONFIG & ENGINE
# ==========================================
st.set_page_config(page_title="GeminiBo v3.7: Whale Commander", layout="wide", page_icon="🏗️")

FEE_RATE = 0.00157
VAT_RATE = 0.07
TOTAL_FEE_FACTOR = FEE_RATE * (1 + VAT_RATE) # ประมาณ 0.168% ต่อขา

def get_stock_metrics(symbol):
    """ ดึงราคาปัจจุบัน และคำนวณ RSI """
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < 15:
            return 0.0, 50.0
        
        price = df['Close'].iloc[-1]
        delta = df['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(price), float(rsi.iloc[-1])
    except:
        return 0.0, 50.0

# ==========================================
# 📊 SIDEBAR & GOAL TRACKER
# ==========================================
st.sidebar.title("🏗️ GeminiBo v3.7")
st.sidebar.markdown("---")

# บันทึกกำไรสะสม (Manual Input สำหรับวันนี้)
st.sidebar.subheader("💰 สรุปผลงานวันนี้")
profit_siri = st.sidebar.number_input("กำไรสุทธิ SIRI", value=219.84)
profit_wha = st.sidebar.number_input("กำไรสุทธิ WHA", value=32.81)
profit_others = st.sidebar.number_input("กำไรอื่นๆ", value=0.0)

total_net = profit_siri + profit_wha + profit_others
st.sidebar.metric("🏆 กำไรสุทธิรวม", f"{total_net:,.2f} บ.")

# Progress Bar สู่ 500 บาท
progress = min(max(total_net / 500.0, 0.0), 1.0)
st.sidebar.write(f"🎯 เป้าหมาย 500 บาท: **{progress*100:.1f}%**")
st.sidebar.progress(progress)

# ==========================================
# 🏹 MAIN COMMAND CENTER
# ==========================================
st.title("🏹 Whale Commander: อ่านใจรายใหญ่")

watchlist = ["WHA", "ROJNA", "AMATA", "SIRI", "MTC", "CPALL", "SAWAD", "PLANB", "THCOM"]
selected_stocks = st.multiselect("เลือกหุ้น 3 ตัวเพื่อเข้าตี:", watchlist, default=["WHA", "ROJNA", "MTC"])

if len(selected_stocks) > 3:
    st.warning("⚠️ กรุณาเลือกเพียง 3 ตัวเพื่อการวิเคราะห์ที่แม่นยำที่สุด")
    selected_stocks = selected_stocks[:3]

cols = st.columns(len(selected_stocks))

for i, sym in enumerate(selected_stocks):
    with cols[i]:
        with st.container(border=True):
            # 1. ข้อมูลทางเทคนิค
            price, rsi = get_stock_metrics(sym)
            st.header(f"🛡️ {sym}")
            
            sub_c1, sub_c2 = st.columns(2)
            sub_c1.metric("ราคา", f"{price:.2f}")
            
            rsi_color = "inverse" if rsi > 70 else "normal" if rsi < 30 else "off"
            sub_c2.metric("RSI (14)", f"{rsi:.1f}")

            # 2. Volume Matrix (ดักทางเจ้ามือ)
            st.markdown("---")
            st.markdown("**🐳 Volume Matrix (ล้านหุ้น)**")
            
            v_col1, v_col2 = st.columns(2)
            with v_col1:
                st.caption("ฝั่ง Bid (รับ)")
                b1 = st.number_input("Bid 1", key=f"b1_{sym}", value=1.0)
                b2 = st.number_input("Bid 2", key=f"b2_{sym}", value=1.0)
                b3 = st.number_input("Bid 3", key=f"b3_{sym}", value=1.0)
            with v_col2:
                st.caption("ฝั่ง Offer (ขวาง)")
                o1 = st.number_input("Offer 1", key=f"o1_{sym}", value=2.0)
                o2 = st.number_input("Offer 2", key=f"o2_{sym}", value=2.0)
                o3 = st.number_input("Offer 3", key=f"o3_{sym}", value=2.0)
            
            total_b = b1 + b2 + b3
            total_o = o1 + o2 + o3
            ratio = total_o / total_b if total_b > 0 else 0
            
            # 3. Whale Intelligence Analysis
            st.markdown("---")
            st.subheader("📡 ผลวิเคราะห์อาการเจ้ามือ")
            
            if total_b < 0.5 and total_o < 0.5:
                st.info("⚖️ **สถานะ: 'เจ้ามือไม่อยู่'**\n\nวอลลุ่มบางเกินไป หุ้นจะแกว่งแคบๆ ไม่สนุกครับ")
            elif ratio > 4:
                st.error("🆘 **สถานะ: 'กำแพงลวง'**\n\nเจ้าขวาง Offer หนาเพื่อบีบให้เราคายของ ห้ามเคาะขวาเด็ดขาด!")
                st.markdown("**กลยุทธ์:** นิ่งสงบสยบความเคลื่อนไหว ตั้งขายดักหน้ากำแพงแค่ครึ่งเดียว")
            elif ratio < 0.4:
                st.warning("🚀 **สถานะ: 'ทางสะดวก'**\n\nเจ้ามือถอน Offer เตรียมลากกระชาก อ่อยเหยื่อให้ตาม")
                st.markdown("**กลยุทธ์:** Let Profit Run อย่าเพิ่งรีบขายหมู ลุ้นไปปล่อยช่วง ATC")
            elif b1 > (b2 + b3) * 2:
                st.success("💎 **สถานะ: 'ซุ่มเก็บของ'**\n\nมีการวาง Bid รับของไม้ใหญ่ที่ช่องแรก")
                st.markdown("**กลยุทธ์:** เข้าตีไม้แรกตามรายใหญ่ได้เลย RSI ยังมีพื้นที่วิ่ง")
            else:
                st.write("📊 **สถานะ: 'สมดุล/เลือกทาง'**\n\nตลาดสู้กันปกติ รอดูไม้ใหญ่ใน Ticker นำทาง")

st.markdown("---")
st.caption("ตำราพิชัยสงครามกล่าวว่า: 'การชนะร้อยครั้งมิใช่ความสามารถอันสูงสุด การชนะโดยไม่ต้องรบเลยต่างหากคือความสามารถอันสูงสุด' — ใช้เครื่องมืออ่านใจเจ้ามือ เพื่อชัยชนะที่ยั่งยืน")
