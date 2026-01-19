"use client"

import { useState, useEffect, useRef } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { motion } from "framer-motion"
import RefineCopyPanel from "@/app/components/RefineCopyPanel"
import MethodologyModal from "@/app/components/MethodologyModal"
import dynamic from "next/dynamic"

const PDFDownloadLink = dynamic(
  () => import("@react-pdf/renderer").then((mod) => mod.PDFDownloadLink),
  {
    ssr: false,
    loading: () => <span className="text-xs text-slate-500">準備中...</span>,
  }
)
import SimulationReportPDF from "@/app/components/pdf/SimulationReportPDF"

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

// ===== Methodology Sidecar Types (New) =====
interface MethodologyData {
  framework: string
  valid_until: string
  entropy_warning: string
  confidence_interval: string
  next_step: {
    action: "Scale" | "Pivot" | "Restart"
    label: string
    style: string
    desc: string
  }
  drivers_summary: string
}

interface SimulationData {
  status: string
  score: number
  summary: string
  productName?: string  // Legacy support
  product_name?: string // Standard backend field
  price?: string | number // Standard backend field
  description?: string // Standard backend field
  market_prices?: {
    success: boolean
    min_price: number
    max_price: number
    avg_price: number
    currency: string
    sources_count: number
    prices: Array<{ source: string; price: number; title: string }>
    market_insight?: string
  }
  genesis: {
    sample_size: number
    personas: Persona[]
    bazi_profile?: BaziProfile
  }
  simulation_metadata?: {
    sample_size: number
    bazi_distribution: BaziDistribution
    source_type?: string  // "pdf" | "image"
    product_category?: string // "tech_electronics" | "collectible_toy" | "food_beverage" | "fashion_accessory" | "home_lifestyle" | "other"
    product_name?: string
    style?: string
  }
  methodology_data?: MethodologyData // 🧬 Sidecar Data
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

// ===== Dynamic Metric Config based on Product Category =====
const METRIC_CONFIG: Record<string, { label: string; subLabel: string; getAdvice: (level: string) => string }> = {
  tech_electronics: {
    label: "技術變現力",
    subLabel: "「是用技術折服人，還是在拼價格？」越少人嫌貴，代表技術帶來的溢價能力越強。",
    getAdvice: (level) => level === "強" ? "💡 建議：技術優勢受到認可，可考慮強化專利/技術文件作為信任背書。" :
      level === "中" ? "💡 建議：技術認可度中等。建議以「長期價值」或「無形效益」重新包裝訴求。" :
        "💡 建議：難以產生技術溢價。消費者對價格敏感，建議建立「不可替代性」來自抬身價，或接受薄利多銷的策略。"
  },
  collectible_toy: {
    label: "收藏價值",
    subLabel: "「是買來收藏還是玩一玩就丟？」越多人想收藏，代表產品有潛力成為經典。",
    getAdvice: (level) => level === "強" ? "💡 建議：收藏價值受認可！可考慮推出限量版或編號系列來強化稀有性。" :
      level === "中" ? "💡 建議：收藏價值中等。建議強調IP故事性或角色情感連結。" :
        "💡 建議：暫時缺乏收藏吸引力。建議透過包裝設計、授權合作或限定活動來提升價值感。"
  },
  food_beverage: {
    label: "口碑潛力",
    subLabel: "「值不值得推薦給朋友？」越多人願意分享，代表產品有病毒式傳播的潛力。",
    getAdvice: (level) => level === "強" ? "💡 建議：口碑潛力極佳！建議設計分享機制（如買一送一、打卡優惠）放大效果。" :
      level === "中" ? "💡 建議：口碑中等。可透過KOL試吃、使用者評論來累積信任感。" :
        "💡 建議：口碑動能不足。建議先改善產品體驗，或透過試吃活動讓消費者親身感受。"
  },
  fashion_accessory: {
    label: "風格認同度",
    subLabel: "「穿戴它會被羨慕還是忽略？」越多人認同其風格，代表品牌調性越精準。",
    getAdvice: (level) => level === "強" ? "💡 建議：風格精準！建議經營社群穿搭內容，讓產品成為「生活態度」的象徵。" :
      level === "中" ? "💡 建議：風格定位需加強。可透過造型師聯名或場景行銷來清晰品牌調性。" :
        "💡 建議：風格辨識度低。建議重新定義目標客群，找到「為誰而設計」的答案。"
  },
  home_lifestyle: {
    label: "實用滿意度",
    subLabel: "「買回家後會不會後悔？」越少人覺得多餘，代表產品真正解決了生活痛點。",
    getAdvice: (level) => level === "強" ? "💡 建議：實用性受認可！可強調使用情境與前後對比，讓價值更具體。" :
      level === "中" ? "💡 建議：實用性有改善空間。建議收集使用者回饋，找出「為什麼不常用」的原因。" :
        "💡 建議：實用性評價較低。消費者可能覺得「不太需要」，建議精準定位使用場景。"
  },
  other: {
    label: "產品差異化",
    subLabel: "「跟其他同類產品有什麼不同？」越多人覺得獨特，代表產品有明確的競爭優勢。",
    getAdvice: (level) => level === "強" ? "💡 建議：差異化明顯！建議以此為核心訴求，強化獨特賣點的傳播。" :
      level === "中" ? "💡 建議：差異化中等。可思考是否有被忽略的獨特功能或價值主張。" :
        "💡 建議：同質化嚴重。建議找出「為什麼選你而不是別人」的答案。"
  }
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
  const [enrichedData, setEnrichedData] = useState<EnrichedPersona>(citizen);
  const [isLoading, setIsLoading] = useState(false);

  // 當 Modal 開啟時，從 API 取得完整的市民資料
  useEffect(() => {
    const fetchCompleteData = async () => {
      if (!citizen.id) return;

      setIsLoading(true);
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${API_BASE_URL}/api/web/citizen/${citizen.id}`);
        const data = await res.json();

        if (!data.error) {
          // 用 API 資料補充/覆蓋現有資料
          const updatedCitizen: EnrichedPersona = {
            ...citizen,
            birth_year: data.birth_year || citizen.birth_year,
            birth_month: data.birth_month || citizen.birth_month,
            birth_day: data.birth_day || citizen.birth_day,
            birth_shichen: data.birth_shichen || citizen.birth_shichen,
            four_pillars: data.four_pillars || citizen.four_pillars,
            day_master: data.day_master || citizen.day_master,
            strength: data.strength || citizen.strength,
            favorable: data.favorable || citizen.favorable,
            current_luck: data.current_luck || citizen.current_luck,
            luck_timeline: data.luck_timeline || citizen.luck_timeline,
            trait: data.trait || citizen.trait,
            // 重新計算顯示欄位
            fullBirthday: data.birth_year && data.birth_month && data.birth_day
              ? `${data.birth_year}年${data.birth_month}月${data.birth_day}日${data.birth_shichen ? ` ${data.birth_shichen}` : ''}`
              : citizen.fullBirthday,
            luckCycle: data.current_luck?.description
              || (data.current_luck?.name ? `目前行${data.current_luck.name}` : citizen.luckCycle)
          };
          setEnrichedData(updatedCitizen);
        }
      } catch (err) {
        console.error("Failed to fetch citizen data:", err);
      }
      setIsLoading(false);
    };

    fetchCompleteData();
  }, [citizen.id]);

  // 使用 enrichedData 替代 citizen（用於顯示）
  const displayCitizen = enrichedData;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in fade-in duration-200" onClick={onClose}>
      <div className="relative bg-slate-900 border border-purple-500/30 rounded-3xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl shadow-purple-900/50" onClick={(e) => e.stopPropagation()}>
        <div className="p-6 border-b border-white/10 bg-slate-900/95 sticky top-0 z-10 flex justify-between items-start">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-950 flex items-center justify-center text-4xl shadow-xl border border-white/10">
              {elementConfig[displayCitizen.element]?.icon || '👤'}
            </div>
            <div>
              <div className="flex items-baseline gap-3">
                <h2 className="text-3xl font-black text-white tracking-tight">{displayCitizen.name}</h2>
                <span className="text-xs font-mono text-slate-500 px-2 py-1 bg-white/5 rounded-full border border-white/5">ID: {displayCitizen.id ? String(displayCitizen.id).padStart(8, '0').slice(0, 8) : '????'}</span>
              </div>
              <div className="flex flex-col gap-1.5 mt-2">
                <div className="flex items-center gap-3 text-sm">
                  <span className="bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30 font-bold">
                    {displayCitizen.occupation || 'AI Citizen'}
                  </span>
                  <span className="text-slate-400">•</span>
                  <span className="text-slate-300 font-medium">{displayCitizen.displayAge || displayCitizen.age} 歲</span>
                  <span className="text-slate-400">•</span>
                  <span className="text-slate-400">{displayCitizen.location || 'Taiwan'}</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
                  <span className="material-symbols-outlined text-[14px]">calendar_month</span>
                  <span>{isLoading ? '載入中...' : displayCitizen.fullBirthday || '生日未知'}</span>
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
              {displayCitizen.detailedTrait}
            </div>
          </section>

          <section className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">命理格局</div>
              <div className="text-xl font-black text-white">{displayCitizen.pattern}</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">能量強弱</div>
              <div className="text-xl font-black text-white">{displayCitizen.strength || "中和"}</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">喜用五行</div>
              <div className="flex gap-1.5 flex-wrap">
                {displayCitizen.favorable?.map(e => (
                  <span key={e} className="text-sm font-bold text-emerald-400 flex items-center">
                    {elementConfig[e]?.icon}{e}
                  </span>
                )) || <span className="text-slate-500">Balance</span>}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">性格標籤</div>
              <div className="text-xl font-black text-amber-400 truncate">{displayCitizen.trait?.split(',')[0] || "多元性格"}</div>
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
                  {displayCitizen.decision_logic}
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
                      {isLoading ? '載入中...' : displayCitizen.luckCycle || "暫無詳細運程描述"}
                    </div>
                  </div>
                </section>
                <section>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
                    <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest">八字命盤</h3>
                  </div>
                  <div className="p-6 rounded-2xl bg-slate-950 border border-white/10 text-center font-mono text-xl md:text-2xl text-white tracking-widest shadow-inner">
                    {isLoading ? '載入中...' : displayCitizen.four_pillars || "無命盤數據"}
                  </div>
                </section>
              </div>

              <section>
                <div className="flex items-center gap-2 mb-3">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">10年大運時間軸</h3>
                </div>
                <div className="space-y-3">
                  {displayCitizen.luck_timeline?.length > 0 ? displayCitizen.luck_timeline.map((pillar, idx) => {
                    const ageMs = parseInt(displayCitizen.age || "30");
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
                  }) : <div className="text-slate-500 text-center py-4">{isLoading ? '載入中...' : '暫無大運資料'}</div>}
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
  const [isPdfReady, setIsPdfReady] = useState(false) // Lazy PDF generation control
  const [showMethodology, setShowMethodology] = useState(false)
  const [isCopied, setIsCopied] = useState(false) // Share button state

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  // 確保加載動畫至少顯示一段時間，提供更好的用戶體驗
  const [hasShownLoading, setHasShownLoading] = useState(false)
  const [minimumLoadingComplete, setMinimumLoadingComplete] = useState(false)
  const [countdown, setCountdown] = useState(120) // 新增倒數計時狀態 (改為 120s)
  const [visibleLogLines, setVisibleLogLines] = useState(0) // 控制可見的日誌行數

  const TOTAL_POPULATION = 1000

  // 設定最短加載時間（3秒）
  useEffect(() => {
    const timer = setTimeout(() => {
      setMinimumLoadingComplete(true)
    }, 3000) // 最少顯示 3 秒加載動畫
    return () => clearTimeout(timer)
  }, [])

  // 倒數計時邏輯
  useEffect(() => {
    if (!minimumLoadingComplete || (data && data.status === "processing")) {
      const timer = setInterval(() => {
        setCountdown((prev) => (prev > 1 ? prev - 1 : 1))
      }, 1000)
      return () => clearInterval(timer)
    }
  }, [minimumLoadingComplete, data?.status])

  // 系統日誌逐行動畫
  useEffect(() => {
    const totalLines = 8; // 7個靜態日誌 + 1個動畫行
    if (visibleLogLines < totalLines) {
      const timer = setTimeout(() => {
        setVisibleLogLines(prev => prev + 1);
      }, 400); // 每 400ms 顯示一行
      return () => clearTimeout(timer);
    }
  }, [visibleLogLines])

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

          const enrichedSuggestions = json.suggestions || [];

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

  // 決定是否顯示加載動畫：
  // 1. 資料尚未載入 (!data)
  // 2. 資料正在處理中 (status === "processing")
  // 3. 最短加載時間尚未完成 (!minimumLoadingComplete) - 確保用戶看到加載動畫
  const shouldShowLoading = !data || data.status === "processing" || !minimumLoadingComplete

  if (shouldShowLoading) {
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
          <div className="flex gap-2 items-center">


            {/* Keeping one placeholder for visual balance if needed, or remove completely */}
            <div className="flex size-10 items-center justify-center overflow-hidden rounded-lg bg-[#283639] text-white/50">
              <span className="material-symbols-outlined">settings</span>
            </div>
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
                <div className="mt-8 text-center space-y-4">
                  <div className="text-[#d8b4fe] text-xl font-bold tracking-widest drop-shadow-[0_0_8px_rgba(216,180,254,0.6)] animate-[flicker_3s_infinite]">系統深度推演中</div>

                  {/* Large Central Countdown */}
                  <div className="flex flex-col items-center justify-center py-2">
                    <span className="text-[64px] leading-none font-black text-white tabular-nums tracking-tighter drop-shadow-[0_0_20px_rgba(216,180,254,0.5)]">
                      {Math.floor(countdown / 60)}:{(countdown % 60).toString().padStart(2, '0')}
                    </span>
                    <span className="text-sm text-[#d8b4fe]/70 tracking-[0.2em] font-mono mt-2">ESTIMATED TIME REMAINING</span>
                  </div>

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
                  visibleLogLines > i && (
                    <div
                      key={i}
                      className="flex gap-3 animate-in fade-in slide-in-from-left-2 duration-300"
                    >
                      <span className="text-cyan-700">{`>`}</span>
                      <span className={log.c}>{log.t}</span>
                    </div>
                  )
                ))}

                {/* Active line - 只在第 8 行才顯示 */}
                {visibleLogLines >= 8 && (
                  <div className="relative flex gap-3 text-[#25d1f4] font-bold shadow-[0_0_15px_rgba(37,209,244,0.1)] bg-[#25d1f4]/5 p-2 rounded border-l-2 border-[#25d1f4] mt-4 overflow-hidden group animate-in fade-in slide-in-from-left-2 duration-300">
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#25d1f4]/10 to-transparent -translate-x-full animate-[shimmer_2s_infinite]"></div>
                    <span className="shrink-0 animate-pulse">{`>`}</span>
                    <p className="drop-shadow-[0_0_5px_rgba(37,209,244,0.5)] z-10">
                      正在計算五行流年影響...
                      <span className="inline-block w-2.5 h-4 bg-[#25d1f4] ml-1 align-middle animate-[blink_1s_steps(2)_infinite] shadow-[0_0_5px_#25d1f4]"></span>
                    </p>
                  </div>
                )}
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
              <span className="text-[#25d1f4] text-sm font-bold tracking-wider">1000 個活躍 AI 市民：已就緒</span>
            </div>
            {/* 預估等待時間 (Moved to Center) */}
            <div className="flex items-center gap-2 text-[#d8b4fe]/50">
              <span className="material-symbols-outlined text-[16px]">hourglass_empty</span>
              <span className="text-xs font-medium">Deep Thinking Mode Active</span>
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
        </footer >
      </div >
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
          <div className="flex items-center gap-2">
            {/* New PDF Download Button (Replaces Share & Old Download) */}
            {/* Share Project Button */}
            <button
              onClick={handleShare}
              className="flex items-center justify-center rounded-lg h-9 px-4 bg-[#302839] hover:bg-[#473b54] transition-colors text-white text-sm font-bold border border-[#473b54] gap-2 active:scale-95 group"
            >
              <span className="material-symbols-outlined text-[18px] group-hover:text-[#a855f7] transition-colors">
                {isCopied ? 'check' : 'share'}
              </span>
              <span>{isCopied ? '已複製連結' : '分享專案結果'}</span>
            </button>

            {/* New PDF Download Button (Replaces Share & Old Download) */}
            {data && data.status === 'ready' && (
              <>
                {!isPdfReady ? (
                  <button
                    onClick={() => setIsPdfReady(true)}
                    className="flex items-center justify-center rounded-lg h-9 px-4 bg-[#7f13ec] hover:bg-[#9d4af2] transition-colors text-white text-sm font-bold shadow-[0_0_10px_rgba(127,19,236,0.5)] gap-2 group"
                  >
                    <span className="material-symbols-outlined text-[18px]">picture_as_pdf</span>
                    <span>準備 PDF 報告</span>
                  </button>
                ) : (
                  <PDFDownloadLink
                    document={<SimulationReportPDF data={data} />}
                    fileName={`MIRRA_Report_${simId.slice(0, 8)}.pdf`}
                    className="flex items-center justify-center rounded-lg h-9 px-4 bg-[#7f13ec] hover:bg-[#9d4af2] transition-colors text-white text-sm font-bold shadow-[0_0_10px_rgba(127,19,236,0.5)] gap-2 group"
                  >
                    {/* @ts-ignore */}
                    {({ blob, url, loading, error }) =>
                      loading ? (
                        <>
                          <span className="material-symbols-outlined text-lg animate-spin">sync</span>
                          <span>報告生成中...</span>
                        </>
                      ) : error ? (
                        <>
                          <span className="material-symbols-outlined text-lg">error</span>
                          <span>失敗: {String(error).slice(0, 10)}...</span>
                          {console.error('PDF Generation Error:', error)}
                        </>
                      ) : (
                        <>
                          <span className="material-symbols-outlined text-[18px] group-hover:scale-110 transition-transform">download</span>
                          <span>立即下載 PDF</span>
                        </>
                      )
                    }
                  </PDFDownloadLink>
                )}
              </>
            )}
            <div className="bg-center bg-no-repeat bg-cover rounded-full size-9 border border-[#302839]" style={{ backgroundImage: 'url("https://api.dicebear.com/7.x/avataaars/svg?seed=Alex")' }}></div>
          </div>
        </div>
      </header>



      {selectedCitizen && <CitizenModal citizen={selectedCitizen} onClose={() => setSelectedCitizen(null)} />}
      <MethodologyModal isOpen={showMethodology} onClose={() => setShowMethodology(false)} />

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
                <h1 className="text-2xl md:text-4xl font-black leading-tight tracking-[-0.033em] text-white">【未來推演】商業模式驗證報告</h1>
                <p className="text-[#ab9db9] text-base md:text-lg max-w-2xl mt-4 leading-relaxed">
                  本報告採用「西方方法論」與「東方八字科學」<button onClick={() => setShowMethodology(true)} className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 font-bold text-glow hover:scale-105 transition-transform cursor-pointer border-b border-purple-500/30 hover:border-purple-400 pb-0.5">雙軌演算法</button>，為您預判市場勝率。
                </p>
                <button
                  onClick={() => setShowMethodology(true)}
                  className="mt-2 inline-flex items-center text-indigo-400 hover:text-indigo-300 cursor-pointer font-medium transition-colors"
                >
                  📖 深入解析：我們如何運用「西方科學方法論」進行驗證？
                </button>
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
                  <p className="text-xs text-white font-mono text-center">*分數源自下面 {Math.max(data.arena_comments?.length || 0, 8)} 位八字代表市民的加權平均</p>
                </div>
              </div>

              {/* 📊 市場比價資訊 */}
              {data.market_prices && data.market_prices.success && (
                <div className="col-span-1 lg:col-span-4 bg-[#1a1a1f] border border-[#302839] rounded-2xl p-5 shadow-xl">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="material-symbols-outlined text-blue-400 text-[20px]">price_check</span>
                    <h3 className="text-[#ab9db9] text-sm font-bold uppercase tracking-wider">市場比價</h3>
                    <span className="text-[10px] bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full font-bold">
                      📊 已比對 {data.market_prices.sources_count} 個平台
                    </span>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-[#231b2e] rounded-lg">
                      <span className="text-sm text-gray-400">最低價</span>
                      <span className="text-lg font-bold text-green-400">${data.market_prices.min_price}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-[#231b2e] rounded-lg">
                      <span className="text-sm text-gray-400">最高價</span>
                      <span className="text-lg font-bold text-red-400">${data.market_prices.max_price}</span>
                    </div>
                    {data.market_prices.avg_price && (
                      <div className="flex justify-between items-center p-3 bg-[#231b2e] rounded-lg">
                        <span className="text-sm text-gray-400">平均價</span>
                        <span className="text-lg font-bold text-amber-400">${data.market_prices.avg_price}</span>
                      </div>
                    )}
                    {data.market_prices.prices && data.market_prices.prices.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-[#302839]">
                        <p className="text-[10px] text-gray-500 mb-2">比價來源：</p>
                        <div className="flex flex-wrap gap-1.5">
                          {data.market_prices.prices.slice(0, 5).map((p: any, idx: number) => (
                            <span key={idx} className="text-[10px] bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded">
                              {p.platform} ${p.price}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {data.market_prices.market_insight && (
                      <p className="text-xs text-gray-400 mt-2 italic">
                        💡 {data.market_prices.market_insight}
                      </p>
                    )}
                    <div className="mt-4 pt-3 border-t border-blue-500/20 flex items-center gap-2">
                      <span className="material-symbols-outlined text-blue-400 text-sm">verified_user</span>
                      <span className="text-[10px] text-blue-300 font-bold tracking-wider">AI 市民已同步參考以上市場價格進行購買意向評估</span>
                    </div>
                  </div>
                </div>
              )}

              {/* 🧬 [Sidecar] 方法論驗證數據 */}
              {data.methodology_data && (
                <div className="col-span-1 lg:col-span-4 bg-[#1a1a1f] border border-[#302839] rounded-2xl p-5 shadow-xl relative overflow-hidden group">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-[40px] -mr-16 -mt-16 pointer-events-none"></div>

                  <div className="flex items-center gap-2 mb-4">
                    <span className="material-symbols-outlined text-cyan-400 text-[20px]">science</span>
                    <h3 className="text-[#ab9db9] text-sm font-bold uppercase tracking-wider">方法論驗證</h3>
                    <span className="text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-full font-bold">
                      Science
                    </span>
                  </div>

                  <div className="space-y-4">
                    {/* 有效期 & 信賴區間 */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-[#231b2e] p-3 rounded-lg border border-white/5">
                        <div className="text-[10px] text-gray-500 font-bold uppercase mb-1">報告有效期</div>
                        <div className="text-sm font-bold text-white font-mono">{data.methodology_data.valid_until}</div>
                      </div>
                      <div className="bg-[#231b2e] p-3 rounded-lg border border-white/5">
                        <div className="text-[10px] text-gray-500 font-bold uppercase mb-1">95% 信賴區間</div>
                        <div className="text-sm font-bold text-cyan-400 font-mono">{data.methodology_data.confidence_interval}</div>
                      </div>
                    </div>

                    {/* 下一步迭代行動 */}
                    <Link
                      href={`/?mode=iteration&action=${data.methodology_data.next_step.action}&ref_score=${data.score}&product_name=${encodeURIComponent(data.product_name || data.simulation_metadata?.product_name || '')}&price=${encodeURIComponent(String(data.price || data.market_prices?.avg_price || ''))}&description=${encodeURIComponent(data.description || data.summary?.slice(0, 200) || '')}`}
                      className="block bg-[#231b2e] p-4 rounded-xl border border-white/5 relative overflow-hidden hover:border-cyan-500/50 transition-all cursor-pointer group/action"
                    >
                      <div className="relative z-10">
                        <div className="text-[10px] text-gray-400 font-bold uppercase mb-2 flex justify-between">
                          <span>精實迭代建議 / NEXT ACTION</span>
                          <span className="text-white/50 group-hover/action:text-cyan-400 transition-colors">{data.methodology_data.next_step.action} ↗</span>
                        </div>
                        <div className="flex items-center gap-3 mb-2">
                          <div className={`size-2 rounded-full ${data.methodology_data.next_step.style.split(' ')[0]}`}></div>
                          <div className="text-lg font-bold text-white group-hover/action:text-cyan-100 transition-colors">{data.methodology_data.next_step.label}</div>
                        </div>
                        <p className="text-xs text-gray-400 leading-relaxed border-t border-white/5 pt-2 mt-2 group-hover/action:text-gray-300 transition-colors">
                          {data.methodology_data.next_step.desc}
                        </p>
                      </div>

                      {/* Background Action Button Overlay */}
                      <div className={`absolute -bottom-2 -right-2 size-16 rounded-full opacity-20 blur-xl ${data.methodology_data.next_step.style.split(' ')[0]} group-hover/action:opacity-40 transition-opacity`}></div>
                    </Link>

                    <div className="text-[10px] text-gray-500 font-mono text-center flex items-center justify-center gap-1 opacity-70">
                      <span className="material-symbols-outlined text-[10px]">lock_clock</span>
                      {data.methodology_data.entropy_warning}
                    </div>
                  </div>
                </div>
              )}
              <div className="col-span-1 lg:col-span-8 flex flex-col gap-6">
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                  {(() => {
                    // 動態計算：正面評價率
                    const totalComments = data.arena_comments?.length || 0;
                    // 確保至少以 10 人計算（依據業務規則核心樣本數至少 10‰）
                    const effectiveComments = Math.max(totalComments, 10);
                    const positiveComments = data.arena_comments?.filter((c: any) => c.sentiment === 'positive').length || 0;
                    const positiveRate = totalComments > 0 ? Math.round((positiveComments / totalComments) * 100) : 0;
                    const positiveLabel = positiveRate >= 70 ? '高度正面' : positiveRate >= 50 ? '中性偏正' : positiveRate >= 30 ? '中性' : '偏負面';

                    // 動態計算：參與深度（覆蓋率）- 確保符合 10‰ 基底
                    const coverageRate = Math.round((effectiveComments / TOTAL_POPULATION) * 100 * 10) / 10;

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
                        label: '參與覆蓋率',
                        // 確保至少顯示 10‰ (業務規則：1,000 人中抽取 10 位代表)
                        value: coverageRate < 1 ? `${Math.max(coverageRate * 10, 10)}‰` : `${Math.min(coverageRate, 99)}%`,
                        sub: `「從 1,000 位 AI 市民中抽取了多少人參與調查？」目前為 ${effectiveComments} / 1,000 人。覆蓋率越高，預演結果越能反映真實市場反應。`,
                        advice: coverageRate >= 5
                          ? '💡 建議：覆蓋率優秀！這份報告的市場代表性極高，可作為決策參考。'
                          : coverageRate >= 1
                            ? '💡 建議：覆蓋率中等。若想獲得更精準的預測，可以再次進行更大規模的預演。'
                            : '💡 建議：目前為免費版 (10/1,000 人)。若需擴大母數至 10,000 人或全量分析，請升級 Pro 版。',
                        improvement: coverageRate >= 5 ? '+1~2%' : coverageRate >= 1 ? '+5~8%' : '若優化可升 Pro 版',
                        icon: 'verified',
                        color: 'text-blue-500'
                      },
                      (() => {
                        // Dynamic metric based on product category
                        const productCategory = data.simulation_metadata?.product_category || 'other';
                        const metricConfig = METRIC_CONFIG[productCategory] || METRIC_CONFIG.other;
                        const metricLevel = sensitivityLevel === '低' ? '強' : sensitivityLevel === '中等' ? '中' : '弱';

                        return {
                          label: metricConfig.label,
                          value: metricLevel,
                          sub: metricConfig.subLabel,
                          advice: metricConfig.getAdvice(metricLevel),
                          improvement: getBoost(w_tech),
                          icon: 'monetization_on',
                          color: sensitivityColor
                        };
                      })(),
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
                              {stat.improvement}
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
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-1 rounded flex items-center gap-1">
                      <span className="material-symbols-outlined text-[12px]">inventory_2</span>
                      市場價格已連動
                    </span>
                    <span className="text-[10px] bg-[#302839] text-gray-400 px-2 py-1 rounded">LIVE FEED</span>
                  </div>
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
                {/* Safe Plugin: Refine Copy Panel */}
                <RefineCopyPanel
                  simId={simId}
                  currentCopy={data.summary || ""}
                  productName={data.simulation_metadata?.product_name || "未知產品"}
                  arenaComments={data.arena_comments || []}
                  style={data.simulation_metadata?.style || "professional"}
                  sourceType={data.simulation_metadata?.source_type || "image"}
                />

                <div className="bg-black/40 border border-[#7f13ec]/20 rounded-2xl p-6 relative overflow-hidden group shadow-[0_0_30px_rgba(127,19,236,0.05)]">
                  <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-[#7f13ec] to-blue-500"></div>
                  <div className="flex items-center gap-2 mb-4"><span className="material-symbols-outlined text-[#7f13ec]">auto_awesome</span><h3 className="text-xs font-bold text-[#7f13ec] tracking-[0.2em] uppercase">STRATEGIC ORACLE // 戰略神諭</h3></div>
                  <div className="font-mono text-sm leading-7 text-gray-300 min-h-[140px]">{typedSummary}<span className="inline-block w-1.5 h-4 ml-1 bg-[#7f13ec] animate-pulse align-middle"></span></div>
                </div>
                <div className="space-y-3">
                  <p className="text-[10px] font-bold text-gray-500 tracking-widest uppercase mb-1">AI 策略建議 / TACTICAL ADVICE</p>
                  {data.suggestions?.slice(0, 3).map((s: any, i: number) => (
                    <div key={i} className="bg-[#1a1a1f] border border-[#302839] rounded-xl p-4 hover:border-cyan-500/30 transition-all group flex flex-col gap-3">
                      <div className="flex items-start gap-3">
                        <div className="bg-[#231b2e] size-8 rounded-lg flex items-center justify-center text-lg shadow-inner opacity-70 group-hover:opacity-100 transition-opacity">{i === 0 ? '🎯' : i === 1 ? '💡' : '⚡'}</div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <h4 className="text-white text-sm font-bold">
                              {typeof s.target === 'object' && s.target !== null
                                ? (s.target.point || s.target.title || s.target.text || JSON.stringify(s.target))
                                : (s.target || '策略目標')}
                            </h4>
                            {s.score_improvement && (
                              <span className="text-[10px] bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full font-bold">
                                {typeof s.score_improvement === 'object' && s.score_improvement !== null
                                  ? (s.score_improvement.point || s.score_improvement.text || s.score_improvement.value || JSON.stringify(s.score_improvement))
                                  : s.score_improvement}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-gray-200 leading-relaxed">
                            {typeof s.advice === 'object' && s.advice !== null
                              ? (s.advice.point || s.advice.text || s.advice.description || JSON.stringify(s.advice))
                              : (s.advice || '載入中...')}
                          </p>
                        </div>
                      </div>

                      {/* 執行時間表 */}
                      <div className="pl-11 space-y-3">
                        <div>
                          <p className="text-[10px] text-[#7f13ec] font-bold uppercase mb-1.5 flex items-center gap-1">
                            <span className="material-symbols-outlined text-[12px]">calendar_month</span>
                            執行時間表
                          </p>
                          <ul className="space-y-1.5">
                            {(s.execution_plan || s.action_plan)?.map((step: any, j: number) => (
                              <li key={j} className="flex items-start gap-2 text-[11px] text-gray-300 hover:text-white transition-colors">
                                <span className="text-cyan-500/70 mt-0.5 font-mono">{j + 1}.</span>
                                <span>
                                  {typeof step === 'object' && step !== null
                                    ? (step.point ? step.point + (step.description ? `: ${step.description}` : '') : (step.text || JSON.stringify(step)))
                                    : step}
                                </span>
                              </li>
                            )) || <li className="text-[10px] text-gray-600 italic">正在生成具體執行方案...</li>}
                          </ul>
                        </div>

                        {/* 成功指標 */}
                        {s.success_metrics && (
                          <div className="bg-green-500/5 border border-green-500/20 rounded-lg p-2.5">
                            <p className="text-[10px] text-green-400 font-bold uppercase mb-1 flex items-center gap-1">
                              <span className="material-symbols-outlined text-[12px]">flag</span>
                              成功指標
                            </p>
                            <p className="text-[11px] text-green-300">
                              {typeof s.success_metrics === 'object' && s.success_metrics !== null
                                ? (Array.isArray(s.success_metrics)
                                  ? s.success_metrics.map((m: any) => (m.point || m.text || JSON.stringify(m))).join('; ')
                                  : (s.success_metrics.point || JSON.stringify(s.success_metrics)))
                                : s.success_metrics}
                            </p>
                          </div>
                        )}

                        {/* 潛在風險 */}
                        {s.potential_risks && (
                          <div className="bg-amber-500/5 border border-amber-500/20 rounded-lg p-2.5">
                            <p className="text-[10px] text-amber-400 font-bold uppercase mb-1 flex items-center gap-1">
                              <span className="material-symbols-outlined text-[12px]">warning</span>
                              潛在風險
                            </p>
                            <p className="text-[11px] text-amber-300">
                              {typeof s.potential_risks === 'object' && s.potential_risks !== null
                                ? (Array.isArray(s.potential_risks)
                                  ? s.potential_risks.map((r: any) => (r.point || r.text || JSON.stringify(r))).join('; ')
                                  : (s.potential_risks.point || JSON.stringify(s.potential_risks)))
                                : s.potential_risks}
                            </p>
                          </div>
                        )}
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