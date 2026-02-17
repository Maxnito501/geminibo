import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURATION & SETUP
# ==========================================
st.set_page_config(
    page_title="GeminiBo Engineer",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ไฟล์เก็บข้อมูล
DB_FILE = 'data.json'

# ฟังก์ชันโหลด/บันทึกข้อมูล
def load_data():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==========================================
# 🎨 SIDEBAR MENU
# ==========================================
st.sidebar.title("🏗️ GeminiBo Control")
st.sidebar.info("Engineering Assistant Mode")
menu = st.sidebar.radio("เลือกเมนูสั่งการ", ["🛡️ Market Sentinel", "📝 Trade Planner", "⚠️ Risk Manager"])

st.sidebar.markdown("---")
st.sidebar.caption(f"Dev by พี่โบ้ | Ver 2.0 Web")

# ==========================================
# 🛡️ MODULE 1: MARKET SENTINEL
# ==========================================
if menu == "🛡️ Market Sentinel":
    st.title("🛡️ Market Sentinel: เรดาร์จับเจ้ามือ")
    st.markdown("วิเคราะห์พฤติกรรม Bid/Offer เพื่ออ่านเกมเจ้ามือ")

    col1, col2 = st.columns(2)
    with col1:
        bid_vol = st.number_input("Bid Volume (ฝั่งรอซื้อ)", min_value=0, value=1000000, step=10000)
    with col2:
        offer_vol = st.number_input("Offer Volume (ฝั่งรอขาย)", min_value=0, value=10000000, step=10000)

    speed = st.radio("ความเร็ว Ticker (การไหลของคำสั่ง)", ["ช้า/ปกติ (Slow)", "เร็ว/รัวๆ (Fast)"])

    if st.button("🚀 วิเคราะห์สถานการณ์", type="primary"):
        # Logic การคำนวณ
        ratio = offer_vol / bid_vol if bid_vol > 0 else 0
        
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Wall Ratio", f"{ratio:.2f} เท่า", delta_color="inverse")
        
        # แสดงผลลัพธ์
        if ratio > 5 and "ช้า" in speed:
            st.error("🚨 RESULT: SQUEEZE (การบีบของ)")
            st.write("""
            **อาการ:** Offer หนาปึ้ก แต่วอลลุ่มแห้ง
            \n**กลยุทธ์:** 🛡️ เจ้ามือกดเก็บของ อย่าเพิ่งไล่ราคา ให้ตั้งรับลึกๆ
            """)
        elif ratio > 3 and "เร็ว" in speed:
            st.success("🚀 RESULT: BREAKOUT ATTEMPT (งัดข้อ)")
            st.write("""
            **อาการ:** Offer หนา แต่มีคนเคาะขวารัวๆ
            \n**กลยุทธ์:** ⚔️ จูงแพะติดมือ! ตามน้ำไม้เล็ก ลุ้นผ่านต้าน
            """)
        elif ratio < 0.5:
            st.warning("🩸 RESULT: PANIC SELL (ทิ้งของ)")
            st.write("""
            **อาการ:** Bid บาง รับไม่อยู่ แรงขายเยอะ
            \n**กลยุทธ์:** ⛔ ห้ามรับมีด! รอสร้างฐานใหม่
            """)
        else:
            st.info("ℹ️ RESULT: NORMAL MARKET (ตลาดปกติ)")
            st.write("เล่นตามกราฟเทคนิคทั่วไป")

# ==========================================
# 📝 MODULE 2: TRADE PLANNER
# ==========================================
elif menu == "📝 Trade Planner":
    st.title("📝 Trade Planner: วางแผนเทรด")
    st.markdown("คำนวณความคุ้มค่า (Risk:Reward) ก่อนเข้าทำ")

    with st.form("trade_form"):
        col1, col2 = st.columns(2)
        with col1:
            symbol = st.text_input("ชื่อหุ้น (Symbol)").upper()
            shares = st.number_input("จำนวนหุ้น", min_value=100, step=100)
        with col2:
            entry_price = st.number_input("ราคาเข้า (Entry)", format="%.2f")
            target_price = st.number_input("เป้าขาย (Target)", format="%.2f")
            stop_loss = st.number_input("จุดตัดขาดทุน (Stop Loss)", format="%.2f")
        
        submitted = st.form_submit_button("💾 คำนวณและบันทึกแผน")

        if submitted:
            if entry_price > 0:
                upside = (target_price - entry_price) * shares
                downside = (entry_price - stop_loss) * shares
                rr = upside / downside if downside > 0 else 0
                
                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                c1.metric("กำไรคาดหวัง (Profit)", f"{upside:,.0f} บ.", delta=f"+{(upside/shares/entry_price)*100:.2f}%")
                c2.metric("ความเสี่ยง (Risk)", f"{downside:,.0f} บ.", delta=f"-{(downside/shares/entry_price)*100:.2f}%", delta_color="inverse")
                c3.metric("R:R Ratio", f"{rr:.2f} เท่า")

                if rr >= 2:
                    st.success("✅ แผนสวย! คุ้มค่าความเสี่ยง (R:R > 2)")
                    # Save to JSON
                    new_data = {
                        "symbol": symbol,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "shares": shares,
                        "entry_price": entry_price,
                        "target_price": target_price,
                        "stop_loss": stop_loss,
                        "status": "Active"
                    }
                    data = load_data()
                    data.append(new_data)
                    save_data(data)
                    st.toast(f"บันทึกแผน {symbol} เรียบร้อย!", icon="💾")
                else:
                    st.warning("⚠️ แผนนี้ไม่คุ้มเสี่ยง (R:R ต่ำกว่า 2) พิจารณาใหม่")

# ==========================================
# ⚠️ MODULE 3: RISK MANAGER
# ==========================================
elif menu == "⚠️ Risk Manager":
    st.title("⚠️ Risk Manager: ตรวจสุขภาพพอร์ต")
    
    data = load_data()
    if not data:
        st.info("ยังไม่มีข้อมูลในพอร์ต ไปสร้างแผนก่อนนะครับ")
    else:
        # แปลงเป็น DataFrame เพื่อแสดงตารางสวยๆ
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        st.markdown("### 🔍 เช็กอาการรายตัว")
        selected_stock = st.selectbox("เลือกหุ้นที่ต้องการเช็ก", df['symbol'].unique())
        
        # ดึงข้อมูลหุ้นที่เลือก
        stock_info = df[df['symbol'] == selected_stock].iloc[-1] # เอาล่าสุด
        
        current_price = st.number_input(f"ราคาปัจจุบันของ {selected_stock}", value=stock_info['entry_price'])
        
        # คำนวณ Time Stop
        entry_date = datetime.strptime(stock_info['date'], "%Y-%m-%d")
        days_held = (datetime.now() - entry_date).days
        
        col1, col2, col3 = st.columns(3)
        col1.metric("ทุน", f"{stock_info['entry_price']:.2f}")
        col2.metric("ปัจจุบัน", f"{current_price:.2f}", delta=f"{current_price - stock_info['entry_price']:.2f}")
        col3.metric("ถือมาแล้ว", f"{days_held} วัน")

        # Logic เตือนภัย
        if current_price <= stock_info['stop_loss']:
            st.error(f"🚨 ALERT: หลุดจุดคัท {stock_info['stop_loss']} แล้ว! ต้องหนี!")
        elif days_held >= 5 and current_price <= stock_info['entry_price']:
            st.warning(f"⏳ TIME STOP: ถือมา {days_held} วันแล้วยังไม่วิ่ง พิจารณาเปลี่ยนตัวเล่น")
        else:
            st.success("✅ สถานะ: ปกติ ถือรันเทรนด์ต่อได้")
