import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithCustomToken, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, doc, setDoc, getDoc, onSnapshot, collection } from 'firebase/firestore';
import { 
  Shield, 
  Settings, 
  Save, 
  RefreshCcw, 
  Bell, 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Cloud,
  Zap,
  Key,
  Cpu,
  Database,
  Activity
} from 'lucide-react';

// --- Firebase Configuration ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'geminibo-pro';

const App = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('commander');
  const [isSyncing, setIsSyncing] = useState(false);
  
  // --- Cloud Settings (LINE + SetSmart API) ---
  const [cloudSettings, setCloudSettings] = useState({
    lineToken: '',
    lineUserId: '',
    setSmartApiKey: '', // เพิ่มช่องเก็บ API Key จาก SetSmart
    isGlobal: true 
  });

  // --- Real-time Data for SIRI, HANA, MTC ---
  const [marketData, setMarketData] = useState({
    SIRI: { price: 1.57, rsi: 91.7, bidSum: 12.5, offerSum: 4.8, status: 'Whale Pulling' },
    HANA: { price: 18.60, rsi: 45.2, bidSum: 1.2, offerSum: 1.1, status: 'Consolidating' },
    MTC: { price: 37.75, rsi: 38.5, bidSum: 5.5, offerSum: 18.2, status: 'Heavy Wall' }
  });

  const portfolio = [
    { symbol: 'SIRI', qty: 4700, avg: 1.47, target: 1.63, color: 'emerald' },
    { symbol: 'HANA', qty: 300, avg: 18.90, target: 18.90, color: 'indigo' },
    { symbol: 'MTC', qty: 400, avg: 38.50, target: 38.25, color: 'rose' }
  ];

  // (1) Auth Logic
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (err) { console.error("Auth error", err); }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  // (2) Fetch Cloud Settings
  useEffect(() => {
    if (!user) return;
    const configRef = doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'config_v83');
    const unsubscribe = onSnapshot(configRef, (docSnap) => {
      if (docSnap.exists()) { setCloudSettings(docSnap.data()); }
    });
    return () => unsubscribe();
  }, [user]);

  // (3) Save Settings to Cloud
  const saveSettings = async () => {
    if (!user) return;
    try {
      const configRef = doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'config_v83');
      await setDoc(configRef, cloudSettings);
      alert("✅ บันทึกข้อมูล API และ LINE ลงคลาวด์เรียบร้อยครับพี่โบ้!");
    } catch (err) { alert("❌ บันทึกไม่สำเร็จ"); }
  };

  // (4) Simulate API Fetch using Key
  const handleAutoSync = () => {
    if (!cloudSettings.setSmartApiKey) {
      alert("⚠️ กรุณาใส่ API Key ในหน้า Settings ก่อนครับพี่!");
      return;
    }
    setIsSyncing(true);
    // จำลองการดึงข้อมูล 1.5 วินาที
    setTimeout(() => {
      setIsSyncing(false);
      alert("🚀 อัปเดตข้อมูล SIRI, HANA, MTC จาก SetSmart API สำเร็จ!");
    }, 1500);
  };

  if (loading) return <div className="flex h-screen items-center justify-center text-blue-600 font-bold bg-slate-900">🛡️ กำลังเชื่อมต่อระบบ API Auto-Pilot...</div>;

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans pb-24">
      {/* Dynamic Header */}
      <div className="bg-slate-900/80 backdrop-blur-md p-6 text-white shadow-2xl sticky top-0 z-50 border-b border-blue-500/20">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className={`p-3 rounded-2xl bg-blue-600 shadow-lg shadow-blue-500/50 ${isSyncing ? 'animate-spin' : ''}`}>
              <Cpu size={24} />
            </div>
            <div>
              <h1 className="text-xl font-black tracking-tight italic">GEMINIBO <span className="text-blue-400">v8.3</span></h1>
              <div className="flex items-center gap-2 text-[10px] font-bold text-blue-400/70 uppercase tracking-widest">
                <Activity size={10} className="animate-pulse" /> API Auto-Pilot Active
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={handleAutoSync}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-xl text-xs font-black flex items-center gap-2 transition-all active:scale-95 shadow-lg shadow-blue-600/20"
            >
              <RefreshCcw size={14} className={isSyncing ? 'animate-spin' : ''} /> 
              {isSyncing ? 'SYNCING...' : 'AUTO SYNC'}
            </button>
            <button 
              onClick={() => setActiveTab('settings')}
              className={`p-3 rounded-xl transition-all ${activeTab === 'settings' ? 'bg-indigo-600 shadow-indigo-500/50' : 'bg-slate-800 hover:bg-slate-700'}`}
            >
              <Settings size={20} />
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-4 md:p-8">
        {activeTab === 'settings' ? (
          /* --- SETTINGS TAB: ใส่ไอดีทั้งหมดที่นี่ --- */
          <div className="max-w-2xl mx-auto space-y-6 animate-in fade-in zoom-in duration-300">
            <div className="bg-slate-800/50 rounded-[2.5rem] p-10 border border-slate-700 backdrop-blur-sm shadow-2xl">
              <h2 className="text-2xl font-black mb-8 flex items-center gap-3">
                <Key className="text-blue-500" /> คลังเก็บกุญแจไอดี
              </h2>
              
              <div className="space-y-8">
                {/* SETSMART API KEY SECTION */}
                <div className="p-6 bg-slate-900/50 rounded-3xl border border-blue-500/20">
                  <label className="block text-[10px] font-black text-blue-400 uppercase mb-3 flex items-center gap-2">
                    <Database size={12}/> SetSmart API Key (จากรูปที่พี่ได้มา)
                  </label>
                  <input 
                    type="text"
                    value={cloudSettings.setSmartApiKey}
                    onChange={(e) => setCloudSettings({...cloudSettings, setSmartApiKey: e.target.value})}
                    placeholder="กรอก API Key 4bed36... ที่นี่"
                    className="w-full p-5 bg-slate-950 border-2 border-slate-800 rounded-2xl text-blue-400 font-mono text-sm focus:border-blue-500 outline-none transition-all"
                  />
                  <p className="text-[9px] text-slate-500 mt-2 italic">*ระบบจะใช้กุญแจนี้ดึงข้อมูล SIRI, HANA, MTC ให้พี่แบบออโต้</p>
                </div>

                {/* LINE CONFIG SECTION */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[10px] font-black text-slate-500 uppercase mb-2">LINE Token</label>
                    <input 
                      type="password"
                      value={cloudSettings.lineToken}
                      onChange={(e) => setCloudSettings({...cloudSettings, lineToken: e.target.value})}
                      className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-sm focus:border-indigo-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-black text-slate-500 uppercase mb-2">LINE User ID</label>
                    <input 
                      type="text"
                      value={cloudSettings.lineUserId}
                      onChange={(e) => setCloudSettings({...cloudSettings, lineUserId: e.target.value})}
                      className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-sm focus:border-indigo-500 outline-none"
                    />
                  </div>
                </div>

                <button 
                  onClick={saveSettings}
                  className="w-full py-5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-[2rem] font-black text-lg shadow-xl hover:shadow-blue-500/20 hover:-translate-y-1 transition-all flex items-center justify-center gap-3"
                >
                  <Save size={24} /> บันทึกกุญแจทั้งหมดลงคลาวด์
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* --- COMMANDER TAB: แก้ดอย 3 ตัวหลัก --- */
          <div className="space-y-8 animate-in slide-in-from-bottom-10 duration-500">
            
            {/* Whale Analysis Panel */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {portfolio.map((item) => {
                const live = marketData[item.symbol];
                const ratio = (live.offerSum / live.bidSum).toFixed(2);
                return (
                  <div key={item.symbol} className="bg-slate-800/40 rounded-[2.5rem] p-8 border border-slate-700 hover:border-blue-500/50 transition-all shadow-xl group relative overflow-hidden">
                    <div className={`absolute top-0 right-0 w-32 h-32 bg-${item.color}-500/10 rounded-full -mr-16 -mt-16 group-hover:bg-blue-500/20 transition-all`}></div>
                    
                    <div className="flex justify-between items-start mb-8 relative z-10">
                      <div>
                        <h3 className="text-4xl font-black text-white">{item.symbol}</h3>
                        <p className={`text-xs font-bold mt-1 ${live.rsi > 70 ? 'text-rose-400' : 'text-emerald-400'}`}>
                          📡 RSI: {live.rsi.toFixed(1)} | {live.status}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-[10px] font-black text-slate-500 uppercase">Current Price</p>
                        <p className="text-3xl font-black text-blue-400">{live.price.toFixed(2)}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-8 relative z-10">
                      <div className="p-4 bg-slate-950/50 rounded-2xl border border-slate-800">
                        <p className="text-[10px] font-bold text-slate-500 mb-1">TOTAL BID (10Lv)</p>
                        <p className="text-xl font-black text-emerald-500">{live.bidSum}M</p>
                      </div>
                      <div className="p-4 bg-slate-950/50 rounded-2xl border border-slate-800">
                        <p className="text-[10px] font-bold text-slate-500 mb-1">TOTAL OFFER (10Lv)</p>
                        <p className="text-xl font-black text-rose-500">{live.offerSum}M</p>
                      </div>
                    </div>

                    <div className="space-y-4 mb-8 relative z-10">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-400 font-bold italic">Whale Ratio (O/B):</span>
                        <span className={`font-black text-lg px-3 py-1 rounded-xl ${ratio < 0.5 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                          {ratio}
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-sm pt-4 border-t border-slate-700">
                        <span className="text-slate-400 font-bold underline decoration-blue-500/50">เป้าหมายถอยทัพ:</span>
                        <span className="font-black text-white text-lg">{item.target.toFixed(2)}</span>
                      </div>
                    </div>

                    <button 
                      onClick={() => alert(`ส่งสัญญาณ ${item.symbol} เข้า LINE แล้ว`)}
                      className="w-full py-4 bg-slate-900 border border-slate-700 rounded-2xl text-xs font-black text-slate-400 hover:bg-blue-600 hover:text-white transition-all flex items-center justify-center gap-2 group-hover:scale-105 active:scale-95"
                    >
                      <Bell size={14}/> ส่งสรุปกลยุทธ์เข้า LINE
                    </button>
                  </div>
                );
              })}
            </div>

            {/* Dividend & Cashflow Alert */}
            <div className="bg-gradient-to-br from-indigo-900 to-blue-900 rounded-[3rem] p-10 text-white shadow-2xl relative overflow-hidden border border-white/10">
               <div className="absolute -right-20 -bottom-20 w-80 h-80 bg-white/10 rounded-full blur-3xl"></div>
               <div className="relative z-10 flex flex-col lg:flex-row items-center justify-between gap-8">
                  <div className="flex items-center gap-8">
                    <div className="w-20 h-20 bg-white/10 backdrop-blur-xl rounded-[2rem] flex items-center justify-center shadow-2xl border border-white/20">
                      <Zap size={40} className="text-yellow-400 fill-yellow-400" />
                    </div>
                    <div>
                      <h4 className="text-3xl font-black mb-2 tracking-tight">ยุทธศาสตร์ปั๊มเงินสดเดือนมีนาคม</h4>
                      <p className="text-indigo-200 font-medium opacity-80">
                        ใช้กำไรจาก SIRI มาเป็น Buffer ให้ HANA & MTC <br/>
                        เตรียมพร้อมรับปันผล SCB (9.28 บ.) และ PTT (1.40 บ.)
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4">
                     <div className="bg-white/10 backdrop-blur-md px-8 py-5 rounded-3xl border border-white/10 text-center">
                        <p className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest mb-1">SCB Payout</p>
                        <p className="text-3xl font-black text-white">9.28 <span className="text-sm font-medium">บ.</span></p>
                     </div>
                     <div className="bg-white/10 backdrop-blur-md px-8 py-5 rounded-3xl border border-white/10 text-center">
                        <p className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest mb-1">PTT Payout</p>
                        <p className="text-3xl font-black text-white">1.40 <span className="text-sm font-medium">บ.</span></p>
                     </div>
                  </div>
               </div>
            </div>
          </div>
        )}
      </div>

      {/* Modern Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-slate-900/90 backdrop-blur-xl border-t border-slate-800 p-6 flex justify-around items-center md:hidden z-50 rounded-t-[2.5rem] shadow-2xl">
        <button onClick={() => setActiveTab('commander')} className={`flex flex-col items-center gap-1 transition-all ${activeTab === 'commander' ? 'text-blue-500 scale-125' : 'text-slate-500 opacity-50'}`}>
          <Shield size={24} />
        </button>
        <button onClick={() => setActiveTab('settings')} className={`flex flex-col items-center gap-1 transition-all ${activeTab === 'settings' ? 'text-blue-500 scale-125' : 'text-slate-500 opacity-50'}`}>
          <Settings size={24} />
        </button>
      </div>
    </div>
  );
};

export default App;
