from settrade_v2.market import MarketData
from settrade_v2.user import Investor

# 1. ตั้งค่ากุญแจ (Sandbox Key)
# พี่โบ้เอา Key ที่ได้จากเว็บ Sandbox มาแปะตรงนี้นะครับ
my_app_id = "A6ci0gEXKmkRPwRY"
my_app_secret = "AMZcHrk9Ytvyj+UPO7BDgvpZ5Cjy8h0H8ocZoNQ6aQPK"

try:
    print("🔄 กำลังเชื่อมต่อ Settrade Sandbox...")
    
    # สร้าง Object ผู้ลงทุน (Investor)
    investor = Investor(
        app_id=my_app_id,
        app_secret=my_app_secret,
        broker_id="SANDBOX",
        app_code="SANDBOX",
        is_auto_queue=False
    )
    
    # สร้าง Object ตลาด (Market)
    market = investor.MarketData()
    
    print("✅ เชื่อมต่อสำเร็จ! พร้อมดึงข้อมูลแล้วครับ")

except Exception as e:
    print(f"❌ เชื่อมต่อไม่ผ่าน: {e}")
