"use client"

import { useState, useEffect, useRef } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { motion } from "framer-motion"

// ===== Type Definitions (Bazi V3) =====
interface BaziDistribution {
  Fire: number
  Water: number
  Metal: number
  Wood: number
  Earth: number
}

interface BaziProfile {
  day_master: string
  day_master_element: string
  strength: "身強" | "身弱" | "中和"
  structure: string
  favorable: string[]
  unfavorable: string[]
}

interface Persona {
  id: string
  name?: string
  age: string
  element: string
  day_master: string
  pattern: string
  trait: string
  location?: string
  decision_logic?: string
  occupation?: string
  birth_year?: number
  birth_month?: number
  birth_day?: number
  birth_shichen?: string
  four_pillars?: string
  current_luck?: { name: string; description: string }
  luck_timeline?: { age_start: number; age_end: number; name: string; description: string }[]
  strength?: string
  favorable?: string[]
}

// Citizen 類型別名（用於 modal 組件兼容性）
type Citizen = Persona

// ===== Element Config =====
const elementConfig: Record<string, { icon: string; color: string; bg: string; glow: string; cn: string; trait: string }> = {
  Fire: { icon: "🔥", color: "text-orange-400", bg: "bg-gradient-to-r from-red-600 to-orange-500", glow: "shadow-orange-500/50", cn: "火", trait: "熱情衝動、直覺行動" },
  Water: { icon: "💧", color: "text-cyan-400", bg: "bg-gradient-to-r from-blue-600 to-cyan-500", glow: "shadow-cyan-500/50", cn: "水", trait: "理性冷靜、深思熟慮" },
  Metal: { icon: "🔩", color: "text-slate-300", bg: "bg-gradient-to-r from-slate-500 to-zinc-400", glow: "shadow-slate-400/50", cn: "金", trait: "精明挑剔、重視品質" },
  Wood: { icon: "🌳", color: "text-emerald-400", bg: "bg-gradient-to-r from-green-600 to-emerald-500", glow: "shadow-emerald-500/50", cn: "木", trait: "成長導向、追求創新" },
  Earth: { icon: "⛰️", color: "text-amber-400", bg: "bg-gradient-to-r from-amber-600 to-yellow-500", glow: "shadow-amber-500/50", cn: "土", trait: "穩重務實、重視CP值" }
}

// ===== DECISION MODELS =====
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

const DEFAULT_DECISION_MODEL = { title: "多元策略型", desc: "能根據不同情境調整決策模式，兼具理性與感性。" };

function getDecisionModel(structure: string | undefined) {
  if (!structure) return DEFAULT_DECISION_MODEL;
  const key = Object.keys(DECISION_MODELS).find(k => structure.includes(k));
  return key ? DECISION_MODELS[key] : DEFAULT_DECISION_MODEL;
}

interface SimulationData {
  status: string
  score: number
  summary: string
  productName?: string  // Added to fix TypeScript error
  genesis: {
    sample_size: number
    personas: Persona[]
    bazi_profile?: BaziProfile
  }
  simulation_metadata?: {
    sample_size: number
    bazi_distribution: BaziDistribution
  }
  bazi_distribution?: BaziDistribution
  arena_comments: Array<{
    sentiment: string
    text: string
    citizen_id?: string
    persona: Persona
    score?: number
  }>
  result?: { summary: string }
  intent?: any
  suggestions?: Array<{ target: string; advice: string; action_plan: string[]; score_improvement?: string }>
  objections?: Array<{ reason: string; percentage: string }>
  buying_intent?: string
}

interface EnrichedPersona extends Persona {
  fullBirthday?: string
  luckCycle?: string
  detailedTrait?: string
  displayAge?: string
}

/**
 * 直接使用後端傳來的市民資料，不再生成假資料
 * 所有資料應該已在 line_bot_service.py 的 _build_simulation_result 中完整填充
 */
const enrichCitizenData = (p: Persona): EnrichedPersona => {
  // 1. 日主：直接使用後端資料
  const dm = p.day_master || "未知";

  // 2. 生日：直接使用後端資料，不再推算
  let fullBirthday = "";
  if (p.birth_year && p.birth_month && p.birth_day) {
    fullBirthday = `${p.birth_year}年${p.birth_month}月${p.birth_day}日`;
    if (p.birth_shichen) fullBirthday += ` ${p.birth_shichen}`;
  } else {
    fullBirthday = "生辰資料缺失";
  }

  // 3. 當前大運：直接使用後端資料
  let luckCycle = "";
  if (p.current_luck && p.current_luck.description) {
    luckCycle = p.current_luck.description;
  } else if (p.current_luck && p.current_luck.name) {
    luckCycle = `目前行${p.current_luck.name}`;
  } else {
    luckCycle = "大運資料載入中...";
  }

  // 4. 性格特質描述
  const traitMap: Record<string, string> = {
    "Fire": "熱情洋溢，行動力強，但有時過於急躁。",
    "Water": "聰明機智，適應力強，心思深沉。",
    "Metal": "果斷剛毅，講求原則，重視效率與SOP。",
    "Wood": "仁慈博愛，富有創意，具備良好的生長性與彈性。",
    "Earth": "誠信穩重，包容力強，是團隊中的定海神針。"
  };
  const detailedTrait = traitMap[p.element] || "性格均衡，適應力良好。";

  // 5. 決策邏輯：直接使用或根據格局生成
  let decisionLogic = p.decision_logic;
  if (!decisionLogic || decisionLogic.includes("根據八字格局特質分析")) {
    const dmModel = getDecisionModel(p.pattern);
    decisionLogic = `【${dmModel.title}】${dmModel.desc}`;
  }

  // 6. 大運時間軸：直接使用後端資料
  const luck_timeline = p.luck_timeline || [];

  // 7. 喜用五行：直接使用後端資料
  const favorable = p.favorable || [];

  // 8. 身強身弱：直接使用後端資料
  const strength = p.strength || "中和";

  return {
    ...p,
    day_master: dm,
    age: p.age,
    displayAge: p.age,
    fullBirthday,
    luckCycle,
    detailedTrait,
    decision_logic: decisionLogic,
    luck_timeline,
    favorable,
    strength
  };
};


function CitizenModal({ citizen, onClose }: { citizen: EnrichedPersona; onClose: () => void }) {
  if (!citizen) return null;
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in fade-in duration-200" onClick={onClose}>
      <div className="relative bg-slate-900 border border-purple-500/30 rounded-3xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl shadow-purple-900/50" onClick={(e) => e.stopPropagation()}>
        <div className="p-6 border-b border-white/10 bg-slate-900/95 sticky top-0 z-10 flex justify-between items-start">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-950 flex items-center justify-center text-4xl shadow-xl border border-white/10">
              {elementConfig[citizen.element]?.icon || '👤'}
            </div>
            <div>
              <div className="flex items-baseline gap-3">
                <h2 className="text-3xl font-black text-white tracking-tight">{citizen.name}</h2>
                <span className="text-xs font-mono text-slate-500 px-2 py-1 bg-white/5 rounded-full border border-white/5">ID: {citizen.id ? String(citizen.id).padStart(8, '0').slice(0, 8) : '????'}</span>
              </div>
              <div className="flex flex-col gap-1.5 mt-2">
                <div className="flex items-center gap-3 text-sm">
                  <span className="bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30 font-bold">
                    {citizen.occupation || 'AI Citizen'}
                  </span>
                  <span className="text-slate-400">•</span>
                  <span className="text-slate-300 font-medium">{citizen.displayAge || citizen.age} 歲</span>
                  <span className="text-slate-400">•</span>
                  <span className="text-slate-400">{citizen.location || 'Taiwan'}</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
                  <span className="material-symbols-outlined text-[14px]">calendar_month</span>
                  <span>{citizen.fullBirthday || '生日未知'}</span>
                </div>
              </div>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-full">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="overflow-y-auto p-6 space-y-6 custom-scrollbar">
          <section>
            <div className="flex items-center gap-2 mb-3">
              <span className="w-2 h-2 rounded-full bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.8)]"></span>
              <h3 className="text-sm font-bold text-purple-400 uppercase tracking-widest">當前狀態解讀</h3>
            </div>
            <div className="p-5 rounded-2xl bg-gradient-to-br from-purple-900/20 to-slate-900 border border-purple-500/30 text-slate-200 leading-relaxed text-lg shadow-inner">
              {citizen.detailedTrait}
            </div>
          </section>

          <section className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">命理格局</div>
              <div className="text-xl font-black text-white">{citizen.pattern}</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">能量強弱</div>
              <div className="text-xl font-black text-white">{citizen.strength || "中和"}</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">喜用五行</div>
              <div className="flex gap-1.5 flex-wrap">
                {citizen.favorable?.map(e => (
                  <span key={e} className="text-sm font-bold text-emerald-400 flex items-center">
                    {elementConfig[e]?.icon}{e}
                  </span>
                )) || <span className="text-slate-500">Balance</span>}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">性格標籤</div>
              <div className="text-xl font-black text-amber-400 truncate">{citizen.trait?.split(',')[0] || "多元性格"}</div>
            </div>
          </section>

          {showDetails && (
            <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
              <section>
                <div className="flex items-center gap-2 mb-3">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                  <h3 className="text-sm font-bold text-cyan-500 uppercase tracking-widest">決策思維模型</h3>
                </div>
                <div className="p-5 rounded-2xl bg-slate-800/30 border border-cyan-500/20 text-slate-200 leading-relaxed text-sm">
                  {citizen.decision_logic}
                </div>
              </section>

              <div className="grid grid-cols-1 gap-6">
                <section>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                    <h3 className="text-sm font-bold text-amber-500 uppercase tracking-widest">當前大運 / CURRENT LUCK</h3>
                  </div>
                  <div className="p-5 rounded-2xl bg-amber-500/5 border border-amber-500/20">
                    <div className="text-amber-100/80 leading-relaxed">
                      {citizen.luckCycle || "暫無詳細運程描述"}
                    </div>
                  </div>
                </section>
                <section>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
                    <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest">八字命盤</h3>
                  </div>
                  <div className="p-6 rounded-2xl bg-slate-950 border border-white/10 text-center font-mono text-xl md:text-2xl text-white tracking-widest shadow-inner">
                    {citizen.four_pillars || "無命盤數據"}
                  </div>
                </section>
              </div>

              <section>
                <div className="flex items-center gap-2 mb-3">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">10年大運時間軸</h3>
                </div>
                <div className="space-y-3">
                  {citizen.luck_timeline?.map((pillar, idx) => {
                    const ageMs = parseInt(citizen.age || "30");
                    const isCurrent = ageMs >= pillar.age_start && ageMs <= pillar.age_end;
                    return (
                      <div key={idx} className={`p-4 rounded-xl border transition-all ${isCurrent ? 'bg-purple-900/30 border-purple-500/50 shadow-[0_0_15px_rgba(168,85,247,0.1)]' : 'bg-slate-800/30 border-white/5 opacity-70 hover:opacity-100'}`}>
                        <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-2">
                          <div className="flex items-center gap-3 min-w-[120px]">
                            <span className={`text-xs font-bold ${isCurrent ? 'text-purple-300' : 'text-slate-500'}`}>{pillar.age_start}-{pillar.age_end}歲</span>
                            <span className={`text-lg font-bold ${isCurrent ? 'text-white' : 'text-slate-300'}`}>{pillar.name}</span>
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

          <button onClick={() => setShowDetails(!showDetails)} className="w-full py-4 rounded-xl bg-purple-500/10 border border-purple-500/30 text-base font-bold text-purple-300 hover:bg-purple-500/20 hover:border-purple-500/50 transition-all flex items-center justify-center gap-2 group">
            {showDetails ? <>收合報告 <span className="group-hover:-translate-y-1 transition-transform">↑</span></> : <>查看完整運勢報告 <span className="group-hover:translate-y-1 transition-transform">↓</span></>}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function WatchPage() {
  const params = useParams()
  const simId = params.id as string
  const [data, setData] = useState<SimulationData | null>(null)
  const [typedSummary, setTypedSummary] = useState("")
  const [selectedCitizen, setSelectedCitizen] = useState<Citizen | null>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  const TOTAL_POPULATION = 1000

  useEffect(() => {
    let intervalId: NodeJS.Timeout

    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        const res = await fetch(`${apiUrl}/simulation/${simId}`)
        if (res.ok) {
          const json = await res.json()

          // Stop polling if ready or failed
          if (json.status === 'ready' || json.status === 'failed') {
            if (intervalId) clearInterval(intervalId)
          }

          // Stable score logic
          const enrichedComments = json.arena_comments?.map((c: any) => {
            const seed = (c.text || "").split("").reduce((acc: number, char: string) => acc + char.charCodeAt(0), 0);
            let baseScore, range;
            switch (c.sentiment?.toLowerCase()) {
              case 'positive': baseScore = 80; range = 20; break;
              case 'negative': baseScore = 30; range = 30; break;
              default: baseScore = 60; range = 20; break;
            }
            const stableScore = baseScore + (seed % range);
            return { ...c, score: c.score || stableScore };
          }) || [];

          // 不再強制填充匿名市民，只顯示真實的 AI 評論
          // 如果評論數量太少，可能是 API 返回問題，不應用虛假數據填充

          const totalScore = enrichedComments.length > 0
            ? Math.floor(enrichedComments.reduce((acc: number, curr: any) => acc + curr.score, 0) / enrichedComments.length)
            : json.score;

          const enrichedSuggestions = (json.suggestions || []).map((s: any) => {
            let action_plan: string[] = [];
            if (s.target.includes("環保") || s.advice.includes("ESG")) {
              action_plan = [
                "製作一份專屬 ESG 影響力報告，量化減碳數據。",
                "在行銷材料中加入 '循環經濟' 認證標章。",
                "舉辦 '綠色投資' 線上說明會，邀請環保意見領袖背書。"
              ];
            } else if (s.target.includes("海外") || s.advice.includes("非洲")) {
              action_plan = [
                "列出非洲/東南亞前 5 大電子產品分銷商名單。",
                "參加今年度的 Global Source 電子展，設立針對性展位。",
                "設計針對新興市場的低門檻代理加盟方案。"
              ];
            } else if (s.target.includes("價格") || s.advice.includes("預算")) {
              action_plan = [
                "推出 '首購優惠' 或 '舊換新' 折抵活動。",
                "製作 '競品價格對比表'，凸顯長期持有成本優勢。",
                "強化產品保固條款，消除對二手/平價產品的品質疑慮。"
              ];
            } else {
              // Fallback generic actions if no match
              action_plan = [
                "進行 A/B 測試優化相關行銷文案。",
                "針對此目標客群投放精準社交媒體廣告。",
                "收集早期使用者的詳細反饋以迭代產品。"
              ];
            }
            return { ...s, action_plan };
          });

          setData({ ...json, arena_comments: enrichedComments, score: totalScore, suggestions: enrichedSuggestions });
        }
      } catch (e) {
        console.error("Fetch Error", e)
      }
    }

    fetchData() // Initial fetch
    intervalId = setInterval(fetchData, 3000) // Poll every 3s

    return () => {
      if (intervalId) clearInterval(intervalId)
    }
  }, [simId])

  const lastSummaryRef = useRef("")
  useEffect(() => {
    if (data?.summary) {
      if (data.summary === lastSummaryRef.current) return
      lastSummaryRef.current = data.summary
      setTypedSummary("")
      let i = 0
      const timer = setInterval(() => {
        i++
        if (i <= data.summary.length) setTypedSummary(data.summary.slice(0, i))
        else clearInterval(timer)
      }, 10)
      return () => clearInterval(timer)
    }
  }, [data?.summary])

  if (!data || data.status === "processing") {
    return (
      <div className="fixed inset-0 bg-[#101f22] text-[#25d1f4] font-mono overflow-hidden z-50 flex flex-col">
        {/* Helper Styles for this specific page */}
        <style jsx global>{`
          @keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
          .animate-spin-slow { animation: spin-slow 15s linear infinite; }
          .scanline {
            background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.1));
            background-size: 100% 4px;
            pointer-events: none;
          }
          @keyframes flicker {
            0%, 19.999%, 22%, 62.999%, 64%, 64.999%, 70%, 100% { opacity: 0.99; text-shadow: 0 0 8px rgba(37,209,244,0.6); }
            20%, 21.999%, 63%, 63.999%, 65%, 69.999% { opacity: 0.4; text-shadow: none; }
          }
          @keyframes typing {
            0% { width: 0 }
            50% { width: 100% }
            100% { width: 100% }
          }
          @keyframes shimmer {
            100% { transform: translateX(100%); }
          }
          @keyframes blink {
            50% { opacity: 0; }
          }
        `}</style>

        {/* Scanline Overlay */}
        <div className="fixed inset-0 z-50 opacity-10 scanline"></div>

        {/* Top Navigation */}
        <header className="flex items-center justify-between whitespace-nowrap border-b border-[#283639] bg-[#0a0f10]/90 backdrop-blur-sm px-6 py-3 z-40">
          <div className="flex items-center gap-4 text-white">
            <div className="size-6 text-[#25d1f4] animate-pulse">
              <span className="material-symbols-outlined text-[24px]">terminal</span>
            </div>
            <div>
              <h2 className="text-white text-lg font-bold leading-tight tracking-wider uppercase">MIRRA // TERMINAL</h2>
              <div className="flex items-center gap-2 text-xs text-[#9cb5ba] font-mono">
                <span>NODE-01</span>
                <span className="size-1.5 rounded-full bg-[#d8b4fe] inline-block"></span>
                <span>ONLINE</span>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="flex size-10 items-center justify-center overflow-hidden rounded-lg bg-[#283639] text-white">
                <span className="size-1.5 bg-[#d8b4fe] rounded-full"></span>
              </div>
            ))}
          </div>
        </header>

        {/* Main Layout */}
        <main className="flex-1 flex overflow-hidden relative">
          {/* Background Grid Decoration */}
          <div className="absolute inset-0 z-0 opacity-5 pointer-events-none" style={{ backgroundImage: "radial-gradient(#d8b4fe 1px, transparent 1px)", backgroundSize: "40px 40px" }}></div>

          {/* Content Container */}
          <div className="flex-1 flex flex-col md:flex-row gap-6 p-6 z-10 w-full max-w-[1600px] mx-auto items-center justify-center h-full">

            {/* LEFT/CENTER: Map Visualization */}
            <div className="relative flex flex-1 w-full h-full items-center justify-center min-h-[400px]">
              {/* Holo Rings */}
              <div className="absolute size-[400px] md:size-[500px] rounded-full border border-[#283639] animate-spin-slow opacity-30"></div>
              <div className="absolute size-[380px] md:size-[480px] rounded-full border border-dashed border-[#d8b4fe]/20 animate-spin-slow" style={{ animationDirection: "reverse", animationDuration: "15s" }}></div>

              {/* Decorative Brackets around map */}
              <div className="absolute top-10 left-10 size-8 border-t-2 border-l-2 border-[#d8b4fe]/50 rounded-tl-lg"></div>
              <div className="absolute top-10 right-10 size-8 border-t-2 border-r-2 border-[#d8b4fe]/50 rounded-tr-lg"></div>
              <div className="absolute bottom-10 left-10 size-8 border-b-2 border-l-2 border-[#d8b4fe]/50 rounded-bl-lg"></div>
              <div className="absolute bottom-10 right-10 size-8 border-b-2 border-r-2 border-[#d8b4fe]/50 rounded-br-lg"></div>

              {/* Central Map Container */}
              <div className="relative z-10 flex flex-col items-center">
                <div className="relative size-[300px] md:size-[400px] flex items-center justify-center">
                  {/* Map Image - Local Asset */}
                  <div className="w-full h-full bg-contain bg-center bg-no-repeat opacity-90 drop-shadow-[0_0_15px_rgba(216,180,254,0.3)] grayscale brightness-125 contrast-125"
                    style={{ backgroundImage: "url('/taiwan-map.png')" }}>
                  </div>

                  {/* Data Collection Animation (Particles streaming to center) */}
                  {[...Array(40)].map((_, i) => {
                    const randomAngle = Math.random() * 360;
                    const startX = 50 + (Math.cos(randomAngle * Math.PI / 180) * 50); // %
                    const startY = 50 + (Math.sin(randomAngle * Math.PI / 180) * 50); // %

                    return (
                      <motion.div
                        key={`particle-${i}`}
                        className="absolute w-1 h-1 bg-purple-400 rounded-full shadow-[0_0_5px_#a855f7]"
                        initial={{ left: `${startX}%`, top: `${startY}%`, opacity: 0, scale: 0 }}
                        animate={{ left: "50%", top: "45%", opacity: [0, 1, 0], scale: [0, 1.5, 0] }} // Move to roughly Taipei/Center
                        transition={{
                          duration: 1.5 + Math.random() * 1.5,
                          repeat: Infinity,
                          delay: Math.random() * 2,
                          ease: "easeIn"
                        }}
                      />
                    );
                  })}

                  {/* Pulse Effects (Fake Agents / Static Nodes) */}
                  <div className="absolute top-1/4 left-1/3 size-2 bg-[#d8b4fe] rounded-full shadow-[0_0_10px_#d8b4fe] animate-ping"></div>
                  <div className="absolute top-1/3 left-1/2 size-1.5 bg-[#d8b4fe] rounded-full shadow-[0_0_10px_#d8b4fe] animate-pulse"></div>
                  <div className="absolute bottom-1/3 left-1/4 size-3 bg-[#d8b4fe] rounded-full shadow-[0_0_15px_#d8b4fe] animate-pulse duration-700"></div>
                  <div className="absolute top-1/2 right-1/3 size-2 bg-[#d8b4fe] rounded-full shadow-[0_0_10px_#d8b4fe] animate-ping delay-300"></div>

                  {/* Central Node Pulse */}
                  <div className="absolute top-[45%] left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-[#d8b4fe] rounded-full blur-md animate-pulse"></div>

                  {/* Radar Scan Effect */}
                  <div className="absolute inset-0 rounded-full bg-gradient-to-b from-transparent via-[#d8b4fe]/5 to-transparent animate-spin-slow opacity-20 pointer-events-none"></div>
                </div>
                <div className="mt-8 text-center space-y-2">
                  <div className="text-[#d8b4fe] text-xl font-bold tracking-widest drop-shadow-[0_0_8px_rgba(216,180,254,0.6)] animate-[flicker_3s_infinite]">系統收集AI市民評論中</div>
                  <div className="text-[#e9d5ff] text-sm font-mono flex items-center justify-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></span>
                    <span className="animate-[typing_3s_steps(20)_infinite] overflow-hidden whitespace-nowrap border-r-2 border-purple-400 pr-1">正在連線所有 AI 市民節點...</span>
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT: System Log */}
            <div className="w-full md:w-[450px] flex flex-col h-[50vh] md:h-[70vh] bg-[#050505]/80 border border-[#283639] rounded-xl overflow-hidden shadow-2xl backdrop-blur-md">
              {/* Log Header */}
              <div className="flex items-center justify-between px-4 py-3 bg-[#111718] border-b border-[#283639]">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-[#d8b4fe] text-[18px]">data_object</span>
                  <span className="text-xs font-bold text-white tracking-wider">SYSTEM LOG</span>
                </div>
                <div className="flex gap-1.5">
                  <div className="size-2 rounded-full bg-[#283639]"></div>
                  <div className="size-2 rounded-full bg-[#283639]"></div>
                  <div className="size-2 rounded-full bg-[#d8b4fe] animate-pulse"></div>
                </div>
              </div>
              {/* Scrollable Area */}
              <div className="flex-1 overflow-y-auto p-4 font-mono text-sm space-y-3 relative">
                {[
                  { t: "[SYSTEM] 連線至 MIRRA-NODE-01 成功", c: "text-[#536b70]" },
                  { t: "載入核心模組: 經濟模型 v4.2 ... 完成", c: "text-[#536b70]" },
                  { t: "正在初始化平行世界...", c: "text-[#7a969c]" },
                  { t: "正在計算 1,000 位市民的八字命盤...", c: "text-[#9cb5ba]" },
                  { t: "正在根據出生地生成人口分佈... [OK]", c: "text-[#9cb5ba]" },
                  { t: "警告: 發現異常變數 (已修正)", c: "text-white font-bold" },
                  { t: "正在模擬市場摩擦係數...", c: "text-gray-200" },
                ].map((log, i) => (
                  <div key={i} className="flex gap-3">
                    <span className="text-cyan-700">{`>`}</span>
                    <span className={log.c}>{log.t}</span>
                  </div>
                ))}

                {/* Active line */}
                <div className="relative flex gap-3 text-[#25d1f4] font-bold shadow-[0_0_15px_rgba(37,209,244,0.1)] bg-[#25d1f4]/5 p-2 rounded border-l-2 border-[#25d1f4] mt-4 overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#25d1f4]/10 to-transparent -translate-x-full animate-[shimmer_2s_infinite]"></div>
                  <span className="shrink-0 animate-pulse">{`>`}</span>
                  <p className="drop-shadow-[0_0_5px_rgba(37,209,244,0.5)] z-10">
                    正在計算五行流年影響...
                    <span className="inline-block w-2.5 h-4 bg-[#25d1f4] ml-1 align-middle animate-[blink_1s_steps(2)_infinite] shadow-[0_0_5px_#25d1f4]"></span>
                  </p>
                </div>
              </div>

              {/* Footer of Log */}
              <div className="p-3 bg-[#111718] border-t border-[#283639] flex justify-between items-center text-[10px] text-[#536b70] uppercase tracking-widest">
                <span>Mem: 64TB / 128TB</span>
                <span>CPU: 89%</span>
              </div>
            </div>
          </div>
        </main>

        {/* Bottom Status Bar */}
        <footer className="bg-[#0a0f10] border-t border-[#283639] px-6 py-3 flex flex-wrap gap-4 items-center justify-between z-40">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#25d1f4] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-[#25d1f4]"></span>
              </span>
              <span className="text-[#25d1f4] text-sm font-bold tracking-wider">1000個活躍代理人 : 已就緒</span>
            </div>
            {/* Progress Bar Mini */}
            <div className="hidden md:flex items-center gap-3 w-64">
              <div className="flex-1 h-1.5 bg-[#283639] rounded-full overflow-hidden">
                <div className="h-full bg-[#25d1f4] w-[85%] shadow-[0_0_10px_#25d1f4]"></div>
              </div>
              <span className="text-xs text-[#25d1f4] font-mono">85%</span>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs text-[#536b70] font-mono">
            <span className="hidden sm:block">SESSION_ID: 0x8F3A21</span>
            <span className="hidden sm:block">|</span>
            <span>PING: 12ms</span>
            <span className="hidden sm:block">|</span>
            <span className="text-[#9cb5ba]">ENCRYPTION: AES-256</span>
          </div>
        </footer>
      </div>
    );
  }


  return (
    <div className="min-h-screen bg-[#191022] text-white font-display overflow-hidden h-screen flex flex-col pt-[100px]">
      <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />

      <header className="flex-none flex items-center justify-between whitespace-nowrap border-b border-[#302839] px-6 py-4 bg-[#141118] z-20">
        <div className="flex items-center gap-4 text-white">
          <span className="text-sm font-medium text-gray-400">預演報告 #{simId.slice(0, 4).toUpperCase()}</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:flex gap-2">
            {/* Share Button */}
            <button
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(window.location.href);
                  // Show toast notification
                  const toast = document.createElement('div');
                  toast.className = 'fixed bottom-6 right-6 bg-green-500 text-white px-4 py-3 rounded-lg shadow-lg z-50 animate-in fade-in slide-in-from-bottom-4 flex items-center gap-2';
                  toast.innerHTML = '<span class="material-symbols-outlined text-lg">check_circle</span>連結已複製到剪貼簿！';
                  document.body.appendChild(toast);
                  setTimeout(() => toast.remove(), 3000);
                } catch (err) {
                  console.error('Failed to copy:', err);
                }
              }}
              className="flex items-center justify-center rounded-lg h-9 px-4 bg-[#7f13ec] hover:bg-[#9d4af2] transition-colors text-white text-sm font-bold shadow-[0_0_10px_rgba(127,19,236,0.5)]"
            >
              <span className="mr-2 material-symbols-outlined text-[18px]">share</span>分享報告
            </button>

            {/* Download Button */}
            <button
              onClick={async () => {
                try {
                  // Dynamic import html2canvas
                  const html2canvas = (await import('html2canvas')).default;
                  const mainContent = document.querySelector('main');
                  if (!mainContent) return;

                  // Show loading toast
                  const loadingToast = document.createElement('div');
                  loadingToast.className = 'fixed bottom-6 right-6 bg-[#302839] text-white px-4 py-3 rounded-lg shadow-lg z-50 flex items-center gap-2';
                  loadingToast.innerHTML = '<span class="material-symbols-outlined text-lg animate-spin">sync</span>正在生成報告圖片...';
                  document.body.appendChild(loadingToast);

                  const canvas = await html2canvas(mainContent as HTMLElement, {
                    backgroundColor: '#191022',
                    scale: 2,
                    useCORS: true,
                  });

                  // Download
                  const link = document.createElement('a');
                  link.download = `MIRRA_Report_${simId.slice(0, 8)}.png`;
                  link.href = canvas.toDataURL('image/png');
                  link.click();

                  // Replace with success toast
                  loadingToast.remove();
                  const successToast = document.createElement('div');
                  successToast.className = 'fixed bottom-6 right-6 bg-green-500 text-white px-4 py-3 rounded-lg shadow-lg z-50 animate-in fade-in slide-in-from-bottom-4 flex items-center gap-2';
                  successToast.innerHTML = '<span class="material-symbols-outlined text-lg">check_circle</span>報告已下載！';
                  document.body.appendChild(successToast);
                  setTimeout(() => successToast.remove(), 3000);
                } catch (err) {
                  console.error('Download failed:', err);
                }
              }}
              className="flex items-center justify-center rounded-lg h-9 w-9 bg-[#302839] hover:bg-[#473b54] text-white transition-colors"
              title="下載報告"
            >
              <span className="material-symbols-outlined text-[20px]">download</span>
            </button>
          </div>
          <div className="bg-center bg-no-repeat bg-cover rounded-full size-9 border border-[#302839]" style={{ backgroundImage: 'url("https://api.dicebear.com/7.x/avataaars/svg?seed=Alex")' }}></div>
        </div>
      </header>

      {selectedCitizen && <CitizenModal citizen={selectedCitizen} onClose={() => setSelectedCitizen(null)} />}

      <div className="flex flex-1 overflow-hidden relative">
        {/* Mobile Hamburger Button */}
        <button
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="md:hidden fixed bottom-6 left-6 z-50 flex items-center justify-center w-14 h-14 rounded-full bg-[#7f13ec] hover:bg-[#9333ea] shadow-lg shadow-purple-500/30 transition-all active:scale-95"
          aria-label="Toggle sidebar"
        >
          <span className="material-symbols-outlined text-white text-2xl">
            {isSidebarOpen ? 'close' : 'filter_list'}
          </span>
        </button>

        {/* Backdrop for mobile */}
        {isSidebarOpen && (
          <div
            className="md:hidden fixed inset-0 bg-black/60 z-30"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}

        {/* Sidebar - Horizontal Collapse */}
        <aside className={`
          flex-none flex flex-col justify-between bg-[#141118] border-r border-[#302839] overflow-y-auto z-40
          md:relative md:translate-x-0
          fixed inset-y-0 left-0 transition-all duration-300 ease-in-out
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
          ${isSidebarCollapsed ? 'w-14 p-2' : 'w-64 p-4'}
        `}>
          {/* Collapse Toggle Button */}
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className={`absolute top-4 z-50 p-1.5 rounded-lg bg-[#302839] hover:bg-[#473b54] text-gray-400 hover:text-white transition-all border border-[#473b54] shadow-lg ${isSidebarCollapsed ? 'right-2' : 'right-3'}`}
            title={isSidebarCollapsed ? "展開側欄" : "收起側欄"}
          >
            <span className={`material-symbols-outlined text-lg transition-transform duration-300 ${isSidebarCollapsed ? 'rotate-180' : ''}`}>
              chevron_left
            </span>
          </button>

          <div className={`flex flex-col gap-6 ${isSidebarCollapsed ? 'items-center' : ''}`}>
            {/* Header */}
            <div className={`${isSidebarCollapsed ? 'hidden' : ''}`}>
              <h1 className="text-white text-base font-bold uppercase tracking-wider mb-1 mt-10">人物誌篩選</h1>
              <p className="text-gray-500 text-xs">篩選 {TOTAL_POPULATION.toLocaleString()} 位 AI 市民</p>
            </div>

            {/* Collapsed Header Icon */}
            {isSidebarCollapsed && (
              <div className="mt-12 text-center">
                <span className="material-symbols-outlined text-2xl text-[#7f13ec]">filter_list</span>
              </div>
            )}

            {/* Content */}
            <div className={`flex flex-col gap-2 ${isSidebarCollapsed ? 'items-center' : ''}`}>
              {/* All Citizens Button */}
              <button className={`flex items-center rounded-lg bg-[#7f13ec]/10 text-white border border-[#7f13ec]/50 transition-all ${isSidebarCollapsed ? 'p-2.5 justify-center' : 'gap-3 px-3 py-2.5'}`} title="所有市民">
                <span className="material-symbols-outlined fill-1 text-[#7f13ec]">groups</span>
                {!isSidebarCollapsed && (
                  <div className="flex flex-col items-start"><span className="text-sm font-bold">所有市民</span><span className="text-[10px] opacity-70">{TOTAL_POPULATION} 名 AI 市民</span></div>
                )}
              </button>

              {!isSidebarCollapsed && <div className="h-px bg-[#302839] my-2"></div>}
              {!isSidebarCollapsed && <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3">原型</p>}

              {/* Persona Buttons */}
              {[{ name: '科技愛好者', bazi: '食神格', icon: 'devices', count: 342 }, { name: '精打細算型', bazi: '正財格', icon: 'savings', count: 215 }, { name: '懷疑論者', bazi: '七殺格', icon: 'sentiment_dissatisfied', count: 140 }, { name: '早期採用者', bazi: '偏財格', icon: 'rocket_launch', count: 188 }, { name: '品牌忠誠者', bazi: '正印格', icon: 'verified', count: 115 }].map((item) => (
                <button
                  key={item.name}
                  className={`flex items-center rounded-lg hover:bg-[#302839] text-[#ab9db9] group transition-colors ${isSidebarCollapsed ? 'p-2.5 justify-center' : 'justify-between gap-3 px-3 py-2'}`}
                  title={isSidebarCollapsed ? `${item.name} (${item.bazi})` : undefined}
                >
                  <div className={`flex items-center ${isSidebarCollapsed ? '' : 'gap-3'}`}>
                    <span className="material-symbols-outlined group-hover:text-[#7f13ec] transition-colors">{item.icon}</span>
                    {!isSidebarCollapsed && (
                      <div className="flex flex-col items-start gap-0.5">
                        <span className="text-sm font-medium group-hover:text-white transition-colors">{item.name}</span>
                        <span className="text-sm text-[#a855f7] font-bold tracking-wide">{item.bazi}</span>
                      </div>
                    )}
                  </div>
                  {!isSidebarCollapsed && <span className="text-xs bg-[#231b2e] px-1.5 py-0.5 rounded text-gray-500">{item.count}</span>}
                </button>
              ))}
            </div>
          </div>
        </aside>

        <main className="flex-1 overflow-y-auto bg-[#191022] p-6 md:p-10 scrollbar-hide">
          <div className="max-w-[1400px] mx-auto flex flex-col gap-8">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
              <div className="flex flex-col gap-2">
                <h1 className="text-4xl md:text-5xl font-black leading-tight tracking-[-0.033em] text-white">{data.status === 'processing' ? '專案分析中...' : '專案預演報告'}</h1>
                <p className="text-[#ab9db9] text-base md:text-lg max-w-2xl">{data.summary ? 'AI 已完成深度輿論場域預演，以下為關鍵數據與洞察報導。' : '正在整合 1,000 位 AI 市民的深度反饋與市場動態數據。'}</p>
              </div>
              <Link href="/#start" className="flex-none flex items-center justify-center rounded-lg h-12 px-6 bg-[#302839] hover:bg-[#473b54] text-white text-sm font-bold tracking-[0.015em] border border-[#473b54] transition-all shadow-lg active:scale-95">
                <span className="material-symbols-outlined mr-2 text-[20px]">play_circle</span>執行新預演
              </Link>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="col-span-1 lg:col-span-4 bg-[#1a1a1f] border border-[#302839] rounded-2xl p-6 shadow-xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-[#7f13ec]/20 rounded-full blur-[60px] -mr-16 -mt-16 pointer-events-none"></div>
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="text-[#ab9db9] text-sm font-bold uppercase tracking-wider">整體可行性</h3>
                    <div className="flex flex-col gap-1 mt-1">
                      <div className="flex items-center gap-2">
                        <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span></span>
                        <p className="text-[10px] text-purple-400 font-medium">即時推演波動中</p>
                      </div>
                    </div>
                  </div>
                  <span className={`text-xs font-bold px-2 py-1 rounded ${data.score >= 70 ? 'bg-green-500/10 text-green-400' : 'bg-amber-500/10 text-amber-400'}`}>{data.score >= 70 ? '核心目標達成' : '需進一步優化'}</span>
                </div>
                <div className="flex flex-col items-center justify-center py-4 gap-4">
                  <div className="relative size-44 md:size-48">
                    <svg className="size-full -rotate-90" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="18" cy="18" r="16" fill="none" stroke="currentColor" strokeWidth="3" className="text-[#302839]" />
                      <circle cx="18" cy="18" r="16" fill="none" stroke="currentColor" strokeWidth="3" strokeDasharray={`${data.score}, 100`} strokeLinecap="round" className="text-[#7f13ec] drop-shadow-[0_0_10px_rgba(127,19,236,0.5)] transition-all duration-1000" />
                    </svg>
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                      <span className="text-5xl md:text-6xl font-black text-white block">{data.score}</span>
                      <span className="text-sm font-medium text-gray-500">滿分 100</span>
                    </div>
                  </div>
                  <p className="text-xs text-white font-mono text-center">*分數源自下面 8 位八字代表市民的加權平均</p>
                </div>
              </div>

              <div className="col-span-1 lg:col-span-8 flex flex-col gap-6">
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                  {(() => {
                    // 動態計算：正面評價率
                    const totalComments = data.arena_comments?.length || 0;
                    const positiveComments = data.arena_comments?.filter((c: any) => c.sentiment === 'positive').length || 0;
                    const positiveRate = totalComments > 0 ? Math.round((positiveComments / totalComments) * 100) : 0;
                    const positiveLabel = positiveRate >= 70 ? '高度正面' : positiveRate >= 50 ? '中性偏正' : positiveRate >= 30 ? '中性' : '偏負面';

                    // 動態計算：參與深度（覆蓋率）
                    const coverageRate = Math.round((totalComments / TOTAL_POPULATION) * 100 * 10) / 10;

                    // 動態計算：價格敏感度（掃描評論中的價格相關關鍵詞）
                    const priceKeywords = ['貴', '價格', '價錢', '太貴', '便宜', '划算', 'CP值', 'cp值', '預算', '成本', '花費', '值得', '不值', '省錢', '促銷', '折扣', 'expensive', 'price', 'cheap', 'affordable', 'budget'];
                    const priceRelatedComments = data.arena_comments?.filter((c: any) =>
                      priceKeywords.some(keyword => (c.text || '').toLowerCase().includes(keyword.toLowerCase()))
                    ).length || 0;
                    const priceSensitivityRate = totalComments > 0 ? Math.round((priceRelatedComments / totalComments) * 100) : 0;

                    // 判斷敏感度等級與商家啟示
                    let sensitivityLevel: string;
                    let sensitivityAdvice: string;
                    let sensitivityColor: string;
                    if (priceSensitivityRate >= 40) {
                      sensitivityLevel = '高';
                      sensitivityAdvice = '建議採促銷策略';
                      sensitivityColor = 'text-rose-500';
                    } else if (priceSensitivityRate >= 20) {
                      sensitivityLevel = '中等';
                      sensitivityAdvice = '需平衡價格與價值';
                      sensitivityColor = 'text-amber-500';
                    } else {
                      sensitivityLevel = '低';
                      sensitivityAdvice = '可強調品質與價值';
                      sensitivityColor = 'text-green-500';
                    }

                    // 生成正面評價率的商家啟示
                    let positiveAdvice: string;
                    if (positiveRate >= 70) {
                      positiveAdvice = '市場反應極佳';
                    } else if (positiveRate >= 50) {
                      positiveAdvice = '可強化產品優勢';
                    } else if (positiveRate >= 30) {
                      positiveAdvice = '建議優化產品定位';
                    } else {
                      positiveAdvice = '需重新審視策略';
                    }

                    // 生成參與深度的商家啟示
                    let coverageAdvice: string;
                    if (coverageRate >= 5) {
                      coverageAdvice = '樣本充足可信';
                    } else if (coverageRate >= 1) {
                      coverageAdvice = '樣本具參考價值';
                    } else {
                      coverageAdvice = '建議擴大樣本';
                    }

                    // Dynamic Score Improvement Logic
                    const currentScore = data.score || 0;
                    const scoreGap = Math.max(0, 100 - currentScore);

                    // Assign improvement weights (Higher weight = More room to improve)
                    // Market Potential (Critical): Low->3, Mid->2, High->1
                    const w_pot = (positiveRate >= 70 ? 1 : positiveRate >= 40 ? 2 : 3) * 2.0;
                    // Confidence (Auxiliary): Low->3, Mid->2, High->1
                    const w_conf = (coverageRate >= 5 ? 1 : coverageRate >= 1 ? 2 : 3) * 1.0;
                    // Tech Monetization (Critical): Strong(Low Sense)->1, Mid->2, Weak(High Sense)->3
                    const w_tech = (sensitivityLevel === '低' ? 1 : sensitivityLevel === '中等' ? 2 : 3) * 1.5;

                    const totalWeight = w_pot + w_conf + w_tech;

                    const getBoost = (weight: number) => {
                      if (scoreGap <= 2) return '+0~1 分'; // Saturation
                      const share = (weight / totalWeight) * scoreGap;
                      // Create a realistic range around the share
                      const min = Math.max(1, Math.floor(share * 0.8));
                      const max = Math.max(min, Math.ceil(share * 1.2));
                      return `+${min}~${max} 分`;
                    };

                    const stats = [
                      {
                        label: '市場潛力',
                        value: positiveRate >= 70 ? '高' : positiveRate >= 40 ? '中' : '低',
                        sub: '「有多少人看了喜歡？」若大部分市民都給予好評，代表產品本身吸引力極強。',
                        advice: positiveRate >= 70
                          ? '💡 建議：趁勝追擊！您可以加大行銷預算來擴大這股熱潮。'
                          : positiveRate >= 40
                            ? '💡 建議：表現四平八穩。試試看強化產品的「獨家特色」，讓大家印象更深刻。'
                            : '💡 建議：市場反應冷淡。可能產品未觸及核心需求，或目標客群設定有誤，建議重新定位賣點。',
                        improvement: getBoost(w_pot),
                        icon: 'trending_up',
                        color: positiveRate >= 60 ? 'text-green-500' : 'text-amber-500'
                      },
                      {
                        label: '信心指數',
                        value: coverageRate < 1 ? `${coverageRate * 10}‰` : `${Math.min(coverageRate * 10, 99)}%`,
                        sub: '「這次調查的聲音夠大聲嗎？」願意表態的市民越多，這份報告的參考價值就越高。',
                        advice: coverageRate >= 5
                          ? '💡 建議：數據非常穩。您可以放心地根據這份報告來制定下一步策略。'
                          : coverageRate >= 1
                            ? '💡 建議：數據可參考。若想更保險，可以更改文案後再跑一次預演。'
                            : '💡 建議：目前為免費版隨機抽樣 (8‰)。若需高信度 (8%↑) 甚至 80%，請升級 Pro 版解鎖千人全量分析。',
                        improvement: coverageRate >= 5 ? '+1~2%' : coverageRate >= 1 ? '+5~8%' : '升級 Pro 版',
                        icon: 'verified',
                        color: 'text-blue-500'
                      },
                      {
                        label: '技術變現力',
                        value: sensitivityLevel === '低' ? '強' : sensitivityLevel === '中等' ? '中' : '弱',
                        sub: '「是用技術折服人，還是在拚價格？」越少人嫌貴，代表技術帶來的溢價能力越強。',
                        advice: sensitivityLevel === '低'
                          ? '💡 建議：太強了！大家不在乎錢。您可以大膽維持高價，甚至推出更貴的進階版。'
                          : sensitivityLevel === '中等'
                            ? '💡 建議：拉鋸戰中。請多強調「買了會省多少錢」或「長期價值」來說服猶豫客。'
                            : '💡 建議：難以產生技術溢價。消費者對價格敏感，建議建立「不可替代性」來自抬身價，或接受薄利多銷的策略。',
                        improvement: getBoost(w_tech),
                        icon: 'monetization_on',
                        color: sensitivityColor
                      },
                    ];

                    return stats.map((stat) => (
                      <div key={stat.label} className="bg-[#1a1a1f] border border-[#302839] rounded-xl p-5 flex flex-col justify-between hover:border-[#7f13ec]/30 transition-colors gap-3">
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`material-symbols-outlined ${stat.color} text-[20px]`}>{stat.icon}</span>
                            <span className="text-[#ab9db9] text-xs font-bold uppercase">{stat.label}</span>
                          </div>
                          <p className="text-2xl font-bold text-white">{stat.value}</p>
                          <span className="text-xs text-gray-400 block mt-1 leading-snug">{stat.sub}</span>
                        </div>
                        <div className="pt-3 border-t border-[#302839]/50 flex flex-col gap-2">
                          <p className="text-xs text-[#d8b4fe] font-medium leading-relaxed">{stat.advice}</p>
                          <div className="flex justify-end">
                            <span className="text-[10px] items-center flex gap-1 text-green-400 font-mono font-bold">
                              <span className="material-symbols-outlined text-[12px]">trending_up</span>
                              若優化可升 {stat.improvement}
                            </span>
                          </div>
                        </div>
                      </div>
                    ));
                  })()}
                </div>
                <div className="flex-1 bg-[#1a1a1f] border border-[#302839] rounded-xl p-6 flex flex-col justify-center">
                  <h3 className="text-white text-sm font-bold mb-4">購買意願轉換率</h3>
                  <div className="flex flex-col gap-4">
                    {[{ label: '絕對購買', value: 42, color: 'bg-[#7f13ec]' }, { label: '可能購買', value: 35, color: 'bg-blue-500' }, { label: '放棄', value: 23, color: 'bg-gray-600' }].map((intent) => (
                      <div key={intent.label} className="flex items-center gap-4 text-xs font-medium">
                        <div className="w-24 text-gray-400 text-right">{intent.label}</div>
                        <div className="flex-1 h-3 bg-[#302839] rounded-full overflow-hidden"><div className={`h-full ${intent.color} rounded-full`} style={{ width: `${intent.value}%` }} /></div>
                        <div className="w-10 text-right text-white font-bold">{intent.value}%</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
              {/* THE ARENA // 輿論競技場 - moved to first position */}
              <div className="xl:col-span-5 space-y-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2"><div className="w-1.5 h-6 bg-cyan-400 rounded-full animate-pulse"></div><div><h2 className="text-lg font-bold text-white tracking-widest uppercase">THE ARENA // 輿論競技場</h2><p className="text-[10px] text-gray-500 font-mono">Real-time Stream of Consciousness</p></div></div>
                  <span className="text-[10px] bg-[#302839] text-gray-400 px-2 py-1 rounded">LIVE FEED</span>
                </div>
                <div className="space-y-4 max-h-[700px] overflow-y-auto pr-2 custom-scrollbar">
                  {data.arena_comments?.map((comment, i) => {
                    const persona = comment.persona;
                    const elem = elementConfig[persona.element] || elementConfig.Fire;
                    const isPositive = comment.sentiment === 'positive';
                    return (
                      <div key={i} className={`group relative p-4 rounded-xl border transition-all duration-300 transform bg-[#1a1a1f] hover:translate-x-1 cursor-pointer ${isPositive ? 'border-l-4 border-l-green-500 border-[#302839]' : comment.sentiment === 'negative' ? 'border-l-4 border-l-rose-500 border-[#302839]' : 'border-l-4 border-l-gray-500 border-[#302839]'}`} onClick={() => setSelectedCitizen(enrichCitizenData(persona))}>
                        <div className="flex items-start gap-3">
                          <div className={`size-10 flex-none rounded-xl ${elem.bg} flex items-center justify-center text-xl shadow-lg group-hover:scale-110 transition-transform`}>{elem.icon}</div>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center justify-between mb-1">
                              <div className="flex items-center gap-2"><span className="text-xs font-bold text-white">{persona.name}</span><span className={`text-[9px] px-1.5 py-0.5 rounded-full font-bold ${elem.bg} text-white opacity-80`}>{elem.cn}</span></div>
                              <div className="flex flex-col items-end"><span className={`text-[10px] font-bold ${isPositive ? 'text-green-400' : comment.sentiment === 'negative' ? 'text-rose-400' : 'text-gray-400'}`}>{isPositive ? 'POSITIVE' : comment.sentiment === 'negative' ? 'NEGATIVE' : 'NEUTRAL'}</span><span className="text-xs font-mono text-purple-400 mt-0.5 font-bold">{comment.score} <span className="text-[9px] text-gray-600">/ 100</span></span></div>
                            </div>
                            <p className="text-sm text-gray-300 leading-relaxed italic">"{comment.text}"</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* GENESIS // 取樣邏輯 - moved to second position */}
              <div className="xl:col-span-3 space-y-6 bg-[#1a1a1f] border border-[#302839] rounded-2xl p-5 flex flex-col">
                <div className="flex items-center gap-2 mb-4"><span className="material-symbols-outlined text-[#a855f7] animate-pulse">grain</span><h3 className="text-[#a855f7] text-sm font-bold uppercase tracking-wider">GENESIS // 取樣邏輯</h3></div>
                <div className="flex flex-col items-center justify-center space-y-8 p-6">
                  <Link href="/citizens" className="relative z-10 w-full text-center group cursor-pointer block p-4 rounded-xl hover:bg-white/5 transition-all duration-300">
                    <span className="material-symbols-outlined text-4xl text-blue-400 mb-2 group-hover:text-purple-400 group-hover:scale-110 transition-all duration-300">public</span>
                    <div className="text-3xl font-black text-white group-hover:text-purple-100 transition-colors">1,000</div>
                    <div className="text-xs text-gray-400 font-bold mt-1 group-hover:text-white transition-colors">所有市民</div>
                    <div className="absolute inset-0 border border-purple-500/0 group-hover:border-purple-500/30 rounded-xl transition-all duration-300" />
                  </Link>
                  <span className="material-symbols-outlined text-gray-600 animate-bounce">keyboard_double_arrow_down</span>
                  <div className="w-full bg-[#302839]/50 rounded-lg p-4 border border-[#7f13ec]/20 text-center"><p className="text-[#a855f7] font-bold text-sm mb-1">八字邏輯推演</p><p className="text-[10px] text-gray-400">依據五行生剋與十神格局，篩選最具因果關聯之代表</p></div>
                  <span className="material-symbols-outlined text-gray-600 animate-bounce">keyboard_double_arrow_down</span>
                  <div className="text-center"><span className="material-symbols-outlined text-4xl text-[#7f13ec] mb-2">groups</span><div className="text-4xl font-black text-white text-glow">{data.arena_comments?.length || 0}</div><div className="text-xs text-gray-300 font-bold mt-1">本場深度參與 AI 市民</div></div>
                </div>
              </div>

              <div className="xl:col-span-4 space-y-6">
                <div className="bg-black/40 border border-[#7f13ec]/20 rounded-2xl p-6 relative overflow-hidden group shadow-[0_0_30px_rgba(127,19,236,0.05)]">
                  <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-[#7f13ec] to-blue-500"></div>
                  <div className="flex items-center gap-2 mb-4"><span className="material-symbols-outlined text-[#7f13ec]">auto_awesome</span><h3 className="text-xs font-bold text-[#7f13ec] tracking-[0.2em] uppercase">STRATEGIC ORACLE // 戰略神諭</h3></div>
                  <div className="font-mono text-sm leading-7 text-gray-300 min-h-[140px]">{typedSummary}<span className="inline-block w-1.5 h-4 ml-1 bg-[#7f13ec] animate-pulse align-middle"></span></div>
                </div>
                <div className="space-y-3">
                  <p className="text-[10px] font-bold text-gray-500 tracking-widest uppercase mb-1">AI 策略建議 / TACTICAL ADVICE</p>
                  {data.suggestions?.slice(0, 3).map((s, i) => (
                    <div key={i} className="bg-[#1a1a1f] border border-[#302839] rounded-xl p-4 hover:border-cyan-500/30 transition-all group flex flex-col gap-3">
                      <div className="flex items-start gap-3">
                        <div className="bg-[#231b2e] size-8 rounded-lg flex items-center justify-center text-lg shadow-inner opacity-70 group-hover:opacity-100 transition-opacity">{i === 0 ? '🎯' : i === 1 ? '💡' : '⚡'}</div>
                        <div className="min-w-0">
                          <h4 className="text-white text-sm font-bold mb-1">{s.target}</h4>
                          <p className="text-xs text-gray-200 leading-relaxed mb-2">{s.advice}</p>
                        </div>
                      </div>

                      {/* Action Steps - Boss requested detail */}
                      <div className="pl-11">
                        <p className="text-[10px] text-[#7f13ec] font-bold uppercase mb-1.5 flex items-center gap-1">
                          <span className="material-symbols-outlined text-[10px]">playlist_add_check</span>
                          執行步驟
                        </p>
                        <ul className="space-y-1.5">
                          {s.action_plan?.map((step: string, j: number) => (
                            <li key={j} className="flex items-start gap-2 text-[11px] text-gray-300 hover:text-white transition-colors">
                              <span className="text-cyan-500/50 mt-0.5">›</span>
                              <span>{step}</span>
                            </li>
                          )) || <li className="text-[10px] text-gray-600 italic">正在生成具體執行方案...</li>}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>

      <style jsx global>{`
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #141118; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #302839; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #473b54; }

        @keyframes flicker {
          0%, 19.9%, 22%, 62.9%, 64%, 64.9%, 70%, 100% { opacity: 1; text-shadow: 0 0 10px rgba(216,180,254,0.8); }
          20%, 21.9%, 63%, 63.9%, 65%, 69.9% { opacity: 0.3; text-shadow: none; }
        }
        @keyframes typing {
          0% { width: 0 }
          80% { width: 100% }
          90% { width: 100% }
          100% { width: 0 } /* Reset to loop */
        }
        @keyframes blink {
          50% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}