import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, doc, setDoc, onSnapshot } from 'firebase/firestore';
import { 
  ShieldCheck, Settings, Target, TrendingUp, TrendingDown, 
  Zap, BarChart3, Activity, Info, Save, Key,
  Search, DollarSign, List, Calculator, AlertTriangle, ArrowRight
} from 'lucide-react';

// --- Firebase Configuration ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'geminibo-sovereign-v32';

const App = () => {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('portfolio');
  const [isSaving, setIsSaving] = useState(false);

  // --- (IRON RULE 1) System Configuration ---
  const [config, setConfig] = useState({
    setSmartApiKey: '',
    setSmartId: '',
    warFund: 58000,
    lineToken: '',
    lastSync: new Date().toLocaleTimeString()
  });

  // --- (IRON RULE 5 & 5.1) All 12 Tactical Units ---
  const [stocks, setStocks] = useState([
    // หุ้นเก่า
    { symbol: 'SIRI', qty: 4200, avg: 1.47, type: 'Old', last: 1.56, rsi: 88, ema5: 1.54, bidSum: 15.2, offSum: 22.8 },
    { symbol: 'MTC', qty: 400, avg: 38.50, type: 'Old', last: 36.75, rsi: 35, ema5: 38.10, bidSum: 4.5, offSum: 18.2 },
    { symbol: 'HANA', qty: 0, avg: 0, type: 'Old', last: 18.60, rsi: 42, ema5: 18.90, bidSum: 2.1, offSum: 2.4 },
    { symbol: 'HMPRO', qty: 400, avg: 7.05, type: 'Old', last: 7.05, rsi: 28, ema5: 7.20, bidSum: 6.2, offSum: 1.4 },
    // หุ้นแปลก/ใหม่
    { symbol: 'TRUE', qty: 0, avg: 0, type: 'Strange', last: 14.20, rsi: 65, ema5: 13.90, bidSum: 12.5, offSum: 31.2 },
    { symbol: 'ADVANC', qty: 0, avg: 0, type: 'Strange', last: 245.0, rsi: 48, ema5: 242.0, bidSum: 1.1, offSum: 0.9 },
    { symbol: 'ITEL', qty: 0, avg: 0, type: 'Strange', last: 2.44, rsi: 52, ema5: 2.40, bidSum: 5.5, offSum: 2.1 },
    // 5 ตัวรุ่ง
    { symbol: 'SCB', qty: 0, avg: 0, type: 'Rising', last: 148.5, rsi: 55, ema5: 146.0, bidSum: 2.5, offSum: 1.8, div: '9.28' },
    { symbol: 'PTT', qty: 100, avg: 33.00, type: 'Rising', last: 36.50, rsi: 62, ema5: 36.10, bidSum: 35.2, offSum: 5.4, div: '1.40' },
    { symbol: 'BBL', qty: 0, avg: 0, type: 'Rising', last: 148.0, rsi: 58, ema5: 145.5, bidSum: 0.9, offSum: 1.1 },
    { symbol: 'CPALL', qty: 0, avg: 0, type: 'Rising', last: 51.25, rsi: 38, ema5: 52.50, bidSum: 2.1, offSum: 4.8 },
    { symbol: 'BDMS', qty: 0, avg: 0, type: 'Rising', last: 27.50, rsi: 45, ema5: 27.25, bidSum: 8.4, offSum: 3.2 }
  ]);

  useEffect(() => {
    signInAnonymously(auth).catch(err => console.error(err));
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!user) return;
    const configRef = doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'sovereign_config');
    return onSnapshot(configRef, (d) => d.exists() && setConfig(d.data()));
  }, [user]);

  const saveConfig = async () => {
    if (!user) return;
    setIsSaving(true);
    await setDoc(doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'sovereign_config'), config);
    setIsSaving(false);
  };

  const updateStockData = (index, field, value) => {
    const newStocks = [...stocks];
    newStocks[index][field] = value;
    setStocks(newStocks);
  };

  const analyzedStocks = useMemo(() => {
    return stocks.map(s => {
      const ratio = s.offSum / s.bidSum || 0;
      const isOwned = s.qty > 0;
      const isProfit = isOwned && s.last >= s.avg;
      const pnl = isOwned ? (s.last - s.avg) * s.qty : 0;
      
      let command = "";
      let cmdColor = "bg-slate-800";

      if (isOwned) {
        if (isProfit) { // กฎ 5.1.1
          if (ratio < 0.5 && s.rsi < 85) { command = "ห้ามขายหมู! รอรันกำไร"; cmdColor = "bg-emerald-600"; }
          else { command = "แบ่งขาย 1/2 หรือหมด (ต้านหนา/RSI ตึง)"; cmdColor = "bg-amber-600"; }
        } else { // กฎ 5.1.2 (ติดดอย)
          if (s.rsi < 35) { command = "รอเด้งก้นเหว (ห้ามคัดล่าง)"; cmdColor = "bg-blue-600"; }
          else if (s.last > s.ema5) { command = "ขายตัด/เฉือนเนื้อ (หนีตาม EMA)"; cmdColor = "bg-rose-600"; }
          else { command = "รอจังหวะถัว (ถ้าหยุดไหล)"; cmdColor = "bg-indigo-600"; }
        }
      } else { // กฎ 6 & 5.2 (ยังไม่มีหุ้น)
        if (ratio < 0.4 && s.last > s.ema5) { command = "ช้อนตามน้ำ! (วาฬดันทางสะดวก)"; cmdColor = "bg-emerald-600 animate-pulse"; }
        else if (s.rsi < 40) { command = "เฝ้าช่องเข้า 5.2 (รอวอลลุ่มสะสม)"; cmdColor = "bg-slate-700"; }
        else { command = "รอกระแสเงินไหลเข้า"; cmdColor = "bg-slate-800"; }
      }

      return { ...s, ratio, isOwned, isProfit, pnl, command, cmdColor };
    });
  }, [stocks]);

  if (!user) return <div className="h-screen bg-slate-950 flex items-center justify-center text-blue-500 font-black animate-pulse text-2xl tracking-tighter">SOVEREIGN BOOTING...</div>;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 font-sans pb-32 overflow-x-hidden">
      
      {/* (IRON RULE 1) MASTER HEADER */}
      <div className="bg-slate-900/90 border-b border-white/5 p-6 sticky top-0 z-50 backdrop-blur-xl shadow-2xl">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-5">
            <div className="bg-blue-600 p-4 rounded-[1.5rem] shadow-lg shadow-blue-500/20">
              <ShieldCheck size={32} />
            </div>
            <div>
              <h1 className="text-2xl font-black italic tracking-tighter uppercase">GEMINIBO <span className="text-blue-500">SOVEREIGN</span> v32.0</h1>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2">
                <Activity size={10} className="text-emerald-500 animate-pulse"/> IRON RULE COMPLIANCE ENGINE
              </p>
            </div>
          </div>
          <div className="flex gap-4">
             <div className="bg-slate-950 px-6 py-3 rounded-2xl border border-slate-800 text-center">
                <p className="text-[9px] font-black text-slate-500 uppercase mb-1">War Fund</p>
                <p className="text-xl font-black text-emerald-400">฿{config.warFund.toLocaleString()}</p>
             </div>
             <button onClick={() => setActiveTab('settings')} className={`p-4 rounded-2xl transition-all ${activeTab === 'settings' ? 'bg-blue-600 shadow-blue-500/50' : 'bg-slate-800 hover:bg-slate-700'}`}>
                <Settings size={20}/>
             </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 md:p-8">
        
        {activeTab === 'settings' ? (
          <div className="max-w-2xl mx-auto bg-slate-900 p-10 rounded-[3.5rem] border border-slate-800 shadow-2xl animate-in zoom-in duration-300">
             <h2 className="text-2xl font-black mb-8 italic flex items-center gap-3"><Key className="text-blue-500"/> (กฎข้อ 1) ตั้งค่า SETSmart Bridge</h2>
             <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-[10px] font-bold text-slate-500 uppercase ml-2">User ID</label>
                    <input type="text" value={config.setSmartId} onChange={(e)=>setConfig({...config, setSmartId: e.target.value})} className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-blue-400 font-mono text-sm outline-none focus:border-blue-500"/>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-bold text-slate-500 uppercase ml-2">API Key</label>
                    <input type="password" value={config.setSmartApiKey} onChange={(e)=>setConfig({...config, setSmartApiKey: e.target.value})} className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-blue-400 font-mono text-sm outline-none focus:border-blue-500"/>
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-500 uppercase ml-2">งบประมาณรวม</label>
                  <input type="number" value={config.warFund} onChange={(e)=>setConfig({...config, warFund: Number(e.target.value)})} className="w-full p-4 bg-slate-950 border border-slate-800 rounded-2xl text-emerald-400 font-black text-2xl outline-none"/>
                </div>
                <button onClick={saveConfig} disabled={isSaving} className="w-full py-5 bg-blue-600 hover:bg-blue-500 rounded-3xl font-black text-xs uppercase tracking-widest shadow-xl transition-all flex justify-center items-center gap-3">
                  <Save size={18}/> {isSaving ? 'RECODRING...' : 'SAVE CONFIGURATION'}
                </button>
             </div>
          </div>
        ) : (
          <div className="space-y-12">
            
            {/* SEARCH & FILTER */}
            <div className="flex flex-wrap gap-4 items-center px-4">
               <h2 className="text-sm font-black text-slate-400 uppercase tracking-[0.4em] italic">สมรภูมิจอมทัพโบ้</h2>
               <div className="flex-1"></div>
               <div className="flex bg-slate-900 p-1 rounded-2xl border border-slate-800">
                  {['Old', 'Strange', 'Rising'].map(t => (
                    <button key={t} className="px-4 py-2 text-[10px] font-black uppercase rounded-xl hover:bg-slate-800 transition-all">{t}</button>
                  ))}
               </div>
            </div>

            {/* MAIN UNIT GRID */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
               {analyzedStocks.map((s, idx) => (
                 <div key={s.symbol} className="bg-slate-900 p-8 rounded-[4rem] border border-slate-800 shadow-xl relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:opacity-[0.07] transition-opacity">
                       <Zap size={140}/>
                    </div>

                    <div className="flex justify-between items-start mb-6 relative z-10">
                       <div>
                          <h3 className="text-5xl font-black italic tracking-tighter">{s.symbol}</h3>
                          <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mt-1 bg-slate-950 inline-block px-2 py-1 rounded-md">{s.type} UNIT</p>
                       </div>
                       <div className="text-right">
                          <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Market Price</p>
                          <p className="text-2xl font-black text-white italic">฿{s.last.toFixed(2)}</p>
                       </div>
                    </div>

                    {/* (IRON RULE 4) PORTFOLIO INPUT */}
                    <div className="grid grid-cols-2 gap-3 mb-6 relative z-10">
                       <div className="bg-slate-950/50 p-3 rounded-2xl border border-slate-800">
                          <p className="text-[8px] font-bold text-slate-600 uppercase mb-1">จำนวนหุ้น</p>
                          <input type="number" value={s.qty} onChange={(e)=>updateStockData(idx, 'qty', Number(e.target.value))} className="bg-transparent w-full font-black text-sm text-blue-400 outline-none"/>
                       </div>
                       <div className="bg-slate-950/50 p-3 rounded-2xl border border-slate-800">
                          <p className="text-[8px] font-bold text-slate-600 uppercase mb-1">ทุนเฉลี่ย</p>
                          <input type="number" value={s.avg} onChange={(e)=>updateStockData(idx, 'avg', Number(e.target.value))} className="bg-transparent w-full font-black text-sm text-indigo-400 outline-none"/>
                       </div>
                    </div>

                    {/* (IRON RULE 1-4) DATA MATRIX */}
                    <div className="grid grid-cols-3 gap-2 mb-8 relative z-10">
                       <div className="bg-slate-800/40 p-3 rounded-2xl text-center">
                          <p className="text-[8px] font-bold text-slate-500">RSI</p>
                          <p className={`text-xs font-black ${s.rsi > 70 ? 'text-rose-500' : 'text-emerald-400'}`}>{s.rsi}</p>
                       </div>
                       <div className="bg-slate-800/40 p-3 rounded-2xl text-center">
                          <p className="text-[8px] font-bold text-slate-500">EMA5</p>
                          <p className="text-xs font-black">{s.ema5}</p>
                       </div>
                       <div className="bg-slate-800/40 p-3 rounded-2xl text-center">
                          <p className="text-[8px] font-bold text-slate-500">WHALE</p>
                          <p className={`text-xs font-black ${s.ratio < 0.5 ? 'text-emerald-400' : 'text-rose-400'}`}>{s.ratio.toFixed(2)}</p>
                       </div>
                    </div>

                    {/* ACTION COMMANDS (Rules 5.1, 5.2, 6) */}
                    <div className={`${s.cmdColor} p-5 rounded-3xl shadow-lg border border-white/5 relative z-10`}>
                       <div className="flex items-center gap-2 mb-2">
                          <Zap size={14} className="text-white fill-white"/>
                          <p className="text-[9px] font-black uppercase tracking-widest text-white/70">คำสั่งยุทธการ</p>
                       </div>
                       <p className="text-sm font-black text-white italic tracking-tight">{s.command}</p>
                       {s.isOwned && (
                         <p className={`text-[10px] font-bold mt-2 ${s.isProfit ? 'text-emerald-300' : 'text-rose-200'}`}>
                           สถานะพอร์ต: {s.isProfit ? '+' : ''}{s.pnl.toLocaleString()} บ.
                         </p>
                       )}
                       {!s.isOwned && s.ratio < 0.5 && (
                         <div className="mt-3 flex items-center gap-2 bg-black/20 p-2 rounded-xl border border-white/10">
                            <Target size={12} className="text-emerald-400"/>
                            <p className="text-[9px] font-bold text-emerald-100">ช่องเข้า 5.2: ฿{s.ema5.toFixed(2)}</p>
                         </div>
                       )}
                    </div>
                 </div>
               ))}
            </div>

            {/* TACTICAL FOOTER */}
            <div className="bg-gradient-to-br from-blue-900/40 to-slate-900 p-12 rounded-[4rem] border border-blue-500/20 shadow-2xl flex flex-col md:flex-row items-center gap-12 relative overflow-hidden">
               <div className="absolute top-0 right-0 p-12 opacity-5"><Activity size={200}/></div>
               <div className="w-28 h-28 bg-blue-600 rounded-[2.5rem] flex items-center justify-center shrink-0 shadow-xl shadow-blue-500/20">
                  <DollarSign size={54} className="text-white" />
               </div>
               <div className="flex-1 text-center md:text-left">
                  <h3 className="text-2xl font-black mb-4 uppercase italic tracking-tight underline decoration-blue-500 decoration-4 underline-offset-8">ปูมบันทึกกฎเหล็ก: จอมทัพโบ้</h3>
                  <p className="text-sm font-bold text-slate-400 leading-relaxed italic">
                    "พี่โบ้ครับ v32.0 ตัวนี้รันตามกฎ 5.1.1 ถึง 5.2 เป๊ะครับ! เราแยกขุนพลเก่า (SIRI, MTC) ออกมาบริหารเพื่อลดความเจ็บปวด และเตรียมหน่วยสอดแนม (TRUE, SCB) เพื่อหาช่องเข้าที่ได้เปรียบวาฬ... ทุกครั้งที่ขยับ พอร์ตต้องเข้มงวดตามวินัยครับ!"
                  </p>
               </div>
            </div>

          </div>
        )}
      </div>

      {/* PERSISTENT TAB BAR */}
      <div className="fixed bottom-0 left-0 right-0 p-8 flex justify-center z-40">
         <div className="bg-slate-900/80 backdrop-blur-2xl border border-white/10 p-2 rounded-[3rem] flex gap-3 shadow-2xl">
            <button onClick={() => setActiveTab('portfolio')} className={`p-5 rounded-[2.5rem] transition-all flex items-center gap-2 ${activeTab === 'portfolio' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' : 'text-slate-500'}`}>
               <List size={24}/> {activeTab === 'portfolio' && <span className="text-xs font-black uppercase tracking-widest">Frontline</span>}
            </button>
            <button onClick={() => setActiveTab('settings')} className={`p-5 rounded-[2.5rem] transition-all flex items-center gap-2 ${activeTab === 'settings' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : 'text-slate-500'}`}>
               <Settings size={24}/> {activeTab === 'settings' && <span className="text-xs font-black uppercase tracking-widest">Bridge</span>}
            </button>
         </div>
      </div>
    </div>
  );
};

export default App;
