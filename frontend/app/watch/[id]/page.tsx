"use client"

import { useState, useEffect, useRef } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"

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
  // Real Bazi Data
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

// ===== Element Config (含個性描述) =====
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

// ===== Mock Bazi Profile =====
const mockBaziProfile: BaziProfile = {
  day_master: "丙火",
  day_master_element: "Fire",
  strength: "身強",
  structure: "傷官格",
  favorable: ["木", "火"],
  unfavorable: ["金", "水"]
}

interface SimulationData {
  status: string
  score: number
  summary: string
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
  }>
  result?: { summary: string }
  // Analysis Fields
  intent?: any
  suggestions?: Array<{ target: string; advice: string; execution_plan: string[]; score_improvement?: string }>
  objections?: Array<{ reason: string; percentage: string }>
  buying_intent?: string
}
interface EnrichedPersona extends Persona {
  fullBirthday?: string
  luckCycle?: string // 10年大運 (Summary text)
  detailedTrait?: string
  displayAge?: string
}

const enrichCitizenData = (p: Persona): EnrichedPersona => {
  // 1. Prefer Real Data if available
  let dm = p.day_master
  if ((!dm || dm === "未知") && !p.four_pillars) {
    // Logic for inference if completely missing
    const dmMap: Record<string, string[]> = {
      "Fire": ["丙火", "丁火"],
      "Water": ["壬水", "癸水"],
      "Metal": ["庚金", "辛金"],
      "Wood": ["甲木", "乙木"],
      "Earth": ["戊土", "己土"]
    }
    const options = dmMap[p.element] || ["甲木"]
    dm = options[Math.floor(Math.random() * options.length)]
  }

  // 2. Format Birthday (Real or Generated)
  let fullBirthday = ""
  if (p.birth_year && p.birth_month && p.birth_day) {
    fullBirthday = `${p.birth_year}年${p.birth_month}月${p.birth_day}日`
    if (p.birth_shichen) fullBirthday += ` ${p.birth_shichen}`
  } else {
    // Inference fallback
    let age = parseInt(p.age)
    if (isNaN(age)) age = Math.floor(Math.random() * (45 - 20 + 1)) + 20
    const currentYear = new Date().getFullYear()
    const birthYear = currentYear - age
    const month = Math.floor(Math.random() * 12) + 1
    const day = Math.floor(Math.random() * 28) + 1
    fullBirthday = `${birthYear}年${month}月${day}日 (推算)`
  }

  // 3. luckCycle text (Real or Generated)
  let luckCycle = ""
  if (p.current_luck && p.current_luck.description) {
    luckCycle = p.current_luck.description
  } else {
    // Inference fallback
    const luckMap: Record<string, string[]> = {
      "正官格": ["目前行運至『東方木地』，官星得地，事業運勢穩步上升，利於爭取升遷或承接重任。天干透出印星，代表長輩貴人提攜。", "行運『財星』流年，財官相生，雖然工作壓力較大，但實質回報豐厚。需注意職場人際關係的和諧。"],
      "七殺格": ["大運走至『食神制殺』之鄉，原本剛烈的煞氣轉化為權威，極具開創力。適合大刀闊斧進行改革或創業。", "行運『印綬』以為化解，心性轉趨沉穩，對於局勢判斷更為精準。過去的挑戰此刻皆成為養分。"],
      "正財格": ["目前行運『食傷生財』，財源廣進，對於投資理財的敏銳度極高。適合評估高價值資產或進行長期佈局。", "行運『官殺』護財，既有財富累積，亦有社會地位提升。生活品質優渥，重視實際物質享受。"],
      "偏財格": ["大運進入『比劫奪財』之運限，需留意財務波動，但也代表有大筆資金流動的機會。適合短線操作或高風險高報酬的投資。", "行運『食神』，財氣通門戶，交際應酬增多，人脈即錢脈。在社交場合中容易獲得意外的商業資訊。"],
      "傷官格": ["行運『財鄉』，傷官生財，才華變現的最佳時機。創意源源不絕，適合從事設計、行銷等需要大量腦力的工作。", "大運遇『印星』，傷官配印，貴不可言。狂放的才華得到體制的認可，名利雙收。"],
      "食神格": ["目前行運『財地』，食神生正財，衣食無憂，心寬體胖。生活悠閒愜意，重視品味與生活質感。", "行運『比劫』，食神洩秀，人緣極佳，在團體中如魚得水。適合透過口碑行銷或社群影響力獲利。"],
    }
    const defaultLuck = ["目前行運平穩，五行流通有情。適合保守經營以及累積實力。", "流年運勢助旺日主，精氣神飽滿，對於新事物的接受度高。"]
    const luckOptions = luckMap[p.pattern] || defaultLuck
    luckCycle = luckOptions[Math.floor(Math.random() * luckOptions.length)]
  }

  // 4. Detailed Trait Analysis (Reuse map)
  const traitMap: Record<string, string> = {
    "Fire": "熱情洋溢，行動力強，但有時過於急躁。直覺敏銳，善於激勵他人。",
    "Water": "聰明機智，適應力強，心思深沉。善於觀察局勢，但有時會想太多。",
    "Metal": "果斷剛毅，講求原則，重視效率與SOP。對於品質有極高的要求，不輕易妥協。",
    "Wood": "仁慈博愛，富有創意，具備良好的生長性與彈性。善於規劃，但偶爾優柔寡斷。",
    "Earth": "誠信穩重，包容力強，是團隊中的定海神針。重視承諾，但有時不知變通。"
  }
  const detailedTrait = traitMap[p.element] || "性格均衡，適應力良好。"

  // 5. Decision Logic (Fix Placeholder)
  let decisionLogic = p.decision_logic;
  if (!decisionLogic || decisionLogic.includes("根據八字格局特質分析")) {
    const dm = getDecisionModel(p.pattern);
    decisionLogic = `【${dm.title}】${dm.desc}`;
  }

  // 6. Generate Mock Timeline if missing
  let luck_timeline = p.luck_timeline || [];
  if (luck_timeline.length === 0) {
    const startAge = Math.floor(Math.random() * 8) + 2;
    const pillars = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉", "甲戌", "乙亥"];
    const startIdx = Math.floor(Math.random() * 5); // Random starting pillar
    const descriptions = [
      "少年運勢，學業順利，得長輩疼愛。",
      "初入社會，需磨練心性，財運平平。",
      "事業起步，貴人多助，有升遷機會。",
      "財運亨通，投資獲利，亦有桃花運。",
      "壓力較大，需注意健康與職場人際。",
      "穩步發展，權力與名聲雙收。",
      "財官雙美，享有一定的社會地位。",
      "晚運安康，含飴弄孫，生活優渥。"
    ];

    for (let i = 0; i < 8; i++) {
      const pAge = startAge + (i * 10);
      luck_timeline.push({
        age_start: pAge,
        age_end: pAge + 9,
        name: pillars[(startIdx + i) % pillars.length] + "運",
        description: descriptions[i % descriptions.length]
      });
    }
  }

  // 7. Fix Favorable Elements
  let favorable = p.favorable;
  if (!favorable || favorable.length === 0) {
    const allElements = ["Wood", "Fire", "Earth", "Metal", "Water"];
    const count = Math.random() > 0.5 ? 2 : 1;
    const shuffled = allElements.sort(() => 0.5 - Math.random());
    favorable = shuffled.slice(0, count);
  }

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
    strength: p.strength || (Math.random() > 0.5 ? "身強" : "身弱")
  }
}

// ===== LOCAL MODAL COMPONENT (Collapsible) =====
function CitizenModal({ citizen, onClose }: { citizen: EnrichedPersona; onClose: () => void }) {
  if (!citizen) return null;

  // State for toggling full view
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in fade-in duration-200" onClick={onClose}>
      <div className="relative bg-slate-900 border border-purple-500/30 rounded-3xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl shadow-purple-900/50" onClick={(e) => e.stopPropagation()}>

        {/* Header (Fixed) */}
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
              <div className="flex items-center gap-3 mt-2 text-sm">
                <span className="bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30 font-bold">
                  {citizen.occupation || 'AI Citizen'}
                </span>
                <span className="text-slate-400">•</span>
                <span className="text-slate-300 font-medium">{citizen.displayAge || citizen.age} 歲</span>
                <span className="text-slate-400">•</span>
                <span className="text-slate-400">{citizen.location || 'Taiwan'}</span>
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
              {citizen.detailedTrait}
            </div>
          </section>

          {/* 2. Key Metrics Grid (Always Visible) */}
          <section className="grid grid-cols-2 gap-4">
            {/* Structure */}
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">命理格局</div>
              <div className="text-xl font-black text-white">{citizen.pattern}</div>
            </div>
            {/* Strength */}
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">能量強弱</div>
              <div className="text-xl font-black text-white">{citizen.strength || "中和"}</div>
            </div>
            {/* Favorable Elements */}
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
            {/* Personality */}
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">性格標籤</div>
              <div className="text-xl font-black text-amber-400 truncate">{citizen.trait?.split(',')[0] || "多元性格"}</div>
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
                <div className="p-5 rounded-2xl bg-slate-800/30 border border-cyan-500/20 text-slate-200 leading-relaxed text-sm">
                  {citizen.decision_logic}
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

              {/* 5. Timeline */}
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
                  {(!citizen.luck_timeline || citizen.luck_timeline.length === 0) && (
                    <div className="text-slate-500 text-center text-sm py-4">無歷史時間軸數據</div>
                  )}
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

export default function WatchPage() {
  const params = useParams()
  const simId = params.id as string
  const [data, setData] = useState<SimulationData | null>(null)
  const [typedSummary, setTypedSummary] = useState("")
  const [showTooltip, setShowTooltip] = useState(false)
  const [showStreamTooltip, setShowStreamTooltip] = useState(false)
  const [error, setError] = useState("")
  const [selectedCitizen, setSelectedCitizen] = useState<EnrichedPersona | null>(null)

  // Constants
  const TOTAL_POPULATION = 1000
  // @ts-ignore
  const SAMPLE_SIZE = data?.genesis?.sample_size || data?.simulation_metadata?.sample_size || 30

  useEffect(() => {
    const fetchData = async () => {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000)

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        const res = await fetch(`${apiUrl}/simulation/${simId}`, { signal: controller.signal })
        clearTimeout(timeoutId)

        if (res.ok) {
          const json = await res.json()
          if (json) {
            setData(json)
            setError("")
          }
        } else {
          throw new Error(`HTTP Error: ${res.status}`)
        }
      } catch (err: any) {
        clearTimeout(timeoutId)
        console.error("Connection Failed:", err)
        if (err.name === 'AbortError') {
          setError("Connection Timeout (Backend not responding)")
        } else {
          setError(err.message || "Connection Failed")
        }
      }
    }
    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [simId])

  const lastSummaryRef = useRef("")

  useEffect(() => {
    if (data?.summary && data.status !== "error") {
      if (data.summary === lastSummaryRef.current) return
      lastSummaryRef.current = data.summary
      setTypedSummary("")
      let i = 0
      const timer = setInterval(() => {
        i++
        if (i <= data.summary.length) {
          setTypedSummary(data.summary.slice(0, i))
        } else {
          clearInterval(timer)
        }
      }, 10)
      return () => clearInterval(timer)
    }
  }, [data?.summary, data?.status])

  const loadingMessages = [
    "Initializing Genesis Engine / 啟動創世紀引擎...",
    "Generating 1000+ AI Citizens / 生成 AI 虛擬市民...",
    "Calculating Purchase Intent / 計算購買意圖...",
    "Reading Bazi Parameters / 讀取八字參數...",
    "Building Opinion Model / 建構輿論模型...",
  ]
  const [loadingMsgIndex, setLoadingMsgIndex] = useState(0)

  useEffect(() => {
    const msgTimer = setInterval(() => {
      setLoadingMsgIndex(prev => (prev + 1) % loadingMessages.length)
    }, 1500)
    return () => clearInterval(msgTimer)
  }, [])

  const getScoreStyle = () => {
    if (!data) return { color: "text-slate-500", glow: "", ring: "ring-slate-500/30" }
    if (data.score >= 70) return { color: "text-emerald-400", glow: "drop-shadow-[0_0_40px_rgba(52,211,153,0.9)]", ring: "ring-emerald-500/50" }
    if (data.score < 50) return { color: "text-rose-500", glow: "drop-shadow-[0_0_40px_rgba(244,63,94,0.9)]", ring: "ring-rose-500/50" }
    return { color: "text-amber-400", glow: "drop-shadow-[0_0_40px_rgba(251,191,36,0.9)]", ring: "ring-amber-500/50" }
  }

  if (error && !data) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center font-mono text-red-500 p-6 text-center">
        <h1 className="text-3xl font-bold mb-4">⚠️ CONNECTION ERROR</h1>
        <p className="text-xl mb-6">{error}</p>
        <p className="text-slate-400 text-sm">Please check your internet connection or try again later.</p>
        <p className="text-slate-500 text-xs mt-4">Backend URL: {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}</p>
      </div>
    )
  }

  if (!data || data.status === "processing") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center font-mono relative overflow-hidden">
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(rgba(6,182,212,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(6,182,212,0.3) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>
        </div>
        <div className="text-center relative z-10 max-w-lg px-6">
          <div className="relative w-40 h-40 mx-auto mb-10">
            <div className="absolute inset-0 border-2 border-cyan-500/20 rounded-full"></div>
            <div className="absolute inset-0 border-2 border-transparent border-t-cyan-400 border-r-cyan-400 rounded-full animate-spin"></div>
            <div className="absolute inset-4 border-2 border-transparent border-b-purple-400 border-l-purple-400 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '2s' }}></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-5xl drop-shadow-[0_0_20px_rgba(6,182,212,0.8)]">🧬</span>
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-black tracking-wider text-white mb-2">
            MIRRA WAR ROOM
          </h1>
          <div className="text-cyan-400 text-lg mb-1">鏡界戰情室</div>
          <div className="text-slate-500 text-xs tracking-widest mb-10">Parallel Reality Simulation Engine / 平行時空模擬引擎</div>
          <div className="h-8 mb-4">
            <div className="text-slate-300 text-sm animate-pulse">{loadingMessages[loadingMsgIndex]}</div>
          </div>
          <div className="text-amber-400/80 text-xs mb-6 flex items-center justify-center gap-2">
            <span>⏱️</span>
            <span>預估等待時間 / Estimated wait: 30秒到1分鐘</span>
          </div>
          <div className="flex justify-center gap-2">
            {[0, 1, 2, 3, 4].map(i => (
              <div key={i} className={`w-2.5 h-2.5 rounded-full transition-all duration-300 ${i === loadingMsgIndex % 5 ? 'bg-cyan-400 scale-125 shadow-lg shadow-cyan-400/50' : 'bg-slate-700'}`}></div>
            ))}
          </div>
          {error && <div className="mt-4 text-red-400 text-xs">Retrying... ({error})</div>}
        </div>
      </div>
    )
  }

  const scoreStyle = getScoreStyle()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-200 font-mono">
      {/* ===== Grid Background ===== */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03]">
        <div className="absolute inset-0" style={{
          backgroundImage: 'linear-gradient(rgba(6,182,212,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(6,182,212,0.5) 1px, transparent 1px)',
          backgroundSize: '60px 60px'
        }}></div>
      </div>

      {/* Citizen Detail Modal - Comprehensive V2 (Collapsible) */}
      {selectedCitizen && (
        <CitizenModal citizen={selectedCitizen} onClose={() => setSelectedCitizen(null)} />
      )}

      {/* ===== 1. WAR ROOM HEADER ===== */}
      <header className="relative z-10 border-b border-cyan-500/30 bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            {/* Left: Logo & Title */}
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 relative rounded-xl overflow-hidden shadow-lg shadow-cyan-500/40 ring-2 ring-cyan-400/30 bg-slate-900">
                <img src="/mirra-logo-new.jpg" alt="MIRRA Logo" className="w-full h-full object-cover" />
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-widest flex items-center gap-2">
                  戰情室 <span className="text-cyan-400">//</span> MIRRA WAR ROOM
                </h1>
                <div className="text-xs text-slate-500 tracking-[0.2em] uppercase">
                  Market Intelligence & Reality Rendering Agent
                </div>
              </div>
            </div>

            {/* Right: Status & Meta */}
            <div className="flex items-center gap-6">
              {/* Status Badge */}
              <div className="flex flex-col items-end">
                <div className={`px-3 py-1 rounded-full text-xs font-bold border ${data?.status === 'processing'
                  ? 'bg-amber-500/20 border-amber-500/50 text-amber-400 animate-pulse'
                  : 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400'
                  }`}>
                  {data?.status === 'processing' ? 'PROCESSING' : 'SYSTEM ONLINE'}
                </div>
              </div>

              {/* Simulation ID */}
              <div className="text-right hidden md:block">
                <div className="text-[10px] text-slate-500 uppercase">Simulation ID</div>
                <div className="text-xs font-mono text-cyan-400">{simId.slice(0, 8)}...</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* ===== MAIN DASHBOARD GRID ===== */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex flex-col xl:flex-row gap-6">

          {/* ===== 【左欄】GENESIS 創世紀與取樣邏輯 ===== */}
          <div className="order-3 xl:order-1 w-full xl:w-[320px] xl:flex-shrink-0 space-y-5">
            {/* Population Funnel */}
            <div className="border border-purple-500/40 bg-slate-900/80 backdrop-blur-md rounded-2xl overflow-hidden">
              <div className="px-5 py-3 bg-gradient-to-r from-purple-900/30 to-transparent border-b border-purple-500/20">
                <div className="text-xs font-bold text-purple-400 tracking-widest uppercase">
                  🧬 GENESIS // 創世紀
                </div>
              </div>

              <div className="p-5">
                {/* A: The Macroverse */}
                <div className="text-center mb-4">
                  <div className="text-4xl mb-2">🌐</div>
                  <div className="text-3xl font-black text-white">{TOTAL_POPULATION.toLocaleString()}</div>
                  <div className="text-xs text-purple-400 uppercase tracking-wider">Total Citizens / AI 市民總數</div>
                  <div className="text-[10px] text-slate-500 mt-1">DATABASE / 永久居民</div>
                  {/* 市民庫連結 */}
                  <Link
                    href={`/citizens?returnTo=/watch/${simId}`}
                    className="inline-block mt-3 px-4 py-2 bg-purple-600/30 border border-purple-500/50 rounded-lg text-xs text-purple-300 hover:bg-purple-600/50 hover:border-purple-400 transition-all"
                  >
                    👁️ 查看完整市民庫 / View All Citizens →
                  </Link>
                </div>

                {/* Arrow Down */}
                <div className="flex justify-center my-3">
                  <div className="text-2xl text-purple-500 animate-bounce">⬇️</div>
                </div>

                {/* B: The Filter */}
                <div
                  className="text-center mb-3 p-3 bg-slate-800/50 rounded-xl border border-slate-700/50 cursor-help relative"
                  onMouseEnter={() => setShowTooltip(true)}
                  onMouseLeave={() => setShowTooltip(false)}
                >
                  <div className="text-xs text-cyan-300 font-bold">Random Sampling for Qualitative Depth</div>
                  <div className="text-[10px] text-slate-500">隨機深度取樣</div>
                  <div className="text-[10px] text-slate-600 mt-1">ⓘ Hover for details / 懸停查看詳情</div>
                  {/* Tooltip */}
                  {showTooltip && (
                    <div className="absolute left-0 right-0 top-full mt-2 p-3 bg-slate-800 border border-cyan-500/30 rounded-lg text-left z-20 shadow-xl">
                      <div className="text-xs text-cyan-300 leading-relaxed">
                        為了模擬真實輿論並確保分析深度，我們從母體中隨機抽選代表進行深度訪談式模擬。
                      </div>
                      <div className="text-[10px] text-slate-500 mt-2">
                        To simulate real opinions with analytical depth, we randomly select representatives for in-depth interview simulation.
                      </div>
                    </div>
                  )}
                </div>

                {/* Arrow Down */}
                <div className="flex justify-center my-3">
                  <div className="text-2xl text-purple-500 animate-bounce" style={{ animationDelay: '0.2s' }}>⬇️</div>
                </div>

                {/* C: The Representatives */}
                <div className="text-center mb-4 p-4 bg-gradient-to-br from-purple-900/30 to-slate-900/50 rounded-xl border border-purple-500/30">
                  <div className="text-3xl mb-2">👥</div>
                  <div className="text-4xl font-black text-purple-300">{SAMPLE_SIZE}</div>
                  <div className="text-xs text-purple-400 uppercase tracking-wider">Active Agents / 本場參與代表</div>
                </div>
              </div>

              {/* Persona Cards */}
              <div className="border border-purple-500/30 bg-slate-900/80 backdrop-blur-md rounded-2xl overflow-hidden">
                <div className="px-5 py-3 border-b border-purple-500/20">
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest">
                    AI Citizen Profiles / 市民畫像
                  </div>
                </div>
                <div className="p-3 space-y-2 max-h-[300px] overflow-y-auto custom-scrollbar">
                  {data.genesis.personas?.map((p, i) => {
                    const elem = elementConfig[p.element] || elementConfig.Fire
                    return (
                      <div key={i}
                        className="group bg-slate-800/40 border border-slate-700/30 rounded-lg p-2 hover:bg-slate-800 hover:border-purple-500/40 transition-all cursor-pointer flex items-center gap-3"
                        onClick={() => setSelectedCitizen(enrichCitizenData(p))}
                      >
                        {/* Icon */}
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center bg-slate-900 shadow-inner text-lg`}>
                          {elem.icon}
                        </div>

                        {/* Info Wrapper */}
                        <div className="flex-1 min-w-0">
                          {/* Top: Name & Code */}
                          <div className="flex justify-between items-center mb-0.5">
                            <div className="text-xs font-bold text-slate-200 truncate">
                              {p.name || `Agent #${String(i + 1).padStart(3, '0')}`}
                            </div>
                            <div className="text-[10px] text-slate-500 font-mono">
                              #{String(i + 1).padStart(2, '0')}
                            </div>
                          </div>

                          {/* Bottom: Bazi & Location */}
                          <div className="flex justify-between items-center text-[10px]">
                            <div className={`flex items-center gap-1 ${elem.color} opacity-80`}>
                              <span>{p.element}</span>
                              <span className="text-slate-600">/</span>
                              <span>{p.pattern}</span>
                            </div>
                            <div className="text-slate-500 truncate max-w-[80px]">
                              {p.location?.split(',')[0]}
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                  {(!data.genesis.personas || data.genesis.personas.length === 0) && (
                    <div className="text-slate-600 text-xs text-center py-6">
                      <div className="text-2xl mb-2">👥</div>
                      Generating citizens... / 生成市民中...
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* ===== 【中欄】THE ARENA 輿論競技場 (Chat Stream) ===== */}
          <div className="order-2 xl:order-2 flex-grow min-w-0 space-y-5">
            {/* Header: Stream of Consciousness */}
            <div className="flex items-center gap-3 mb-2">
              <div className="w-2 h-8 bg-cyan-500 rounded-full animate-pulse"></div>
              <div>
                <h2 className="text-xl font-bold text-white tracking-widest uppercase flex items-center gap-2">
                  THE ARENA <span className="text-slate-600">|</span> 輿論競技場
                  {/* Info Icon with Tooltip */}
                  <div
                    className="relative group cursor-help ml-2"
                    onMouseEnter={() => setShowStreamTooltip(true)}
                    onMouseLeave={() => setShowStreamTooltip(false)}
                  >
                    <span className="text-slate-500 hover:text-cyan-400 transition-colors text-sm">ⓘ</span>
                    {showStreamTooltip && (
                      <div className="absolute left-0 bottom-full mb-2 w-64 p-3 bg-slate-900/95 border border-cyan-500/30 rounded-lg text-xs text-slate-300 shadow-xl z-30">
                        <div className="font-bold text-cyan-400 mb-1">Focus Group Stream</div>
                        <div>
                          即使模擬使用了 1000 位市民的數據，此處僅即時展示其中 <span className="text-white font-bold">5-8 位焦點小組代表</span> 的即時思考流，以方便閱讀。
                        </div>
                      </div>
                    )}
                  </div>
                </h2>
                <div className="text-xs text-slate-500">Real-time Consumer Consciousness Stream</div>
              </div>
            </div>

            {/* Chat Container */}
            <div className="space-y-4">
              {data.arena_comments?.map((comment, i) => {
                const persona = comment.persona
                const elem = elementConfig[persona.element] || elementConfig.Fire
                const sentimentColor = comment.sentiment === 'positive' ? 'border-l-4 border-l-emerald-500 bg-emerald-950/20'
                  : comment.sentiment === 'negative' ? 'border-l-4 border-l-rose-500 bg-rose-950/20'
                    : 'border-l-4 border-l-slate-500 bg-slate-900/40' // Neutral

                return (
                  <div key={i}
                    className={`p-4 rounded-r-xl border border-slate-700/50 backdrop-blur-sm ${sentimentColor} transition-all hover:translate-x-1 cursor-pointer hover:shadow-lg`}
                    onClick={() => {
                      // Smart Hydration: Try to find full data in genesis list
                      let fullPersona = persona
                      if (data.genesis?.personas) {
                        const match = data.genesis.personas.find(p => p.name === persona.name)
                        if (match) {
                          // Merge Strategy: Use genesis data as base, overlay comment specific
                          fullPersona = {
                            ...match,
                            ...persona,
                            age: match.age || persona.age,
                            day_master: match.day_master || persona.day_master,
                            trait: match.trait || persona.trait,
                            strength: match.strength || persona.strength,
                            favorable: match.favorable || persona.favorable
                          }
                        }
                      }
                      setSelectedCitizen(enrichCitizenData(fullPersona))
                    }}
                  >
                    <div className="flex items-start gap-4">
                      {/* Avatar */}
                      <div className={`relative w-10 h-10 flex-shrink-0 rounded-lg ${elem.bg} flex items-center justify-center text-lg border border-slate-600 shadow-lg`}>
                        {elem.icon}
                        <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-slate-900 rounded-full flex items-center justify-center text-[10px] border border-slate-700">
                          {comment.sentiment === 'positive' ? '👍' : comment.sentiment === 'negative' ? '👎' : '😐'}
                        </div>
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-center mb-1">
                          <div className="flex items-center gap-2">
                            <span className={`font-bold text-sm ${elem.color}`}>{persona.name || 'Unknown Agent'}</span>
                            <span className="text-[10px] text-slate-500 px-1.5 py-0.5 bg-slate-800 rounded">{persona.element}行 / {persona.pattern}</span>
                            {/* Bazi Identity Badge */}
                            <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full border bg-slate-900/80 text-[10px] ${comment.sentiment === 'positive' ? 'border-emerald-500/30 text-emerald-300'
                              : comment.sentiment === 'negative' ? 'border-rose-500/30 text-rose-300'
                                : 'border-amber-500/30 text-amber-300'
                              }`}>
                              <span>{elem.icon}</span>
                              <span className="font-mono">{elem.cn}</span>
                              <span className="text-slate-600">|</span>
                              <span>{persona.pattern}</span>
                            </div>
                          </div>
                          <div className="text-[10px] text-slate-600 font-mono">
                            {/* <span className="hidden sm:inline">ID:</span> {persona.id?.slice(0, 4)} */}
                            {comment.sentiment.toUpperCase()}
                          </div>
                        </div>
                        <div className="text-slate-200 text-sm leading-relaxed">{comment.text}</div>
                      </div>
                    </div>
                  </div>
                )
              })}
              {(!data.arena_comments || data.arena_comments.length === 0) && (
                <div className="text-center py-16 text-slate-600">
                  <div className="text-5xl mb-4">💬</div>
                  <div className="text-sm">Awaiting opinion data... / 等待輿論數據...</div>
                </div>
              )}
            </div>
          </div>

          {/* ===== 【右欄】ORACLE 戰略神諭 (Dashboard & Insights) ===== */}
          <div className="order-1 xl:order-3 w-full xl:w-[360px] xl:flex-shrink-0 space-y-6">

            {/* 1. Cyberpunk Oracle Dashboard (Holographic HUD) */}
            <div className="bg-black/40 border border-white/10 rounded-xl p-6 shadow-[0_0_30px_rgba(255,255,255,0.05)] relative overflow-hidden group">
              {/* Background Grid */}
              <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(circle, #333 1px, transparent 1px)', backgroundSize: '10px 10px' }}></div>

              <div className="relative z-10 flex flex-col items-center">
                <div className="text-xs text-slate-500 tracking-[0.3em] mb-4 uppercase">Purchase Intent Score</div>

                {/* Donut Gauge Container */}
                <div className="relative w-48 h-48 flex items-center justify-center">
                  {/* Outer Ring (Static) */}
                  <div className="absolute inset-0 rounded-full border border-white/5"></div>
                  {/* Inner Ring (Static) */}
                  <div className="absolute inset-4 rounded-full border border-white/5"></div>

                  {/* SVG Gauge */}
                  <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 100 100">
                    {/* Track */}
                    <circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke="rgba(255,255,255,0.1)"
                      strokeWidth="2" // Thinner track
                      strokeDasharray="283"
                      strokeDashoffset="70" // Leave gap at bottom (270 deg)
                      strokeLinecap="round"
                    />
                    {/* Progress Bar */}
                    <circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke={data.score < 40 ? '#f43f5e' : data.score < 70 ? '#fbbf24' : '#34d399'}
                      strokeWidth="4" // Thicker progress
                      strokeDasharray="283"
                      strokeDashoffset={283 - (283 * (data.score * 0.75) / 100)} // Scale to 270 deg (0.75)
                      strokeLinecap="round"
                      className={`transition-all duration-1000 ease-out ${data.score < 40 ? 'drop-shadow-[0_0_10px_rgba(244,63,94,0.8)]' : data.score < 70 ? 'drop-shadow-[0_0_10px_rgba(251,191,36,0.8)]' : 'drop-shadow-[0_0_10px_rgba(52,211,153,0.8)]'}`}
                    />
                  </svg>

                  {/* Center Score */}
                  <div className="absolute flex flex-col items-center">
                    <span className={`text-6xl font-black font-mono tracking-tighter ${scoreStyle.color} drop-shadow-[0_0_20px_rgba(255,255,255,0.3)]`}>
                      {data.score}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono mt-[-5px]">/ 100</span>
                  </div>
                </div>

                {/* Conclusion Label */}
                <div className={`mt-4 px-4 py-1 rounded-full border bg-white/5 backdrop-blur-sm text-xs font-bold tracking-wider ${scoreStyle.color} ${scoreStyle.ring.replace('ring-', 'border-')}`}>
                  [ {data.intent || 'ANALYZING...'} ]
                </div>
              </div>
            </div>

            {/* 2. Strategic Insight (Typewriter) */}
            <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-5 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-purple-500 to-cyan-500"></div>
              <div className="text-[10px] font-bold text-slate-500 mb-3 tracking-widest uppercase">
                戰略洞察 STRATEGIC INSIGHT
              </div>
              <div className="font-mono text-sm leading-7 text-slate-300 min-h-[100px]">
                {typedSummary}
                <span className="inline-block w-1.5 h-4 ml-1 bg-cyan-400 animate-pulse align-middle"></span>
              </div>
            </div>

            {/* 3. Actionable Suggestions */}
            <div className="space-y-3">
              <div className="text-[10px] font-bold text-slate-500 tracking-widest uppercase mb-1">
                AI 策略建議 / TACTICAL ADVICE
              </div>
              {data.suggestions?.slice(0, 3).map((s, i) => (
                <div key={i} className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-3 hover:border-cyan-500/30 transition-colors group">
                  <div className="flex items-start gap-3">
                    <div className="text-xl opacity-50 group-hover:opacity-100 transition-opacity">
                      {i === 0 ? '🎯' : i === 1 ? '💡' : '⚡'}
                    </div>
                    <div>
                      <div className="text-white text-base font-bold mb-1">{s.target}</div>
                      <div className="text-slate-400 text-sm leading-relaxed">{s.advice}</div>

                      {/* Execution Plan (New) */}
                      {s.execution_plan && s.execution_plan.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-slate-700/30">
                          {s.execution_plan.slice(0, 2).map((step, idx) => (
                            <div key={idx} className="text-sm text-white flex gap-1.5 mb-1">
                              <span className="text-cyan-400 font-bold">{idx + 1}.</span>
                              <span>{step}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Score Impact (New) */}
                      {s.score_improvement && (
                        <div className="mt-2 text-[10px]">
                          <span className="bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded border border-emerald-500/20">
                            {s.score_improvement}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* 4. Objection Analysis */}
            <div className="bg-black/20 border border-rose-500/20 rounded-xl p-4">
              <div className="text-[10px] font-bold text-rose-400 tracking-widest uppercase mb-3 flex items-center gap-2">
                <span>⚠️</span> RISK FACTORS / 抗性分析
              </div>
              <div className="space-y-3">
                {data.objections?.slice(0, 2).map((obj, i) => (
                  <div key={i}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-rose-100">{obj.reason}</span>
                      <span className="text-rose-400 font-mono">{obj.percentage}%</span>
                    </div>
                    <div className="h-1 bg-rose-900/30 rounded-full overflow-hidden">
                      <div className="h-full bg-rose-500/50 rounded-full" style={{ width: `${obj.percentage}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      </main>

      {/* ===== FOOTER ===== */}
      <footer className="relative z-10 mt-8 text-center text-xs text-slate-600 border-t border-slate-800 py-4">
        MIRRA WAR ROOM 鏡界戰情室 • AI Market Research Intelligence • Powered by Bazi Engine v3.0
      </footer>

      {/* Custom Scrollbar */}
      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: rgba(30, 41, 59, 0.5); border-radius: 2px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(6, 182, 212, 0.3); border-radius: 2px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(6, 182, 212, 0.5); }
      `}</style>
    </div>
  )
}