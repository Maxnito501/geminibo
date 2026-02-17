import json
import os
from datetime import datetime

class TradePlanner:
    def __init__(self, db_file='data.json'):
        self.db_file = db_file

    def load_data(self):
        if not os.path.exists(self.db_file):
            return []
        with open(self.db_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_data(self, new_entry):
        data = self.load_data()
        data.append(new_entry)
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("💾 บันทึกแผนเรียบร้อย!")

    def run(self):
        print(f"\n--- 📈 Trade Planner: สร้างแผนเทรดใหม่ ---")
        try:
            symbol = input("ชื่อหุ้น (Symbol): ").upper()
            shares = float(input("จำนวนหุ้น: "))
            avg_price = float(input("ราคาต้นทุน: "))
            target_price = float(input("ราคาเป้าหมายขายทำกำไร: "))
            stop_loss = float(input("จุด Stop Loss: "))
            
            # คำนวณเบื้องต้น
            total_cost = shares * avg_price
            risk_amt = (avg_price - stop_loss) * shares
            reward_amt = (target_price - avg_price) * shares
            rr_ratio = reward_amt / risk_amt if risk_amt > 0 else 0
            
            print(f"\n📊 R:R Ratio ของแผนนี้คือ {rr_ratio:.2f} เท่า")
            
            confirm = input("ยืนยันบันทึกแผนนี้ไหม? (y/n): ")
            if confirm.lower() == 'y':
                entry = {
                    "symbol": symbol,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "shares": shares,
                    "entry_price": avg_price,
                    "target_price": target_price,
                    "stop_loss": stop_loss,
                    "status": "Active"
                }
                self.save_data(entry)
                
        except ValueError:
            print("❌ Error: ใส่ตัวเลขผิดครับ")
