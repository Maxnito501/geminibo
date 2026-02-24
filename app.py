import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, doc, setDoc, onSnapshot } from 'firebase/firestore';
import { 
  ShieldCheck, Settings, Target, TrendingUp, TrendingDown, 
  Zap, Activity, Info, Save, Key, List, DollarSign, AlertTriangle
} from 'lucide-react';

// --- Firebase Setup (Stable) ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'geminibo-v37-master';

const App = () => {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('owned');
  const [isSaving, setIsSaving] = useState(false);

  // --- (IRON RULE 1) System Persistence ---
  const [config, setConfig] = useState({
    setSmartApiKey: '',
    setSmartId: '',
    warFund: 58000,
    lastLoss: 1000
  });

  // --- (IRON RULE 5) Database ขุนพล 11 ตัว (ถาวร) ---
  const [stocks, setStocks] = useState([
    { symbol: 'SIRI', qty: 4200, avg: 1.47, last: 1.56, rsi: 88, ema5: 1.54, bidSum: 15.2, offSum: 22.8, type: 'Owned' },
    { symbol: 'MTC', qty: 400, avg: 38.50, last: 36.75, rsi: 35, ema5: 38.10, bidSum: 4.5, offSum: 18.2, type: 'Owned' },
    { symbol: 'HANA', qty: 0, avg: 0, last: 18.60, rsi: 42, ema5: 18.90, bidSum: 2.1, offSum: 2.4, type: 'Owned' },
    { symbol: 'HMPRO', qty: 400, avg: 7.05, last: 7.05, rsi: 28, ema5: 7.20, bidSum: 6.2, offSum: 1.4, type: 'Owned' },
    { symbol: 'TRUE', qty: 0, avg: 0, last: 14.30, rsi: 72, ema5: 14.10, bidSum: 17.3, offSum: 66.5, type: 'Hunting' },
    { symbol: 'SCB', qty: 0, avg: 0, last: 148.5, rsi: 55, ema5: 146.0, bidSum: 2.5, offSum: 1.8, type: 'Hunting' },
    { symbol: 'PTT', qty: 100, avg: 33.00, last: 36.50, rsi: 62, ema5: 36.10, bidSum: 35.2, offSum: 5.4, type: 'Hunting' },
    { symbol: 'ADVANC', qty: 0, avg: 0, last: 245.0, rsi: 48, ema5: 242.0, bidSum: 1.1, offSum: 0.9, type: 'Hunting' },
    { symbol: 'ITEL', qty: 0, avg: 0, last: 2.44, rsi: 52, ema5: 2.40, bidSum: 5.5, offSum: 2.1, type: 'Hunting' },
    { symbol: 'CPALL', qty: 0, avg: 0, last: 51.25, rsi: 38, ema5: 50.50, bidSum: 2.1, offSum: 4.8, type: 'Hunting' },
    { symbol: 'BDMS', qty: 0, avg: 0, last: 27.50, rsi: 45, ema5: 27.25, bidSum: 8.4, offSum: 3.2, type: 'Hunting' }
  ]);

  // Auth & Cloud Sync
  useEffect(() => {
    signInAnonymously(auth).catch(console.error);
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!user) return;
    const configRef = doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'config_v37');
    return onSnapshot(configRef, (d) => d.exists() && setConfig(d.data()));
  }, [user]);

  const saveConfig = async () => {
    if (!user) return;
    setIsSaving(true);
    await setDoc(doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'config_v37'), config);
    setIsSaving(false);
  };

  const updateStock = (idx, field, val) => {
    const newStocks = [...stocks];
    newStocks[idx][field] = val;
    setStocks(newStocks);
  };

  // --- (IRON BRAIN) คำสั่งยุทธการ ---
  const analyzed = useMemo(() => {
    return stocks.map(s => {
      const ratio = s.offSum / s.bidSum || 0;
      const isOwned = s.qty > 0;
      const isProfit = isOwned && s.last >= s.avg;
      const pnl = isOwned ? (s.last - s.avg) * s.qty : 0;
      
      let cmd = "รอกระแสเงิน";
      let color = "bg-slate-800";

      if (isOwned) {
        if (isProfit) { // 5.1.1
          cmd = ratio < 0.5 ? "💎 ห้ามขายหมู!" : "💰 แบ่งขาย 1/2";
          color = ratio < 0.5 ? "bg-emerald-600" : "bg-amber-600";
        } else { // 5.1.2
          cmd = s.rsi < 35 ? "⚖️ รอเด้งก้นเหว" : "🚨 หนีตาม EMA";
          color = s.rsi < 35 ? "bg-blue-600" : "bg-rose-600";
        }
      } else { // 5.2
        if (ratio < 0.4 && s.last > s.ema5) { cmd = "🏹 ช้อนตามน้ำ!"; color = "bg-emerald-600 animate-pulse"; }
        else if (s.rsi < 40) { cmd = "🎯 เฝ้าช่องเข้า"; color = "bg-slate-700"; }
      }
      return { ...s, ratio, isOwned, isProfit, pnl, cmd, color };
    });
  }, [stocks]);

  if (!user) return <div className="h-screen bg-[#020617] flex items-center justify-center text-blue-500 font-black animate-pulse">FIXING SYSTEM...</div>;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 font-sans pb-32">
      {/* Header */}
      <div className="bg-slate-900/90 border-b border-white/5 p-6 sticky top-0 z-50 backdrop-blur-xl flex justify-between items-center shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="bg-blue-600 p-3 rounded-2xl shadow-lg shadow-blue-500/20"><ShieldCheck className="text-white" size={24}/></div>
          <div>
            <h1 className="text-lg font-black italic uppercase tracking-tighter">GEMINIBO <span className="text-blue-500">MASTER</span> v37</h1>
            <p className="text-[8px] font-bold text-slate-500 uppercase tracking-widest leading-none">Iron Rule Integrated</p>
          </div>
        </div>
        <div className="flex gap-3">
          <div className="bg-slate-950 px-4 py-2 rounded-xl border border-slate-800 text-center">
             <p className="text-[8px] font-black text-slate-500 uppercase">War Fund</p>
             <p className="text-sm font-black text-emerald-400">฿{config.warFund.toLocaleString()}</p>
          </div>
          <button onClick={() => setActiveTab('settings')} className={`p-3 rounded-xl transition-all ${activeTab === 'settings' ? 'bg-blue-600' : 'bg-slate-800'}`}><Settings size={18}/></button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-4 md:p-8">
        {activeTab === 'settings' ? (
          /* Settings (Rule 1) */
          <div className="max-w-xl mx-auto space-y-6 animate-in zoom-in duration-300">
             <div className="bg-slate-900 p-8 rounded-[3rem] border border-slate-800 shadow-2xl">
                <h2 className="text-xl font-black mb-6 italic flex items-center gap-2"><Key size={18} className="text-blue-500"/> (ข้อ 1) SETSmart ID Bridge</h2>
                <div className="space-y-4">
                   <div className="grid grid-cols-2 gap-3">
                      <input type="text" value={config.setSmartId} onChange={(e)=>setConfig({...config, setSmartId: e.target.value})} placeholder="User ID" className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-sm outline-none"/>
                      <input type="password" value={config.setSmartApiKey} onChange={(e)=>setConfig({...config, setSmartApiKey: e.target.value})} placeholder="API Key" className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-sm outline-none"/>
                   </div>
                   <input type="number" value={config.warFund} onChange={(e)=>setConfig({...config, warFund: Number(e.target.value)})} placeholder="เงินสดในมือ" className="w-full bg-slate-950 p-4 rounded-xl border border-slate-800 font-black text-emerald-400 outline-none"/>
                   <button onClick={saveConfig} disabled={isSaving} className="w-full py-4 bg-blue-600 hover:bg-blue-500 rounded-2xl font-black text-xs uppercase tracking-widest shadow-xl transition-all">
                     {isSaving ? 'MEMORIZING...' : 'SAVE CONFIGURATION'}
                   </button>
                </div>
             </div>
             <div className="bg-rose-900/10 border border-rose-500/20 p-6 rounded-3xl flex justify-between items-center">
                <p className="text-xs font-bold text-rose-400 italic flex items-center gap-2"><AlertTriangle size={14}/> ยอดติดลบสะสม:</p>
                <p className="text-xl font-black text-rose-500">฿{config.lastLoss.toLocaleString()}</p>
             </div>
          </div>
        ) : (
          /* Main Dashboard */
          <div className="space-y-8">
            <div className="flex gap-2 p-1 bg-slate-900 rounded-2xl border border-slate-800 w-fit mx-auto md:mx-0">
               {['Owned', 'Hunting'].map(t => (
                 <button 
                  key={t} onClick={() => setActiveTab(t.toLowerCase())}
                  className={`px-6 py-2 text-[10px] font-black uppercase rounded-xl transition-all ${activeTab === t.toLowerCase() ? 'bg-blue-600 text-white' : 'text-slate-500 hover:bg-slate-800'}`}
                 >
                   {t === 'Owned' ? 'ทัพหลัก' : 'หน่วยล่า'}
                 </button>
               ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
               {analyzed.filter(s => s.type.toLowerCase() === activeTab).map((s, i) => (
                 <div key={s.symbol} className="bg-slate-900 p-6 rounded-[3rem] border border-slate-800 shadow-xl relative overflow-hidden group hover:border-blue-500/30 transition-all">
                    <div className="absolute top-0 right-0 p-4 opacity-[0.02] group-hover:opacity-[0.05] transition-opacity"><Activity size={100}/></div>
                    
                    <div className="flex justify-between items-start mb-4 relative z-10">
                       <h3 className="text-4xl font-black italic tracking-tighter">{s.symbol}</h3>
                       <div className="text-right">
                          <p className="text-[8px] font-black text-slate-500 uppercase italic">Market</p>
                          <p className="text-xl font-black text-white italic">฿{s.last.toFixed(2)}</p>
                       </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2 mb-4 relative z-10">
                       <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                          <p className="text-[7px] font-bold text-slate-600 uppercase">หุ้น</p>
                          <input type="number" value={s.qty} onChange={(e)=>updateStock(stocks.findIndex(st=>st.symbol===s.symbol), 'qty', Number(e.target.value))} className="bg-transparent w-full font-black text-xs text-blue-400 outline-none"/>
                       </div>
                       <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                          <p className="text-[7px] font-bold text-slate-600 uppercase">ทุน</p>
                          <input type="number" value={s.avg} onChange={(e)=>updateStock(stocks.findIndex(st=>st.symbol===s.symbol), 'avg', Number(e.target.value))} className="bg-transparent w-full font-black text-xs text-indigo-400 outline-none"/>
                       </div>
                    </div>

                    <div className="grid grid-cols-3 gap-1 mb-5 text-center relative z-10">
                       <div className="bg-slate-800/40 p-2 rounded-lg">
                          <p className="text-[7px] font-bold text-slate-500 uppercase tracking-tighter">RSI</p>
                          <p className={`text-[10px] font-black ${s.rsi > 75 ? 'text-rose-500' : 'text-emerald-400'}`}>{s.rsi}</p>
                       </div>
                       <div className="bg-slate-800/40 p-2 rounded-lg">
                          <p className="text-[7px] font-bold text-slate-500 uppercase tracking-tighter">Whale</p>
                          <p className={`text-[10px] font-black ${s.ratio < 0.5 ? 'text-emerald-400' : 'text-rose-400'}`}>{s.ratio.toFixed(2)}</p>
                       </div>
                       <div className="bg-slate-800/40 p-2 rounded-lg">
                          <p className="text-[7px] font-bold text-slate-500 uppercase tracking-tighter">EMA 5</p>
                          <p className="text-[10px] font-black text-slate-300">{s.ema5.toFixed(2)}</p>
                       </div>
                    </div>

                    <div className={`${s.color} p-4 rounded-2xl shadow-lg border border-white/5 relative z-10`}>
                       <div className="flex items-center gap-1.5 mb-1 opacity-70">
                          <Zap size={12} className="text-white fill-white"/>
                          <p className="text-[8px] font-black uppercase text-white">Iron Rule Order</p>
                       </div>
                       <p className="text-xs font-black text-white italic leading-tight uppercase">{s.cmd}</p>
                       {s.isOwned && (
                         <p className={`text-[9px] font-bold mt-1 ${s.isProfit ? 'text-emerald-100' : 'text-rose-100'}`}>
                           PNL: {s.pnl.toLocaleString()} บ.
                         </p>
                       )}
                    </div>
                 </div>
               ))}
            </div>

            <div className="mt-12 bg-gradient-to-br from-blue-950 to-slate-900 p-8 rounded-[4rem] border border-blue-500/20 flex flex-col md:flex-row items-center gap-8 shadow-2xl relative overflow-hidden">
               <div className="absolute top-0 right-0 p-12 opacity-5"><Activity size={200}/></div>
               <div className="w-20 h-20 bg-blue-600 rounded-3xl flex items-center justify-center shrink-0 shadow-xl shadow-blue-500/20"><DollarSign size={32} className="text-white" /></div>
               <div className="flex-1 text-center md:text-left">
                  <h3 className="text-xl font-black mb-2 uppercase italic tracking-tight underline decoration-blue-500 decoration-4 underline-offset-4">ปูมบันทึกจอมทัพ</h3>
                  <p className="text-xs font-bold text-slate-400 leading-relaxed italic">
                    "พี่โบ้ครับ v37 คือความนิ่งเหนือความผันผวน... เราลบปัญหาตัว Baht Sign ทิ้ง และเน้นแค่แรงวาฬกับราคาที่ได้เปรียบ กระสุน {config.warFund.toLocaleString()} บาท คือดาบที่จะไปทวงคืนแสนแรกตามกฎเหล็กครับ!"
                  </p>
               </div>
            </div>
          </div>
        )}
      </div>

      {/* Nav */}
      <div className="fixed bottom-0 left-0 right-0 p-8 flex justify-center z-40 bg-gradient-to-t from-[#020617] to-transparent">
         <div className="bg-slate-900/80 backdrop-blur-2xl border border-white/10 p-2 rounded-[3.5rem] flex gap-4 shadow-2xl">
            <button onClick={() => setActiveTab('owned')} className={`p-4 rounded-[2.5rem] transition-all ${activeTab === 'owned' ? 'bg-blue-600 text-white shadow-xl shadow-blue-600/40' : 'text-slate-500 hover:bg-slate-800'}`}>
               <List size={24}/>
            </button>
            <button onClick={() => setActiveTab('hunting')} className={`p-4 rounded-[2.5rem] transition-all ${activeTab === 'hunting' ? 'bg-orange-600 text-white shadow-xl shadow-orange-600/40' : 'text-slate-500 hover:bg-slate-800'}`}>
               <Target size={24}/>
            </button>
            <button onClick={() => setActiveTab('settings')} className={`p-4 rounded-[2.5rem] transition-all ${activeTab === 'settings' ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-600/40' : 'text-slate-500 hover:bg-slate-800'}`}>
               <Settings size={24}/>
            </button>
         </div>
      </div>
    </div>
  );
};

export default App;
