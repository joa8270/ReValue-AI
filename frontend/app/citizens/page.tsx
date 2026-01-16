"use client"

import { useState, useEffect, Suspense } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"

export const dynamic = "force-dynamic"

// ===== DATA INTERFACES =====
interface BaziProfile {
    birth_year?: number
    birth_month?: number
    birth_day?: number
    birth_hour?: number
    birth_shichen?: string
    four_pillars?: string
    strength?: string
    structure?: string
    favorable_elements?: string[]
    unfavorable_elements?: string[]
    day_master?: string
    element?: string
    current_state?: string
    luck_pillars?: Array<{
        pillar: string
        gan: string
        age_start: number
        age_end: number
        description?: string
    }>
}

interface Citizen {
    id: string
    name: string
    gender: string
    age: number
    location: string
    bazi_profile: BaziProfile
    traits: string[]
    occupation: string
}

// ===== CONSTANTS & MAPPINGS =====
const DECISION_MODELS: Record<string, { title: string; desc: string }> = {
    "正官格": { title: "邏輯審慎型", desc: "決策前必先評估風險與合規性，偏好有前例可循的方案，重視SOP與權責劃分。" },
    "七殺格": { title: "果斷執行型", desc: "面對危機敢於下重注，決策速度快，重視結果大於過程，關鍵時刻能展現魄力。" },
    "正財格": { title: "穩健數據型", desc: "重視成本效益分析 (CP值)，每一分錢都要花在刀口上，偏好低風險、穩定回報的選擇。" },
    "偏財格": { title: "機會捕捉型", desc: "商業嗅覺敏銳，願意為高潛在回報承擔風險，決策豪爽，善於利用槓桿。" },
    "正印格": { title: "長遠規劃型", desc: "決策著重長期價值與品牌信譽，不喜歡短視近利的行為，會考慮對整體的影響。" },
    "偏印格": { title: "創新反骨型", desc: "討厭隨波逐流，喜歡獨特、非主流的選擇，決策帶有直覺色彩，常有出人意表的洞見。" },
    "食神格": { title: "品味直覺型", desc: "重視個人喜好與美感體驗，決策較感性，追求「感覺對了」與心理舒適度。" },
    "傷官格": { title: "顛覆突破型", desc: "喜歡打破常規，不按牌理出牌，決策往往挑戰現狀，旨在證明自己的獨特能力。" },
    "建祿格": { title: "務實自主型", desc: "相信自己的判斷，不輕易被話術影響，重視實際掌控權與執行可行性。" },
    "羊刃格": { title: "效率目標型", desc: "目標導向極強，為了達成目的可以排除萬難，決策快狠準，不喜歡拖泥帶水。" },
    "從財格": { title: "順勢而為型", desc: "懂得利用大環境趨勢，決策靈活，適應力強，哪裡有利就往哪裡去。" },
    "從殺格": { title: "權力導向型", desc: "具有強烈的企圖心，決策服務於地位的提升與影響力的擴大。" },
    "從兒格": { title: "智慧策略型", desc: "靠才華與創意取勝，決策靈活多變，不喜歡被死板的規則束縛。" },
    "專旺格": { title: "堅持本色型", desc: "意志堅定，一條路走到黑，在專業領域有極強的決策自信。" }
};

const HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"];
const EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];

function generateMockPillars() {
    const getPair = () => HEAVENLY_STEMS[Math.floor(Math.random() * 10)] + EARTHLY_BRANCHES[Math.floor(Math.random() * 12)];
    return `${getPair()}  ${getPair()}  ${getPair()}  ${getPair()}`;
}

// Fallback for unknown structures
const DEFAULT_DECISION_MODEL = { title: "多元策略型", desc: "能根據不同情境調整決策模式，兼具理性與感性。" };

function getDecisionModel(structure: string | undefined) {
    if (!structure) return DEFAULT_DECISION_MODEL;
    const key = Object.keys(DECISION_MODELS).find(k => structure.includes(k));
    return key ? DECISION_MODELS[key] : DEFAULT_DECISION_MODEL;
}

// ===== ELEMENT COLOR MAPPING =====
const ELEMENT_COLORS: Record<string, { bg: string; text: string; border: string }> = {
    "金": { bg: "bg-slate-400", text: "text-slate-900", border: "border-slate-300" },
    "木": { bg: "bg-emerald-400", text: "text-emerald-900", border: "border-emerald-300" },
    "水": { bg: "bg-blue-400", text: "text-blue-900", border: "border-blue-300" },
    "火": { bg: "bg-orange-400", text: "text-orange-900", border: "border-orange-300" },
    "土": { bg: "bg-amber-500", text: "text-amber-900", border: "border-amber-400" },
};

function getElementColor(element: string | undefined) {
    if (!element) return ELEMENT_COLORS["土"]; // Default
    const key = Object.keys(ELEMENT_COLORS).find(k => element.includes(k));
    return key ? ELEMENT_COLORS[key] : ELEMENT_COLORS["土"];
}

function parseFourPillars(fourPillars: string | undefined) {
    if (!fourPillars) return null;
    const parts = fourPillars.trim().split(/\s+/);
    if (parts.length !== 4) return null;
    return {
        year: parts[0],
        month: parts[1],
        day: parts[2],
        hour: parts[3]
    };
}

// ===== AVATAR MAPPING (使用 DiceBear API 動態生成頭像) =====
function getAvatarPath(citizenId: string, age: number, gender: string, name?: string): string {
    // 使用市民姓名或 ID 作為種子，確保同一人頭像一致
    const seed = name || citizenId;

    // 根據性別和年齡選擇適合的風格
    // adventurer-neutral 適合真實感、多樣化的頭像
    const style = 'adventurer-neutral';

    // 構建 DiceBear URL，添加性別和年齡相關參數
    // DiceBear 會根據 seed 生成一致的頭像
    return `https://api.dicebear.com/7.x/${style}/svg?seed=${encodeURIComponent(seed)}&backgroundColor=transparent`;
}

// ===== COMPONENTS =====

function CitizenModal({ citizen, onClose }: { citizen: Citizen; onClose: () => void }) {
    if (!citizen) return null;

    // State for toggling full view
    const [showDetails, setShowDetails] = useState(false);

    const decisionModel = getDecisionModel(citizen.bazi_profile?.structure);
    const luckPillars = citizen.bazi_profile?.luck_pillars || [];

    // Find current luck pillar
    const currentLuck = luckPillars.find(l => citizen.age >= l.age_start && citizen.age <= l.age_end) || luckPillars[0];

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in fade-in duration-200" onClick={onClose}>
            <div className="relative bg-slate-900 border border-purple-500/30 rounded-3xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl shadow-purple-900/50" onClick={(e) => e.stopPropagation()}>

                {/* Header (Fixed) */}
                <div className="p-6 border-b border-white/10 bg-slate-900/95 sticky top-0 z-10 flex justify-between items-start">
                    <div className="flex items-center gap-5">
                        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-950 flex items-center justify-center text-4xl shadow-xl border border-white/10">
                            {citizen.gender === '女' ? '👩' : '👨'}
                        </div>
                        <div>
                            <div className="flex items-baseline gap-3">
                                <h2 className="text-3xl font-black text-white tracking-tight">{citizen.name}</h2>
                                <span className="text-xs font-mono text-slate-500 px-2 py-1 bg-white/5 rounded-full border border-white/5">ID: {String(citizen.id).padStart(8, '0').slice(0, 8)}</span>
                            </div>
                            <div className="flex items-center gap-3 mt-2 text-sm">
                                <span className="bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30 font-bold">
                                    {citizen.occupation}
                                </span>
                                <span className="text-slate-400">•</span>
                                <span className="text-slate-300 font-medium">{citizen.gender}</span>
                                <span className="text-slate-400">•</span>
                                <span className="text-slate-300 font-medium">{citizen.age} 歲</span>
                                <span className="text-slate-400">•</span>
                                <span className="text-slate-400">{citizen.location}</span>
                            </div>
                            {/* 生辰資料顯示 */}
                            <div className="flex items-center gap-2 mt-2 text-xs text-slate-400 font-mono">
                                <span>📅</span>
                                <span>
                                    {citizen.bazi_profile?.birth_year && citizen.bazi_profile?.birth_month && citizen.bazi_profile?.birth_day
                                        ? `${citizen.bazi_profile.birth_year}年${citizen.bazi_profile.birth_month}月${citizen.bazi_profile.birth_day}日 ${citizen.bazi_profile.birth_shichen || ''}`
                                        : '生辰資料缺失'}
                                </span>
                            </div>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-slate-500 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-full"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Scrollable Content */}
                <div className="overflow-y-auto p-6 space-y-6 custom-scrollbar">

                    {/* 1. Current State Interpretation (Always Visible) */}
                    <section>
                        <div className="flex items-center gap-2 mb-3">
                            <span className="w-2 h-2 rounded-full bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.8)]"></span>
                            <h3 className="text-sm font-bold text-purple-400 uppercase tracking-widest">當前狀態解讀</h3>
                        </div>
                        <div className="p-5 rounded-2xl bg-gradient-to-br from-purple-900/20 to-slate-900 border border-purple-500/30 text-slate-200 leading-relaxed text-lg shadow-inner">
                            {citizen.bazi_profile.current_state}
                        </div>
                    </section>

                    {/* 2. Key Metrics Grid (Always Visible) */}
                    <section className="grid grid-cols-2 gap-4">
                        {/* Structure */}
                        <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                            <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">命理格局</div>
                            <div className="text-xl font-black text-white">{citizen.bazi_profile.structure || "未定格"}</div>
                        </div>
                        {/* Strength */}
                        <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                            <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">能量強弱</div>
                            <div className="text-xl font-black text-white">{citizen.bazi_profile.strength || "未知"}</div>
                        </div>
                        {/* Favorable Elements */}
                        <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                            <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">喜用五行</div>
                            <div className="flex gap-1.5 flex-wrap">
                                {citizen.bazi_profile.favorable_elements?.map(e => (
                                    <span key={e} className="text-sm font-bold text-emerald-400">{e}</span>
                                )) || <span className="text-slate-500">None</span>}
                            </div>
                        </div>
                        {/* Personality */}
                        <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                            <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">性格標籤</div>
                            <div className="text-xl font-black text-amber-400 truncate">{citizen.traits?.[0] || "多元性格"}</div>
                        </div>
                    </section>

                    {/* Expandable Content */}
                    {showDetails && (
                        <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
                            {/* 3. Decision Model */}
                            <section>
                                <div className="flex items-center gap-2 mb-3">
                                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                                    <h3 className="text-sm font-bold text-cyan-500 uppercase tracking-widest">決策思維模型</h3>
                                </div>
                                <div className="p-5 rounded-2xl bg-slate-800/30 border border-cyan-500/20">
                                    <div className="text-lg font-bold text-white mb-2">{decisionModel.title}</div>
                                    <div className="text-slate-400 leading-relaxed text-sm">
                                        {decisionModel.desc}
                                    </div>
                                </div>
                            </section>

                            {/* 4. Current Luck & Chart */}
                            <div className="grid grid-cols-1 gap-6">
                                <section>
                                    <div className="flex items-center gap-2 mb-3">
                                        <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                                        <h3 className="text-sm font-bold text-amber-500 uppercase tracking-widest">當前大運 / CURRENT LUCK</h3>
                                    </div>
                                    <div className="p-5 rounded-2xl bg-amber-500/5 border border-amber-500/20">
                                        <div className="text-xl font-bold text-amber-200 mb-2">
                                            {currentLuck ? `${currentLuck.pillar} 運 (${currentLuck.age_start}-${currentLuck.age_end}歲)` : "運程分析中"}
                                        </div>
                                        <div className="text-amber-100/80 leading-relaxed">
                                            {currentLuck?.description || "暫無詳細運程描述"}
                                        </div>
                                    </div>
                                </section>

                                <section>
                                    <div className="flex items-center gap-2 mb-3">
                                        <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
                                        <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest">八字命盤</h3>
                                    </div>
                                    <div className="p-6 rounded-2xl bg-slate-950 border border-white/10 text-center font-mono text-xl md:text-2xl text-white tracking-widest shadow-inner">
                                        {citizen.bazi_profile.four_pillars || generateMockPillars()}
                                    </div>
                                </section>
                            </div>

                            {/* 5. Timeline */}
                            <section>
                                <div className="flex items-center gap-2 mb-3">
                                    <span className="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
                                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">10年大運時間軸</h3>
                                </div>
                                <div className="space-y-3">
                                    {luckPillars.slice(0, 8).map((pillar: any, idx: number) => {
                                        const isCurrent = citizen.age >= pillar.age_start && citizen.age <= pillar.age_end;
                                        return (
                                            <div key={idx} className={`p-4 rounded-xl border transition-all ${isCurrent ? 'bg-purple-900/30 border-purple-500/50 shadow-[0_0_15px_rgba(168,85,247,0.1)]' : 'bg-slate-800/30 border-white/5 opacity-70 hover:opacity-100'}`}>
                                                <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-2">
                                                    <div className="flex items-center gap-3 min-w-[120px]">
                                                        <span className={`text-xs font-bold ${isCurrent ? 'text-purple-300' : 'text-slate-500'}`}>{pillar.age_start}-{pillar.age_end}歲</span>
                                                        <span className={`text-lg font-bold ${isCurrent ? 'text-white' : 'text-slate-300'}`}>{pillar.pillar}</span>
                                                    </div>
                                                    {isCurrent && <span className="text-[10px] bg-purple-500 text-white px-2 py-0.5 rounded-full font-bold tracking-wider">當前運勢 CURRENT</span>}
                                                </div>
                                                {pillar.description && (
                                                    <div className={`text-sm leading-relaxed ${isCurrent ? 'text-purple-100' : 'text-slate-400'}`}>
                                                        {pillar.description}
                                                    </div>
                                                )}
                                            </div>
                                        )
                                    })}
                                </div>
                            </section>
                        </div>
                    )}

                    {/* Button */}
                    <button
                        onClick={() => setShowDetails(!showDetails)}
                        className="w-full py-4 rounded-xl bg-purple-500/10 border border-purple-500/30 text-base font-bold text-purple-300 hover:bg-purple-500/20 hover:border-purple-500/50 transition-all flex items-center justify-center gap-2 group"
                    >
                        {showDetails ? (
                            <>收合報告 <span className="group-hover:-translate-y-1 transition-transform">↑</span></>
                        ) : (
                            <>查看完整運勢報告 <span className="group-hover:translate-y-1 transition-transform">↓</span></>
                        )}
                    </button>

                </div>
            </div>
        </div>
    );
}

function CitizensContent() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const returnTo = searchParams.get("returnTo") || "/"

    const [citizens, setCitizens] = useState<Citizen[]>([])
    const [total, setTotal] = useState(0)
    const [loading, setLoading] = useState(true)
    const [page, setPage] = useState(0)
    const [search, setSearch] = useState("")
    const [selectedCitizen, setSelectedCitizen] = useState<Citizen | null>(null)
    const limit = 30

    useEffect(() => {
        fetchCitizens()
    }, [page])

    const fetchCitizens = async () => {
        setLoading(true)
        try {
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const res = await fetch(`${API_BASE_URL}/citizens?limit=${limit}&offset=${page * limit}`)
            const data = await res.json()
            setCitizens(data.citizens || [])
            setTotal(data.total || 0)
        } catch (e) {
            console.error("Failed to fetch citizens:", e)
        }
        setLoading(false)
    }

    const filteredCitizens = citizens.filter(c =>
        c.name.includes(search) ||
        c.location?.includes(search) ||
        c.bazi_profile?.structure?.includes(search) ||
        c.bazi_profile?.current_state?.includes(search)
    )

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 font-sans pt-[100px]">
            {/* Modal... */}
            {selectedCitizen && (
                <CitizenModal citizen={selectedCitizen} onClose={() => setSelectedCitizen(null)} />
            )}

            {/* Header */}
            <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur-md sticky top-[80px] z-20">
                <div className="max-w-7xl mx-auto px-4 py-6">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                        <div>
                            <button onClick={() => router.back()} className="text-purple-400 hover:text-purple-300 text-sm mb-2 flex items-center gap-1 transition-colors">
                                <span>←</span> 返回上一頁
                            </button>
                            <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
                                <span className="p-2 bg-purple-600 rounded-lg shadow-lg shadow-purple-500/20">🧬</span>
                                MIRRA AI 虛擬市民資料庫
                            </h1>
                            <div className="text-xs text-slate-500 font-mono uppercase tracking-widest mt-2 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                實時人口資料庫 • 總數: {total.toLocaleString()}
                            </div>
                        </div>

                        {/* Search */}
                        <div className="w-full md:w-auto">
                            <div className="relative group">
                                <div className="absolute inset-0 bg-purple-500/10 blur-xl group-hover:bg-purple-500/20 transition-all rounded-full" />
                                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 z-10">🔍</span>
                                <input
                                    type="text"
                                    placeholder="搜尋姓名、格局、個性描述..."
                                    className="relative z-10 pl-11 pr-6 py-3 bg-slate-900/50 border border-white/10 rounded-2xl text-white focus:outline-none focus:border-purple-500/50 focus:ring-4 focus:ring-purple-500/5 transition-all w-full md:min-w-[400px] backdrop-blur-sm"
                                    value={search}
                                    onChange={(e) => setSearch(e.target.value)}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Grid */}
            <main className="max-w-7xl mx-auto px-4 py-12">
                {loading ? (
                    <div className="flex flex-col justify-center items-center py-40 gap-4">
                        <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
                        <div className="text-slate-500 font-mono text-sm">正在同步人口數據...</div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {filteredCitizens.map((citizen) => {
                            const pillars = parseFourPillars(citizen.bazi_profile.four_pillars || generateMockPillars());
                            const dayMasterElement = citizen.bazi_profile.element || "土";
                            const elementStyle = getElementColor(dayMasterElement);

                            return (
                                <div key={citizen.id} className="group relative bg-[#241a30] rounded-xl overflow-hidden border border-[#362b45] hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-purple-500/10">

                                    {/* Day Master Badge - Redesigned with Element-Specific Styling */}
                                    <div className="absolute top-3 right-3 z-20 flex flex-col items-end gap-1">
                                        <span className="text-[9px] text-gray-400 font-mono tracking-wider">日主</span>
                                        <div className={`
                                            relative size-11 rounded-full flex items-center justify-center
                                            border-[3px] font-bold text-lg tracking-tight
                                            transition-all duration-300 group-hover:scale-110
                                            ${dayMasterElement === 'Metal' ? 'bg-gradient-to-br from-slate-300 to-slate-500 border-slate-200 text-slate-900 shadow-lg shadow-slate-400/50' : ''}
                                            ${dayMasterElement === 'Wood' ? 'bg-gradient-to-br from-emerald-300 to-emerald-600 border-emerald-200 text-emerald-950 shadow-lg shadow-emerald-400/50' : ''}
                                            ${dayMasterElement === 'Water' ? 'bg-gradient-to-br from-blue-300 to-blue-600 border-blue-200 text-blue-950 shadow-lg shadow-blue-400/50' : ''}
                                            ${dayMasterElement === 'Fire' ? 'bg-gradient-to-br from-orange-300 to-orange-600 border-orange-200 text-orange-950 shadow-lg shadow-orange-400/50' : ''}
                                            ${dayMasterElement === 'Earth' ? 'bg-gradient-to-br from-amber-400 to-amber-700 border-amber-200 text-amber-950 shadow-lg shadow-amber-400/50' : ''}
                                        `}>
                                            {pillars?.day?.charAt(0) || '?'}
                                            {/* Glow effect ring */}
                                            <div className={`
                                                absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 transition-opacity
                                                ${dayMasterElement === 'Metal' ? 'ring-4 ring-slate-300/30' : ''}
                                                ${dayMasterElement === 'Wood' ? 'ring-4 ring-emerald-300/30' : ''}
                                                ${dayMasterElement === 'Water' ? 'ring-4 ring-blue-300/30' : ''}
                                                ${dayMasterElement === 'Fire' ? 'ring-4 ring-orange-300/30' : ''}
                                                ${dayMasterElement === 'Earth' ? 'ring-4 ring-amber-300/30' : ''}
                                            `} />
                                        </div>
                                    </div>

                                    {/* Header Visual */}
                                    <div className="h-32 bg-[#1a1324] relative overflow-hidden">
                                        <div className="absolute inset-0 bg-gradient-to-t from-[#241a30] to-transparent"></div>
                                        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20"></div>
                                    </div>

                                    {/* Content */}
                                    <div className="px-5 pb-5 -mt-12 relative z-10">
                                        <div className="flex items-end justify-between mb-3">
                                            <div className="size-20 rounded-xl overflow-hidden border-2 border-[#241a30] shadow-md bg-black relative">
                                                {/* Real Avatar Photo */}
                                                <img
                                                    src={getAvatarPath(citizen.id, citizen.age, citizen.gender, citizen.name)}
                                                    alt={citizen.name}
                                                    className="w-full h-full object-cover"
                                                />
                                            </div>
                                            <div className="text-right">
                                                <span className="text-xs font-mono text-gray-500 block">#{String(citizen.id).padStart(4, '0').slice(0, 4)}</span>
                                                <span className="text-[10px] text-gray-600">{citizen.location || "台灣"}</span>
                                            </div>
                                        </div>

                                        <h3 className="text-xl font-bold text-white mb-0.5">{citizen.name}</h3>
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-[10px] text-gray-400 px-1.5 py-0.5 rounded bg-gray-800/50 border border-gray-700/50">
                                                {citizen.gender}
                                            </span>
                                            <span className="text-[10px] text-gray-400 px-1.5 py-0.5 rounded bg-gray-800/50 border border-gray-700/50">
                                                {citizen.age}歲
                                            </span>
                                        </div>
                                        <p className={`text-sm font-medium mb-1 uppercase tracking-wide ${elementStyle.text.replace('text-', 'text-').replace('-900', '-400')}`}>
                                            {citizen.occupation}
                                        </p>
                                        <p className="text-[10px] text-gray-500 mb-3">
                                            出生: {citizen.bazi_profile.birth_year && citizen.bazi_profile.birth_month && citizen.bazi_profile.birth_day
                                                ? `${citizen.bazi_profile.birth_year}.${String(citizen.bazi_profile.birth_month).padStart(2, '0')}.${String(citizen.bazi_profile.birth_day).padStart(2, '0')} ${citizen.bazi_profile.birth_shichen || ''}`
                                                : '未知'}
                                        </p>

                                        {/* Additional Info from Modal */}
                                        {citizen.bazi_profile.current_state && (
                                            <div className="mb-3 p-2 rounded-lg bg-purple-500/5 border border-purple-500/10">
                                                <div className="text-[9px] font-bold text-purple-400 uppercase tracking-widest mb-1">當前運勢</div>
                                                <div className="text-[11px] text-slate-300 line-clamp-2 leading-relaxed">
                                                    {citizen.bazi_profile.current_state}
                                                </div>
                                            </div>
                                        )}

                                        {/* Four Pillars Grid */}
                                        {pillars && (
                                            <div className="grid grid-cols-4 gap-1 text-center bg-[#1a1324] rounded-md p-2 mb-3 border border-[#302839]">
                                                <div className="flex flex-col text-[10px] text-gray-500">
                                                    <span>年</span>
                                                    <span className="text-white text-sm font-serif">{pillars.year}</span>
                                                </div>
                                                <div className="flex flex-col text-[10px] text-gray-500">
                                                    <span>月</span>
                                                    <span className="text-white text-sm font-serif">{pillars.month}</span>
                                                </div>
                                                <div className={`flex flex-col text-[10px] font-bold ${elementStyle.text.replace('-900', '-400')} bg-${dayMasterElement === '金' ? 'slate' : dayMasterElement === '木' ? 'emerald' : dayMasterElement === '水' ? 'blue' : dayMasterElement === '火' ? 'orange' : 'amber'}-500/10 rounded`}>
                                                    <span>日</span>
                                                    <span className="text-lg font-serif">{pillars.day}</span>
                                                </div>
                                                <div className="flex flex-col text-[10px] text-gray-500">
                                                    <span>時</span>
                                                    <span className="text-white text-sm font-serif">{pillars.hour}</span>
                                                </div>
                                            </div>
                                        )}

                                        {/* Tags - Enhanced */}
                                        <div className="flex flex-wrap gap-2 mb-3">
                                            {citizen.bazi_profile.structure && (
                                                <span className="px-2 py-1 rounded bg-[#302839] text-[10px] text-gray-300 font-medium border border-[#3e344a]">
                                                    {citizen.bazi_profile.structure}
                                                </span>
                                            )}
                                            {citizen.bazi_profile.strength && (
                                                <span className="px-2 py-1 rounded bg-[#302839] text-[10px] text-gray-300 font-medium border border-[#3e344a]">
                                                    {citizen.bazi_profile.strength}
                                                </span>
                                            )}
                                            {citizen.bazi_profile.favorable_elements && citizen.bazi_profile.favorable_elements.length > 0 && (
                                                <span className="px-2 py-1 rounded bg-emerald-500/10 text-[10px] text-emerald-400 font-medium border border-emerald-500/30">
                                                    喜: {citizen.bazi_profile.favorable_elements.slice(0, 2).join('、')}
                                                </span>
                                            )}
                                        </div>

                                        <button
                                            onClick={() => setSelectedCitizen(citizen)}
                                            className="w-full py-2 rounded-lg bg-[#302839] hover:bg-[#3e344a] border border-[#3e344a] text-xs font-bold text-gray-300 transition-all"
                                        >
                                            完整報告
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                        {/* Add remaining grid closure if needed, but replace_file handles blocks */}
                    </div>
                )}

                {/* Pagination */}
                <div className="mt-8 flex justify-center gap-4">
                    <button
                        onClick={() => setPage(p => Math.max(0, p - 1))}
                        disabled={page === 0}
                        className="px-4 py-2 bg-slate-800 rounded hover:bg-slate-700 disabled:opacity-50 text-sm"
                    >
                        Previous
                    </button>
                    <span className="text-sm text-slate-500 py-2">
                        Page {page + 1}
                    </span>
                    <button
                        onClick={() => setPage(p => p + 1)}
                        disabled={(page + 1) * limit >= total}
                        className="px-4 py-2 bg-slate-800 rounded hover:bg-slate-700 disabled:opacity-50 text-sm"
                    >
                        Next
                    </button>
                </div>
            </main >
        </div >
    )
}

export default function CitizensPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">Loading Database...</div>}>
            <CitizensContent />
        </Suspense>
    )
}
