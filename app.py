import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, doc, setDoc, onSnapshot } from 'firebase/firestore';
import { 
  ShieldCheck, 
  Settings, 
  Save, 
  Target, 
  TrendingUp, 
  TrendingDown, 
  Zap, 
  BarChart3, 
  Activity,
  AlertTriangle,
  Info,
  DollarSign
} from 'lucide-react';

// --- Firebase Config (Standardized for Stable execution) ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'geminibo-iron-v21';

const App = () => {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('commander');
  const [isSaving, setIsSaving] = useState(false);
  
  // (Iron Rule 1) Setup for SetSmart Data Integration
  const [config, setConfig] = useState({
    setSmartApiKey: '',
    lineToken: '',
    autoSync: true
  });

  // (Iron Rule 5) Portfolio & Watchlist Data
  const [portfolio, setPortfolio] = useState([
    { symbol: 'SIRI', qty: 4700, avg: 1.47, current: 1.56, trend: 'UP', rsi: 88, rvol: 2.1 },
    { symbol: 'MTC', qty: 400, avg: 38.50, current: 36.75, trend: 'DOWN', rsi: 35, rvol: 0.8 },
    { symbol: 'HANA', qty: 300, avg: 18.90, current: 18.60, trend: 'DOWN', rsi: 42, rvol: 1.2 }
  ]);

  const watchlist = [
    { symbol: 'TRUE', type: 'Strange', current: 14.10, trend: 'UP', ratio: 0.38 },
    { symbol: 'ADVANC', type: 'Strange', current: 245.0, trend: 'SIDE', ratio: 0.85 },
    { symbol: 'ITEL', type: 'Strange', current: 2.44, trend: 'UP', ratio: 0.52 },
    { symbol: 'SCB', type: 'Rising', current: 148.5, trend: 'UP', ratio: 0.45, div: '9.28' },
    { symbol: 'PTT', type: 'Rising', current: 34.50, trend: 'SIDE', ratio: 0.60, div: '1.40' },
    { symbol: 'BBL', type: 'Rising', current: 148.0, trend: 'UP', ratio: 0.42 },
    { symbol: 'CPALL', type: 'Rising', current: 51.25, trend: 'DOWN', ratio: 1.20 },
    { symbol: 'BDMS', type: 'Rising', current: 27.50, trend: 'UP', ratio: 0.35 }
  ];

  useEffect(() => {
    signInAnonymously(auth).catch(err => console.error(err));
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!user) return;
    const configRef = doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'main_config');
    return onSnapshot(configRef, (d) => d.exists() && setConfig(d.data()));
  }, [user]);

  const saveConfig = async () => {
    if (!user) return;
    setIsSaving(true);
    await setDoc(doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'main_config'), config);
    setIsSaving(false);
  };

  if (!user) return <div className="h-screen bg-slate-950 flex items-center justify-center text-blue-500 font-black animate-pulse">BOOTING IRON COMMANDER...</div>;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 font-sans pb-24">
      {/* Header */}
      <div className="bg-slate-900/80 border-b border-white/5 p-6 sticky top-0 z-50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="bg-blue-600 p-3 rounded-2xl shadow-lg shadow-blue-500/20">
              <ShieldCheck size={28} />
            </div>
            <div>
              <h1 className="text-xl font-black italic tracking-tighter">GEMINIBO <span className="text-blue-500">v21.0</span></h1>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Iron Rule Compliant System</p>
            </div>
          </div>
          <div className="flex gap-2">
            {['commander', 'settings'].map(t => (
              <button 
                key={t} onClick={() => setActiveTab(t)}
                className={`p-3 rounded-xl transition-all ${activeTab === t ? 'bg-blue-600' : 'bg-slate-800'}`}
              >
                {t === 'commander' ? <BarChart3 size={20}/> : <Settings size={20}/>}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 md:p-8">
        {activeTab === 'settings' ? (
          <div className="max-w-2xl mx-auto bg-slate-900 p-10 rounded-[3rem] border border-slate-800 shadow-2xl animate-in zoom-in duration-300">
             <h2 className="text-2xl font-black mb-8 flex items-center gap-3">
               <Activity className="text-blue-500" /> (ข้อ 1) ตั้งค่า SetSmart Data
             </h2>
             <div className="space-y-6">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-2">SetSmart API Key</label>
                  <input 
                    type="password" value={config.setSmartApiKey}
                    onChange={(e) => setConfig({...config, setSmartApiKey: e.target.value})}
                    placeholder="รหัสลับสำหรับดึงราคา/วอลลุ่มออโต้"
                    className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl font-mono text-sm focus:border-blue-500 outline-none"
                  />
                </div>
                <button 
                  onClick={saveConfig} disabled={isSaving}
                  className="w-full py-5 bg-blue-600 hover:bg-blue-500 rounded-3xl font-black text-xs uppercase tracking-widest shadow-xl transition-all"
                >
                  {isSaving ? 'SAVING...' : 'SAVE CONFIGURATION'}
                </button>
             </div>
          </div>
        ) : (
          <div className="space-y-12 animate-in slide-in-from-bottom-10 duration-500">
            
            {/* Owned Section (Old Stocks) */}
            <section>
               <h2 className="text-sm font-black text-rose-400 uppercase tracking-[0.4em] mb-6 italic ml-4">
                 <AlertTriangle className="inline mr-2" size={16}/> กองทัพเก่า (ตามกฎเหล็กข้อ 6-7)
               </h2>
               <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                 {portfolio.map(s => {
                    const isProfit = s.current > s.avg;
                    return (
                      <div key={s.symbol} className="bg-slate-900 p-8 rounded-[3.5rem] border border-slate-800 relative overflow-hidden group">
                        <div className={`absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity`}>
                          {isProfit ? <TrendingUp size={120}/> : <TrendingDown size={120}/>}
                        </div>
                        <div className="flex justify-between items-start mb-6">
                          <h3 className="text-5xl font-black italic tracking-tighter">{s.symbol}</h3>
                          <span className={`text-[9px] font-black px-2 py-1 rounded-lg ${isProfit ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                            {isProfit ? 'PROFIT' : 'DOI'}
                          </span>
                        </div>
                        <div className="space-y-3 mb-8">
                           <div className="flex justify-between text-xs font-bold text-slate-500">
                              <span>ทุนพี่โบ้: {s.avg.toFixed(2)}</span>
                              <span className={isProfit ? 'text-emerald-400' : 'text-rose-400'}>ตลาด: {s.current.toFixed(2)}</span>
                           </div>
                           <div className="p-4 bg-slate-950 rounded-2xl text-[10px] font-bold italic leading-relaxed">
                              {isProfit ? `🔥 กฎข้อ 6: ห้ามขายหมู! แบ่งขาย 1/2 ที่แนวต้าน` : `🚨 กฎข้อ 7: รอเด้งขายตัด หรือเฉือนเนื้อรักษาทัพ`}
                           </div>
                        </div>
                        <div className="flex gap-2">
                           <div className="flex-1 bg-slate-800 p-2 rounded-xl text-center">
                              <p className="text-[8px] font-bold text-slate-500">RSI</p>
                              <p className="text-sm font-black">{s.rsi}</p>
                           </div>
                           <div className="flex-1 bg-slate-800 p-2 rounded-xl text-center">
                              <p className="text-[8px] font-bold text-slate-500">RVOL</p>
                              <p className="text-sm font-black">{s.rvol}</p>
                           </div>
                        </div>
                      </div>
                    );
                 })}
               </div>
            </section>

            {/* Watchlist Section (New & Rising) */}
            <section>
               <h2 className="text-sm font-black text-blue-400 uppercase tracking-[0.4em] mb-6 italic ml-4">
                 <Zap className="inline mr-2" size={16}/> หน่วยสอดแนมขุนพลใหม่ (ตามกฎข้อ 8)
               </h2>
               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                 {watchlist.map(w => (
                    <div key={w.symbol} className="bg-slate-900/50 p-6 rounded-[2.5rem] border border-slate-800 hover:border-blue-500/50 transition-all">
                       <div className="flex justify-between items-center mb-4">
                          <h4 className="text-2xl font-black italic">{w.symbol}</h4>
                          <span className="text-[8px] font-black text-slate-500 px-2 py-1 bg-slate-800 rounded-full uppercase">{w.type}</span>
                       </div>
                       <div className="space-y-2 mb-6">
                          <p className="text-xs font-bold text-slate-400">Whale Ratio: <span className={w.ratio < 0.4 ? 'text-emerald-400' : 'text-slate-200'}>{w.ratio}</span></p>
                          {w.div && <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">DIV: ฿{w.div}</p>}
                       </div>
                       <button className="w-full py-3 bg-slate-800 hover:bg-blue-600 rounded-2xl text-[9px] font-black uppercase tracking-widest transition-all">
                          {w.ratio < 0.5 ? '🏹 ช้อนตามน้ำ' : '⌛ รอดูจังหวะ'}
                       </button>
                    </div>
                 ))}
               </div>
            </section>

            {/* Strategic Footer */}
            <div className="bg-blue-900/10 border-2 border-blue-500/30 p-10 rounded-[4rem] flex flex-col md:flex-row items-center gap-10 shadow-2xl">
               <div className="w-24 h-24 bg-blue-600 rounded-[2.5rem] flex items-center justify-center shrink-0 shadow-xl">
                  <DollarSign size={48} className="text-white" />
               </div>
               <div className="flex-1">
                  <h3 className="text-2xl font-black mb-4 italic uppercase">ยุทธวิธีสะสมเสบียง 58,000 บาท</h3>
                  <p className="text-sm font-bold text-slate-300 leading-relaxed italic">
                    "พี่โบ้ครับ การล้างพอร์ตเก่า (MTC, HANA) เพื่อมาเข้าทัพใหม่ที่ Whale Ratio < 0.4 (TRUE, BDMS) จะทำให้พี่ขยับเข้าใกล้แสนแรกได้เร็วกว่าการรอหุ้นที่เทรนด์พังครับ... นาทีนี้ใช้ 'วินัย' นำทางครับพี่!"
                  </p>
               </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
};

export default App;
