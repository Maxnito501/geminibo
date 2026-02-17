from settrade_v2.market import MarketData
from settrade_v2.user import Investor

# 1. ตั้งค่ากุญแจ (Sandbox Key)
# พี่โบ้เอา Key ที่ได้จากเว็บ Sandbox มาแปะตรงนี้นะครับ
my_app_id = "A6ci0gEXKmkRPwRY"
my_app_secret = "AMZcHrk9Ytvyj+UPO7BDgvpZ5Cjy8h0H8ocZoNQ6aQPK"
TARGET_STOCK = "PTT"  # ชื่อหุ้นที่อยากลองของ (ตัวใหญ่หมด)

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
        
        # เช็กว่าตลาดเปิดไหม หรือดึงข้อมูลได้ไหม
        if quote['last'] is None:
            print("❌ ไม่พบข้อมูล (ตลาดอาจจะปิด หรือชื่อหุ้นผิด)")
            return

        # -----------------------------------------------------
        # 📊 ส่วนแสดงผล (DASHBOARD)
        # -----------------------------------------------------
        print("\n" + "="*40)
        print(f"   🏗️  STOCK INFO: {TARGET_STOCK}")
        print("="*40)
        print(f"💰 ราคาล่าสุด  : {quote['last']:.2f} บาท")
        print(f"📈 เปลี่ยนแปลง : {quote['change']:.2f} ({quote['percent_change']}%)")
        print(f"📦 Volume รวม : {quote['total_volume']:,} หุ้น")
        print(f"🕒 เวลาอัปเดต : {quote['time']}")
        print("-" * 40)

        # 3. เจาะกำแพง Bid/Offer 5 ช่อง (Market Depth)
        # จัดเตรียมข้อมูลใส่ List เพื่อวนลูปแสดงผลง่ายๆ
        bids = [
            (quote['bid_price1'], quote['bid_volume1']),
            (quote['bid_price2'], quote['bid_volume2']),
            (quote['bid_price3'], quote['bid_volume3']),
            (quote['bid_price4'], quote['bid_volume4']),
            (quote['bid_price5'], quote['bid_volume5'])
        ]
        offers = [
            (quote['offer_price1'], quote['offer_volume1']),
            (quote['offer_price2'], quote['offer_volume2']),
            (quote['offer_price3'], quote['offer_volume3']),
            (quote['offer_price4'], quote['offer_volume4']),
            (quote['offer_price5'], quote['offer_volume5'])
        ]

        # หัวตาราง
        print(f"{'BID (รอซื้อ)':<20} | {'OFFER (รอขาย)':<20}")
        print("-" * 45)

        # วนลูปแสดง 5 ช่อง
        for i in range(5):
            # จัด Format ให้สวยงาม (ใส่ลูกน้ำคั่นหลักพัน)
            bid_vol = f"{bids[i][1]:,}" if bids[i][1] != 0 else "-"
            bid_prc = f"{bids[i][0]:.2f}" if bids[i][0] != 0 else "-"
            
            off_prc = f"{offers[i][0]:.2f}" if offers[i][0] != 0 else "-"
            off_vol = f"{offers[i][1]:,}" if offers[i][1] != 0 else "-"

            # แสดงผลบรรทัดต่อบรรทัด
            print(f"{bid_vol:>10} @ {bid_prc:<6} | {off_prc:>6} @ {off_vol:<10}")

        print("-" * 45)

        # 4. คำนวณ Wall Ratio (วิเคราะห์เจ้ามือ)
        top_bid = quote['bid_volume1']
        top_offer = quote['offer_volume1']
        
        if top_bid > 0:
            ratio = top_offer / top_bid
            print(f"📊 Wall Ratio (Offer/Bid): {ratio:.2f} เท่า")
            
            # Logic ตัดสินใจ
            if ratio > 5:
                print("🚨 STATUS: SQUEEZE! (โดนขวางหนัก -> เจ้าเก็บของ/กดราคา)")
            elif ratio < 0.2:
                print("🩸 STATUS: PANIC/DUMP! (Bid รับไม่อยู่ -> ระวังไหลลง)")
            elif ratio > 3:
                print("🚧 STATUS: HEAVY RESISTANCE (แนวต้านหนา)")
            else:
                print("ℹ️ STATUS: NORMAL (ตลาดปกติ)")
        else:
            print("⚠️ ข้อมูล Bid/Offer ไม่เพียงพอคำนวณ Ratio")

    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        print("💡 คำแนะนำ: เช็ก App ID/Secret หรือ Internet อีกทีครับ")

# --- สั่งรันโปรแกรม ---
if __name__ == "__main__":
    run_market_check()
