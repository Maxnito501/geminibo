class MarketSentinel:
    def run(self):
        print(f"\n--- 🛡️ Market Sentinel: อ่านใจเจ้ามือ ---")
        try:
            bid = float(input("Bid Volume: "))
            offer = float(input("Offer Volume: "))
            
            ratio = offer / bid if bid > 0 else 0
            print(f"📊 Wall Ratio: {ratio:.2f}")
            
            if ratio > 5:
                print("🚨 Squeeze: เจ้าขวางเก็บของ (ถ้าตลาดเงียบ) หรือ กดไม่ให้ขึ้น")
            elif ratio < 0.5:
                print("🩸 Panic: แรงขายท่วม (ระวังรับมีด)")
            else:
                print("ℹ️ Normal: ตลาดปกติ")
        except:
            print("❌ Input Error")
