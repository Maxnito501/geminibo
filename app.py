import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ==========================================
# ⚙️ CONFIG & ENGINE (v4.6 Portfolio Sniper)
# ==========================================
st.set_page_config(page_title="GeminiBo v4.6: Portfolio Sniper", layout="wide", page_icon="🏹")

def get_advanced_metrics(symbol):
    """ ดึงข้อมูลราคา, RSI, RVOL และแนวรับแนวต้าน """
    try:
        ticker = yf.Ticker(f"{symbol}.BK")
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < 10:
            return None
        
        price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        change_pct = ((price - prev_price) / prev_price) * 100
        high_5d = df['High'].iloc[-5:].max()
        low_5d = df['Low'].iloc[-5:].min()

        # RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # RVOL (Relative Volume)
        avg_vol_5d = df['Volume'].iloc[-6:-1].mean()
        curr_vol = df['Volume'].iloc[-1]
        rvol = curr_vol / avg_vol_5d if avg_vol_5d > 0 else 1.0
        
        return {
            "price": price,
            "change": change_pct,
            "rsi": rsi.iloc[-1],
            "rvol": rvol,
            "resistance": high_5d,
            "support": low_5d
        }
    except:
        return None

# ==========================================
# 📊 SIDEBAR: PORTFOLIO TACTICS
# ==========================================
st.sidebar.title("⚔️ ยุทธวิธีจอมทัพ")
st.sidebar.info("เป้าหมายพรุ่งนี้: ปรับทัพเพื่ออาทิตย์หน้า")

with st.sidebar.expander("🍎 แผน SIRI (2,000 + 2,700 หุ้น)", expanded=True):
    st.write("ต้านย่อย: 1.62 - 1.63 (ขาย 2,000)")
    st.write("ต้านใหญ่: 1.66+ (Run 2,700)")
    siri_price = st.number_input("ราคา SIRI ปัจจุบัน", value=1.61, step=0.01)
    if siri_price >= 1.66:
        st.error("🔥 ห้ามขายหมู! ทะลุต้านใหญ่แล้ว")
    elif siri_price >= 1.62:
        st.warning("🎯 ถึงจุดขายบางส่วน (2,000 หุ้น)")

with st.sidebar.expander("🐌 แผน MTC (สายเฉื่อย)", expanded=True):
    st.write("สถานะ: เทรนดีแต่ไม่ซิ่ง")
    if st.button("ประเมินจุดถอนสมอ MTC"):
        st.write("กลยุทธ์: หาก RSI < 50 และ RVOL < 0.8 ให้สลับตัวรบ")

# ==========================================
# 🏹 SCANNER: SEARCHING FOR NEXT WEEK WHALES
# ==========================================
st.title("🏹 GeminiBo v4.6: Market Sniper")

watchlist = ["WHA", "ROJNA", "AMATA", "SIRI", "MTC", "CPALL", "SAWAD", "PLANB", "THCOM", "JMT", "BTS"]

st.subheader("🔍 ระบบสแกนหุ้นซิ่ง (Auto-Scan)")
scan_results = []
for sym in watchlist:
    m = get_advanced_metrics(sym)
    if m:
        # เงื่อนไขหุ้นซิ่ง: RVOL เริ่มมา (1.0-1.5) แต่ RSI ยังไม่สูง (40-60) และราคายังไม่พุ่งแรงมาก
        status = "รอดูเชิง"
        if m['rvol'] > 1.2 and m['rsi'] < 60:
            status = "🚀 พร้อมซิ่ง (ดักรอ)"
        elif m['rsi'] > 70:
            status = "⚠️ ระวังดอย"
        elif m['rvol'] > 2.0:
            status = "🐳 วาฬบุก!"
        
        scan_results.append({
            "หุ้น": sym,
            "ราคา": f"{m['price']:.2f}",
            "RVOL": round(m['rvol'], 2),
            "RSI": round(m['rsi'], 1),
            "สถานะ": status
        })

df_scan = pd.DataFrame(scan_results)
# กรองเฉพาะตัวที่น่าสนใจ
ready_to_zip = df_scan[df_scan['สถานะ'].str.contains("พร้อมซิ่ง|วาฬบุก")]
if not ready_to_zip.empty:
    st.dataframe(ready_to_zip, use_container_width=True, hide_index=True)
else:
    st.write("ยังไม่พบหุ้นซิ่งที่เข้าเงื่อนไข... รอนาทีทองช่วงบ่าย")

# ==========================================
# 🎯 MAIN MONITOR: 3 ขุนพลหลัก
# ==========================================
st.markdown("---")
st.subheader("🎯 เจาะลึก 3 ขุนพลที่เลือก")
selected_stocks = st.multiselect("เลือกหุ้นเพื่อดูละเอียด:", watchlist, default=["SIRI", "WHA", "MTC"])

cols = st.columns(3)
for i, sym in enumerate(selected_stocks[:3]):
    data = get_advanced_metrics(sym)
    with cols[i]:
        with st.container(border=True):
            if data:
                st.header(f"🛡️ {sym}")
                st.metric("ราคาปัจจุบัน", f"{data['price']:.2f}", f"{data['change']:.2f}%")
                
                # กันขายหมู Logic
                if sym == "SIRI":
                    if data['price'] >= 1.66:
                        st.success("💎 **SUPER HOLD (กันขายหมู)**\nทะลุ 1.66 วอลลุ่มต้องตาม รันไปต่ออาทิตย์หน้า!")
                    elif 1.62 <= data['price'] <= 1.63:
                        st.warning("🎯 **แบ่งทำกำไร**\nขาย 2,000 หุ้นตามแผน เพื่อลดความเสี่ยง")
                
                # MTC Logic
                if sym == "MTC":
                    if data['rvol'] < 1.0:
                        st.info("🐢 **สถานะเฉื่อย**\nเทรนดีแต่ขาดแรงเหวี่ยง พิจารณาย้ายไปตัวซิ่งข้างบน")

                st.write(f"📊 **RSI:** {data['rsi']:.1f} | **RVOL:** {data['rvol']:.2f}")
                st.write(f"📉 **แนวรับ:** {data['support']:.2f} | 📈 **แนวต้าน:** {data['resistance']:.2f}")

st.markdown("---")
st.caption("ยุทธศาสตร์อาทิตย์หน้า: 'ทิ้งถ่วง เก็บสด ดักวาฬ' — จอมทัพโบ้เน้นความคม ไม่เน้นความเร็วที่ไร้ทิศทาง")
