"use client"

import { useState, useEffect, useRef } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { motion } from "framer-motion"
import RefineCopyPanel from "@/app/components/RefineCopyPanel"
import MethodologyModal from "@/app/components/MethodologyModal"
import ABMEvolutionVisualization from "@/app/components/ABMEvolutionVisualization"
import { useLanguage } from "@/app/context/LanguageContext"
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
  name?: any
  age: string
  element: string
  day_master: string
  pattern: string
  trait: string
  location?: string
  decision_logic?: string
  occupation?: any
  birth_year?: number
  birth_month?: number
  birth_day?: number
  birth_shichen?: string
  four_pillars?: string
  current_luck?: { name: string; description: string; ten_god?: string }
  luck_timeline?: { age_start: number; age_end: number; name: string; description: string; ten_god?: string }[]
  strength?: string
  favorable?: string[]
}

// Citizen 類型別名（用於 modal 組件兼容性）
type Citizen = Persona

// SimulationData 類型定義
interface SimulationData {
  status: string
  score: number
  summary: string
  genesis: {
    total_population: number
    sample_size: number
    personas: Persona[]
  }
  arena_comments: Array<{
    sentiment: string
    text: string
    citizen_id?: string
    persona: Persona
    score?: number
  }>
  intent?: string
  suggestions?: Array<{ target: string; advice: string; execution_plan: string[]; score_improvement?: string }>
  objections?: Array<{ reason: string; percentage: string }>
  product_name?: string
  price?: string | number
  description?: string
  market_prices?: {
    success: boolean
    prices: Array<{ platform: string; price: number; note: string }>
    min_price: number
    max_price: number
    avg_price?: number
    sources_count: number
    search_summary: string
    market_insight?: string
  }
  simulation_metadata?: {
    style?: string
    product_name?: string
    source_type?: string
    product_category?: string
    targeting?: {
      age_range?: [number, number]
      gender?: string
      occupations?: string[]
      tam?: number  // 動態計算的潛在市場規模
    }
    expert_mode?: boolean
    analysis_scenario?: string
  }
  methodology_data?: {
    valid_until: string
    confidence_interval: string
    next_step: {
      action: string
      label: string
      desc: string
      style: string
    }
    entropy_warning: string
    abm_evolution?: {
      rounds: number[]
      average_scores: number[]
      logs: string[]
      product_element?: string
      price_ratio?: number
    }
    abm_analytics?: {
      consensus: number
      polarization: number
      herding_strength: number
      network_density: number
      element_preferences?: { [key: string]: number }
    }
    metric_advice?: {
      [key: string]: string
    }
  }
}

// ===== Element Config (Dynamic) =====
const getElementConfig = (t: any) => ({
  Fire: { icon: "🔥", color: "text-orange-400", bg: "bg-gradient-to-r from-red-600 to-orange-500", glow: "shadow-orange-500/50", cn: t('bazi.elements.Fire.word') || "火", trait: t('bazi.elements.Fire.trait') },
  Water: { icon: "💧", color: "text-cyan-400", bg: "bg-gradient-to-r from-blue-600 to-cyan-500", glow: "shadow-cyan-500/50", cn: t('bazi.elements.Water.word') || "水", trait: t('bazi.elements.Water.trait') },
  Metal: { icon: "🔩", color: "text-slate-300", bg: "bg-gradient-to-r from-slate-500 to-zinc-400", glow: "shadow-slate-400/50", cn: t('bazi.elements.Metal.word') || "金", trait: t('bazi.elements.Metal.trait') },
  Wood: { icon: "🌳", color: "text-emerald-400", bg: "bg-gradient-to-r from-green-600 to-emerald-500", glow: "shadow-emerald-500/50", cn: t('bazi.elements.Wood.word') || "木", trait: t('bazi.elements.Wood.trait') },
  Earth: { icon: "⛰️", color: "text-amber-400", bg: "bg-gradient-to-r from-amber-600 to-yellow-500", glow: "shadow-amber-500/50", cn: t('bazi.elements.Earth.word') || "土", trait: t('bazi.elements.Earth.trait') }
})

// ===== DECISION MODELS (Dynamic) =====
const getDecisionModels = (t: any) => ({
  "正官格": { title: t('bazi.decision_models.正官格.title'), desc: t('bazi.decision_models.正官格.desc') },
  "七殺格": { title: t('bazi.decision_models.七殺格.title'), desc: t('bazi.decision_models.七殺格.desc') },
  "七杀格": { title: t('bazi.decision_models.七殺格.title'), desc: t('bazi.decision_models.七殺格.desc') }, // Simplified mapping
  "正財格": { title: t('bazi.decision_models.正財格.title'), desc: t('bazi.decision_models.正財格.desc') },
  "正财格": { title: t('bazi.decision_models.正財格.title'), desc: t('bazi.decision_models.正財格.desc') }, // Simplified mapping
  "偏財格": { title: t('bazi.decision_models.偏財格.title'), desc: t('bazi.decision_models.偏財格.desc') },
  "偏财格": { title: t('bazi.decision_models.偏財格.title'), desc: t('bazi.decision_models.偏財格.desc') }, // Simplified mapping
  "正印格": { title: t('bazi.decision_models.正印格.title'), desc: t('bazi.decision_models.正印格.desc') },
  "偏印格": { title: t('bazi.decision_models.偏印格.title'), desc: t('bazi.decision_models.偏印格.desc') },
  "食神格": { title: t('bazi.decision_models.食神格.title'), desc: t('bazi.decision_models.食神格.desc') },
  "傷官格": { title: t('bazi.decision_models.傷官格.title'), desc: t('bazi.decision_models.傷官格.desc') },
  "伤官格": { title: t('bazi.decision_models.傷官格.title'), desc: t('bazi.decision_models.傷官格.desc') }, // Simplified mapping
  "建祿格": { title: t('bazi.decision_models.建祿格.title'), desc: t('bazi.decision_models.建祿格.desc') },
  "建禄格": { title: t('bazi.decision_models.建祿格.title'), desc: t('bazi.decision_models.建祿格.desc') }, // Simplified mapping
  "羊刃格": { title: t('bazi.decision_models.羊刃格.title'), desc: t('bazi.decision_models.羊刃格.desc') },
  "從財格": { title: t('bazi.decision_models.從財格.title'), desc: t('bazi.decision_models.從財格.desc') },
  "从财格": { title: t('bazi.decision_models.從財格.title'), desc: t('bazi.decision_models.從財格.desc') }, // Simplified mapping
  "從殺格": { title: t('bazi.decision_models.從殺格.title'), desc: t('bazi.decision_models.從殺格.desc') },
  "从杀格": { title: t('bazi.decision_models.從殺格.title'), desc: t('bazi.decision_models.從殺格.desc') }, // Simplified mapping
  "從兒格": { title: t('bazi.decision_models.從兒格.title'), desc: t('bazi.decision_models.從兒格.desc') },
  "从兒格": { title: t('bazi.decision_models.從兒格.title'), desc: t('bazi.decision_models.從兒格.desc') }, // Simplified mapping
  "從強格": { title: t('bazi.decision_models.從強格.title'), desc: t('bazi.decision_models.從強格.desc') },
  "从强格": { title: t('bazi.decision_models.從強格.title'), desc: t('bazi.decision_models.從強格.desc') }, // Simplified mapping
  "專旺格": { title: t('bazi.decision_models.專旺格.title'), desc: t('bazi.decision_models.專旺格.desc') },
  "专旺格": { title: t('bazi.decision_models.專旺格.title'), desc: t('bazi.decision_models.專旺格.desc') }, // Simplified mapping
  "default": {
    title: t('bazi.decision_models.default.title') || '多元策略型',
    desc: t('bazi.decision_models.default.desc') || '能根據不同情境調整決策模式。'
  }
});

function getDecisionModel(structure: string | undefined, t: any) {
  const models = getDecisionModels(t);
  if (!structure) return models.default;
  // Match the Chinese key from backend
  const key = Object.keys(models).find(k => k !== 'default' && structure.includes(k));
  return (models as any)[key || 'default'] || models.default;
}

// ===== Dynamic Metric Config (Dynamic) =====
const getMetricConfig = (t: any) => ({
  tech_electronics: {
    label: t('report.metrics.tech_electronics.label'),
    subLabel: t('report.metrics.tech_electronics.subLabel'),
    getAdvice: (level: string) => level === "high" ? t('report.metrics.tech_electronics.advice_high') :
      level === "mid" ? t('report.metrics.tech_electronics.advice_mid') :
        t('report.metrics.tech_electronics.advice_low')
  },
  collectible_toy: {
    label: t('report.metrics.collectible_toy.label'),
    subLabel: t('report.metrics.collectible_toy.subLabel'),
    getAdvice: (level: string) => level === "high" ? t('report.metrics.collectible_toy.advice_high') :
      level === "mid" ? t('report.metrics.collectible_toy.advice_mid') :
        t('report.metrics.collectible_toy.advice_low')
  },
  food_beverage: {
    label: t('report.metrics.food_beverage.label'),
    subLabel: t('report.metrics.food_beverage.subLabel'),
    getAdvice: (level: string) => level === "high" ? t('report.metrics.food_beverage.advice_high') :
      level === "mid" ? t('report.metrics.food_beverage.advice_mid') :
        t('report.metrics.food_beverage.advice_low')
  },
  fashion_accessory: {
    label: t('report.metrics.fashion_accessory.label'),
    subLabel: t('report.metrics.fashion_accessory.subLabel'),
    getAdvice: (level: string) => level === "high" ? t('report.metrics.fashion_accessory.advice_high') :
      level === "mid" ? t('report.metrics.fashion_accessory.advice_mid') :
        t('report.metrics.fashion_accessory.advice_low')
  },
  home_lifestyle: {
    label: t('report.metrics.home_lifestyle.label'),
    subLabel: t('report.metrics.home_lifestyle.subLabel'),
    getAdvice: (level: string) => level === "high" ? t('report.metrics.home_lifestyle.advice_high') :
      level === "mid" ? t('report.metrics.home_lifestyle.advice_mid') :
        t('report.metrics.home_lifestyle.advice_low')
  },
  other: {
    label: t('report.metrics.other.label'),
    subLabel: t('report.metrics.other.subLabel'),
    getAdvice: (level: string) => level === "high" ? t('report.metrics.other.advice_high') :
      level === "mid" ? t('report.metrics.other.advice_mid') :
        t('report.metrics.other.advice_low')
  }
})

interface EnrichedPersona extends Persona {
  fullBirthday?: string
  luckCycle?: string
  detailedTrait?: string
  displayAge?: string
}

/**
 * 獲取在地化後的字串 (P0 Fix for Parallel Universe)
 */
const getLocalizedValue = (val: any, lang: string): string => {
  if (!val) return "";

  let target = val;

  // 如果是字串，嘗試解析它是否為 JSON 物件
  if (typeof val === 'string' && val.trim().startsWith('{')) {
    try {
      target = JSON.parse(val);
    } catch (e) {
      // 解析失敗則維持原樣
      return val;
    }
  }

  if (typeof target === 'object' && target !== null) {
    const key = lang === 'zh-TW' ? 'TW' : lang === 'zh-CN' ? 'CN' : 'US';
    // 依序回退：目標語系 -> 繁體 -> 簡體 -> 英文
    return target[key] || target['TW'] || target['CN'] || target['US'] || "";
  }

  return String(target);
};

/**
 * 直接使用後端傳來的市民資料，不再生成假資料
 * 所有資料應該已在 line_bot_service.py 的 _build_simulation_result 中完整填充
 */
const enrichCitizenData = (p: Persona, t: any, lang: string): EnrichedPersona => {
  // 1. 日主
  const dm = p.day_master || t('report.ui.unknown') || "未知";

  // 2. 生日
  let fullBirthday = "";
  if (p.birth_year && p.birth_month && p.birth_day) {
    fullBirthday = `${p.birth_year}/${p.birth_month}/${p.birth_day}`;
  } else {
    fullBirthday = t('report.ui.birthday_unknown');
  }

  // 3. 當前大運 (Dynamic localizable)
  let luckCycle = "";
  if (p.current_luck) {
    // Priority: 1. Ten God Translation, 2. Localized Description, 3. Localized Name
    if (p.current_luck.ten_god) {
      luckCycle = t(`bazi.luck_descriptions.${p.current_luck.ten_god}`) || getLocalizedValue(p.current_luck.description, lang);
    } else {
      const desc = getLocalizedValue(p.current_luck.description, lang);
      if (desc) luckCycle = desc;
      else {
        const name = getLocalizedValue(p.current_luck.name, lang);
        luckCycle = name || t('report.ui.unknown_stage');
      }
    }
  } else {
    luckCycle = t('report.ui.unknown_stage');
  }

  // 4. 性格特質描述 (Dynamic) - Updated to use bazi.elements
  const elementKey = p.element || "General";
  const detailedTrait = t(`bazi.elements.${elementKey}.detailed`) || t('bazi.elements.General.detailed');

  // 5. 決策邏輯 (Dynamic)
  let decisionLogic = getLocalizedValue(p.decision_logic, lang);
  if (!decisionLogic || decisionLogic.includes("根據八字格局特質分析") || decisionLogic.includes("根据八字格局特质分析")) {
    const dmModel = getDecisionModel(p.pattern, t);
    decisionLogic = `【${dmModel.title}】${dmModel.desc}`;
  }

  // 6. 大運時間軸 - Localized
  const luck_timeline = p.luck_timeline?.map(l => ({
    ...l,
    name: l.ten_god ? (t(`bazi.ten_gods.${l.ten_god}`) || l.name) : l.name,
    description: l.ten_god ? (t(`bazi.luck_descriptions.${l.ten_god}`) || getLocalizedValue(l.description, lang)) : getLocalizedValue(l.description, lang)
  })) || [];

  // 7. 喜用五行 - Localized
  const favorable = p.favorable?.map(elem => {
    // elem might be "Fire", "Wood" (English) or "火", "木" (Chinese from legacy)
    // Map legacy Chinese to English keys if needed, but assuming DB has English keys now? 
    // Actually DB `favorable` is likely ["Wood", "Fire"] from create_citizens.py logic.
    // But let's check input. If it is English Key, translate it.
    // If it is Chinese, try to find Key.
    // Simple approach: try translating as key first.
    return t(`bazi.elements.${elem}.word`) !== `bazi.elements.${elem}.word` ? t(`bazi.elements.${elem}.word`) : elem;
  }) || [];

  // 8. 身強身弱
  const strength = t(`bazi.strength.${p.strength}`) || p.strength || "中和";

  // Handle traits (array or string)
  let traitDisplay = "";
  if (Array.isArray(p.trait)) {
    traitDisplay = p.trait.map(tr => t(`bazi.traits.${tr}`) || tr).join('、');
  } else {
    traitDisplay = getLocalizedValue(p.trait, lang);
  }

  return {
    ...p,
    day_master: dm,
    trait: traitDisplay,
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
  const { t, language } = useLanguage();
  const elementConfig = getElementConfig(t);
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
          // 使用統一的 enrichCitizenData 處理 API 資料並在地化
          const enriched = enrichCitizenData(data, t, language);
          setEnrichedData(enriched);
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
                <h2 className="text-3xl font-black text-white tracking-tight">
                  {getLocalizedValue(displayCitizen.name, language)}
                </h2>
                <span className="text-xs font-mono text-slate-500 px-2 py-1 bg-white/5 rounded-full border border-white/5">{t('report.ui.id') || "ID"}: {displayCitizen.id ? String(displayCitizen.id).padStart(8, '0').slice(0, 8) : '????'}</span>
              </div>
              <div className="flex flex-col gap-1.5 mt-2">
                <div className="flex items-center gap-3 text-sm">
                  <span className="bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30 font-bold">
                    {getLocalizedValue(displayCitizen.occupation, language) || 'AI Citizen'}
                  </span>
                  <span className="text-slate-400">•</span>
                  <span className="text-slate-300 font-medium">{displayCitizen.displayAge || displayCitizen.age} {t('report.ui.age')}</span>
                  <span className="text-slate-400">•</span>
                  <span className="text-slate-400">{getLocalizedValue(displayCitizen.location, language) || 'Taiwan'}</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
                  <span className="material-symbols-outlined text-[14px]">calendar_month</span>
                  <span>{isLoading ? t('report.ui.preparing') : displayCitizen.fullBirthday || t('report.ui.birthday_unknown')}</span>
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
              <h3 className="text-sm font-bold text-purple-400 uppercase tracking-widest">{t('report.ui.current_status')}</h3>
            </div>
            <div className="p-5 rounded-2xl bg-gradient-to-br from-purple-900/20 to-slate-900 border border-purple-500/30 text-slate-200 leading-relaxed text-lg shadow-inner">
              {displayCitizen.detailedTrait}
            </div>
          </section>

          <section className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">{t('report.ui.bazi_structure')}</div>
              <div className="text-xl font-black text-white">{getDecisionModel(displayCitizen.pattern, t).title}</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">{t('report.ui.energy_strength')}</div>
              <div className="text-xl font-black text-white">{displayCitizen.strength || "中和"}</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">{t('report.ui.favorable_elements')}</div>
              <div className="flex gap-1.5 flex-wrap">
                {displayCitizen.favorable?.map(e => (
                  <span key={e} className="text-sm font-bold text-emerald-400 flex items-center">
                    {elementConfig[e]?.icon}{elementConfig[e]?.cn || e}
                  </span>
                )) || <span className="text-slate-500">{t('report.ui.balance')}</span>}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
              <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">{t('report.ui.character_tag')}</div>
              <div className="text-xl font-black text-amber-400 truncate">{displayCitizen.trait?.split(',')[0] || "多元性格"}</div>
            </div>
          </section>

          {showDetails && (
            <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
              <section>
                <div className="flex items-center gap-2 mb-3">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                  <h3 className="text-sm font-bold text-cyan-500 uppercase tracking-widest">{t('report.ui.decision_model')}</h3>
                </div>
                <div className="p-5 rounded-2xl bg-slate-800/30 border border-cyan-500/20 text-slate-200 leading-relaxed text-sm">
                  {displayCitizen.decision_logic}
                </div>
              </section>

              <div className="grid grid-cols-1 gap-6">
                <section>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                    <h3 className="text-sm font-bold text-amber-500 uppercase tracking-widest">{t('report.ui.current_luck')}</h3>
                  </div>
                  <div className="p-5 rounded-2xl bg-amber-500/5 border border-amber-500/20">
                    <div className="text-amber-100/80 leading-relaxed">
                      {isLoading ? t('report.ui.preparing') : displayCitizen.luckCycle || t('report.ui.no_luck_desc')}
                    </div>
                  </div>
                </section>
                <section>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
                    <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest">{t('report.ui.bazi_chart')}</h3>
                  </div>
                  <div className="p-6 rounded-2xl bg-slate-950 border border-white/10 text-center font-mono text-xl md:text-2xl text-white tracking-widest shadow-inner">
                    {isLoading ? t('report.ui.preparing') : (
                      typeof displayCitizen.four_pillars === 'string'
                        ? displayCitizen.four_pillars
                        : (displayCitizen.four_pillars && typeof displayCitizen.four_pillars === 'object'
                          ? `${(displayCitizen.four_pillars as any).year || ''} ${(displayCitizen.four_pillars as any).month || ''} ${(displayCitizen.four_pillars as any).day || ''} ${(displayCitizen.four_pillars as any).hour || ''}`.trim()
                          : t('report.ui.no_bazi_data')
                        )
                    )}
                  </div>
                </section>
              </div>

              <section>
                <div className="flex items-center gap-2 mb-3">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">{t('report.ui.luck_timeline')}</h3>
                </div>
                <div className="space-y-3">
                  {displayCitizen.luck_timeline?.length > 0 ? displayCitizen.luck_timeline.map((pillar, idx) => {
                    const ageMs = parseInt(displayCitizen.age || "30");
                    const isCurrent = ageMs >= pillar.age_start && ageMs <= pillar.age_end;
                    return (
                      <div key={idx} className={`p-4 rounded-xl border transition-all ${isCurrent ? 'bg-purple-900/30 border-purple-500/50 shadow-[0_0_15px_rgba(168,85,247,0.1)]' : 'bg-slate-800/30 border-white/5 opacity-70 hover:opacity-100'}`}>
                        <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-2">
                          <div className="flex items-center gap-3 min-w-[120px]">
                            <span className={`text-xs font-bold ${isCurrent ? 'text-purple-300' : 'text-slate-500'}`}>{pillar.age_start}-{pillar.age_end}{t('report.ui.age')}</span>
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
                  }) : <div className="text-slate-500 text-center py-4">{isLoading ? t('report.ui.preparing') : t('report.ui.no_timeline_data')}</div>}
                </div>
              </section>
            </div>
          )}

          <button onClick={() => setShowDetails(!showDetails)} className="w-full py-4 rounded-xl bg-purple-500/10 border border-purple-500/30 text-base font-bold text-purple-300 hover:bg-purple-500/20 hover:border-purple-500/50 transition-all flex items-center justify-center gap-2 group">
            {showDetails ? <>{t('report.ui.collapse')} <span className="group-hover:-translate-y-1 transition-transform">↑</span></> : <>{t('report.ui.expand')} <span className="group-hover:translate-y-1 transition-transform">↓</span></>}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function WatchPage() {
  const { t, language } = useLanguage()
  const elementConfig = getElementConfig(t)
  const METRIC_CONFIG = getMetricConfig(t)
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
    const summaryText = getLocalizedValue(data?.summary, language);
    if (summaryText) {
      const summaryKey = `${summaryText}_${language}`;
      if (summaryKey === lastSummaryRef.current) return;
      lastSummaryRef.current = summaryKey;

      setTypedSummary("");
      let i = 0;
      const timer = setInterval(() => {
        i++;
        if (i <= summaryText.length) {
          setTypedSummary(summaryText.slice(0, i));
        } else {
          clearInterval(timer);
        }
      }, 10);
      return () => clearInterval(timer);
    }
  }, [data?.summary, language]);

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
                  <div className="text-[#d8b4fe] text-xl font-bold tracking-widest drop-shadow-[0_0_8px_rgba(216,180,254,0.6)] animate-[flicker_3s_infinite]">{t('report.ui.loading_long_time')}</div>

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
                  { t: `[SYSTEM] ${t('report.logs.connected') || "Connected to MIRRA-NODE-01"}`, c: "text-[#536b70]" },
                  { t: `${t('report.logs.loading_citizens') || "Loading Economic Models v4.2..."} [OK]`, c: "text-[#536b70]" },
                  { t: t('report.logs.analyzing') || "Initializing Parallel Worlds...", c: "text-[#7a969c]" },
                  { t: t('report.logs.generating') || "Calculating 1,000 Bazi Charts...", c: "text-[#9cb5ba]" },
                  { t: t('report.logs.generating') || "Generating Population Distribution...", c: "text-[#9cb5ba]" },
                  { t: "WARNING: Anomalous Variable Detected (Fixed)", c: "text-white font-bold" },
                  { t: "Simulating Market Friction Coefficients...", c: "text-gray-200" },
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
              <span className="text-[#25d1f4] text-sm font-bold tracking-wider">{TOTAL_POPULATION.toLocaleString()} {t('report.ui.all_citizens')} : {t('report.ui.ready') || "Ready"}</span>
            </div>
            {/* 預估等待時間 (Moved to Center) */}
            <div className="flex items-center gap-2 text-[#d8b4fe]/50">
              <span className="material-symbols-outlined text-[16px]">hourglass_empty</span>
              <span className="text-xs font-medium">{t('report.ui.deep_thinking') || "Deep Thinking Mode Active"}</span>
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
            {data && false && ( // 暫時隱藏
              <PDFDownloadLink
                document={<SimulationReportPDF data={data} language={language} />}
                fileName={`MIRRA_Report_${data.simulation_metadata?.product_name || 'Project'}_${language}.pdf`}
                className="flex items-center justify-center rounded-lg h-9 px-4 bg-[#7f13ec] hover:bg-[#9333ea] transition-all text-white text-sm font-bold border border-purple-500/30 gap-2 active:scale-95 group shadow-[0_0_15px_rgba(127,19,236,0.2)]"
              >
                {/* @ts-ignore - react-pdf type mismatch */}
                {({ loading }) => (
                  <>
                    <span className={`material-symbols-outlined text-[18px] ${loading ? 'animate-spin' : ''}`}>
                      {loading ? 'sync' : 'download'}
                    </span>
                    <span>{loading ? (t('report.ui.preparing') || '準備中...') : (t('report.ui.download_pdf') || '下載 PDF 報告')}</span>
                  </>
                )}
              </PDFDownloadLink>
            )}
            {/* Share Project Button */}
            <button
              onClick={handleShare}
              className="flex items-center justify-center rounded-lg h-9 px-4 bg-[#302839] hover:bg-[#473b54] transition-colors text-white text-sm font-bold border border-[#473b54] gap-2 active:scale-95 group"
            >
              <span className="material-symbols-outlined text-[18px] group-hover:text-[#a855f7] transition-colors">
                {isCopied ? 'check' : 'share'}
              </span>
              <span>{isCopied ? t('report.ui.copy_link') : t('report.ui.share_project')}</span>
            </button>

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

          <div className={`flex flex-col gap-4 ${isSidebarCollapsed ? 'items-center' : ''}`}>
            {/* === 三層數據漏斗 UI === */}
            {!isSidebarCollapsed && (
              <div className="mt-10 space-y-3 px-1">
                {/* 標題 */}
                <h1 className="text-white text-sm font-bold uppercase tracking-wider flex items-center gap-2">
                  {t('report.ui.filter_title')}
                </h1>

                {/* 三層卡片 */}
                <div className="space-y-2">
                  {/* Level 1: TAM */}
                  <div className="bg-gradient-to-r from-blue-900/30 to-indigo-900/30 rounded-lg p-2.5 border border-blue-500/20">
                    <div className="text-blue-400 text-[10px] font-medium mb-0.5">
                      {t('report.ui.funnel_tam')}
                    </div>
                    <div className="text-white text-lg font-bold">
                      {/* 動態 TAM：從 simulation_metadata.targeting.tam 讀取，默認 18.6M */}
                      {(data?.simulation_metadata?.targeting?.tam || 18600000).toLocaleString()}
                    </div>
                  </div>

                  {/* Level 2: Simulated - 重點強調 */}
                  <div className="bg-gradient-to-r from-purple-900/40 to-violet-900/40 rounded-lg p-3 border-2 border-purple-500/50 relative group shadow-lg shadow-purple-500/10">
                    <div className="flex items-center justify-between">
                      <div className="text-purple-400 text-[10px] font-medium">
                        {t('report.ui.funnel_simulated')}
                      </div>
                      {/* Info Icon */}
                      <span className="text-gray-500 hover:text-purple-400 transition-colors cursor-help text-xs" title={t('report.ui.sampling_tooltip')}>ⓘ</span>
                    </div>
                    <div className="text-white text-2xl font-bold mt-1">{(data?.genesis?.total_population || 1000).toLocaleString()}</div>
                    <div className="text-purple-300/70 text-[10px]">{t('report.ui.ai_citizens_computing')}</div>
                  </div>

                  {/* Level 3: Focus Group */}
                  <div className="bg-gradient-to-r from-amber-900/30 to-orange-900/30 rounded-lg p-2.5 border border-amber-500/20">
                    <div className="text-amber-400 text-[10px] font-medium mb-0.5">
                      {t('report.ui.funnel_focus')}
                    </div>
                    <div className="text-white text-lg font-bold">{data?.genesis?.sample_size || 10}</div>
                    <div className="text-amber-300/70 text-[10px]">{t('report.ui.kol_display')}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Collapsed Header Icon */}
            {isSidebarCollapsed && (
              <div className="mt-12 text-center">
                <span className="material-symbols-outlined text-2xl text-[#7f13ec]">filter_list</span>
              </div>
            )}

            {/* Content */}
            <div className={`flex flex-col gap-2 ${isSidebarCollapsed ? 'items-center' : ''}`}>
              {/* All Citizens Button */}
              <button className={`flex items-center rounded-lg bg-[#7f13ec]/10 text-white border border-[#7f13ec]/50 transition-all ${isSidebarCollapsed ? 'p-2.5 justify-center' : 'gap-3 px-3 py-2.5'}`} title={t('report.ui.all_citizens')}>
                <span className="material-symbols-outlined fill-1 text-[#7f13ec]">groups</span>
                {!isSidebarCollapsed && (
                  <div className="flex flex-col items-start"><span className="text-sm font-bold">{t('report.ui.all_citizens')}</span><span className="text-[10px] opacity-70">{t('report.ui.all_citizens_sub').replace('{count}', (data?.genesis?.total_population || 1000).toLocaleString())}</span></div>
                )}
              </button>

              {!isSidebarCollapsed && <div className="h-px bg-[#302839] my-2"></div>}
              {!isSidebarCollapsed && <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3">原型</p>}

              {/* Persona Buttons - 使用固定分佈比例顯示 1,000 位市民組成 */}
              {(() => {
                // 固定分佈比例（基於 1,000 位市民的合理分佈）
                const FIXED_DISTRIBUTION = {
                  tech: 320,    // 食神格 - 科技愛好者
                  budget: 230,  // 正財格 - 精打細算型
                  skeptic: 150, // 七殺格 - 懷疑論者
                  early: 180,   // 偏財格 - 早期採用者
                  loyal: 120    // 正印格 - 品牌忠誠者
                };

                const personaItems = [
                  { key: 'tech', bazi: '食神格', icon: 'devices', count: FIXED_DISTRIBUTION.tech },
                  { key: 'budget', bazi: '正財格', icon: 'savings', count: FIXED_DISTRIBUTION.budget },
                  { key: 'skeptic', bazi: '七殺格', icon: 'sentiment_dissatisfied', count: FIXED_DISTRIBUTION.skeptic },
                  { key: 'early', bazi: '偏財格', icon: 'rocket_launch', count: FIXED_DISTRIBUTION.early },
                  { key: 'loyal', bazi: '正印格', icon: 'verified', count: FIXED_DISTRIBUTION.loyal }
                ];

                return personaItems.map((item) => (
                  <button
                    key={item.key}
                    className={`flex items-center rounded-lg hover:bg-[#302839] text-[#ab9db9] group transition-colors ${isSidebarCollapsed ? 'p-2.5 justify-center' : 'justify-between gap-3 px-3 py-2'}`}
                    title={isSidebarCollapsed ? `${t('report.ui.persona_types.' + item.key)}` : undefined}
                  >
                    <div className={`flex items-center ${isSidebarCollapsed ? '' : 'gap-3'}`}>
                      <span className="material-symbols-outlined group-hover:text-[#7f13ec] transition-colors">{item.icon}</span>
                      {!isSidebarCollapsed && (
                        <div className="flex flex-col items-start gap-0.5">
                          <span className="text-sm font-medium group-hover:text-white transition-colors">{t('report.ui.persona_types.' + item.key)}</span>
                          {/* @ts-ignore - getDecisionModels may have dynamic keys */}
                          <span className="text-sm text-[#a855f7] font-bold tracking-wide">{getDecisionModels(t)[item.bazi]?.title || item.bazi}</span>
                        </div>
                      )}
                    </div>
                    {!isSidebarCollapsed && <span className="text-xs bg-[#231b2e] px-1.5 py-0.5 rounded text-gray-500">{item.count}</span>}
                  </button>
                ));
              })()}
            </div>
          </div>
        </aside>

        <main className="flex-1 overflow-y-auto bg-[#191022] p-6 md:p-10 scrollbar-hide">
          <div className="max-w-[1400px] mx-auto flex flex-col gap-8">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
              <div className="flex flex-col gap-2">
                <h1 className="text-2xl md:text-4xl font-black leading-tight tracking-[-0.033em] text-white">
                  {t('report.ui.methodology_title')}
                </h1>
                <p className="text-[#ab9db9] text-base md:text-lg max-w-2xl mt-4 leading-relaxed">
                  {t('report.ui.methodology_desc')}
                  <button onClick={() => setShowMethodology(true)} className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 font-bold text-glow hover:scale-105 transition-transform cursor-pointer border-b border-purple-500/30 hover:border-purple-400 pb-0.5 mx-1">
                    {t('report.ui.dual_algo')}
                  </button>
                  {t('report.ui.predict_win_rate')}
                </p>
                <button
                  onClick={() => setShowMethodology(true)}
                  className="mt-2 inline-flex items-center text-indigo-400 hover:text-indigo-300 cursor-pointer font-medium transition-colors"
                >
                  {t('report.ui.methodology_link')}
                </button>
              </div>
              <Link href="/#start" className="flex-none flex items-center justify-center rounded-lg h-12 px-6 bg-[#302839] hover:bg-[#473b54] text-white text-sm font-bold tracking-[0.015em] border border-[#473b54] transition-all shadow-lg active:scale-95">
                <span className="material-symbols-outlined mr-2 text-[20px]">play_circle</span>{t('report.ui.open_new_sim')}
              </Link>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="col-span-1 lg:col-span-4 bg-[#1a1a1f] border border-[#302839] rounded-2xl p-6 shadow-xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-[#7f13ec]/20 rounded-full blur-[60px] -mr-16 -mt-16 pointer-events-none"></div>
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="text-[#ab9db9] text-sm font-bold uppercase tracking-wider">{t('report.ui.goal_achieved').replace('核心目標達成', '整體可行性') || "Overall Feasibility"}</h3>
                    <div className="flex flex-col gap-1 mt-1">
                      <div className="flex items-center gap-2">
                        <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span></span>
                        <p className="text-[10px] text-purple-400 font-medium">{t('report.ui.feasibility_status')}</p>
                      </div>
                    </div>
                  </div>
                  <span className={`text-xs font-bold px-2 py-1 rounded ${data.score >= 70 ? 'bg-green-500/10 text-green-400' : 'bg-amber-500/10 text-amber-400'}`}>{data.score >= 70 ? t('report.ui.goal_achieved') : t('report.ui.needs_opt')}</span>
                </div>
                <div className="flex flex-col items-center justify-center py-4 gap-4">
                  <div className="relative size-44 md:size-48">
                    <svg className="size-full -rotate-90" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="18" cy="18" r="16" fill="none" stroke="currentColor" strokeWidth="3" className="text-[#302839]" />
                      <circle cx="18" cy="18" r="16" fill="none" stroke="currentColor" strokeWidth="3" strokeDasharray={`${data.score}, 100`} strokeLinecap="round" className="text-[#7f13ec] drop-shadow-[0_0_10px_rgba(127,19,236,0.5)] transition-all duration-1000" />
                    </svg>
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                      <span className="text-5xl md:text-6xl font-black text-white block">{data.score}</span>
                      <span className="text-sm font-medium text-gray-500">{t('report.ui.score_unit')}</span>
                    </div>
                  </div>
                  <p className="text-xs text-white font-mono text-center">{t('report.ui.score_note').replace('{count}', Math.max(data.arena_comments?.length || 0, 8).toString())}</p>
                </div>
              </div>

              {/* 📊 市場比價資訊 */}
              {data.market_prices && data.market_prices.success && (
                <div className="col-span-1 lg:col-span-4 bg-[#1a1a1f] border border-[#302839] rounded-2xl p-5 shadow-xl">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="material-symbols-outlined text-blue-400 text-[20px]">price_check</span>
                    <h3 className="text-[#ab9db9] text-sm font-bold uppercase tracking-wider">{t('report.ui.market_price_title')}</h3>
                    <span className="text-[10px] bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full font-bold">
                      📊 {t('report.simulation_form.format_market_compare').replace('{count}', data.market_prices.sources_count.toString()).replace('{summary}', '')}
                    </span>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-[#231b2e] rounded-lg">
                      <span className="text-sm text-gray-400">{t('report.ui.min_price')}</span>
                      <span className="text-lg font-bold text-green-400">${data.market_prices.min_price}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-[#231b2e] rounded-lg">
                      <span className="text-sm text-gray-400">{t('report.ui.max_price')}</span>
                      <span className="text-lg font-bold text-red-400">${data.market_prices.max_price}</span>
                    </div>
                    {data.market_prices.avg_price && (
                      <div className="flex justify-between items-center p-3 bg-[#231b2e] rounded-lg">
                        <span className="text-sm text-gray-400">{t('report.ui.avg_price')}</span>
                        <span className="text-lg font-bold text-amber-400">${data.market_prices.avg_price}</span>
                      </div>
                    )}
                    {data.market_prices.prices && data.market_prices.prices.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-[#302839]">
                        <p className="text-[10px] text-gray-500 mb-2">{t('report.ui.price_source_label')}:</p>
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
                      <span className="text-[10px] text-blue-300 font-bold tracking-wider">{t('report.ui.ai_price_ref')}</span>
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
                    <h3 className="text-[#ab9db9] text-sm font-bold uppercase tracking-wider">{t('report.ui.methodology_main_title')}</h3>
                    <span className="text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-full font-bold">
                      Science
                    </span>
                  </div>

                  <div className="space-y-4">
                    {/* 有效期 & 信賴區間 */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-[#231b2e] p-3 rounded-lg border border-white/5">
                        <div className="text-[10px] text-gray-500 font-bold uppercase mb-1">{t('report.ui.report_validity')}</div>
                        <div className="text-sm font-bold text-white font-mono">{data.methodology_data.valid_until}</div>
                      </div>
                      <div className="bg-[#231b2e] p-3 rounded-lg border border-white/5">
                        <div className="text-[10px] text-gray-500 font-bold uppercase mb-1">{t('report.ui.confidence_interval')}</div>
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
                          <span>{t('report.ui.next_action')}</span>
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

                    <div className="text-sm text-white font-mono text-center flex items-center justify-center gap-2">
                      <span className="material-symbols-outlined text-sm">lock_clock</span>
                      {data.methodology_data.entropy_warning}
                    </div>
                  </div>
                </div>
              )}

              {/* 🧬 ABM 意見演化視覺化 */}
              {data.methodology_data?.abm_evolution && (
                <div className="col-span-1 lg:col-span-4">
                  <ABMEvolutionVisualization
                    data={data.methodology_data.abm_evolution}
                    analytics={data.methodology_data.abm_analytics}
                  />
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
                        label: t('report.metrics.market_potential.label'),
                        value: positiveRate >= 70 ? t('report.metrics.market_potential.value_high') : positiveRate >= 40 ? t('report.metrics.market_potential.value_mid') : t('report.metrics.market_potential.value_low'),
                        sub: t('report.metrics.market_potential.sub_label'),
                        advice: data.methodology_data?.metric_advice?.market_potential || (positiveRate >= 70
                          ? t('report.metrics.market_potential.advice_high')
                          : positiveRate >= 40
                            ? t('report.metrics.market_potential.advice_mid')
                            : t('report.metrics.market_potential.advice_low')),
                        improvement: getBoost(w_pot),
                        icon: 'trending_up',
                        color: positiveRate >= 60 ? 'text-green-500' : 'text-amber-500'
                      },
                      {
                        label: t('report.metrics.coverage.label'),
                        // 確保至少顯示 10‰ (業務規則：1,000 人中抽取 10 位代表)
                        value: coverageRate < 1 ? `${Math.max(coverageRate * 10, 10)}‰` : `${Math.min(coverageRate, 99)}%`,
                        sub: t('report.metrics.coverage.sub_label_prefix') + effectiveComments + t('report.metrics.coverage.sub_label_suffix'),
                        advice: data.methodology_data?.metric_advice?.coverage || (coverageRate >= 5
                          ? t('report.metrics.coverage.advice_high')
                          : coverageRate >= 1
                            ? t('report.metrics.coverage.advice_mid')
                            : t('report.metrics.coverage.advice_low')),
                        improvement: coverageRate >= 5 ? '+1~2%' : coverageRate >= 1 ? '+5~8%' : t('report.metrics.coverage.advice_low').includes('Pro') ? 'Pro' : '+10%',
                        icon: 'verified',
                        color: 'text-blue-500'
                      },
                      (() => {
                        // Dynamic metric based on product category
                        const productCategory = data.simulation_metadata?.product_category || 'other';
                        const metricConfig = getMetricConfig(t)[productCategory as keyof ReturnType<typeof getMetricConfig>] || getMetricConfig(t).other;
                        const metricLevel = sensitivityLevel === '低' ? t('report.metrics.level.strong') : sensitivityLevel === '中等' ? t('report.metrics.level.mid') : t('report.metrics.level.weak');

                        return {
                          label: metricConfig.label,
                          value: metricLevel,
                          sub: metricConfig.subLabel,
                          advice: data.methodology_data?.metric_advice?.collection_value || metricConfig.getAdvice(metricLevel),
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
                  <h3 className="text-white text-sm font-bold mb-4">{t('report.ui.buy_intent_rate')}</h3>
                  <div className="flex flex-col gap-4">
                    {[{ label: t('report.ui.intent_high'), value: 42, color: 'bg-[#7f13ec]' }, { label: t('report.ui.intent_mid'), value: 35, color: 'bg-blue-500' }, { label: t('report.ui.intent_low'), value: 23, color: 'bg-gray-600' }].map((intent) => (
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
              {/* Column 1: THE ARENA + TACTICAL ADVICE */}
              <div className="xl:col-span-5 space-y-6">
                {/* THE ARENA // 輿論競技場 */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2"><div className="w-1.5 h-6 bg-cyan-400 rounded-full animate-pulse"></div><div><h2 className="text-lg font-bold text-white tracking-widest uppercase">{t('report.ui.arena_title')}</h2><p className="text-[10px] text-gray-500 font-mono">Real-time Stream of Consciousness</p></div></div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-1 rounded flex items-center gap-1">
                        <span className="material-symbols-outlined text-[12px]">inventory_2</span>
                        {t('report.ui.market_linked')}
                      </span>
                      <span className="text-[10px] bg-[#302839] text-gray-400 px-2 py-1 rounded">{t('report.ui.live_feed')}</span>
                    </div>
                  </div>
                  <div className="space-y-4 max-h-[700px] overflow-y-auto pr-2 custom-scrollbar">
                    {data.arena_comments?.map((comment, i) => {
                      const persona = comment.persona;
                      // [Fix] Normalize element key (capitalize first letter) to handle "wood"/"Wood" mismatch
                      const rawElem = persona.element || "Fire";
                      const normalizedElem = rawElem.charAt(0).toUpperCase() + rawElem.slice(1).trim();
                      const elem = elementConfig[normalizedElem] || elementConfig[rawElem] || elementConfig.Fire;
                      const isPositive = comment.sentiment === 'positive';
                      return (
                        <div key={i} className={`group relative p-4 rounded-xl border transition-all duration-300 transform bg-[#1a1a1f] hover:translate-x-1 cursor-pointer ${isPositive ? 'border-l-4 border-l-green-500 border-[#302839]' : comment.sentiment === 'negative' ? 'border-l-4 border-l-rose-500 border-[#302839]' : 'border-l-4 border-l-gray-500 border-[#302839]'}`} onClick={() => setSelectedCitizen(enrichCitizenData(persona, t, language))}>
                          <div className="flex items-start gap-3">
                            <div className={`size-10 flex-none rounded-xl ${elem.bg} flex items-center justify-center text-xl shadow-lg group-hover:scale-110 transition-transform`}>{elem.icon}</div>
                            <div className="min-w-0 flex-1">
                              <div className="flex items-center justify-between mb-1">
                                <div className="flex items-center gap-2"><span className="text-xs font-bold text-white">{getLocalizedValue(persona.name, language)}</span><span className={`text-[9px] px-1.5 py-0.5 rounded-full font-bold ${elem.bg} text-white opacity-80`}>{elem.cn}</span></div>
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

                {/* AI 策略建議 / TACTICAL ADVICE - moved here */}
                <div className="space-y-3">
                  <p className="text-xs font-bold text-gray-500 tracking-widest uppercase mb-2">{t('report.ui.tactical_advice')}</p>
                  {data.suggestions?.slice(0, 3).map((s: any, i: number) => (
                    <div key={i} className="bg-[#1a1a1f] border border-[#302839] rounded-xl p-4 hover:border-cyan-500/30 transition-all group flex flex-col gap-3">
                      <div className="flex items-start gap-3">
                        <div className="bg-[#231b2e] size-8 rounded-lg flex items-center justify-center text-lg shadow-inner opacity-70 group-hover:opacity-100 transition-opacity">{i === 0 ? '🎯' : i === 1 ? '💡' : '⚡'}</div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <h4 className="text-white text-sm font-bold">
                              {getLocalizedValue(s.target, language) || '策略目標'}
                            </h4>
                            {s.score_improvement && (
                              <span className="text-[10px] bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full font-bold">
                                {getLocalizedValue(s.score_improvement, language)}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-200 leading-relaxed">
                            {getLocalizedValue(s.advice, language) || '載入中...'}
                          </p>
                        </div>
                      </div>

                      {/* 執行時間表 */}
                      <div className="pl-11 space-y-3">
                        <div>
                          <p className="text-[10px] text-[#7f13ec] font-bold uppercase mb-1.5 flex items-center gap-1">
                            <span className="material-symbols-outlined text-[12px]">calendar_month</span>
                            {t('report.ui.execution_schedule')}
                          </p>
                          <ul className="space-y-1.5">
                            {(s.execution_plan || s.action_plan)?.map((step: any, j: number) => (
                              <li key={j} className="flex items-start gap-2 text-xs text-gray-300 hover:text-white transition-colors">
                                <span className="text-cyan-500/70 mt-0.5 font-mono">{j + 1}.</span>
                                <span>
                                  {getLocalizedValue(step, language)}
                                </span>
                              </li>
                            )) || <li className="text-xs text-gray-600 italic">{t('report.ui.generating_plan')}</li>}
                          </ul>
                        </div>

                        {/* 成功指標 */}
                        {s.success_metrics && (
                          <div className="bg-green-500/5 border border-green-500/20 rounded-lg p-2.5">
                            <p className="text-[10px] text-green-400 font-bold uppercase mb-1 flex items-center gap-1">
                              <span className="material-symbols-outlined text-[12px]">flag</span>
                              {t('report.ui.success_metrics')}
                            </p>
                            <p className="text-xs text-green-300">
                              {getLocalizedValue(s.success_metrics, language)}
                            </p>
                          </div>
                        )}

                        {/* 潛在風險 */}
                        {s.potential_risks && (
                          <div className="bg-amber-500/5 border border-amber-500/20 rounded-lg p-2.5">
                            <p className="text-[10px] text-amber-400 font-bold uppercase mb-1 flex items-center gap-1">
                              <span className="material-symbols-outlined text-[12px]">warning</span>
                              {t('report.ui.potential_risks')}
                            </p>
                            <p className="text-[11px] text-amber-300">
                              {getLocalizedValue(s.potential_risks, language)}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Column 2: GENESIS // 取樣邏輯 */}
              <div className="xl:col-span-3 space-y-6 bg-[#1a1a1f] border border-[#302839] rounded-2xl p-5 flex flex-col">
                <div className="flex items-center gap-2 mb-4"><span className="material-symbols-outlined text-[#a855f7] animate-pulse">grain</span><h3 className="text-[#a855f7] text-sm font-bold uppercase tracking-wider">{t('report.ui.genesis_title')}</h3></div>
                <div className="flex flex-col items-center justify-center space-y-8 p-6">
                  <Link href="/citizens" className="relative z-10 w-full text-center group cursor-pointer block p-4 rounded-xl hover:bg-white/5 transition-all duration-300">
                    <span className="material-symbols-outlined text-4xl text-blue-400 mb-2 group-hover:text-purple-400 group-hover:scale-110 transition-all duration-300">public</span>
                    <div className="text-3xl font-black text-white group-hover:text-purple-100 transition-colors">1,000</div>
                    <div className="text-xs text-gray-400 font-bold mt-1 group-hover:text-white transition-colors">{t('report.ui.all_citizens')}</div>
                    <div className="absolute inset-0 border border-purple-500/0 group-hover:border-purple-500/30 rounded-xl transition-all duration-300" />
                  </Link>
                  <span className="material-symbols-outlined text-gray-600 animate-bounce">keyboard_double_arrow_down</span>
                  <div className="w-full bg-[#302839]/50 rounded-lg p-4 border border-[#7f13ec]/20 text-center"><p className="text-[#a855f7] font-bold text-sm mb-1">{t('report.ui.bazi_deduction')}</p><p className="text-[10px] text-gray-400">{t('report.ui.bazi_deduction_desc')}</p></div>
                  <span className="material-symbols-outlined text-gray-600 animate-bounce">keyboard_double_arrow_down</span>
                  <div className="text-center"><span className="material-symbols-outlined text-4xl text-[#7f13ec] mb-2">groups</span><div className="text-4xl font-black text-white text-glow">{data.arena_comments?.length || 0}</div><div className="text-xs text-gray-300 font-bold mt-1">{t('report.ui.participating_citizens')}</div></div>
                </div>
              </div>

              {/* Column 3: Refine Copy Panel + Strategic Oracle */}
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

                {/* STRATEGIC ORACLE */}
                <div className="bg-black/40 border border-[#7f13ec]/20 rounded-2xl p-6 relative overflow-hidden group shadow-[0_0_30px_rgba(127,19,236,0.05)]">
                  <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-[#7f13ec] to-blue-500"></div>
                  <div className="flex items-center gap-2 mb-4"><span className="material-symbols-outlined text-[#7f13ec]">auto_awesome</span><h3 className="text-xs font-bold text-[#7f13ec] tracking-[0.2em] uppercase">{t('report.ui.oracle_title')}</h3></div>
                  <div className="font-mono text-sm leading-7 text-gray-300 min-h-[140px]">{typedSummary}<span className="inline-block w-1.5 h-4 ml-1 bg-[#7f13ec] animate-pulse align-middle"></span></div>
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