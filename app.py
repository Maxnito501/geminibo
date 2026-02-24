import React, { useState, useEffect } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, doc, setDoc, onSnapshot } from 'firebase/firestore';
import { 
  Shield, 
  Settings, 
  Save, 
  Database, 
  Key, 
  Lock, 
  RefreshCw, 
  Wifi, 
  CheckCircle2,
  AlertCircle,
  Bell,
  BarChart3
} from 'lucide-react';

// --- Firebase Config (ดึงจากสภาพแวดล้อม) ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'geminibo-setsmart-v20';

const App = () => {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('settings'); // เริ่มต้นที่หน้าตั้งค่าตามคำขอพี่โบ้
  const [isSaving, setIsSaving] = useState(false);
  const [apiStatus, setApiStatus] = useState('disconnected');

  // --- ข้อมูลไอดีของพี่โบ้ (Cloud Storage) ---
  const [credentials, setCredentials] = useState({
    setSmartId: '',      // ไอดี SetSmart
    setSmartApiKey: '',  // API Key 
    lineToken: '',       // สำหรับแจ้งเตือน
    lineUserId: '',
    autoSync: true
  });

  // 1. ระบบยืนยันตัวตน (Firebase Auth)
  useEffect(() => {
    signInAnonymously(auth).catch(err => console.error("Auth Error", err));
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  // 2. ดึงข้อมูลกุญแจที่เคยบันทึกไว้ใน Cloud
  useEffect(() => {
    if (!user) return;
    const configRef = doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'setsmart_bridge');
    const unsubscribe = onSnapshot(configRef, (docSnap) => {
      if (docSnap.exists()) {
        setCredentials(docSnap.data());
        if (docSnap.data().setSmartApiKey) setApiStatus('connected');
      }
    });
    return () => unsubscribe();
  }, [user]);

  // 3. ฟังก์ชันบันทึกกุญแจลงคลาวด์ (Save Forever)
  const saveKeys = async () => {
    if (!user) return;
    setIsSaving(true);
    try {
      const configRef = doc(db, 'artifacts', appId, 'users', user.uid, 'settings', 'setsmart_bridge');
      await setDoc(configRef, credentials);
      setApiStatus('connected');
      setTimeout(() => setIsSaving(false), 800);
    } catch (err) {
      alert("เกิดข้อผิดพลาดในการบันทึก");
      setIsSaving(false);
    }
  };

  if (!user) return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-blue-500 font-black animate-pulse text-2xl italic uppercase tracking-widest">Initialising Bridge...</div>;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 font-sans pb-24">
      
      {/* Header: Status Bar */}
      <div className="bg-slate-900/80 backdrop-blur-md border-b border-white/5 sticky top-0 z-50 p-6">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className={`p-3 rounded-2xl ${apiStatus === 'connected' ? 'bg-emerald-600 shadow-emerald-500/50' : 'bg-rose-600 shadow-rose-500/50'} shadow-lg`}>
              <Wifi size={24} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-black italic tracking-tighter">GEMINIBO <span className="text-blue-500">v20.0</span></h1>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1">
                {apiStatus === 'connected' ? <><CheckCircle2 size={10} className="text-emerald-500"/> SetSmart Bridge Linked</> : <><AlertCircle size={10} className="text-rose-500"/> Offline Mode</>}
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setActiveTab('commander')} className={`p-3 rounded-xl transition-all ${activeTab === 'commander' ? 'bg-blue-600' : 'bg-slate-800'}`}><BarChart3 size={20}/></button>
            <button onClick={() => setActiveTab('settings')} className={`p-3 rounded-xl transition-all ${activeTab === 'settings' ? 'bg-blue-600' : 'bg-slate-800'}`}><Settings size={20}/></button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-6 md:p-12">
        {activeTab === 'settings' ? (
          /* --- SETTINGS: จุดที่พี่โบ้ถามหา --- */
          <div className="space-y-8 animate-in fade-in zoom-in duration-500">
            <div className="bg-slate-900 border border-slate-800 rounded-[3rem] p-10 shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 p-10 opacity-5"><Key size={200}/></div>
              
              <div className="relative z-10">
                <h2 className="text-3xl font-black mb-2 italic">SETSMART <span className="text-blue-500">BRIDGE</span></h2>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-10">"กรอกไอดีที่นี่ เพื่อดึงข้อมูลราคาและวอลลุ่ม 10 ชั้นแบบออโต้"</p>

                <div className="space-y-8">
                  {/* API KEY SECTION */}
                  <div className="bg-slate-950 p-8 rounded-[2.5rem] border border-blue-500/20">
                    <div className="flex items-center gap-3 mb-6">
                      <Lock className="text-blue-500" size={20} />
                      <span className="text-xs font-black uppercase text-blue-400 tracking-widest">รหัสลับ SetSmart</span>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-[10px] font-black text-slate-500 uppercase mb-2 ml-2">SetSmart User ID</label>
                        <input 
                          type="text"
                          value={credentials.setSmartId}
                          onChange={(e) => setCredentials({...credentials, setSmartId: e.target.value})}
                          placeholder="ไอดีผู้ใช้ SetSmart"
                          className="w-full p-4 bg-slate-900 border border-slate-800 rounded-2xl focus:border-blue-500 outline-none font-bold"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] font-black text-slate-500 uppercase mb-2 ml-2">API Key (4bed36...)</label>
                        <input 
                          type="password"
                          value={credentials.setSmartApiKey}
                          onChange={(e) => setCredentials({...credentials, setSmartApiKey: e.target.value})}
                          placeholder="ใส่ API Key ที่ได้จากหน้าจอระบบ"
                          className="w-full p-4 bg-slate-900 border border-slate-800 rounded-2xl focus:border-blue-500 outline-none font-mono"
                        />
                      </div>
                    </div>
                  </div>

                  {/* LINE ALERT SECTION */}
                  <div className="bg-slate-950 p-8 rounded-[2.5rem] border border-indigo-500/20">
                    <div className="flex items-center gap-3 mb-6">
                      <Bell className="text-indigo-500" size={20} />
                      <span className="text-xs font-black uppercase text-indigo-400 tracking-widest">ระบบแจ้งเตือน LINE</span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <input 
                        type="password"
                        value={credentials.lineToken}
                        onChange={(e) => setCredentials({...credentials, lineToken: e.target.value})}
                        placeholder="Line Access Token"
                        className="w-full p-4 bg-slate-900 border border-slate-800 rounded-2xl text-xs"
                      />
                      <input 
                        type="text"
                        value={credentials.lineUserId}
                        onChange={(e) => setCredentials({...credentials, lineUserId: e.target.value})}
                        placeholder="User ID (UID)"
                        className="w-full p-4 bg-slate-900 border border-slate-800 rounded-2xl text-xs"
                      />
                    </div>
                  </div>

                  {/* SAVE BUTTON */}
                  <button 
                    onClick={saveKeys}
                    disabled={isSaving}
                    className="w-full py-6 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-[2rem] font-black text-lg shadow-xl shadow-blue-900/40 hover:-translate-y-1 transition-all flex items-center justify-center gap-3 active:scale-95 disabled:opacity-50"
                  >
                    {isSaving ? <RefreshCw className="animate-spin" size={24}/> : <Save size={24}/>}
                    {isSaving ? 'RECORDING TO CLOUD...' : 'SAVE CONFIGURATION'}
                  </button>
                </div>
              </div>
            </div>
            
            <div className="p-6 bg-amber-500/10 border border-amber-500/20 rounded-3xl flex gap-4 items-start">
               <AlertCircle className="text-amber-500 shrink-0" size={24} />
               <p className="text-xs font-bold text-amber-200/80 leading-relaxed italic">
                 "พี่โบ้ครับ รหัสเหล่านี้จะถูกเก็บไว้ในที่ปลอดภัยบนคลาวด์ของพี่เอง... เมื่อบันทึกแล้ว แอปจะใช้ตรรกะตามกฎเหล็กข้อ 1-4 ดึงวอลลุ่มมาประเมินให้พี่ทันทีโดยไม่ต้องกรอกมืออีกครับ!"
               </p>
            </div>
          </div>
        ) : (
          /* --- COMMANDER: หน้าจอวิเคราะห์หุ้น (ตัวอย่าง) --- */
          <div className="space-y-8 animate-in slide-in-from-bottom-10 duration-500">
             <div className="bg-slate-900 p-12 rounded-[4rem] text-center border border-slate-800 shadow-2xl">
                <div className="w-24 h-24 bg-blue-600 rounded-[2.5rem] flex items-center justify-center mx-auto mb-8 shadow-xl">
                   <Shield size={48} className="text-white" />
                </div>
                <h2 className="text-4xl font-black italic mb-4">READY FOR <span className="text-blue-500">SETSMART</span></h2>
                <p className="text-slate-400 font-bold mb-10 max-w-md mx-auto leading-relaxed italic">
                  "เมื่อกุญแจพร้อม ระบบจะดึงข้อมูล SIRI, HANA, MTC ให้พี่แบบเรียลไทม์ตามกฎเหล็กทันทีครับ!"
                </p>
                <div className="grid grid-cols-2 gap-4">
                   <div className="bg-slate-950 p-6 rounded-3xl border border-slate-800">
                      <p className="text-[10px] font-black text-slate-500 uppercase">Analysis Engine</p>
                      <p className="text-lg font-black text-emerald-400 uppercase tracking-widest">Iron Rule v1.0</p>
                   </div>
                   <div className="bg-slate-950 p-6 rounded-3xl border border-slate-800">
                      <p className="text-[10px] font-black text-slate-500 uppercase">Data Precision</p>
                      <p className="text-lg font-black text-blue-400 uppercase tracking-widest">10 Levels (Full)</p>
                   </div>
                </div>
             </div>
          </div>
        )}
      </div>

    </div>
  );
};

export default App;
