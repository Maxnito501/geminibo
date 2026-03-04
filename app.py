import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, doc, setDoc, onSnapshot } from 'firebase/firestore';
import { 
  ShieldCheck, Settings, Target, TrendingUp, TrendingDown, 
  Zap, BarChart3, Activity, Info, Save, Key,
  List, DollarSign, AlertCircle, RefreshCw, History, Flame, 
  ShieldAlert, Plane, HeartPulse, Waves, ShoppingCart, Scissors
} from 'lucide-react';

// --- Firebase Standard Setup ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'geminibo-sovereign-v100';

const App = () => {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('portfolio');
  const [isSaving, setIsSaving] = useState(false);

  // --- (IRON RULE 1) System Persistence & War Fund ---
  const [config, setConfig] = useState({
    warFund: 12783, // เงินสดใน Dime ล่าสุด
    backupFund: 18000, // ใน KTB
    totalRealizedLoss: 1600, // MTC + JAS
    warMode: true
  });

  // --- (IRON RULE 5) ขุนพลรบ (รวม BH และตัวถัว) ---
  const [stocks, setStocks] = useState([
    { symbol: 'BH', qty: 0, avg: 0, last: 186.5, rsi: 18, wave: 'C-Bottom', impact: 'Defense', broker: 'Dime', note: 'สอยของถูกจาก Panic Sell' },
    { symbol: 'AOT', qty: 200, avg: 54.50, last: 51.50, rsi: 22, wave: 'Wave C', impact: 'War Victim', broker: 'Dime', note: 'รอถัว 51.00 ไม้สไนเปอร์' },
    { symbol: 'PTG', qty: 200, avg: 9.62, last: 9.40, rsi: 35, wave: 'Wave 2', impact: 'Defense', broker: 'Streaming', note: 'รอ Rebound เข้า Wave 3' },
    { symbol: 'SIRI', qty: 2000, avg: 1.47, last: 1.52, rsi: 85, wave: 'Wave 5', impact: 'Neutral', broker: 'Dime', note: 'รันปันผลของฟรี' },
    { symbol: 'PTT', qty: 100, avg: 33.00, last: 36.75, rsi: 65, wave: 'Super Trend', impact: 'War Profiteer', broker: 'Streaming', note: 'ปันผล 1.40 รออยู่' },
    { symbol: 'CPF', qty: 0, avg: 0, last: 21.10, rsi: 42, wave: 'Wave 1 Start', impact: 'Defense', broker: 'Streaming', note: 'มังกรเสบียงจ่อเบรก' }
  ]);

  useEffect(() => {
    signInAnonymously(auth).catch(console.error);
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!user) return;
    const configRef = doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'sovereign_v100');
    return onSnapshot(configRef, (d) => d.exists() && setConfig(d.data()));
  }, [user]);

  const saveConfig = async () => {
    if (!user) return;
    setIsSaving(true);
    await setDoc(doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'sovereign_v100'), config);
    setIsSaving(false);
  };

  const analyzed = useMemo(() => {
    return stocks.map(s => {
      const isOwned = s.qty > 0;
      const profitVal = isOwned ? (s.last - s.avg) * s.qty : 0;
      const isProfit = isOwned && s.last >= s.avg;
      
      let cmd = "รอกระแสเงิน";
      let color = "bg-slate-800";

      if (isOwned) {
        if (s.rsi < 30) { cmd = "⚖️ จุดถัวสไนเปอร์ (Wave C)"; color = "bg-blue-600 animate-pulse"; }
        else if (isProfit) { cmd = "💎 Let Profit Run"; color = "bg-emerald-600"; }
        else { cmd = "🚨 เฝ้าจุดดีดคืนทุน"; color = "bg-rose-600"; }
      } else {
        if (s.impact === 'Defense') { cmd = "🛡️ ช้อนสวนสงคราม!"; color = "bg-orange-600 animate-bounce"; }
        else { cmd = "📡 สอดแนมวาฬ"; }
      }
      return { ...s, isOwned, isProfit, profitVal, cmd, color };
    });
  }, [stocks]);

  if (!user) return <div className="h-screen bg-slate-950 flex items-center justify-center text-blue-500 font-black animate-pulse uppercase italic tracking-tighter text-2xl">War & Wave Engine Initializing...</div>;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 font-sans pb-32">
      
      {/* (IRON RULE 1) MASTER HEADER */}
      <div className="bg-slate-900 border-b-2 border-rose-500/50 p-6 sticky top-0 z-50 backdrop-blur-xl shadow-2xl flex justify-between items-center">
        <div className="flex items-center gap-5">
          <div className="bg-rose-600 p-4 rounded-3xl shadow-lg animate-pulse"><ShieldAlert size={32} className="text-white" /></div>
          <div>
            <h1 className="text-xl font-black italic uppercase tracking-tighter">GEMINIBO <span className="text-rose-500">MASTER</span> v100</h1>
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-none flex items-center gap-2 italic">
               <Flame size={12} className="text-orange-500"/> War & Wave Sovereign Mode
            </p>
          </div>
        </div>
        <div className="bg-slate-950 px-6 py-3 rounded-2xl border border-slate-800 text-center shadow-inner">
             <p className="text-[9px] font-black text-slate-500 uppercase mb-1 italic">Active Ammo (Dime)</p>
             <p className="text-lg font-black text-emerald-400">฿{config.warFund.toLocaleString()}</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 md:p-8">
        
        {/* Recovery Dashboard */}
        <div className="bg-slate-900 p-8 rounded-[4rem] border border-slate-800 mb-10 shadow-xl flex flex-col md:flex-row justify-between items-center gap-8 relative overflow-hidden">
           <div className="absolute top-0 right-0 p-8 opacity-5"><History size={200}/></div>
           <div className="text-center md:text-left">
              <h3 className="text-xs font-black uppercase text-blue-400 tracking-[0.4em] mb-4 italic flex items-center gap-2">
                 <Target size={16}/> ยอดทวงคืน (MTC + JAS)
              </h3>
              <p className="text-7xl font-black text-white italic tracking-tighter mb-2">฿{config.totalRealizedLoss.toLocaleString()}</p>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-relaxed">
                "เราจะใช้กำไรจาก BH และ PTT เย็บแผลเก่าให้จบในเดือนมีนาคม!"
              </p>
           </div>
           <div className="grid grid-cols-1 gap-3 w-full md:w-auto">
              <div className="bg-slate-950 px-8 py-4 rounded-3xl border border-slate-800 text-center shadow-inner">
                 <p className="text-[9px] font-black text-indigo-400 uppercase">KTB Fortress</p>
                 <p className="text-xl font-black text-indigo-200 italic">฿{config.backupFund.toLocaleString()}</p>
              </div>
           </div>
        </div>

        {/* Strategic Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
           {analyzed.map((s, idx) => (
             <div key={s.symbol} className="bg-slate-900 p-8 rounded-[4rem] border border-slate-800 shadow-xl relative overflow-hidden group hover:border-emerald-500/30 transition-all">
                <div className="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:opacity-[0.1] transition-opacity"><Waves size={140}/></div>

                <div className="flex justify-between items-start mb-6 relative z-10">
                   <div>
                      <h3 className="text-5xl font-black italic tracking-tighter flex items-center gap-2">
                        {s.symbol} {s.symbol === 'BH' && <HeartPulse size={24} className="text-rose-400 animate-pulse"/>}
                        {s.symbol === 'AOT' && <Plane size={24} className="text-blue-400"/>}
                      </h3>
                      <div className="flex gap-2 mt-1">
                        <span className="text-[8px] font-black uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-400">{s.broker}</span>
                        <span className={`text-[8px] font-black uppercase px-2 py-0.5 rounded ${s.impact === 'Defense' ? 'bg-orange-500/20 text-orange-400' : 'bg-rose-500/20 text-rose-400'}`}>{s.impact}</span>
                      </div>
                   </div>
                   <div className="text-right">
                      <p className="text-[10px] font-black text-slate-500 uppercase mb-1">Market</p>
                      <p className="text-3xl font-black text-white italic tracking-tighter">฿{s.last.toFixed(2)}</p>
                   </div>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-6 relative z-10 text-center">
                   <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 shadow-inner">
                      <p className="text-[8px] font-bold text-slate-600 uppercase mb-1 italic">Elliott Wave</p>
                      <p className="text-[11px] font-black text-blue-400 uppercase">{s.wave}</p>
                   </div>
                   <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 shadow-inner">
                      <p className="text-[8px] font-bold text-slate-600 uppercase mb-1 italic">RSI Status</p>
                      <p className={`text-sm font-black ${s.rsi < 30 ? 'text-emerald-400 animate-pulse' : 'text-slate-300'}`}>{s.rsi}</p>
                   </div>
                </div>

                <div className={`${s.color} p-6 rounded-[2.5rem] shadow-xl relative z-10 border border-white/10`}>
                   <div className="flex items-center gap-2 mb-2 opacity-80">
                      <Zap size={14} className="text-white fill-white"/>
                      <p className="text-[9px] font-black uppercase tracking-widest text-white italic">Commander Action</p>
                   </div>
                   <p className="text-xs font-black text-white italic leading-none uppercase text-center">{s.cmd}</p>
                   {s.isOwned && (
                     <div className="flex justify-between items-center mt-3 border-t border-white/10 pt-2">
                        <p className="text-[9px] font-black text-white opacity-70 uppercase tracking-widest">PnL Net:</p>
                        <p className={`text-xs font-black ${s.isProfit ? 'text-emerald-100' : 'text-rose-100'}`}>
                           {s.isProfit ? '+' : ''}{s.profitVal.toLocaleString()} บ.
                        </p>
                     </div>
                   )}
                </div>
                
                <p className="mt-4 text-[9px] font-bold text-slate-600 italic px-2 tracking-tight leading-relaxed">"{s.note}"</p>
             </div>
           ))}
        </div>

        {/* Strategy Log Section */}
        <div className="mt-16 bg-gradient-to-br from-indigo-950 to-blue-950 p-12 rounded-[5rem] border border-blue-500/20 shadow-2xl flex flex-col lg:flex-row items-center gap-12 relative overflow-hidden">
           <div className="absolute top-0 right-0 p-12 opacity-5"><BarChart3 size={250}/></div>
           <div className="w-32 h-32 bg-blue-600 rounded-[3rem] flex items-center justify-center shrink-0 shadow-xl shadow-blue-500/20">
              <ShieldCheck size={64} className="text-white" />
           </div>
           <div className="flex-1 text-center lg:text-left">
              <h3 className="text-3xl font-black mb-4 uppercase italic tracking-tight underline decoration-blue-500 decoration-8 underline-offset-[12px] underline text-white">สาส์นจอมทัพ: แผนรับมือสงคราม</h3>
              <p className="text-sm font-bold text-slate-300 leading-relaxed italic mb-8 max-w-2xl font-sans">
                "พี่โบ้ครับ ในกองเพลิงตะวันออกกลาง... BH และ CPF คือฐานที่มั่นที่ต่างชาติจะโยกเงินมาพักครับ <br/><br/>
                ส่วน AOT ที่ดิ่งลงมาคือ Wave C ขาลงสุดท้าย... เราจะใช้เงินจากการขาย JAS (4,400 บ.) มาสไนเปอร์ถัวที่ 51.00 เพื่อดึงทุนคืน และรอลุ้นมังกรพ่นไฟคืนกำไรครับพี่!"
              </p>
              <div className="flex flex-wrap justify-center lg:justify-start gap-4">
                 <div className="bg-slate-950 px-5 py-2 rounded-xl border border-slate-800 text-[10px] font-black text-emerald-400 uppercase italic flex items-center gap-2">
                    <HeartPulse size={12}/> Entry Target: BH @ 186.5
                 </div>
                 <div className="bg-slate-950 px-5 py-2 rounded-xl border border-slate-800 text-[10px] font-black text-blue-400 uppercase italic flex items-center gap-2">
                    <Waves size={12}/> Reversal Zone: AOT @ 51.0
                 </div>
              </div>
           </div>
        </div>

      </div>

      {/* Nav */}
      <div className="fixed bottom-0 left-0 right-0 p-8 flex justify-center z-40 bg-gradient-to-t from-[#020617] to-transparent pointer-events-none">
         <div className="bg-slate-900/80 backdrop-blur-2xl border border-white/10 p-2 rounded-[3.5rem] flex gap-4 shadow-2xl pointer-events-auto transition-all border-t-2 border-t-rose-500/20">
            <button onClick={() => setActiveTab('portfolio')} className={`p-5 rounded-[2.5rem] transition-all flex items-center gap-3 ${activeTab === 'portfolio' ? 'bg-blue-600 text-white shadow-xl shadow-blue-600/40' : 'text-slate-500 hover:bg-slate-800'}`}>
               <List size={28}/> {activeTab === 'portfolio' && <span className="text-xs font-black uppercase tracking-widest italic">สมรภูมิล่า</span>}
            </button>
            <button onClick={() => setActiveTab('settings')} className={`p-5 rounded-[2.5rem] transition-all flex items-center gap-3 ${activeTab === 'settings' ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-600/40' : 'text-slate-500 hover:bg-slate-800'}`}>
               <Settings size={28}/> {activeTab === 'settings' && <span className="text-xs font-black uppercase tracking-widest italic">คลังกุญแจ</span>}
            </button>
         </div>
      </div>
    </div>
  );
};

export default App;
