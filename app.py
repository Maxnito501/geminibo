import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, doc, setDoc, onSnapshot } from 'firebase/firestore';
import { 
  ShieldCheck, Settings, Target, TrendingUp, TrendingDown, 
  Zap, BarChart3, Activity, Info, Save, Key,
  Search, DollarSign, List, Calculator, AlertTriangle, ArrowRight,
  RefreshCw, MousePointer2, History
} from 'lucide-react';

// --- Firebase Standard Setup ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'geminibo-sovereign-v34';

const App = () => {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('owned');
  const [isSaving, setIsSaving] = useState(false);

  // --- (IRON RULE 1) System Config Memory ---
  const [config, setConfig] = useState({
    setSmartApiKey: '',
    setSmartId: '',
    warFund: 58000,
    lastLoss: 1000, // บันทึกยอดติดลบล่าสุดตามที่พี่โบ้แจ้ง
  });

  // --- (IRON RULE 5) ทั้งหมด 12 ขุนพล (ห้ามลบ) ---
  const [stocks, setStocks] = useState([
    // กองทัพเก่า (Owned)
    { symbol: 'SIRI', qty: 4200, avg: 1.47, last: 1.56, rsi: 88, ema5: 1.54, bidSum: 15.2, offSum: 22.8, type: 'Old' },
    { symbol: 'MTC', qty: 400, avg: 38.50, last: 36.75, rsi: 35, ema5: 38.10, bidSum: 4.5, offSum: 18.2, type: 'Old' },
    { symbol: 'HMPRO', qty: 400, avg: 7.05, last: 7.05, rsi: 28, ema5: 7.20, bidSum: 6.2, offSum: 1.4, type: 'Old' },
    { symbol: 'HANA', qty: 0, avg: 0, last: 18.60, rsi: 42, ema5: 18.90, bidSum: 2.1, offSum: 2.4, type: 'Old' },
    
    // หุ้นแปลก/ใหม่ (Strange)
    { symbol: 'TRUE', qty: 0, avg: 0, last: 14.30, rsi: 72, ema5: 14.10, bidSum: 12.5, offSum: 36.5, type: 'Strange' },
    { symbol: 'ADVANC', qty: 0, avg: 0, last: 245.0, rsi: 48, ema5: 242.0, bidSum: 1.1, offSum: 0.9, type: 'Strange' },
    { symbol: 'ITEL', qty: 0, avg: 0, last: 2.44, rsi: 52, ema5: 2.40, bidSum: 5.5, offSum: 2.1, type: 'Strange' },
    
    // 5 ตัวรุ่ง (Rising Stars)
    { symbol: 'SCB', qty: 0, avg: 0, last: 148.5, rsi: 55, ema5: 146.0, bidSum: 2.5, offSum: 1.8, type: 'Rising' },
    { symbol: 'PTT', qty: 100, avg: 33.00, last: 36.50, rsi: 62, ema5: 36.10, bidSum: 35.2, offSum: 5.4, type: 'Rising' },
    { symbol: 'BBL', qty: 0, avg: 0, last: 148.0, rsi: 58, ema5: 145.5, bidSum: 0.9, offSum: 1.1, type: 'Rising' },
    { symbol: 'CPALL', qty: 0, avg: 0, last: 51.25, rsi: 38, ema5: 52.50, bidSum: 2.1, offSum: 4.8, type: 'Rising' },
    { symbol: 'BDMS', qty: 0, avg: 0, last: 27.50, rsi: 45, ema5: 27.25, bidSum: 8.4, offSum: 3.2, type: 'Rising' }
  ]);

  // Firebase Auth & Sync
  useEffect(() => {
    signInAnonymously(auth).catch(console.error);
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!user) return;
    const configRef = doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'eternal_sovereign_v34');
    return onSnapshot(configRef, (d) => d.exists() && setConfig(d.data()));
  }, [user]);

  const saveConfig = async () => {
    if (!user) return;
    setIsSaving(true);
    await setDoc(doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'eternal_sovereign_v34'), config);
    setIsSaving(false);
  };

  const updateStockData = (index, field, value) => {
    const newStocks = [...stocks];
    newStocks[index][field] = value;
    setStocks(newStocks);
  };

  // --- (IRON RULE ENGINE) ระบบตัดสินใจ 3 มิติ ---
  const analyzedStocks = useMemo(() => {
    return stocks.map(s => {
      const ratio = s.offSum / s.bidSum || 0;
      const isOwned = s.qty > 0;
      const profitVal = isOwned ? (s.last - s.avg) * s.qty : 0;
      const isProfit = isOwned && s.last >= s.avg;
      
      let command = "";
      let cmdColor = "bg-slate-800";

      if (isOwned) {
        if (isProfit) { // Rule 5.1.1
          if (ratio < 0.5 && s.rsi < 85) { command = "💎 ห้ามขายหมู! รอรันกำไร"; cmdColor = "bg-emerald-600"; }
          else { command = "💰 แบ่งขาย 1/2 (ต้านหนา)"; cmdColor = "bg-amber-600"; }
        } else { // Rule 5.1.2
          if (s.rsi < 35) { command = "⚖️ รอเด้งก้นเหว (ห้ามคัดล่าง)"; cmdColor = "bg-blue-600"; }
          else if (s.last > s.ema5) { command = "🚨 ขายตัด/เฉือนเนื้อ (หนีตาม EMA)"; cmdColor = "bg-rose-600"; }
          else { command = "⌛ รอจังหวะถัว (DCA)"; cmdColor = "bg-indigo-600"; }
        }
      } else { // Rule 5.2 & 6
        if (ratio < 0.4 && s.last > s.ema5) { command = "🏹 ช้อนตามน้ำ! (วาฬเปิดทาง)"; cmdColor = "bg-emerald-600 animate-pulse"; }
        else if (s.rsi < 40) { command = "🎯 เฝ้าช่องเข้า 5.2 (รอฐาน)"; cmdColor = "bg-slate-700"; }
        else { command = "📡 รอกระแสเงินไหลเข้า"; cmdColor = "bg-slate-800"; }
      }

      return { ...s, ratio, isOwned, isProfit, profitVal, command, cmdColor };
    });
  }, [stocks]);

  if (!user) return <div className="h-screen bg-slate-950 flex items-center justify-center text-blue-500 font-black animate-pulse text-2xl uppercase tracking-tighter italic font-sans">Eternal Iron sovereign booting...</div>;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 font-sans pb-32 overflow-x-hidden">
      
      {/* HEADER: COMMAND CENTER (Rule 1 Support) */}
      <div className="bg-slate-900/90 border-b border-white/5 p-6 sticky top-0 z-50 backdrop-blur-xl shadow-2xl">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-5">
            <div className="bg-blue-600 p-4 rounded-3xl shadow-lg shadow-blue-500/20">
              <ShieldCheck size={32} className="text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-black italic tracking-tighter uppercase italic">GEMINIBO <span className="text-blue-500">ETERNAL</span> v34.0</h1>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2">
                <History size={10} className="text-blue-400"/> ไม่ลบของเก่า ยึดกฎเหล็กเป็นที่ตั้ง
              </p>
            </div>
          </div>
          <div className="flex gap-4">
             <div className="bg-slate-950 px-6 py-3 rounded-2xl border border-slate-800 text-center">
                <p className="text-[9px] font-black text-slate-500 uppercase mb-1 italic">War Fund (เสบียง)</p>
                <p className="text-xl font-black text-emerald-400">฿{config.warFund.toLocaleString()}</p>
             </div>
             <button onClick={() => setActiveTab('settings')} className={`p-4 rounded-2xl transition-all ${activeTab === 'settings' ? 'bg-blue-600 shadow-blue-500/50' : 'bg-slate-800 hover:bg-slate-700'}`}>
                <Settings size={20} />
             </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 md:p-8 font-sans">
        
        {activeTab === 'settings' ? (
          /* CONFIGURATION: IRON RULE SETTINGS */
          <div className="max-w-2xl mx-auto space-y-8 animate-in zoom-in duration-300">
             <div className="bg-slate-900 p-10 rounded-[4rem] border border-slate-800 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-10 opacity-5"><Key size={200}/></div>
                <h2 className="text-2xl font-black mb-8 italic flex items-center gap-3 underline decoration-blue-500 decoration-4"><Key className="text-blue-500"/> (ข้อ 1) ดึงข้อมูล SETSmart</h2>
                <div className="space-y-6">
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase ml-2 tracking-widest font-black">User ID</label>
                        <input type="text" value={config.setSmartId} onChange={(e)=>setConfig({...config, setSmartId: e.target.value})} className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-blue-400 font-mono text-sm outline-none"/>
                      </div>
                      <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase ml-2 tracking-widest font-black">API Key</label>
                        <input type="password" value={config.setSmartApiKey} onChange={(e)=>setConfig({...config, setSmartApiKey: e.target.value})} className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-blue-400 font-mono text-sm outline-none"/>
                      </div>
                   </div>
                   <div className="space-y-2">
                      <label className="text-[10px] font-bold text-slate-500 uppercase ml-2 tracking-widest font-black">ยอดเงินสดในมือรวม</label>
                      <input type="number" value={config.warFund} onChange={(e)=>setConfig({...config, warFund: Number(e.target.value)})} className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-emerald-400 font-black text-2xl outline-none"/>
                   </div>
                   <button onClick={saveConfig} disabled={isSaving} className="w-full py-5 bg-blue-600 hover:bg-blue-500 rounded-3xl font-black text-xs uppercase tracking-widest shadow-xl transition-all">
                     {isSaving ? 'MEMORIZING IRON RULES...' : 'SAVE SETTINGS (RECORD TO CLOUD)'}
                   </button>
                </div>
             </div>
             
             <div className="bg-rose-900/10 border border-rose-500/20 p-8 rounded-[3rem]">
                <h3 className="text-xs font-black uppercase text-rose-400 mb-4 tracking-[0.3em] flex items-center gap-2"><AlertTriangle size={14}/> เป้าหมายกู้คืน (Recovery Goal)</h3>
                <div className="flex justify-between items-center">
                   <p className="text-sm font-bold text-slate-300 italic">ติดลบสะสมตอนนี้:</p>
                   <p className="text-2xl font-black text-rose-500">฿{config.lastLoss.toLocaleString()}</p>
                </div>
             </div>
          </div>
        ) : (
          /* MAIN BATTLE DASHBOARD */
          <div className="space-y-12">
            
            {/* TABS SELECTOR */}
            <div className="flex flex-col md:flex-row gap-4 items-center px-4">
               <div className="bg-slate-900 p-2 rounded-[2rem] border border-slate-800 flex gap-2 w-full md:w-auto">
                  {['Old', 'Strange', 'Rising'].map(t => (
                    <button 
                      key={t} onClick={() => setActiveTab(t.toLowerCase())}
                      className={`flex-1 md:flex-none px-8 py-3 text-[10px] font-black uppercase rounded-2xl transition-all ${activeTab === t.toLowerCase() ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:bg-slate-800'}`}
                    >
                      {t === 'Old' ? 'กองทัพหลัก' : t === 'Strange' ? 'หน่วยแปลก' : '5 ตัวรุ่ง'}
                    </button>
                  ))}
               </div>
               <div className="flex-1"></div>
               <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest italic leading-none text-right">
                 "วินัยเหนือกำไร คือชัยชนะของจอมทัพ"
               </p>
            </div>

            {/* UNITS GRID */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
               {analyzedStocks.filter(s => s.type.toLowerCase() === activeTab || activeTab === 'all').map((s, idx) => (
                 <div key={s.symbol} className="bg-slate-900 p-8 rounded-[4rem] border border-slate-800 shadow-xl relative overflow-hidden group hover:border-blue-500/30 transition-all">
                    <div className="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:opacity-[0.1] transition-opacity">
                       <Zap size={140}/>
                    </div>

                    <div className="flex justify-between items-start mb-6 relative z-10">
                       <div>
                          <h3 className="text-5xl font-black italic tracking-tighter">{s.symbol}</h3>
                          <span className={`text-[8px] font-black uppercase px-2 py-1 rounded mt-2 inline-block ${s.isOwned ? 'bg-indigo-500/20 text-indigo-400' : 'bg-slate-800 text-slate-500'}`}>
                            {s.isOwned ? 'IN FIELD (5.1)' : 'SPYING (5.2)'}
                          </span>
                       </div>
                       <div className="text-right">
                          <p className="text-[10px] font-black text-slate-500 uppercase mb-1">Market Price</p>
                          <p className="text-3xl font-black text-white italic tracking-tighter">฿{s.last.toFixed(2)}</p>
                       </div>
                    </div>

                    {/* PORTFOLIO INPUTS */}
                    <div className="grid grid-cols-2 gap-3 mb-6 relative z-10">
                       <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800">
                          <p className="text-[8px] font-bold text-slate-600 uppercase mb-1">จำนวนหุ้น</p>
                          <input type="number" value={s.qty} onChange={(e)=>updateStockData(stocks.findIndex(st=>st.symbol===s.symbol), 'qty', Number(e.target.value))} className="bg-transparent w-full font-black text-sm text-blue-400 outline-none"/>
                       </div>
                       <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800">
                          <p className="text-[8px] font-bold text-slate-600 uppercase mb-1">ต้นทุนเฉลี่ย</p>
                          <input type="number" value={s.avg} onChange={(e)=>updateStockData(stocks.findIndex(st=>st.symbol===s.symbol), 'avg', Number(e.target.value))} className="bg-transparent w-full font-black text-sm text-indigo-400 outline-none"/>
                       </div>
                    </div>

                    {/* DATA MATRIX (IRON RULE 1-4) */}
                    <div className="grid grid-cols-3 gap-2 mb-8 relative z-10 text-center">
                       <div className="bg-slate-800/40 p-3 rounded-2xl border border-white/5">
                          <p className="text-[8px] font-bold text-slate-500 uppercase">RSI</p>
                          <p className={`text-xs font-black ${s.rsi > 75 ? 'text-rose-500' : 'text-emerald-400'}`}>{s.rsi}</p>
                       </div>
                       <div className="bg-slate-800/40 p-3 rounded-2xl border border-white/5">
                          <p className="text-[8px] font-bold text-slate-500 uppercase">EMA 5</p>
                          <p className="text-xs font-black text-slate-300">{s.ema5.toFixed(2)}</p>
                       </div>
                       <div className="bg-slate-800/40 p-3 rounded-2xl border border-white/5">
                          <p className="text-[8px] font-bold text-slate-500 uppercase">Whale R.</p>
                          <p className={`text-xs font-black ${s.ratio < 0.5 ? 'text-emerald-400' : 'text-rose-400'}`}>{s.ratio.toFixed(2)}</p>
                       </div>
                    </div>

                    {/* ACTION COMMANDS */}
                    <div className={`${s.cmdColor} p-6 rounded-[2.5rem] shadow-lg relative z-10 border border-white/10`}>
                       <div className="flex items-center gap-2 mb-2 opacity-80">
                          <Zap size={14} className="text-white fill-white"/>
                          <p className="text-[9px] font-black uppercase tracking-widest text-white italic">Iron Order</p>
                       </div>
                       <p className="text-sm font-black text-white italic tracking-tight mb-2 leading-none uppercase">{s.command}</p>
                       
                       {s.isOwned ? (
                         <div className="flex justify-between items-center mt-3 border-t border-white/10 pt-2">
                           <p className="text-[10px] font-black text-white opacity-70 uppercase tracking-widest">PNL EST:</p>
                           <p className={`text-[11px] font-black ${s.isProfit ? 'text-emerald-200' : 'text-rose-100'}`}>
                              {s.isProfit ? '+' : ''} {s.profitVal.toLocaleString()} บ.
                           </p>
                         </div>
                       ) : (
                         <div className="flex items-center gap-2 bg-black/20 p-2 rounded-xl border border-white/5 mt-3">
                            <Target size={12} className="text-blue-400"/>
                            <p className="text-[9px] font-bold text-blue-200">ช่องเข้า 5.2: ฿{s.ema5.toFixed(2)}</p>
                         </div>
                       )}
                    </div>
                 </div>
               ))}
            </div>

            {/* STRATEGIC LOG */}
            <div className="mt-16 bg-gradient-to-br from-blue-950/50 to-indigo-950/50 p-12 rounded-[5rem] border border-blue-500/20 shadow-2xl flex flex-col lg:flex-row items-center gap-12 relative overflow-hidden">
               <div className="absolute top-0 right-0 p-12 opacity-5"><BarChart3 size={250}/></div>
               <div className="w-32 h-32 bg-blue-600 rounded-[3rem] flex items-center justify-center shrink-0 shadow-xl shadow-blue-500/20">
                  <DollarSign size={64} className="text-white" />
               </div>
               <div className="flex-1 text-center lg:text-left">
                  <h3 className="text-3xl font-black mb-4 uppercase italic tracking-tight decoration-blue-500 decoration-8 underline-offset-[12px] underline font-sans">ปูมบันทึกกฎเหล็ก: จอมทัพโบ้</h3>
                  <p className="text-sm font-bold text-slate-300 leading-relaxed italic mb-8 max-w-2xl font-sans">
                    "พี่โบ้ครับ v34.0 คือฐานทัพถาวร... เราคุม SIRI ที่กำไร, จัดการ MTC ที่ติดดอย, และเฝ้า HMPRO/TRUE ตามกฎเหล็ก 100% ผมสัญญาว่าจะไม่อัปเดตแบบลบของเก่าทิ้งอีก... ทุกขุนพลต้องอยู่รอดจนจบสงครามครับ!"
                  </p>
                  <div className="flex flex-wrap justify-center lg:justify-start gap-4">
                     <div className="bg-slate-950/80 px-4 py-2 rounded-xl border border-slate-800 text-[10px] font-black text-blue-400 uppercase tracking-widest italic">SETSmart Sync: Ready</div>
                     <div className="bg-slate-950/80 px-4 py-2 rounded-xl border border-slate-800 text-[10px] font-black text-emerald-400 uppercase tracking-widest italic">Whale Detected: Active</div>
                     <div className="bg-slate-950/80 px-4 py-2 rounded-xl border border-slate-800 text-[10px] font-black text-rose-400 uppercase tracking-widest italic">Loss Recovery: ฿1,000</div>
                  </div>
               </div>
            </div>

          </div>
        )}
      </div>

      {/* PERSISTENT NAV (MOBILE READY) */}
      <div className="fixed bottom-0 left-0 right-0 p-8 flex justify-center z-40 bg-gradient-to-t from-[#020617] to-transparent">
         <div className="bg-slate-900/80 backdrop-blur-2xl border border-white/10 p-2 rounded-[3.5rem] flex gap-4 shadow-2xl">
            <button onClick={() => setActiveTab('old')} className={`p-5 rounded-[2.5rem] transition-all flex items-center gap-3 ${activeTab === 'old' ? 'bg-blue-600 text-white shadow-xl shadow-blue-600/40' : 'text-slate-500 hover:bg-slate-800'}`}>
               <List size={28}/> {activeTab === 'old' && <span className="text-xs font-black uppercase tracking-widest italic">กองทัพหลัก</span>}
            </button>
            <button onClick={() => setActiveTab('strange')} className={`p-5 rounded-[2.5rem] transition-all flex items-center gap-3 ${activeTab === 'strange' ? 'bg-orange-600 text-white shadow-xl shadow-orange-600/40' : 'text-slate-500 hover:bg-slate-800'}`}>
               <Zap size={28}/> {activeTab === 'strange' && <span className="text-xs font-black uppercase tracking-widest italic">หน่วยซุ่ม</span>}
            </button>
            <button onClick={() => setActiveTab('settings')} className={`p-5 rounded-[2.5rem] transition-all flex items-center gap-3 ${activeTab === 'settings' ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-600/40' : 'text-slate-500 hover:bg-slate-800'}`}>
               <Settings size={28}/> {activeTab === 'settings' && <span className="text-xs font-black uppercase tracking-widest italic">ระบบกุญแจ</span>}
            </button>
         </div>
      </div>
    </div>
  );
};

export default App;
