"use client"

import { useState, useEffect, Suspense } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import CitizenModal, {
    Citizen,
    I18N,
    generateMockPillars,
    getElementColor,
    parseFourPillars,
    getAvatarPath,
    translateGender
} from "../components/CitizenModal"

export const dynamic = "force-dynamic"

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

    // State for Filter & Pagination
    const [market, setMarket] = useState<'TW' | 'US' | 'CN'>('TW');
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 12;

    const [debouncedSearch, setDebouncedSearch] = useState("")

    // Debounce search input
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(search)
            setCurrentPage(1) // Reset to page 1 on search
        }, 500)
        return () => clearTimeout(timer)
    }, [search])

    useEffect(() => {
        fetchCitizens()
    }, [])

    const fetchCitizens = async () => {
        setLoading(true)
        try {
            // [V7 Update] Priority: API -> Static File (Fallback)
            // We want real-time DB data, not stale static JSON.
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const url = `${API_BASE_URL}/citizens/genesis`

            try {
                const res = await fetch(url)
                if (res.ok) {
                    const data = await res.json()

                    // [Fix] Handle both Legacy (List) and New (Object) API responses
                    // Because server hot-reload might fail or be delayed
                    let list: Citizen[] = [];
                    let totalCount = 0;

                    if (Array.isArray(data)) {
                        list = data;
                        totalCount = data.length;
                    } else {
                        list = data.citizens || [];
                        totalCount = data.total || 0;
                    }

                    setCitizens(list)
                    setTotal(totalCount)
                    setLoading(false)
                    return
                }
            } catch (e: any) {
                console.warn("API fetch failed, trying static file...", e)
            }

            // Fallback to local static file
            const res = await fetch('/citizens.json')
            if (res.ok) {
                const data = await res.json()
                setCitizens(data.citizens || [])
                setTotal(data.total || 0)
            }
        } catch (e: any) {
            console.error("Failed to fetch citizens:", e)
        }
        setLoading(false)
    }



    // STRICT FILTERING LOGIC

    const filteredCitizens = citizens.filter(c => {
        // 1. Region Filter: REMOVED for Multiverse Logic (One Soul, Three Masks)
        // We want to show the SAME 1000 citizens, just different masks.

        // 2. Search Filter
        if (debouncedSearch) {
            const term = debouncedSearch.toLowerCase();
            const pTW = c.profiles?.TW;
            const pCN = c.profiles?.CN;
            const pUS = c.profiles?.US;

            return (
                // Search Root Name
                c.name.toLowerCase().includes(term) ||
                // Search Localized Names (Multiverse)
                (pTW?.name || "").toLowerCase().includes(term) ||
                (pCN?.name || "").toLowerCase().includes(term) ||
                (pUS?.name || "").toLowerCase().includes(term) ||
                // Search ID
                String(c.id).includes(term) ||
                // Search Structure
                (c.bazi_profile?.structure || "").includes(term) ||
                (c.bazi_profile?.structure_en || "").toLowerCase().includes(term) ||
                // Search Traits
                (pUS?.traits?.[0] || "").toLowerCase().includes(term) ||
                (c.traits?.[0] || "").includes(term)
            );
        }
        return true;
    });

    // PAGINATION LOGIC
    const totalPages = Math.ceil(filteredCitizens.length / itemsPerPage);
    const paginatedCitizens = filteredCitizens.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );

    // Reset page when market changes
    useEffect(() => {
        setCurrentPage(1);
    }, [market]);

    const getProfile = (c: Citizen) => {
        // Find profile with actual content, prioritizing current market, then TW
        const pTW = c.profiles?.TW;
        const pM = c.profiles?.[market];

        const hasContent = (val: string | undefined) => val && val !== "None" && val !== "none" && val !== "未知" && val !== "Unknown";

        const name = hasContent(pM?.name) ? pM!.name : (hasContent(pTW?.name) ? pTW!.name : (c.name || "Unknown"));
        const city = hasContent(pM?.city) ? pM!.city : (hasContent(pTW?.city) ? pTW!.city : (c.location || "Unknown"));
        const job = hasContent(pM?.job) ? pM!.job : (hasContent(pTW?.job) ? pTW!.job : (typeof c.occupation === 'string' ? c.occupation : c.occupation?.['TW'] || "Unknown"));
        const pain = hasContent(pM?.pain) ? pM!.pain : (hasContent(pTW?.pain) ? pTW!.pain : null);

        return { name, city, job, pain };
    }

    const t: any = I18N[market] || I18N['TW'];

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 font-sans pt-[100px]">
            {/* Modal */}
            {selectedCitizen && (
                <CitizenModal citizen={selectedCitizen} market={market} onClose={() => setSelectedCitizen(null)} />
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
                                實時人口資料庫 • 顯示: {filteredCitizens.length} / 總數: {total}
                            </div>
                        </div>

                        {/* Market Selector & Search Group */}
                        <div className="flex flex-col md:flex-row gap-4 w-full md:w-auto items-center">
                            {/* Market Toggle */}
                            <div className="flex bg-slate-900/80 p-1 rounded-xl border border-white/10">
                                {(['TW', 'US', 'CN'] as const).map((m) => (
                                    <button
                                        key={m}
                                        onClick={() => setMarket(m)}
                                        className={`px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${market === m
                                            ? 'bg-purple-600 text-white shadow-lg'
                                            : 'text-slate-400 hover:text-white hover:bg-white/5'
                                            }`}
                                    >
                                        <span>{m === 'TW' ? '🇹🇼' : m === 'US' ? '🇺🇸' : '🇨🇳'}</span>
                                        {m}
                                    </button>
                                ))}
                            </div>

                            {/* Search */}
                            <div className="relative group w-full md:w-auto">
                                <div className="absolute inset-0 bg-purple-500/10 blur-xl group-hover:bg-purple-500/20 transition-all rounded-full" />
                                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 z-10">🔍</span>
                                <input
                                    type="text"
                                    placeholder="搜尋姓名、格局、個性描述..."
                                    className="relative z-10 pl-11 pr-6 py-2.5 bg-slate-900/50 border border-white/10 rounded-xl text-white focus:outline-none focus:border-purple-500/50 focus:ring-4 focus:ring-purple-500/5 transition-all w-full md:min-w-[300px] backdrop-blur-sm"
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
                        <div className="text-slate-500 font-mono text-sm">{t.loading}</div>
                    </div>
                ) : (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {paginatedCitizens.map((citizen) => {
                                const pillars = parseFourPillars(
                                    (market === 'US' && citizen.bazi_profile.four_pillars_en)
                                        ? citizen.bazi_profile.four_pillars_en
                                        : (citizen.bazi_profile.four_pillars || generateMockPillars())
                                );
                                const dayMasterElement = citizen.bazi_profile.element || "土";
                                const elementStyle = getElementColor(dayMasterElement);

                                // 🌍 Global Identity Context
                                const profile = getProfile(citizen);

                                return (
                                    <div key={citizen.id} className="group relative bg-[#241a30] rounded-xl overflow-hidden border border-[#362b45] hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-purple-500/10">

                                        {/* Day Master Badge */}
                                        <div className="absolute top-3 right-3 z-20 flex flex-col items-end gap-1">
                                            <span className="text-[9px] text-gray-400 font-mono tracking-wider">{market === 'US' ? 'DM' : '日主'}</span>
                                            <div className={`
                                                relative size-11 rounded-full flex items-center justify-center
                                                border-[3px] font-bold text-lg tracking-tight
                                                transition-all duration-300 group-hover:scale-110
                                                ${(dayMasterElement === 'Metal' || dayMasterElement === '金') ? 'bg-gradient-to-br from-slate-300 to-slate-500 border-slate-200 text-slate-900 shadow-lg shadow-slate-400/50' : ''}
                                                ${(dayMasterElement === 'Wood' || dayMasterElement === '木') ? 'bg-gradient-to-br from-emerald-300 to-emerald-600 border-emerald-200 text-emerald-950 shadow-lg shadow-emerald-400/50' : ''}
                                                ${(dayMasterElement === 'Water' || dayMasterElement === '水') ? 'bg-gradient-to-br from-blue-300 to-blue-600 border-blue-200 text-blue-950 shadow-lg shadow-blue-400/50' : ''}
                                                ${(dayMasterElement === 'Fire' || dayMasterElement === '火') ? 'bg-gradient-to-br from-orange-300 to-orange-600 border-orange-200 text-orange-950 shadow-lg shadow-orange-400/50' : ''}
                                                ${(dayMasterElement === 'Earth' || dayMasterElement === '土') ? 'bg-gradient-to-br from-amber-400 to-amber-700 border-amber-200 text-amber-950 shadow-lg shadow-amber-400/50' : ''}
                                            `}>
                                                {pillars?.day?.charAt(0) || '?'}
                                                {/* Glow effect ring */}
                                                <div className={`
                                                    absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 transition-opacity
                                                    ${(dayMasterElement === 'Metal' || dayMasterElement === '金') ? 'ring-4 ring-slate-300/30' : ''}
                                                    ${(dayMasterElement === 'Wood' || dayMasterElement === '木') ? 'ring-4 ring-emerald-300/30' : ''}
                                                    ${(dayMasterElement === 'Water' || dayMasterElement === '水') ? 'ring-4 ring-blue-300/30' : ''}
                                                    ${(dayMasterElement === 'Fire' || dayMasterElement === '火') ? 'ring-4 ring-orange-300/30' : ''}
                                                    ${(dayMasterElement === 'Earth' || dayMasterElement === '土') ? 'ring-4 ring-amber-300/30' : ''}
                                                `} />
                                            </div>
                                        </div>

                                        {/* Header Visual */}
                                        <div className="h-32 bg-[#1a1324] relative overflow-hidden">
                                            <div className="absolute inset-0 bg-gradient-to-t from-[#241a30] to-transparent"></div>
                                            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20"></div>
                                            {/* Market Flag Overlay */}
                                            {market !== 'TW' && (
                                                <div className="absolute top-3 left-3 px-2 py-1 bg-black/50 backdrop-blur rounded text-xl border border-white/10">
                                                    {market === 'US' ? '🇺🇸' : '🇨🇳'}
                                                </div>
                                            )}
                                        </div>

                                        {/* Content */}
                                        <div className="px-5 pb-5 -mt-12 relative z-10">
                                            <div className="flex items-end justify-between mb-3">
                                                <div className="size-20 rounded-xl overflow-hidden border-2 border-[#241a30] shadow-md bg-black relative">
                                                    <img
                                                        src={getAvatarPath(citizen.id, citizen.age, citizen.gender, profile.name)}
                                                        alt={profile.name}
                                                        className="w-full h-full object-cover"
                                                    />
                                                </div>
                                                <div className="text-right">
                                                    <span className="text-xs font-mono text-gray-500 block">#{String(citizen.id).padStart(4, '0').slice(0, 4)}</span>
                                                    <span className="text-xs text-gray-600">{profile.city || "Unknown"}</span>
                                                </div>
                                            </div>

                                            <h3 className="text-xl font-bold text-white mb-0.5 tracking-tight">{profile.name}</h3>
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-[10px] text-gray-400 px-1.5 py-0.5 rounded bg-gray-800/50 border border-gray-700/50">
                                                    {translateGender(citizen.gender, market)}
                                                </span>
                                                <span className="text-[10px] text-gray-400 px-1.5 py-0.5 rounded bg-gray-800/50 border border-gray-700/50">
                                                    {citizen.age}{t.age}
                                                </span>
                                            </div>
                                            <p className={`text-sm font-medium mb-1 uppercase tracking-wide ${elementStyle.text.replace('text-', 'text-').replace('-900', '-400')}`}>
                                                {profile.job}
                                            </p>

                                            {/* 🔥 Pain Point Badge with Tooltip Implementation */}
                                            {profile.pain && (
                                                <div className="mt-3 group/tooltip relative">
                                                    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-red-500/30 bg-red-500/10 text-[10px] font-bold text-red-300 cursor-help hover:bg-red-500/20 transition-colors">
                                                        <span>⚠️</span>
                                                        <span className="truncate max-w-[200px]">{profile.pain}</span>
                                                    </div>

                                                    {/* Custom Tooltip */}
                                                    <div className="absolute bottom-full left-0 mb-2 w-48 p-2 bg-slate-900 border border-white/10 rounded-lg shadow-xl text-xs text-slate-300 opacity-0 group-hover/tooltip:opacity-100 transition-opacity pointer-events-none z-50">
                                                        <div className="font-bold text-white mb-1">
                                                            {market === 'US' ? 'Core Anxiety' : '當前核心焦慮'}
                                                        </div>
                                                        {profile.pain}
                                                        <div className="absolute -bottom-1 left-4 w-2 h-2 bg-slate-900 border-b border-r border-white/10 rotate-45"></div>
                                                    </div>
                                                </div>
                                            )}


                                            {/* Current Luck / State Box */}
                                            {(() => {
                                                const state = (citizen.bazi_profile as any).localized_state?.[market] ||
                                                    (citizen.bazi_profile as any).localized_state?.['TW'] ||
                                                    citizen.bazi_profile.current_state;

                                                if (!state || state === "None" || state === "Unknown") return null;

                                                return (
                                                    <div className="mb-3 p-2 rounded-lg bg-purple-500/5 border border-purple-500/10">
                                                        <div className="text-[9px] font-bold text-purple-400 uppercase tracking-widest mb-1">{t.current_state}</div>
                                                        <div className="text-[11px] text-slate-300 line-clamp-2 leading-relaxed">
                                                            {state}
                                                        </div>
                                                    </div>
                                                );
                                            })()}


                                            {/* Bazi Info (Always Show for Authenticity) */}
                                            <div className="text-[10px] text-gray-500 mb-3 font-mono">
                                                <div>
                                                    {(() => {
                                                        const { birth_year, birth_month, birth_day, birth_hour, birth_shichen } = citizen.bazi_profile || {};
                                                        if (birth_year && birth_month && birth_day) {
                                                            const datePart = `${birth_year}-${String(birth_month).padStart(2, '0')}-${String(birth_day).padStart(2, '0')}`;
                                                            const timePart = birth_shichen ? ` ${birth_shichen}` : (birth_hour !== undefined && birth_hour !== null ? ` ${String(birth_hour).padStart(2, '0')}:00` : '');
                                                            return datePart + timePart;
                                                        }
                                                        return 'Unknown Date';
                                                    })()}
                                                </div>
                                                <div className="flex gap-2 mt-1 text-purple-300">
                                                    <span>{pillars?.year || '??'}</span>
                                                    <span>{pillars?.month || '??'}</span>
                                                    <span>{pillars?.day || '??'}</span>
                                                    <span>{pillars?.hour || '??'}</span>
                                                </div>
                                            </div>

                                            <button

                                                onClick={() => setSelectedCitizen(citizen)}
                                                className="w-full py-2 rounded-lg bg-[#302839] hover:bg-[#3e344a] border border-[#3e344a] text-xs font-bold text-gray-300 transition-all"
                                            >
                                                {t.analysis_report}
                                            </button>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* Improved Pagination UI */}
                        {totalPages > 1 && (
                            <div className="mt-12 flex justify-center items-center gap-6 pb-12">
                                <button
                                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                    disabled={currentPage === 1}
                                    className="px-6 py-3 bg-slate-800 rounded-xl hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed text-sm font-bold border border-white/5 transition-all flex items-center gap-2"
                                >
                                    <span>←</span> {t.prev_page}
                                </button>

                                <div className="flex flex-col items-center">
                                    <span className="text-white font-bold tracking-widest text-lg">
                                        {currentPage}
                                    </span>
                                    <span className="text-xs text-slate-500 uppercase tracking-wider">
                                        / {totalPages}
                                    </span>
                                </div>

                                <button
                                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                    disabled={currentPage === totalPages}
                                    className="px-6 py-3 bg-slate-800 rounded-xl hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed text-sm font-bold border border-white/5 transition-all flex items-center gap-2"
                                >
                                    {t.next_page} <span>→</span>
                                </button>
                            </div>
                        )}
                    </>
                )}
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
