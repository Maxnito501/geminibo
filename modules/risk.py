import json
import os
from datetime import datetime

class RiskManager:
    def __init__(self, db_file='data.json'):
        self.db_file = db_file

    def check_portfolio(self):
        if not os.path.exists(self.db_file):
            print("📭 ยังไม่มีข้อมูลการเทรด (ไปสร้างแผนก่อนนะครับ)")
            return

        with open(self.db_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"\n--- ⚠️ Risk Manager: ตรวจสุขภาพพอร์ต ---")
        current_date = datetime.now()

        for item in data:
            if item['status'] != 'Active': continue

            # คำนวณเวลาที่ถือมา (Time Stop)
            entry_date = datetime.strptime(item['date'], "%Y-%m-%d")
            days_held = (current_date - entry_date).days
            
            print(f"\n📌 หุ้น: {item['symbol']} (ถือมา {days_held} วัน)")
            
            # รับราคาปัจจุบันเพื่อประเมิน
            try:
                curr_price = float(input(f"   ราคาปัจจุบันของ {item['symbol']}: "))
                
                # 1. เช็กจุดคัท (Price Stop)
                if curr_price <= item['stop_loss']:
                    loss = ((item['entry_price'] - curr_price) / item['entry_price']) * 100
                    print(f"   🚨 ALERT: หลุดจุดคัทแล้ว! (ลบ {loss:.2f}%) -> ต้องหนี!")
                
                # 2. เช็กเวลา (Time Stop) - สมมติกฎ 5 วัน
                elif days_held >= 5 and curr_price <= item['entry_price']:
                    print(f"   ⏳ TIME STOP: ครบ 5 วันแล้วราคายังไม่วิ่ง -> พิจารณาเปลี่ยนตัวเล่น")
                
                else:
                    print(f"   ✅ สถานะ: ปกติ (ถือต่อได้)")

            except ValueError:
                print("   ❌ ใส่ราคาผิด ข้ามไปตัวถัดไป...")
