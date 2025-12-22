
import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Monitor,
  Smartphone,
  Laptop,
  Apple,
  ArrowLeft,
  Cpu,
  Zap,
  Battery,
  HardDrive,
  CheckCircle,
  Wand2,
  AlertTriangle,
  CircleDollarSign,
  Layers,
  Fingerprint,
  User as UserIcon,
  History,
  LogOut,
  ChevronRight,
  Clock,
  Search,
  ExternalLink,
  Loader2,
  Info,
  Camera,
  Upload,
  ImageIcon,
  Trash2,
  FileText,
  Globe,
  Tag,
  ShoppingBag,
  Store,
  Sparkles,
  Check,
  Settings,
  HelpCircle,
  Plus,
  X
} from 'lucide-react';
import { DeviceType, HardwareSpecs, StorageType, VisualGrade, ValuationResult, User, HistoryEntry } from './types';
import TouchTestModal from './components/TouchTestModal';
import AuthModal from './components/AuthModal';
import MarketplaceLinks from './components/MarketplaceLinks';
import { generateAIAdvice, getRealMarketValuation, analyzeHardwareScreenshot } from './services/geminiService';

const DeviceButton: React.FC<{ icon: React.ReactNode, label: string, subLabel: string, onClick: () => void }> = ({ icon, label, subLabel, onClick }) => (
  <button onClick={onClick} className="group relative bg-slate-900 border border-slate-800 p-6 md:p-8 rounded-[2rem] hover:border-indigo-500/50 hover:bg-slate-800/50 transition-all flex flex-col items-center gap-4 shadow-xl active:scale-95">
    <div className="p-4 bg-slate-800 rounded-2xl group-hover:scale-110 transition-transform duration-300">
      {icon}
    </div>
    <div className="text-center">
      <p className="text-sm md:text-lg font-black text-white uppercase tracking-tight">{label}</p>
      <p className="text-[10px] md:text-xs text-slate-500 font-bold uppercase tracking-widest">{subLabel}</p>
    </div>
  </button>
);

const App: React.FC = () => {
  const [step, setStep] = useState<'landing' | 'analysis' | 'history'>('landing');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [currentHistoryId, setCurrentHistoryId] = useState<string | null>(null);

  const [specs, setSpecs] = useState<HardwareSpecs & { aiKeywords?: string }>({
    modelName: '未偵測到型號 / Unknown Model',
    os: DeviceType.WINDOWS,
    ram: '偵測中... / Detecting...',
    cpu: '偵測中... / Detecting...',
    gpu: '偵測中... / Detecting...',
    battery: '偵測中... / Detecting...',
    storage: StorageType.SSD,
    storageCapacity: '未偵測 / N/A',
    grade: VisualGrade.A,
    defects: [],
    userAgent: navigator.userAgent
  });

  const [isScanningImage, setIsScanningImage] = useState(false);
  const [pendingImages, setPendingImages] = useState<string[]>([]);
  const [showScanSuccess, setShowScanSuccess] = useState<{ model: string } | null>(null);
  const [isTouchModalOpen, setIsTouchModalOpen] = useState(false);
  const [valuation, setValuation] = useState<ValuationResult | null>(null);
  const [isValuing, setIsValuing] = useState(false);
  const [aiResponse, setAiResponse] = useState<string | null>(null);
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('vc_current_user');
    if (savedUser) {
      try {
        const user = JSON.parse(savedUser);
        setCurrentUser(user);
        loadHistory(user.id);
      } catch (e) {
        localStorage.removeItem('vc_current_user');
      }
    }
  }, []);

  const loadHistory = (userId: string) => {
    try {
      const allHistory = JSON.parse(localStorage.getItem('vc_history') || '{}');
      const userHistory = allHistory[userId];
      if (Array.isArray(userHistory)) {
        setHistory(userHistory);
      } else {
        setHistory([]);
      }
    } catch (e) {
      console.error("Failed to load history:", e);
      setHistory([]);
    }
  };

  const handleLoginSuccess = (user: User) => {
    setCurrentUser(user);
    localStorage.setItem('vc_current_user', JSON.stringify(user));

    // Save pending valuation if exists (fix for lost history)
    if (valuation && specs) {
      const allHistory = JSON.parse(localStorage.getItem('vc_history') || '{}');
      const userHistory = allHistory[user.id] || [];
      const newEntry: HistoryEntry = {
        specs,
        valuation,
        aiAdvice: aiResponse || undefined,
        id: Date.now().toString(),
        timestamp: Date.now()
      };
      userHistory.unshift(newEntry);
      allHistory[user.id] = userHistory;
      localStorage.setItem('vc_history', JSON.stringify(allHistory));
      setHistory(userHistory);
    } else {
      loadHistory(user.id);
    }

    if (step === 'landing') {
      setStep('history');
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('vc_current_user');
    setStep('landing');
    setValuation(null);
    setAiResponse(null);
    setPendingImages([]);
  };

  const handleBack = () => {
    if (step === 'history') {
      setStep('analysis');
    } else if (step === 'analysis') {
      setStep('landing');
      setValuation(null);
      setAiResponse(null);
    }
  };

  const saveToHistory = (entry: Omit<HistoryEntry, 'id' | 'timestamp'>): string => {
    if (!currentUser) return '';

    try {
      const allHistory = JSON.parse(localStorage.getItem('vc_history') || '{}');
      const userHistory = allHistory[currentUser.id] || [];
      const newId = Date.now().toString();
      const newEntry: HistoryEntry = { ...entry, id: newId, timestamp: Date.now() };
      userHistory.unshift(newEntry);
      allHistory[currentUser.id] = userHistory;
      localStorage.setItem('vc_history', JSON.stringify(allHistory));
      setHistory(userHistory);
      return newId;
    } catch (e) {
      console.error("Save history failed:", e);
      return '';
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    Array.from(files).forEach(file => {
      const reader = new FileReader();
      reader.onload = (event) => {
        const base64 = event.target?.result as string;
        setPendingImages(prev => [...prev, base64]);
      };
      reader.readAsDataURL(file);
    });
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const removePendingImage = (index: number) => {
    setPendingImages(prev => prev.filter((_, i) => i !== index));
  };

  const startBatchScan = async () => {
    if (pendingImages.length === 0) return;
    setIsScanningImage(true);
    setAiError(null);
    try {
      const extracted = await analyzeHardwareScreenshot(pendingImages);
      const finalModel = extracted.modelName || 'Unknown Device';

      setSpecs(prev => ({
        ...prev,
        modelName: finalModel,
        cpu: extracted.cpu || prev.cpu,
        ram: extracted.ram || prev.ram,
        gpu: extracted.gpu || prev.gpu,
        storageCapacity: extracted.storageCapacity || prev.storageCapacity,
        storage: (extracted as any).storageType === 'hdd' ? StorageType.HDD : StorageType.SSD,
        aiKeywords: (extracted as any).searchKeywords
      }));

      setIsScanningImage(false);
      setPendingImages([]);
      setShowScanSuccess({ model: finalModel });
    } catch (err: any) {
      console.error(err);
      setAiError(err.message || "圖片辨識失敗。 Recognition failed.");
      setIsScanningImage(false);
    }
  };

  const calculateValuation = async () => {
    setIsValuing(true);
    setValuation(null);
    try {
      const result = await getRealMarketValuation(specs);
      let finalOffer = result.finalOffer || 0;
      const notes: string[] = [];
      if (specs.storage === StorageType.HDD) { finalOffer -= 1000; notes.push("硬碟老舊 / HDD Penalty (-$1,000)"); }
      if (specs.grade === VisualGrade.C) { finalOffer -= 2000; notes.push("外觀損傷 / Cosmetic Damage (-$2,000)"); }

      const fullResult: ValuationResult = {
        scrapPrice: result.scrapPrice || 0,
        potentialPrice: result.potentialPrice || 0,
        finalOffer: Math.max(result.scrapPrice || 500, finalOffer),
        marketAnalysis: result.marketAnalysis || "",
        sources: result.sources || [],
        notes: notes.length > 0 ? notes : ["設備符合市場平均水準 / Normal Condition"]
      };

      setValuation(fullResult);
      if (currentUser) {
        const id = saveToHistory({ specs, valuation: fullResult });
        setCurrentHistoryId(id);
      }
    } catch (err: any) {
      console.error(err);
      setAiError(err.message || "估價服務暫時無法使用。 Service unavailable.");
    } finally {
      setIsValuing(false);
    }
  };

  const handleGenerateAI = async () => {
    setIsAiLoading(true);
    setAiError(null);
    try {
      const result = await generateAIAdvice(specs, valuation || undefined);
      setAiResponse(result);
      setTimeout(() => document.getElementById('ai-section')?.scrollIntoView({ behavior: 'smooth' }), 100);
    } catch (err: any) {
      setAiError(err.message);
    } finally {
      setIsAiLoading(false);
    }
  };

  const getOptimizedSearchKeyword = () => {
    if (specs.aiKeywords) return specs.aiKeywords;
    let base = specs.modelName;
    const noise = [/Custom Gaming Desktop PC/gi, /Desktop PC/gi, /Laptop/gi, /Gaming PC/gi, /未偵測到型號/g, /Unknown Model/gi, /\//g, /[()]/g, /Intel Core/gi, /NVIDIA GeForce/gi];
    let cleaned = base;
    noise.forEach(n => cleaned = cleaned.replace(n, ' '));
    if (cleaned.trim().length < 5) {
      const cpu = specs.cpu.replace(/偵測中.*|Detecting.*/gi, '').replace(/Intel Core /gi, '').trim();
      const gpu = specs.gpu.replace(/偵測中.*|Detecting.*/gi, '').replace(/NVIDIA GeForce /gi, '').trim();
      cleaned = `${cpu} ${gpu}`;
    }
    return cleaned.replace(/\s+/g, ' ').trim();
  };

  const optimizedKeyword = getOptimizedSearchKeyword();
  const encodedQuery = encodeURIComponent(optimizedKeyword);

  const marketplaces = [
    { name: '台灣蝦皮 / Shopee', url: `https://shopee.tw/search?keyword=${encodedQuery}`, icon: 'https://cf.shopee.tw/file/09697ec89e90089e0000000000000000', color: 'bg-orange-500/10 text-orange-400' },
    { name: '露天拍賣 / Ruten', url: `https://www.ruten.com.tw/find/?q=${encodedQuery}`, icon: 'https://www.ruten.com.tw/favicon.ico', color: 'bg-blue-500/10 text-blue-400' },
    { name: 'BigGo 比價 / BigGo', url: `https://biggo.com.tw/s/${encodedQuery}/`, icon: 'https://biggo.com.tw/favicon.ico', color: 'bg-indigo-500/10 text-indigo-400' },
    { name: 'eBay Global / eBay', url: `https://www.ebay.com/sch/i.html?_nkw=${encodedQuery}`, icon: 'https://cdn-icons-png.flaticon.com/512/5968/5968852.png', color: 'bg-blue-600/10 text-blue-500' },
    { name: 'Amazon Used / Amazon', url: `https://www.amazon.com/s?k=${encodedQuery}&i=warehouse-deals`, icon: 'https://cdn-icons-png.flaticon.com/512/5968/5968705.png', color: 'bg-yellow-500/10 text-yellow-500' },
    { name: 'FB Marketplace / FB', url: `https://www.facebook.com/marketplace/search/?query=${encodedQuery}`, icon: 'https://cdn-icons-png.flaticon.com/512/5968/5968764.png', color: 'bg-indigo-600/10 text-indigo-500' },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans transition-colors duration-500">
      <nav className="bg-slate-900/80 border-b border-slate-800 sticky top-0 z-50 px-3 md:px-4 h-16 flex items-center backdrop-blur-md">
        <div className="max-w-5xl mx-auto w-full flex justify-between items-center gap-2">
          <div className="flex items-center gap-2 md:gap-3 cursor-pointer overflow-hidden group" onClick={handleBack}>
            <div className="p-1.5 rounded-lg group-hover:bg-slate-800 transition-colors">
              <ArrowLeft className={`w-5 h-5 ${step === 'landing' ? 'text-slate-700' : 'text-slate-400 group-hover:text-indigo-400'} flex-shrink-0 transition-colors`} />
            </div>
            <h1 className="text-base md:text-xl font-black tracking-tighter italic whitespace-nowrap">VALUECHECK <span className="text-indigo-400">AI</span> <span className="text-[10px] bg-indigo-500/20 px-2 py-0.5 rounded text-indigo-300 ml-1">Secure v2.0</span></h1>
          </div>
          <div className="flex items-center gap-2 md:gap-4 flex-shrink-0">
            <button
              onClick={() => { if (!currentUser) setIsAuthModalOpen(true); else setStep('history'); }}
              className={`text-[11px] md:text-sm font-bold flex items-center gap-1.5 px-2 md:px-3 py-1.5 rounded-lg transition-all ${step === 'history' ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'}`}
            >
              <History className="w-3.5 h-3.5 md:w-4 md:h-4" />
              <span className="xs:inline">歷史紀錄 / History</span>
            </button>
            {currentUser ? (
              <div className="flex items-center gap-2">
                <span className="hidden sm:inline text-xs font-bold text-slate-500 uppercase tracking-tighter">Hi, {currentUser.name}</span>
                <div onClick={handleLogout} title="登出 / Logout" className="cursor-pointer bg-slate-800 p-2 rounded-full hover:bg-red-500/20 group transition-all">
                  <LogOut className="w-3.5 h-3.5 md:w-4 md:h-4 text-slate-300 group-hover:text-red-400" />
                </div>
              </div>
            ) : (
              <button onClick={() => setIsAuthModalOpen(true)} className="text-[11px] md:text-sm font-bold text-indigo-400 px-3 md:px-4 py-1.5 md:py-2 bg-indigo-500/10 border border-indigo-500/20 rounded-xl hover:bg-indigo-500/20 transition-all">登入 / Login</button>
            )}
          </div>
        </div>
      </nav>


      {aiError && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-[100] bg-red-500 text-white px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 animate-in fade-in slide-in-from-top-5 duration-300">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span className="font-bold">{aiError}</span>
          <button onClick={() => setAiError(null)} className="ml-3 hover:bg-white/20 p-1 rounded-full transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {step === 'landing' ? (
        <div className="flex-grow flex flex-col items-center justify-center p-6 text-center">
          <div className="mb-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="w-24 h-24 bg-slate-900 rounded-[2.5rem] shadow-2xl flex items-center justify-center mx-auto mb-8 text-indigo-400 border border-slate-800">
              <CircleDollarSign className="w-12 h-12" />
            </div>
            <h2 className="text-3xl md:text-5xl font-black text-white mb-2 tracking-tighter uppercase leading-tight">AI 智慧估值 / AI Valuation</h2>
            <h2 className="text-xl md:text-4xl font-bold text-slate-300 mb-6 tracking-tight">精準關鍵字匹配 / Precise Search</h2>
          </div>
          <div className="grid grid-cols-2 gap-4 w-full max-w-lg">
            <DeviceButton icon={<Apple className="w-10 h-10 text-slate-300" />} label="iPhone / iPad" subLabel="蘋果裝置 / Apple" onClick={() => { setSpecs(p => ({ ...p, os: DeviceType.IOS })); setStep('analysis'); }} />
            <DeviceButton icon={<Smartphone className="w-10 h-10 text-emerald-500" />} label="Android" subLabel="安卓設備 / Android" onClick={() => { setSpecs(p => ({ ...p, os: DeviceType.ANDROID })); setStep('analysis'); }} />
            <DeviceButton icon={<Laptop className="w-10 h-10 text-blue-400" />} label="PC / Laptop" subLabel="個人電腦 / PC" onClick={() => { setSpecs(p => ({ ...p, os: DeviceType.WINDOWS })); setStep('analysis'); }} />
            <DeviceButton icon={<Monitor className="w-10 h-10 text-indigo-400" />} label="Mac Station" subLabel="蘋果工作站 / Mac" onClick={() => { setSpecs(p => ({ ...p, os: DeviceType.MACOS })); setStep('analysis'); }} />
          </div>
        </div>
      ) : step === 'history' ? (
        <main className="max-w-4xl mx-auto w-full p-6">
          <h2 className="text-2xl font-black mb-8 flex items-center gap-3"><History className="w-6 h-6 text-indigo-400" /> 估價歷史 / History</h2>
          <div className="space-y-4">
            {history.length > 0 ? history.map((entry) => (
              <div key={entry.id} className="bg-slate-900 border border-slate-800 p-6 rounded-[2rem] hover:border-indigo-500/30 transition-all flex items-center justify-between group">
                <div className="flex items-center gap-6">
                  <div className="p-3 bg-slate-800 rounded-xl text-indigo-400"><Clock className="w-5 h-5" /></div>
                  <div>
                    <h4 className="font-black text-white">{entry.specs.modelName}</h4>
                    <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">{new Date(entry.timestamp).toLocaleString()} • TWD ${entry.valuation.finalOffer.toLocaleString()}</p>
                  </div>
                </div>
                <button onClick={() => { setSpecs(entry.specs); setValuation(entry.valuation); setAiResponse(entry.aiAdvice || null); setStep('analysis'); }} className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl hover:bg-indigo-500/20 transition-all"><ChevronRight className="w-5 h-5" /></button>
              </div>
            )) : (
              <div className="text-center py-20 bg-slate-900/50 rounded-[2rem] border border-dashed border-slate-800">
                <History className="w-12 h-12 text-slate-700 mx-auto mb-4" />
                <p className="text-slate-500 font-bold uppercase tracking-widest">目前尚無紀錄 / No History Found</p>
              </div>
            )}
          </div>
        </main>
      ) : (
        <main className="max-w-4xl mx-auto w-full p-4 md:p-6 pb-24">
          <section className="mb-8 bg-indigo-600/10 border border-indigo-500/20 rounded-[2.5rem] p-6 md:p-10 text-center relative overflow-hidden group shadow-2xl animate-in fade-in slide-in-from-top-4 duration-700">
            <div className="relative z-10">
              <div className="w-20 h-20 bg-indigo-500/20 rounded-[1.75rem] flex items-center justify-center mx-auto mb-6 text-indigo-400 border border-indigo-500/30 shadow-lg group-hover:scale-110 transition-transform duration-500">
                <Sparkles className="w-10 h-10" />
              </div>
              <h3 className="text-2xl font-black text-white mb-3 tracking-tight italic">AI 智慧型號掃描 / AI Auto-Scan</h3>
              <p className="text-sm md:text-base text-yellow-400 mb-8 max-w-md mx-auto leading-relaxed font-bold">
                只需上傳「關於本機」或「系統資訊」截圖，AI 將自動優化搜尋關鍵字。支援同時上傳多張截圖。
              </p>

              <div className="flex flex-col items-center justify-center gap-6 mb-10">
                {pendingImages.length > 0 && (
                  <div className="flex flex-wrap justify-center gap-4 p-4 bg-slate-900/50 rounded-3xl border border-slate-800 w-full max-w-2xl">
                    {pendingImages.map((img, idx) => (
                      <div key={idx} className="relative group w-24 h-24">
                        <img src={img} alt="preview" className="w-full h-full object-cover rounded-xl border border-indigo-500/30" />
                        <button
                          onClick={() => removePendingImage(idx)}
                          className="absolute -top-2 -right-2 bg-red-500 text-white p-1 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="w-24 h-24 border-2 border-dashed border-slate-700 rounded-xl flex flex-col items-center justify-center text-slate-500 hover:border-indigo-500 hover:text-indigo-400 transition-all group"
                    >
                      <Plus className="w-6 h-6 mb-1" />
                      <span className="text-[10px] font-black uppercase">Add More</span>
                    </button>
                  </div>
                )}

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full">
                  {pendingImages.length === 0 ? (
                    <button onClick={() => fileInputRef.current?.click()} className="w-full sm:w-auto flex items-center justify-center gap-3 px-10 py-5 bg-indigo-500 hover:bg-indigo-600 text-white font-black rounded-2xl shadow-2xl shadow-indigo-500/20 transition-all active:scale-95">
                      <Camera className="w-6 h-6" />
                      <span className="uppercase tracking-widest italic font-bold">選擇截圖 / SELECT IMAGES</span>
                    </button>
                  ) : (
                    <button
                      onClick={startBatchScan}
                      disabled={isScanningImage}
                      className={`w-full sm:w-auto flex items-center justify-center gap-3 px-12 py-5 bg-emerald-500 hover:bg-emerald-600 text-white font-black rounded-2xl shadow-2xl shadow-emerald-500/20 transition-all active:scale-95 ${isScanningImage ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      {isScanningImage ? <Loader2 className="w-6 h-6 animate-spin" /> : <Sparkles className="w-6 h-6" />}
                      <span className="uppercase tracking-widest italic font-bold">開始辨識 / START SCAN ({pendingImages.length})</span>
                    </button>
                  )}
                  <input type="file" ref={fileInputRef} onChange={handleImageUpload} className="hidden" accept="image/*" multiple />
                </div>
              </div>

              <div className="pt-8 border-t border-indigo-500/10 max-w-2xl mx-auto">
                <div className="flex items-center justify-center gap-2 mb-6 text-indigo-300">
                  <HelpCircle className="w-4 h-4" />
                  <span className="text-xs font-black uppercase tracking-widest italic">如何取得系統資訊截圖？ / How to take screenshot?</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <ScreenshotGuideItem icon={<Apple className="w-4 h-4" />} label="iOS" path="設定 > 一般 > 關於本機" enPath="Settings > General > About" />
                  <ScreenshotGuideItem icon={<Smartphone className="w-4 h-4" />} label="Android" path="設定 > 關於手機" enPath="Settings > About Phone" />
                  <ScreenshotGuideItem icon={<Monitor className="w-4 h-4" />} label="Windows" path="設定 > 系統 > 系統資訊" enPath="Settings > System > About" />
                  <ScreenshotGuideItem icon={<Laptop className="w-4 h-4" />} label="macOS" path="蘋果選單 > 關於這台 Mac" enPath="Apple Menu > About Mac" />
                </div>
              </div>
            </div>
          </section>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-10">
            <div className="lg:col-span-5 space-y-6">
              <section className="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden">
                <h3 className="text-lg font-black text-white mb-8 flex items-center gap-3 uppercase tracking-tight">
                  <Zap className="w-5 h-5 text-indigo-400" /> 硬體清單 / Device Specs
                </h3>

                <div className="space-y-6">
                  <SpecItem icon={<Tag className="w-4 h-4 text-emerald-400" />} label="設備型號 / Product Model" value={specs.modelName} onChange={(v) => setSpecs(p => ({ ...p, modelName: v }))} />
                  <SpecItem icon={<Cpu className="w-4 h-4" />} label="處理器 / CPU" value={specs.cpu} onChange={(v) => setSpecs(p => ({ ...p, cpu: v }))} />
                  <SpecItem icon={<Layers className="w-4 h-4" />} label="記憶體 / RAM" value={specs.ram} onChange={(v) => setSpecs(p => ({ ...p, ram: v }))} />
                  <SpecItem icon={<Monitor className="w-4 h-4" />} label="顯示卡 / GPU" value={specs.gpu} onChange={(v) => setSpecs(p => ({ ...p, gpu: v }))} />

                  <div className="pt-6 border-t border-slate-800">
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">優化後關鍵字 / Cleaned Keywords</label>
                      <span className="text-[10px] text-indigo-400 font-bold uppercase">Better Search!</span>
                    </div>
                    <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-xl px-4 py-3 text-sm font-bold text-indigo-300 italic">
                      {optimizedKeyword}
                    </div>
                  </div>
                </div>

                <button
                  onClick={calculateValuation}
                  disabled={isValuing}
                  className="w-full mt-10 bg-white text-slate-950 hover:bg-indigo-50 font-black py-5 rounded-2xl shadow-xl flex items-center justify-center gap-3 transition-all active:scale-[0.98] disabled:opacity-50"
                >
                  {isValuing ? <Loader2 className="w-6 h-6 animate-spin" /> : <Search className="w-6 h-6" />}
                  <span className="uppercase tracking-wider italic">開始市場估價 / Start Valuation</span>
                </button>
              </section>
            </div>

            <div className="lg:col-span-7 space-y-6">
              {valuation ? (
                <section className="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-8 md:p-10 shadow-2xl animate-in fade-in zoom-in-95 duration-500 overflow-hidden relative">
                  <div className="mb-12 relative z-10">
                    <h3 className="text-[10px] md:text-xs font-black text-indigo-400 mb-2 uppercase tracking-[0.2em] leading-tight">
                      {optimizedKeyword} <br className="md:hidden" /> 市場估值 / MARKET VALUE
                    </h3>
                    <h2 className="text-4xl md:text-7xl font-black text-white tracking-tighter italic leading-none">
                      TWD <span className="text-white">${valuation.finalOffer.toLocaleString()}</span>
                    </h2>
                  </div>

                  <div className="mb-12 relative z-10 space-y-6">
                    <h4 className="text-xs font-black text-slate-100 uppercase tracking-widest flex items-center gap-2">
                      <Store className="w-4 h-4 text-indigo-400" /> 實時行情連結 / Real-time Market Search
                    </h4>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {marketplaces.map((m) => (
                        <a key={m.name} href={m.url} target="_blank" rel="noopener noreferrer" className={`flex flex-col items-center justify-center p-4 rounded-2xl border border-slate-800 hover:border-indigo-500/50 transition-all group ${m.color}`}>
                          <img src={m.icon} alt={m.name} className="w-6 h-6 mb-2 rounded shadow-sm group-hover:scale-110 transition-transform" onError={(e) => (e.currentTarget.style.display = 'none')} />
                          <span className="text-[9px] font-black uppercase tracking-tight text-center leading-tight">{m.name}</span>
                        </a>
                      ))}
                    </div>
                  </div>

                  <div className="mb-12 relative z-10">
                    <h4 className="text-xs font-black text-slate-100 mb-4 uppercase tracking-widest">市場洞察 / Market Insights</h4>
                    <p className="text-sm text-slate-400 leading-relaxed font-medium bg-slate-800/30 p-6 rounded-[2rem] border border-slate-800 italic">"{valuation.marketAnalysis}"</p>
                  </div>

                  {!aiResponse && (
                    <button onClick={handleGenerateAI} disabled={isAiLoading} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black py-5 rounded-2xl shadow-2xl flex items-center justify-center gap-3 transition-all active:scale-[0.98]">
                      {isAiLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Wand2 className="w-6 h-6" />}
                      <span className="uppercase tracking-widest italic">生成售賣策略 / Generate Sales Strategy</span>
                    </button>
                  )}

                  {aiResponse && (
                    <div id="ai-section" className="mt-10 p-8 bg-gradient-to-br from-indigo-500/10 to-slate-900 border border-indigo-500/20 rounded-[2.5rem] relative z-10">
                      <div className="flex items-center gap-3 mb-6">
                        <div className="p-2.5 bg-indigo-500 rounded-xl shadow-lg"><Wand2 className="w-5 h-5 text-white" /></div>
                        <h4 className="text-sm font-black text-white uppercase tracking-widest">專家策略分析 / Expert Strategy</h4>
                      </div>
                      <div className="prose prose-invert prose-sm max-w-none text-slate-300 leading-relaxed font-medium">
                        {aiResponse.split('\n').map((line, i) => <p key={i} className="mb-4">{line}</p>)}
                      </div>
                      <MarketplaceLinks content={aiResponse} deviceInfo={specs.modelName} />
                    </div>
                  )}
                </section>
              ) : (
                <div className="bg-slate-900/50 border border-dashed border-slate-800 rounded-[2.5rem] p-12 h-full min-h-[400px] flex flex-col items-center justify-center text-center opacity-60">
                  <div className="w-20 h-20 bg-slate-800 rounded-3xl flex items-center justify-center mb-6 text-slate-600">
                    <Tag className="w-10 h-10" />
                  </div>
                  <h3 className="text-xl font-black text-slate-500 mb-2 tracking-tight uppercase">等待分析中 / Ready for Analysis</h3>
                  <p className="text-xs text-slate-600 font-bold max-w-xs uppercase tracking-widest">請上傳截圖，AI 將自動清洗關鍵字以利搜尋。支援多圖合併辨識。</p>
                </div>
              )}
            </div>
          </div>
        </main>
      )}

      {showScanSuccess && (
        <div className="fixed inset-0 bg-black/80 z-[100] flex items-center justify-center p-4 backdrop-blur-md animate-in fade-in duration-300">
          <div className="bg-slate-900 border border-indigo-500/30 rounded-[2.5rem] w-full max-w-sm overflow-hidden shadow-2xl p-10 text-center animate-in zoom-in-95 duration-300">
            <div className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6 text-emerald-400 border border-emerald-500/30">
              <CheckCircle className="w-10 h-10" />
            </div>
            <h3 className="text-2xl font-black text-white mb-2 tracking-tight italic">辨識完成 / Scan Complete</h3>
            <p className="text-sm text-slate-400 mb-8 font-medium">
              偵測到型號：<span className="text-indigo-400 font-bold">{showScanSuccess.model}</span><br />
              規格已從多張截圖中自動整合並同步至清單。<br />
              <span className="text-[10px] text-slate-500 uppercase font-black">Multi-image sync successful.</span>
            </p>
            <button
              onClick={() => setShowScanSuccess(null)}
              className="w-full bg-white text-slate-950 font-black py-4 rounded-2xl shadow-xl hover:bg-indigo-50 transition-all active:scale-95 uppercase tracking-widest italic"
            >
              確定 / Confirm
            </button>
          </div>
        </div>
      )}

      <TouchTestModal isOpen={isTouchModalOpen} onClose={() => setIsTouchModalOpen(false)} />
      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} onLogin={handleLoginSuccess} />
    </div>
  );
};

const ScreenshotGuideItem: React.FC<{ icon: React.ReactNode, label: string, path: string, enPath: string }> = ({ icon, label, path, enPath }) => (
  <div className="flex flex-col items-center bg-slate-800/40 p-3 rounded-xl border border-slate-800 group hover:border-indigo-500/30 transition-all">
    <div className="mb-2 text-slate-500 group-hover:text-indigo-400 transition-colors">{icon}</div>
    <span className="text-[10px] font-black text-slate-200 mb-1 uppercase tracking-tighter">{label}</span>
    <p className="text-[9px] text-indigo-300 font-bold leading-tight">{path}</p>
    <p className="text-[8px] text-slate-500 font-bold italic mt-0.5">{enPath}</p>
  </div>
);

const SpecItem: React.FC<{ icon: React.ReactNode, label: string, value: string, onChange: (v: string) => void }> = ({ icon, label, value, onChange }) => {
  const [isEditing, setIsEditing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  useEffect(() => { if (isEditing) inputRef.current?.focus(); }, [isEditing]);

  return (
    <div className="space-y-1.5 group">
      <div className="flex items-center justify-between px-1">
        <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.15em] flex items-center gap-2">
          <span className="text-slate-600">{icon}</span> {label}
        </label>
        <button onClick={() => setIsEditing(!isEditing)} className="text-[10px] font-black text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity uppercase tracking-widest">
          {isEditing ? '儲存 / Save' : '編輯 / Edit'}
        </button>
      </div>
      {isEditing ? (
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onBlur={() => setIsEditing(false)}
          onKeyDown={(e) => e.key === 'Enter' && setIsEditing(false)}
          className="w-full bg-slate-800 border border-indigo-500/30 rounded-xl px-4 py-3.5 text-sm font-bold text-white outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all"
        />
      ) : (
        <div className="bg-slate-800/30 border border-slate-800 rounded-xl px-4 py-3.5 flex items-center justify-between cursor-pointer hover:bg-slate-800/50 transition-colors" onClick={() => setIsEditing(true)}>
          <span className="text-sm font-bold text-slate-300 truncate pr-4">{value}</span>
          <ChevronRight className="w-4 h-4 text-slate-600 flex-shrink-0" />
        </div>
      )}
    </div>
  );
};

export default App;
