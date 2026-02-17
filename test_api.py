# ==========================================
# 🏗️ Project: GeminiBo - API Tester (Debugged)
# 🛠️ Dev: P'Bo (Engineering Mode)
# 🎯 Purpose: ดึงราคา + Bid/Offer 5 ช่อง (แบบไม่หลุด)
# ==========================================

import time
from settrade_v2.market import MarketData
from settrade_v2.user import Investor

# ---------------------------------------------------------
# 🔑 ส่วนตั้งค่า (CONFIG) - พี่โบ้แก้ 2 บรรทัดนี้ครับ
# ---------------------------------------------------------
SANDBOX_APP_ID = "A6ci0gEXKmkRPwRY"
SANDBOX_APP_SECRET = "AMZcHrk9Ytvyj+UPO7BDgvpZ5Cjy8h0H8ocZoNQ6aQPK"
TARGET_STOCK = "PTT" 

def run_market_check():
    print(f"🔄 กำลังเชื่อมต่อ Settrade Sandbox... (Target: {TARGET_STOCK})")
    
    try:
        # 1. เชื่อมต่อระบบ (Authentication)
        investor = Investor(
            app_id=SANDBOX_APP_ID,
            app_secret=SANDBOX_APP_SECRET,
            broker_id="SANDBOX",
            app_code="SANDBOX",
            is_auto_queue=False
        )
        market = investor.MarketData()
        
        # 2. ดึงข้อมูล Real-time (Get Quote)
        quote = market.get_quote_symbol(TARGET_STOCK)
        
        if not quote or quote.get('last') is None:
            print("❌ ไม่พบข้อมูลหุ้นตัวนี้ (ตลาดอาจปิดหรือชื่อผิด)")
            return

        # --- แก้ไขจุดที่ทำให้โปรแกรมหลุด (Error Handling) ---
        last_price = quote.get('last', 0)
        change = quote.get('change', 0)
        # ป้องกันกรณีไม่มีค่า percent_change ส่งมาจาก Server
        pct_change = quote.get('percent_change', 0)
        total_vol = quote.get('total_volume', 0)
        update_time = quote.get('time', '--:--:--')

        # -----------------------------------------------------
        # 📊 ส่วนแสดงผล (DASHBOARD)
        # -----------------------------------------------------
        print("\n" + "="*45)
        print(f"   🏗️  STOCK INFO: {TARGET_STOCK}")
        print("="*45)
        print(f"💰 ราคาล่าสุด  : {last_price:.2f} บาท")
        print(f"📈 เปลี่ยนแปลง : {change:.2f} ({pct_change}%)")
        print(f"📦 Volume รวม : {total_vol:,} หุ้น")
        print(f"🕒 เวลาอัปเดต : {update_time}")
        print("-" * 45)

        # 3. เจาะกำแพง Bid/Offer 5 ช่อง (ใช้ .get ป้องกัน Error)
        print(f"{'BID (รอซื้อ)':<21} | {'OFFER (รอขาย)':<21}")
        print("-" * 45)

        for i in range(1, 6):
            b_vol = quote.get(f'bid_volume{i}', 0)
            b_prc = quote.get(f'bid_price{i}', 0)
            o_prc = quote.get(f'offer_price{i}', 0)
            o_vol = quote.get(f'offer_volume{i}', 0)

            # จัด Format การแสดงผล
            bid_str = f"{b_vol:,.0f} @ {b_prc:.2f}" if b_prc > 0 else "-"
            off_str = f"{o_prc:.2f} @ {o_vol:,.0f}" if o_prc > 0 else "-"
            print(f"{bid_str:<21} | {off_str:<21}")

        print("-" * 45)

        # 4. วิเคราะห์เจ้ามือ
        top_bid = quote.get('bid_volume1', 0)
        top_offer = quote.get('offer_volume1', 0)
        
        if top_bid > 0:
            ratio = top_offer / top_bid
            print(f"📊 Wall Ratio (Offer/Bid): {ratio:.2f} เท่า")
            if ratio > 5:
                print("🚨 STATUS: SQUEEZE! (ขวางหนา - เจ้าเก็บของ)")
            elif ratio < 0.2:
                print("🩸 STATUS: PANIC/DUMP! (ระวังแรงเทขาย)")
            else:
                print("ℹ️ STATUS: NORMAL (ตลาดปกติ)")

    except Exception as e:
        print(f"\n❌ ระบบขัดข้อง: {str(e)}")

if __name__ == "__main__":
    run_market_check()
