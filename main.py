import sys
import os
# Import แอปลูกจากโฟลเดอร์ modules
from modules.sentinel import MarketSentinel
from modules.planner import TradePlanner
from modules.risk import RiskManager

class GeminiBoApp:
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def run(self):
        while True:
            self.clear_screen()
            print("==========================================")
            print("   🤖 GeminiBo: Stock Engineering v1.1    ")
            print("==========================================")
            print("1. 🛡️  Market Sentinel (อ่าน Bid/Offer)")
            print("2. 📝  Trade Planner (สร้าง/บันทึกแผน)")
            print("3. ⚠️  Risk Manager (เช็กพอร์ต/เวลา)")
            print("4. 🚪  Exit")
            print("==========================================")
            
            choice = input("เลือกเมนู: ")
            
            if choice == '1':
                MarketSentinel().run()
            elif choice == '2':
                TradePlanner().run()
            elif choice == '3':
                RiskManager().check_portfolio()
            elif choice == '4':
                sys.exit()
            
            input("\nกด Enter เพื่อกลับเมนูหลัก...")

if __name__ == "__main__":
    GeminiBoApp().run()
