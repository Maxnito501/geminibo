import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, doc, setDoc, onSnapshot } from 'firebase/firestore';
import { 
  ShieldCheck, Settings, Target, TrendingUp, TrendingDown, 
  Zap, BarChart3, Activity, Info, Save, Key,
  List, DollarSign, AlertCircle, RefreshCw, History, Waves, Scissors, Coins, ShieldAlert
} from 'lucide-react';

// --- Firebase Configuration ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'geminibo-sovereign-v101';

const App = () => {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('portfolio');
  const [isSaving, setIsSaving] = useState(false);

  // --- (IRON RULE 1) System Persistence & Liquidity Data ---
  const [config, setConfig] = useState({
    dimeCash: 12783, // 8383 + 4400 (JAS Sale)
    inxCash: 1000,
    ktbBackup: 18000,
    accumulatedLoss: 1600, // MTC 1000 + JAS 600
  });

  // --- (IRON RULE 5) ขุนพลรบ (Updated for War Mode & Elliott Wave) ---
  const [stocks, setStocks] = useState([
    { symbol: 'SIRI', qty: 2300, avg: 1.47, last: 1.44, wave: 'Support 1', type: 'Owned', action: 'HOLD FOR DIV' },
    { symbol: 'AOT', qty: 200, avg: 54.50, last: 48.50, wave: 'Wave C Bottom', type: 'Owned', action: 'DCA @ 47.00' },
    { symbol: 'BH', qty: 50, avg: 186.0, last: 174.0, wave: 'Consolidate', type: 'Owned', action: 'ACCUMULATE' },
    { symbol: 'PTG', qty: 200, avg: 9.60, last: 8.55, wave: 'Bearish', type: 'Owned', action: 'CUT @ 8.40' },
    { symbol: 'PTT', qty: 100, avg: 33.00, last: 35.50, wave: 'Bullish', type: 'Owned', action: 'HOLD (XD TOMORROW)' },
    { symbol: 'SCB', qty: 25, avg: 135.50, last: 142.50, wave: 'Uptrend', type: 'Owned', action: 'HOLD FOR DIV' },
    { symbol: 'PTTEP', qty: 0, avg: 0, last: 141.0, wave: 'War Spike', type: 'Hunting', action: 'BUY ON DIP' },
    { symbol: 'BDMS', qty: 0, avg: 0, last: 27.5, wave: 'Defensive', type: 'Hunting', action: 'WATCH 27.00' },
    { symbol: 'CPALL', qty: 0, avg: 0, last: 51.5, wave: 'Safe Haven', type: 'Hunting', action: 'WATCH 50.00' }
  ]);

  useEffect(() => {
    signInAnonymously(auth).catch(console.error);
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!user) return;
    const configRef = doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'sovereign_v101');
    return onSnapshot(configRef, (d) => d.exists() && setConfig(d.data()));
  }, [user]);

  const analyzed = useMemo(() => {
    return stocks.map(s => {
      const isOwned = s.qty > 0;
      const profitVal = isOwned ? (s.last - s.avg) * s.qty : 0;
      const isProfit = isOwned && s.last >= s.avg;
      
      let color = "bg-slate-800";
      if (isOwned) {
        color = isProfit ? "bg-emerald-600" : (s.last / s.avg < 0.9 ? "bg-rose-900 border-2 border-rose-500" : "bg-rose-600");
      } else {
        color = "bg-blue-600 animate-pulse";
      }

      return { ...s, isOwned, isProfit, profitVal, color };
    });
  }, [stocks]);

  if (!user) return <div className="h-screen bg-slate-950 flex items-center justify-center text-blue-500 font-black animate-pulse text-2xl uppercase italic">Resurrection Engine Booting...</div>;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 font-sans pb-32">
      
      {/* (FIXED CHARACTER ERROR) HEADER */}
      <div className="bg-slate-900 border-b-2 border-blue-500/50 p-6 sticky top-0 z-50 backdrop-blur-xl shadow-2xl flex justify-between items-center">
        <div className="flex items-center gap-5">
          <div className="bg-blue-600 p-4 rounded-3xl shadow-lg"><ShieldCheck size={32} /></div>
          <div>
            <h1 className="text-xl font-black italic tracking-tighter uppercase">GEMINIBO <span className="text-blue-500">MASTER</span> v101.0</h1>
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-none flex items-center gap-1">
               <Waves size={10} className="text-blue-400 animate-bounce"/> ELLIOTT WAVE & WAR RECOVERY
            </p>
          </div>
        </div>
        <div className="flex gap-4">
           <div className="bg-slate-950 px-6 py-3 rounded-2xl border border-slate-800 text-center shadow-inner">
                <p className="text-[9px] font-black text-slate-500 uppercase mb-1 italic">Total Liquidity</p>
                <p className="text-lg font-black text-emerald-400">THB {(config.dimeCash + config.inxCash).toLocaleString()}</p>
           </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 md:p-8">
        
        {/* Cash Allocation Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
           <div className="bg-slate-900 p-8 rounded-[3.5rem] border border-slate-800 shadow-xl relative overflow-hidden">
              <p className="text-[9px] font-black text-blue-400 uppercase mb-2 italic">Dime Frontline</p>
              <p className="text-4xl font-black text-white italic">THB {config.dimeCash.toLocaleString()}</p>
              <div className="mt-4 p-2 bg-blue-500/10 border border-blue-500/20 rounded-xl text-[9px] font-bold text-blue-400 uppercase text-center italic">
                *Includes THB 4,400 from JAS
              </div>
           </div>
           <div className="bg-slate-900 p-8 rounded-[3.5rem] border border-slate-800 shadow-xl relative overflow-hidden">
              <p className="text-[9px] font-black text-rose-500 uppercase mb-2 italic">Recovery Target</p>
              <p className="text-4xl font-black text-rose-500 italic">THB {config.accumulatedLoss.toLocaleString()}</p>
              <p className="text-[10px] font-bold text-slate-500 mt-2 uppercase italic leading-none">MTC 1k + JAS 0.6k</p>
           </div>
           <div className="bg-slate-950 p-8 rounded-[3.5rem] border-2 border-indigo-500/30 shadow-inner group">
              <p className="text-[9px] font-black text-indigo-400 uppercase mb-2 flex items-center gap-1 italic">
                 <ShieldAlert size={10}/> KTB Fortress (BACKUP)
              </p>
              <p className="text-4xl font-black text-indigo-200 italic opacity-50 group-hover:opacity-100 transition-opacity">THB {config.ktbBackup.toLocaleString()}</p>
              <div className="absolute bottom-0 left-0 h-1 bg-indigo-500 w-full shadow-[0_0_10px_#6366f1]"></div>
           </div>
        </div>

        {/* Tactical Units Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
           {analyzed.map((s, idx) => (
             <div key={s.symbol} className="bg-slate-900 p-8 rounded-[4rem] border border-slate-800 shadow-xl relative overflow-hidden group hover:border-blue-500/30 transition-all">
                <div className="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:opacity-[0.1] transition-opacity"><Zap size={140}/></div>

                <div className="flex justify-between items-start mb-6 relative z-10">
                   <div>
                      <h3 className="text-5xl font-black italic tracking-tighter flex items-center gap-3">
                        {s.symbol} {s.symbol === 'AOT' && <Waves size={24} className="text-blue-500"/>}
                      </h3>
                      <p className="text-[10px] font-black text-slate-500 uppercase mt-1 italic tracking-widest">{s.qty > 0 ? `${s.qty.toLocaleString()} หุ้น` : 'UNIT HUNTING'}</p>
                   </div>
                   <div className="text-right">
                      <p className="text-[10px] font-black text-slate-500 uppercase mb-1">Market</p>
                      <p className="text-2xl font-black text-white italic tracking-tighter">THB {s.last.toFixed(2)}</p>
                   </div>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-6 relative z-10 text-center font-sans">
                   <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 shadow-inner">
                      <p className="text-[8px] font-bold text-slate-600 uppercase mb-1 italic">Elliott Wave</p>
                      <p className="text-[10px] font-black text-blue-400 uppercase">{s.wave}</p>
                   </div>
                   <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 shadow-inner">
                      <p className="text-[8px] font-bold text-slate-600 uppercase mb-1 italic">PnL Net</p>
                      <p className={`text-sm font-black ${s.isProfit ? 'text-emerald-400' : 'text-rose-400'}`}>
                         {s.isOwned ? `${s.isProfit ? '+' : ''}${s.profitVal.toLocaleString()}` : '-'}
                      </p>
                   </div>
                </div>

                <div className={`${s.color} p-6 rounded-[2.5rem] shadow-xl relative z-10 border border-white/10`}>
                   <div className="flex items-center gap-2 mb-2 opacity-80">
                      <Target size={14} className="text-white animate-pulse"/>
                      <p className="text-[9px] font-black uppercase tracking-widest text-white italic">Commander Order</p>
                   </div>
                   <p className="text-xs font-black text-white italic leading-none uppercase text-center tracking-tight">{s.action}</p>
                </div>
                
                <p className="mt-4 text-[9px] font-bold text-slate-600 italic px-2 text-center tracking-tight">"{s.note}"</p>
             </div>
           ))}
        </div>

        {/* Global Strategy Footer */}
        <div className="mt-16 bg-gradient-to-br from-indigo-950/80 to-slate-950 p-12 rounded-[5rem] border border-blue-500/20 shadow-2xl flex flex-col lg:flex-row items-center gap-12 relative overflow-hidden">
           <div className="absolute top-0 right-0 p-12 opacity-5"><BarChart3 size={250}/></div>
           <div className="w-32 h-32 bg-blue-600 rounded-[3rem] flex items-center justify-center shrink-0 shadow-xl shadow-blue-500/20 text-white">
              <History size={64} />
           </div>
           <div className="flex-1 text-center lg:text-left text-white">
              <h4 className="text-3xl font-black mb-4 uppercase italic tracking-tight underline decoration-blue-500 decoration-8 underline-offset-8">สาส์นจอมทัพ: แผนคืนชีพ 100K</h4>
              <p className="text-sm font-bold text-slate-300 leading-relaxed italic mb-8 max-w-2xl font-sans text-center lg:text-left mx-auto lg:mx-0">
                "พี่โบ้ครับ การล้างพอร์ตที่มีปัญหาเพื่อถือเงินสดคือชัยชนะของสติ... พรุ่งนี้เราจะใช้กำไรปันผลจาก PTT และการเฝ้าจุด Wave C ของ AOT ที่ THB 47.00 เพื่อดึงต้นทุนคืน... และเราจะไม่แตะต้องเงิน 18,000 ใน KTB เด็ดขาดครับ!"
              </p>
           </div>
        </div>

      </div>

      {/* Nav */}
      <div className="fixed bottom-0 left-0 right-0 p-8 flex justify-center z-40 bg-gradient-to-t from-[#020617] to-transparent pointer-events-none">
         <div className="bg-slate-900/80 backdrop-blur-2xl border border-white/10 p-2 rounded-[3.5rem] flex gap-4 shadow-2xl pointer-events-auto transition-all border-t-2 border-t-blue-500/20">
            <button onClick={() => setActiveTab('portfolio')} className={`p-5 rounded-[2.5rem] transition-all flex items-center gap-3 ${activeTab === 'portfolio' ? 'bg-blue-600 text-white shadow-xl shadow-blue-600/40' : 'text-slate-500 hover:bg-slate-800'}`}>
               <List size={28}/> {activeTab === 'portfolio' && <span className="text-xs font-black uppercase tracking-widest italic">ขุนพลรบ</span>}
            </button>
            <button onClick={() => setActiveTab('settings')} className={`p-5 rounded-[2.5rem] transition-all flex items-center gap-3 ${activeTab === 'settings' ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-600/40' : 'text-slate-500 hover:bg-slate-800'}`}>
               <Settings size={28}/> {activeTab === 'settings' && <span className="text-xs font-black uppercase tracking-widest italic">ตั้งค่า</span>}
            </button>
         </div>
      </div>
    </div>
  );
};

export default App;
