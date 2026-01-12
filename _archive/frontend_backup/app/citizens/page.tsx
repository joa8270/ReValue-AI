"use client"

import { useState, useEffect, Suspense } from "react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"

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

// Fallback for unknown structures
const DEFAULT_DECISION_MODEL = { title: "多元策略型", desc: "能根據不同情境調整決策模式，兼具理性與感性。" };

function getDecisionModel(structure: string | undefined) {
    if (!structure) return DEFAULT_DECISION_MODEL;
    const key = Object.keys(DECISION_MODELS).find(k => structure.includes(k));
    return key ? DECISION_MODELS[key] : DEFAULT_DECISION_MODEL;
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
                                <span className="text-xs font-mono text-slate-500 px-2 py-1 bg-white/5 rounded-full border border-white/5">ID: {citizen.id.slice(0, 8)}</span>
                            </div>
                            <div className="flex items-center gap-3 mt-2 text-sm">
                                <span className="bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30 font-bold">
                                    {citizen.occupation}
                                </span>
                                <span className="text-slate-400">•</span>
                                <span className="text-slate-300 font-medium">{citizen.age} 歲</span>
                                <span className="text-slate-400">•</span>
                                <span className="text-slate-400">{citizen.location}</span>
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
                                        {citizen.bazi_profile.four_pillars || "無命盤數據"}
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
                                                    {isCurrent && <span className="text-[10px] bg-purple-500 text-white px-2 py-0.5 rounded-full font-bold tracking-wider">CURRENT</span>}
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
            const res = await fetch(`https://mirra-backend.onrender.com/citizens?limit=${limit}&offset=${page * limit}`)
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
        <div className="min-h-screen bg-slate-950 text-slate-200 font-sans">
            {/* Modal for Detailed Report */}
            {selectedCitizen && (
                <CitizenModal citizen={selectedCitizen} onClose={() => setSelectedCitizen(null)} />
            )}

            {/* Header */}
            <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur-md sticky top-0 z-20">
                <div className="max-w-7xl mx-auto px-4 py-6">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                        <div>
                            <Link href={returnTo} className="text-purple-400 hover:text-purple-300 text-sm mb-2 flex items-center gap-1 transition-colors">
                                <span>←</span> {returnTo === '/' ? '返回首頁' : '返回戰情室'}
                            </Link>
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
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8">
                        {filteredCitizens.map((citizen) => (
                            <div key={citizen.id} className="group relative bg-slate-900/40 border border-white/5 rounded-3xl p-8 hover:bg-slate-900/60 transition-all duration-500 hover:scale-[1.01] overflow-hidden">
                                {/* Background Decorative Element */}
                                <div className="absolute -right-20 -top-20 w-64 h-64 bg-purple-600/5 blur-[100px] rounded-full group-hover:bg-purple-600/10 transition-colors" />

                                <div className="relative z-10">
                                    <div className="flex justify-between items-start mb-8">
                                        <div className="flex items-center gap-5">
                                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center text-3xl shadow-2xl border border-white/5 group-hover:border-purple-500/30 transition-colors">
                                                {citizen.gender === '女' ? '👩' : '👨'}
                                            </div>
                                            <div>
                                                <div className="font-black text-2xl text-white tracking-tight">{citizen.name}</div>
                                                <div className="flex items-center gap-2 mt-1">
                                                    <span className="text-sm font-medium text-slate-400">{citizen.occupation}</span>
                                                    <span className="text-slate-600">•</span>
                                                    <span className="text-sm font-medium text-slate-400">{citizen.age} 歲</span>
                                                    <span className="text-slate-600">•</span>
                                                    <span className="text-sm font-medium text-slate-400">{citizen.location}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="px-3 py-1.5 rounded-full bg-white/5 border border-white/5 text-[10px] text-slate-500 font-mono">
                                            ID: {citizen.id.slice(0, 8)}
                                        </div>
                                    </div>

                                    {/* Colloquial Interpretation */}
                                    <div className="mb-6 p-4 rounded-xl bg-purple-500/5 border border-purple-500/10">
                                        <div className="text-[10px] font-bold text-purple-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                                            <span className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" />
                                            當前狀態解讀
                                        </div>
                                        <div className="text-sm text-slate-200 font-normal leading-relaxed">
                                            {citizen.bazi_profile.current_state || "正在進行深度分析中..."}
                                        </div>
                                    </div>

                                    {/* Tech Stack (Grid of Pill Info) */}
                                    <div className="grid grid-cols-2 gap-3 mb-6">
                                        <div className="flex flex-col gap-1 p-3 rounded-xl bg-white/5 border border-white/5">
                                            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">命理格局</span>
                                            <span className="text-sm font-bold text-white truncate">{citizen.bazi_profile.structure}</span>
                                        </div>
                                        <div className="flex flex-col gap-1 p-3 rounded-xl bg-white/5 border border-white/5">
                                            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">能量強弱</span>
                                            <span className="text-sm font-bold text-white">{citizen.bazi_profile.strength}</span>
                                        </div>
                                        <div className="flex flex-col gap-1 p-3 rounded-xl bg-white/5 border border-white/5">
                                            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">喜用五行</span>
                                            <div className="flex gap-1.5">
                                                {citizen.bazi_profile.favorable_elements?.slice(0, 3).map(e => (
                                                    <span key={e} className="text-[11px] font-bold text-emerald-400">{e}</span>
                                                )) || <span className="text-[11px] text-slate-500">None</span>}
                                            </div>
                                        </div>
                                        <div className="flex flex-col gap-1 p-3 rounded-xl bg-white/5 border border-white/5">
                                            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">性格標籤</span>
                                            <div className="flex gap-1.5 overflow-hidden">
                                                {Array.isArray(citizen.traits) && citizen.traits.length > 0 ? (
                                                    <span className="text-[11px] font-bold text-amber-400 truncate">{citizen.traits[0]}</span>
                                                ) : <span className="text-[11px] text-amber-400 font-bold">多元性格</span>}
                                            </div>
                                        </div>
                                    </div>

                                    <button
                                        onClick={() => setSelectedCitizen(citizen)}
                                        className="w-full py-3 rounded-xl bg-purple-500/10 border border-purple-500/30 text-sm font-bold text-purple-300 hover:bg-purple-500/20 hover:border-purple-500/50 transition-all"
                                    >
                                        查看完整運勢報告
                                    </button>
                                </div>
                            </div>
                        ))}
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
            </main>
        </div>
    )
}

export default function CitizensPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">Loading Database...</div>}>
            <CitizensContent />
        </Suspense>
    )
}
