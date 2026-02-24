import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, doc, setDoc, onSnapshot } from 'firebase/firestore';
import { 
  ShieldCheck, Settings, Target, TrendingUp, TrendingDown, 
  Zap, BarChart3, Activity, Info, Save, Key,
  Search, DollarSign, List, Calculator, AlertTriangle, ArrowRight,
  RefreshCw, MousePointer2
} from 'lucide-react';

// --- Firebase Standard Config ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'geminibo-sovereign-v33';

const App = () => {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('portfolio');
  const [isSaving, setIsSaving] = useState(false);

  // --- (กฎข้อ 1) ระบบตั้งค่าที่จำฝังใจ ---
  const [config, setConfig] = useState({
    setSmartApiKey: '',
    setSmartId: '',
    warFund: 58000,
    lineToken: '',
    riskLimit: 1.0, // คัทลอสที่ 1% ตามแผน
  });

  // --- (กฎข้อ 5 & 5.1) ข้อมูลกองทัพทั้งหมด (เก่า + ใหม่) ---
  const [stocks, setStocks] = useState([
    // กลุ่มหุ้นในมือ (Owned)
    { symbol: 'SIRI', qty: 4200, avg: 1.47, type: 'Owned', last: 1.56, rsi: 88, ema5: 1.54, bidSum: 15.2, offSum: 22.8, note: 'ตัวแบกพอร์ต' },
    { symbol: 'MTC', qty: 400, avg: 38.50, type: 'Owned', last: 36.75, rsi: 35, ema5: 38.10, bidSum: 4.5, offSum: 18.2, note: 'รอเด้งขายตัด' },
    { symbol: 'HMPRO', qty: 400, avg: 7.05, type: 'Owned', last: 7.05, rsi: 28, ema5: 7.20, bidSum: 6.2, offSum: 1.4, note: 'รับ 7.05 แล้ว รอ 7.00' },
    
    // กลุ่มหุ้นสอดแนม/ล่าปันผล (Rule 5.2 / 6)
    { symbol: 'PTT', qty: 100, avg: 33.00, type: 'Rising', last: 36.50, rsi: 62, ema5: 36.10, bidSum: 35.2, offSum: 5.4, div: '1.40' },
    { symbol: 'TRUE', qty: 0, avg: 0, type: 'Strange', last: 14.30, rsi: 72, ema5: 14.10, bidSum: 12.5, offSum: 36.5, note: 'กำแพง 3 ชั้น' },
    { symbol: 'SCB', qty: 0, avg: 0, type: 'Rising', last: 148.5, rsi: 55, ema5: 146.0, bidSum: 2.5, offSum: 1.8, div: '9.28' },
    { symbol: 'HANA', qty: 0, avg: 0, type: 'Strange', last: 18.80, rsi: 42, ema5: 18.90, bidSum: 1.2, offSum: 1.8, note: 'ขายแล้ว 18.80 รอช้อนใหม่' },
    { symbol: 'ITEL', qty: 0, avg: 0, type: 'Strange', last: 2.44, rsi: 52, ema5: 2.40, bidSum: 5.5, offSum: 2.1, note: 'ม้าซุ่มวอลลุ่ม' },
    { symbol: 'CPALL', qty: 0, avg: 0, type: 'Rising', last: 51.25, rsi: 38, ema5: 52.50, bidSum: 2.1, offSum: 4.8, note: 'แนวรับ 50.00' },
    { symbol: 'BDMS', qty: 0, avg: 0, type: 'Rising', last: 27.50, rsi: 45, ema5: 27.25, bidSum: 8.4, offSum: 3.2, note: 'หุ้นหลบภัย' }
  ]);

  // Firebase Auth & Cloud Sync
  useEffect(() => {
    signInAnonymously(auth).catch(console.error);
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!user) return;
    const configRef = doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'sovereign_config_v33');
    return onSnapshot(configRef, (d) => d.exists() && setConfig(d.data()));
  }, [user]);

  const saveConfig = async () => {
    if (!user) return;
    setIsSaving(true);
    await setDoc(doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'sovereign_config_v33'), config);
    setIsSaving(false);
  };

  const updateStockData = (index, field, value) => {
    const newStocks = [...stocks];
    newStocks[index][field] = value;
    setStocks(newStocks);
  };

  // --- (IRON RULE ENGINE) ระบบสั่งการอัตโนมัติ ---
  const analyzedStocks = useMemo(() => {
    return stocks.map(s => {
      const ratio = s.offSum / s.bidSum || 0;
      const isOwned = s.qty > 0;
      const profit = isOwned ? (s.last - s.avg) * s.qty : 0;
      const isProfit = isOwned && s.last >= s.avg;
      
      let command = "";
      let cmdColor = "bg-slate-800";

      if (isOwned) {
        if (isProfit) { // กฎ 5.1.1
          if (ratio < 0.5 && s.rsi < 85) { command = "💎 ห้ามขายหมู! รอรันกำไร"; cmdColor = "bg-emerald-600"; }
          else { command = "💰 แบ่งขาย 1/2 (ต้านหนา/RSI ตึง)"; cmdColor = "bg-amber-600"; }
        } else { // กฎ 5.1.2 (ติดดอย)
          if (s.rsi < 35) { command = "⚖️ รอเด้งก้นเหว (ห้ามคัดล่าง)"; cmdColor = "bg-blue-600"; }
          else if (s.last > s.ema5) { command = "🚨 ขายตัด/เฉือนเนื้อ (หนีตาม EMA)"; cmdColor = "bg-rose-600"; }
          else { command = "⌛ รอจังหวะถัว (ถ้าหยุดไหล)"; cmdColor = "bg-indigo-600"; }
        }
      } else { // กฎ 6 & 5.2 (ยังไม่มีหุ้น)
        if (ratio < 0.4 && s.last > s.ema5) { command = "🏹 ช้อนตามน้ำ! (วาฬเปิดทาง)"; cmdColor = "bg-emerald-600 border-2 border-emerald-400 animate-pulse"; }
        else if (s.rsi < 40) { command = "🎯 เฝ้าช่องเข้า 5.2 (จ่อก้นเหว)"; cmdColor = "bg-slate-700"; }
        else { command = "📡 รอกระแสเงินไหลเข้า"; cmdColor = "bg-slate-800"; }
      }

      return { ...s, ratio, isOwned, isProfit, profit, command, cmdColor };
    });
  }, [stocks]);

  if (!user) return <div className="h-screen bg-[#020617] flex items-center justify-center text-blue-500 font-black animate-pulse text-2xl tracking-widest uppercase">Initializing v33.0...</div>;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 font-sans pb-32 overflow-x-hidden">
      
      {/* HEADER: (RULE 1) SETSMART COMMAND CENTER */}
      <div className="bg-slate-900/90 border-b border-white/5 p-6 sticky top-0 z-50 backdrop-blur-xl shadow-2xl">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-5">
            <div className="bg-blue-600 p-4 rounded-3xl shadow-lg shadow-blue-500/20">
              <ShieldCheck size={32} className="text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-black italic tracking-tighter uppercase">GEMINIBO <span className="text-blue-500">MASTER</span> v33.0</h1>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2">
                <Activity size={10} className="text-emerald-500 animate-pulse"/> INTEGRATED IRON RULES
              </p>
            </div>
          </div>
          <div className="flex gap-4">
             <div className="bg-slate-950 px-6 py-3 rounded-2xl border border-slate-800 text-center">
                <p className="text-[9px] font-black text-slate-500 uppercase mb-1">War Fund</p>
                <p className="text-xl font-black text-emerald-400">฿{config.warFund.toLocaleString()}</p>
             </div>
             <button onClick={() => setActiveTab('settings')} className={`p-4 rounded-2xl transition-all ${activeTab === 'settings' ? 'bg-blue-600 shadow-blue-500/50' : 'bg-slate-800 hover:bg-slate-700'}`}>
                <Settings size={20} />
             </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 md:p-8">
        
        {activeTab === 'settings' ? (
          /* CONFIGURATION: (IRON RULE 1 & 2) */
          <div className="max-w-2xl mx-auto space-y-8 animate-in zoom-in duration-300">
             <div className="bg-slate-900 p-10 rounded-[4rem] border border-slate-800 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-10 opacity-5"><Key size={200}/></div>
                <h2 className="text-2xl font-black mb-8 italic flex items-center gap-3"><Key className="text-blue-500"/> (ข้อ 1) SETSmart ID Bridge</h2>
                <div className="space-y-6">
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase ml-2">User ID</label>
                        <input type="text" value={config.setSmartId} onChange={(e)=>setConfig({...config, setSmartId: e.target.value})} className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-blue-400 font-mono text-sm outline-none"/>
                      </div>
                      <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase ml-2">API Key</label>
                        <input type="password" value={config.setSmartApiKey} onChange={(e)=>setConfig({...config, setSmartApiKey: e.target.value})} className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-blue-400 font-mono text-sm outline-none"/>
                      </div>
                   </div>
                   <div className="space-y-2">
                      <label className="text-[10px] font-bold text-slate-500 uppercase ml-2">กระสุนเงินสดรวม</label>
                      <input type="number" value={config.warFund} onChange={(e)=>setConfig({...config, warFund: Number(e.target.value)})} className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-emerald-400 font-black text-2xl outline-none"/>
                   </div>
                   <button onClick={saveConfig} disabled={isSaving} className="w-full py-5 bg-blue-600 hover:bg-blue-500 rounded-3xl font-black text-xs uppercase tracking-widest shadow-xl transition-all">
                     {isSaving ? 'MEMORIZING...' : 'SAVE CONFIGURATION'}
                   </button>
                </div>
             </div>

             <div className="p-8 bg-indigo-900/20 border border-indigo-500/20 rounded-[3rem]">
                <h3 className="text-xs font-black uppercase text-indigo-400 mb-4 tracking-[0.2em]">📜 ท่องกฎเหล็กก่อนออกรบ</h3>
                <ul className="space-y-3 text-[11px] font-bold text-slate-400 italic">
                  <li>• อัปเกรดทุกครั้งต้องอิงราคาและวอลลุ่มจาก SETSmart เท่านั้น</li>
                  <li>• ถ้ามีหุ้นแล้ว (กำไร) -> ห้ามขายหมู / (ดอย) -> รอเด้งขายตัด</li>
                  <li>• ถ้ายังไม่มีหุ้น -> รอช้อนตามน้ำ หรือหาช่องเข้า 5.2</li>
                </ul>
             </div>
          </div>
        ) : (
          /* MAIN DASHBOARD: (IRON RULE 5.1 & 5.2) */
          <div className="space-y-12">
            
            {/* SEARCH & GROUPING */}
            <div className="flex flex-col md:flex-row gap-4 items-center px-4">
               <h2 className="text-sm font-black text-slate-400 uppercase tracking-[0.4em] italic flex items-center gap-3">
                 <List size={18} className="text-blue-500"/> รายงานสมรภูมิขุนพล 11 ตัว
               </h2>
               <div className="flex-1"></div>
               <div className="bg-slate-900 p-2 rounded-2xl border border-slate-800 flex gap-2 overflow-x-auto no-scrollbar">
                  {['Owned', 'Strange', 'Rising'].map(t => (
                    <button key={t} className="px-5 py-2 text-[9px] font-black uppercase rounded-xl hover:bg-slate-800 border border-transparent hover:border-slate-700 transition-all">{t}</button>
                  ))}
               </div>
            </div>

            {/* INTEGRATED UNIT GRID (NO LOSS OF DATA) */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
               {analyzedStocks.map((s, idx) => (
                 <div key={s.symbol} className="bg-slate-900 p-8 rounded-[4rem] border border-slate-800 shadow-xl relative overflow-hidden group transition-all hover:border-blue-500/30">
                    <div className="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:opacity-[0.1] transition-opacity">
                       <Zap size={140}/>
                    </div>

                    <div className="flex justify-between items-start mb-6 relative z-10">
                       <div>
                          <h3 className="text-5xl font-black italic tracking-tighter">{s.symbol}</h3>
                          <span className={`text-[8px] font-black uppercase px-2 py-1 rounded ${s.type === 'Owned' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-slate-800 text-slate-500'}`}>
                            {s.type} UNIT
                          </span>
                       </div>
                       <div className="text-right">
                          <p className="text-[10px] font-bold text-slate-500 uppercase mb-1 tracking-tighter">Market Price</p>
                          <p className="text-2xl font-black text-white italic">฿{s.last.toFixed(2)}</p>
                       </div>
                    </div>

                    {/* (IRON RULE 4) PORTFOLIO INPUT FIELDS */}
                    <div className="grid grid-cols-2 gap-3 mb-6 relative z-10">
                       <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800 group-hover:border-blue-500/20 transition-all">
                          <p className="text-[8px] font-bold text-slate-600 uppercase mb-1">จำนวนหุ้น</p>
                          <input type="number" value={s.qty} onChange={(e)=>updateStockData(idx, 'qty', Number(e.target.value))} className="bg-transparent w-full font-black text-sm text-blue-400 outline-none"/>
                       </div>
                       <div className="bg-slate-950/80 p-3 rounded-2xl border border-slate-800 group-hover:border-blue-500/20 transition-all">
                          <p className="text-[8px] font-bold text-slate-600 uppercase mb-1">ต้นทุน (Cost)</p>
                          <input type="number" value={s.avg} onChange={(e)=>updateStockData(idx, 'avg', Number(e.target.value))} className="bg-transparent w-full font-black text-sm text-indigo-400 outline-none"/>
                       </div>
                    </div>

                    {/* (IRON RULE 1-3) 3-PILLAR DATA MATRIX */}
                    <div className="grid grid-cols-3 gap-2 mb-8 relative z-10 text-center">
                       <div className="bg-slate-800/40 p-3 rounded-2xl">
                          <p className="text-[8px] font-bold text-slate-500 uppercase">RSI</p>
                          <p className={`text-xs font-black ${s.rsi > 70 ? 'text-rose-500' : 'text-emerald-400'}`}>{s.rsi}</p>
                       </div>
                       <div className="bg-slate-800/40 p-3 rounded-2xl">
                          <p className="text-[8px] font-bold text-slate-500 uppercase">EMA 5</p>
                          <p className="text-xs font-black text-slate-300">{s.ema5.toFixed(2)}</p>
                       </div>
                       <div className="bg-slate-800/40 p-3 rounded-2xl">
                          <p className="text-[8px] font-bold text-slate-500 uppercase">Whale R.</p>
                          <p className={`text-xs font-black ${s.ratio < 0.5 ? 'text-emerald-400' : 'text-rose-400'}`}>{s.ratio.toFixed(2)}</p>
                       </div>
                    </div>

                    {/* (IRON RULE 5.1, 5.2, 6) COMMAND ENGINE */}
                    <div className={`${s.cmdColor} p-6 rounded-[2.5rem] shadow-lg relative z-10 border border-white/10`}>
                       <div className="flex items-center gap-2 mb-2 opacity-70">
                          <Zap size={14} className="text-white fill-white"/>
                          <p className="text-[9px] font-black uppercase tracking-widest text-white">คำสั่งยุทธการ (Iron Order)</p>
                       </div>
                       <p className="text-sm font-black text-white italic tracking-tight mb-2 leading-none uppercase">{s.command}</p>
                       
                       {s.isOwned ? (
                         <p className={`text-[10px] font-black ${s.isProfit ? 'text-emerald-200' : 'text-rose-100'}`}>
                           {s.isProfit ? 'WIN: ' : 'LOSS: '} {s.profit.toLocaleString()} บ.
                         </p>
                       ) : (
                         <div className="flex items-center gap-2 bg-black/20 p-2 rounded-xl border border-white/5">
                            <Target size={12} className="text-blue-400"/>
                            <p className="text-[9px] font-bold text-blue-200">ช่องเข้า: ฿{s.ema5.toFixed(2)}</p>
                         </div>
                       )}
                    </div>
                    
                    {/* FOOTER NOTE PER STOCK */}
                    <p className="mt-4 text-[9px] font-bold text-slate-600 italic px-2">"{s.note}"</p>
                 </div>
               ))}
            </div>

            {/* TACTICAL FOOTER: THE COMMANDER'S LOG */}
            <div className="mt-16 bg-gradient-to-br from-indigo-950 to-blue-950 p-12 rounded-[5rem] border border-blue-500/20 shadow-2xl flex flex-col lg:flex-row items-center gap-12 relative overflow-hidden">
               <div className="absolute top-0 right-0 p-12 opacity-5"><Activity size={250}/></div>
               <div className="w-32 h-32 bg-blue-600 rounded-[3rem] flex items-center justify-center shrink-0 shadow-xl shadow-blue-500/20">
                  <DollarSign size={64} className="text-white" />
               </div>
               <div className="flex-1 text-center lg:text-left">
                  <h3 className="text-3xl font-black mb-4 uppercase italic tracking-tight decoration-blue-500 decoration-8 underline-offset-[12px] underline">ปูมบันทึกกฎเหล็ก: จอมทัพโบ้</h3>
                  <p className="text-sm font-bold text-slate-300 leading-relaxed italic mb-8 max-w-2xl">
                    "พี่โบ้ครับ v33.0 คือฐานบัญชาการที่ไม่ลบอะไรทิ้งเลย... เราคุม SIRI ที่กำไร, จัดการ MTC ที่ติดดอย, และเตรียมรวบ HMPRO ที่ 7.00 พร้อมเฝ้ารถด่วน TRUE ตามกฎเหล็ก 100% ครับ!"
                  </p>
                  <div className="flex flex-wrap justify-center lg:justify-start gap-4">
                     <div className="bg-slate-950/80 px-4 py-2 rounded-xl border border-slate-800 text-[10px] font-black text-blue-400">SETSMART SYNC: READY</div>
                     <div className="bg-slate-950/80 px-4 py-2 rounded-xl border border-slate-800 text-[10px] font-black text-emerald-400">WHALE DETECTION: ACTIVE</div>
                     <div className="bg-slate-950/80 px-4 py-2 rounded-xl border border-slate-800 text-[10px] font-black text-amber-400">DOI RECOVERY: IN PROGRESS</div>
                  </div>
               </div>
            </div>

          </div>
        )}
      </div>

      {/* PERSISTENT BOTTOM NAVIGATION (RULE 5) */}
      <div className="fixed bottom-0 left-0 right-0 p-8 flex justify-center z-40 bg-gradient-to-t from-[#020617] to-transparent">
         <div className="bg-slate-900/80 backdrop-blur-2xl border border-white/10 p-2 rounded-[3.5rem] flex gap-4 shadow-2xl">
            <button onClick={() => setActiveTab('portfolio')} className={`p-5 rounded-[2.5rem] transition-all flex items-center gap-3 ${activeTab === 'portfolio' ? 'bg-blue-600 text-white shadow-xl shadow-blue-600/40' : 'text-slate-500 hover:bg-slate-800'}`}>
               <List size={28}/> {activeTab === 'portfolio' && <span className="text-xs font-black uppercase tracking-widest">สมรภูมิหลัก</span>}
            </button>
            <button onClick={() => setActiveTab('settings')} className={`p-5 rounded-[2.5rem] transition-all flex items-center gap-3 ${activeTab === 'settings' ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-600/40' : 'text-slate-500 hover:bg-slate-800'}`}>
               <Settings size={28}/> {activeTab === 'settings' && <span className="text-xs font-black uppercase tracking-widest">ระบบกุญแจ</span>}
            </button>
         </div>
      </div>
    </div>
  );
};

export default App;
