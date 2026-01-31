"use client"

import { useState } from "react"
import Link from "next/link"

// ===== DATA INTERFACES =====
export interface BaziProfile {
    birth_year?: number
    birth_month?: number
    birth_day?: number
    birth_hour?: number
    birth_shichen?: string
    four_pillars?: any // Can be string or object {year, month, day, hour}
    strength?: string
    structure?: string
    structure_en?: string // Added for strict US localization support
    favorable_elements?: string[]
    unfavorable_elements?: string[]
    day_master?: string
    element?: string
    current_state?: string
    birth_info?: {
        month: number
        day?: number
        hour: number
    }
    luck_pillars?: Array<{
        pillar: string
        gan: string
        age_start: number
        age_end: number
        description?: string
        localized_description?: Record<string, string>
    }>
    luck_timeline?: any[] // Added for debugging/V6 compatibility
    localized_state?: Record<string, string> // Added for Multiverse support
    localized_strength?: Record<string, string> // Added for Localization
    localized_favorable_elements?: Record<string, string[]> // Added for Localization
}

export interface Citizen {
    id: string
    name: string
    region?: string // Added for strict filtering
    gender: string
    age: number
    location: string
    bazi_profile: BaziProfile
    traits: string[]

    occupation: string | Record<string, string>
    profiles: {
        TW: { name: string; city: string; job: string; pain: string, traits?: string[] }
        US: { name: string; city: string; job: string; pain: string, traits?: string[] }
        CN: { name: string; city: string; job: string; pain: string, traits?: string[] }
    }
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

const DECISION_MODELS_EN: Record<string, { title: string; desc: string }> = {
    "Director (Officer)": { title: "Logical & Prudent", desc: "Evaluates risks and compliance before deciding. Prefers proven solutions and clear responsibilities." },
    "Pioneer (7-Killings)": { title: "Decisive Executor", desc: "Dares to bet big in crises. Fast decision-making, results-oriented, and commanding in critical moments." },
    "Financier (Wealth)": { title: "Data-Driven Pragmatist", desc: "Focuses on cost-benefit analysis (ROI). Every penny counts. Prefers low-risk, stable returns." },
    "Entrepreneur (Windfall)": { title: "Opportunity Hunter", desc: "Sharp business sense. Willing to take risks for high returns. Decisive and good at leveraging resources." },
    "Mentor (Resource)": { title: "Long-Term Planner", desc: "Focuses on long-term value and reputation. Dislikes shortsightedness. Considers holistic impact." },
    "Strategist (Owl)": { title: "Unconventional Innovator", desc: "Hates following the crowd. Prefers unique, non-mainstream choices. Intuitive and insightful." },
    "Artist (Chef)": { title: "Taste & Intuition", desc: "Values personal preference and aesthetic experience. Emotional decision-making. Seeks 'the right feel' and comfort." },
    "Disruptor (Hurting)": { title: "Rule Breaker", desc: "Likes to break norms and challenge the status quo. Decisions often aim to prove unique capabilities." },
    "Builder (Prosperity)": { title: "Pragmatic Independent", desc: "Trusts own judgment. Not easily swayed. Values actual control and feasibility." },
    "Warrior (Blade)": { title: "Goal-Oriented Efficient", desc: "Extremely goal-driven. Overcomes all obstacles. Fast, precise, and ruthless decisions." },
};

const DECISION_MODELS_CN: Record<string, { title: string; desc: string }> = {
    "正官格": { title: "逻辑审慎型", desc: "决策前必先评估风险与合规性，偏好有前例可循的方案，重视SOP与权责划分。" },
    "七殺格": { title: "果断执行型", desc: "面对危机敢于下重注，决策速度快，重视结果大于过程，关键时刻能展现魄力。" },
    "正財格": { title: "稳健数据型", desc: "重视成本效益分析 (CP值)，每一分钱都要花在刀口上，偏好低风险、稳定回报的选择。" },
    "偏財格": { title: "机会捕捉型", desc: "商业嗅觉敏锐，愿意为高潜在回报承担风险，决策豪爽，善于利用杠杆。" },
    "正印格": { title: "长远规划型", desc: "决策着重长期价值与品牌信誉，不喜欢短视近利的行为，会考虑对整体的影响。" },
    "偏印格": { title: "创新反骨型", desc: "讨厌随波逐流，喜欢独特、非主流的选择，决策带有直觉色彩，常有出人意表的洞见。" },
    "食神格": { title: "品味直觉型", desc: "重视个人喜好与美感体验，决策较感性，追求「感觉对了」与心理舒适度。" },
    "傷官格": { title: "颠覆突破型", desc: "喜欢打破常规，不按牌理出牌，决策往往挑战现状，旨在证明自己的独特能力。" },
    "建祿格": { title: "务实自主型", desc: "相信自己的判断，不轻易被话术影响，重视实际掌控权与执行可行性。" },
    "羊刃格": { title: "效率目标型", desc: "目标导向极强，为了达成目的可以排除万难，决策快狠准，不喜欢拖泥带水。" },
    "從財格": { title: "顺势而为型", desc: "懂得利用大环境趋势，决策灵活，适应力强，哪里有利就往哪里去。" },
    "從殺格": { title: "权力导向型", desc: "具有强烈的企图心，决策服务于地位的提升与影响力的扩大。" },
    "從兒格": { title: "智慧策略型", desc: "靠才华与创意取胜，决策灵活多变，不喜欢被死板的规则束缚。" },
    "專旺格": { title: "坚持本色型", desc: "意志坚定，一条路走到黑，在专业领域有极强的决策自信。" }
};

const HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"];
const EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];

export function generateMockPillars() {
    const getPair = () => HEAVENLY_STEMS[Math.floor(Math.random() * 10)] + EARTHLY_BRANCHES[Math.floor(Math.random() * 12)];
    return `${getPair()}  ${getPair()}  ${getPair()}  ${getPair()}`;
}

// Fallback for unknown structures
const DEFAULT_DECISION_MODEL = { title: "多元策略型", desc: "能根據不同情境調整決策模式，兼具理性與感性。" };
const DEFAULT_DECISION_MODEL_EN = { title: "Adaptive Strategist", desc: "Adjusts decision modes based on context. Balances rationality and sensibility." };
const DEFAULT_DECISION_MODEL_CN = { title: "多元策略型", desc: "能根据不同情境调整决策模式，兼具理性与感性。" };

export function getDecisionModel(structure: string | undefined, market: string = 'TW') {
    if (!structure) {
        if (market === 'US') return DEFAULT_DECISION_MODEL_EN;
        if (market === 'CN') return DEFAULT_DECISION_MODEL_CN;
        return DEFAULT_DECISION_MODEL;
    }

    // Check for "Follow" types or "Strong" types that might not be in basic EN map yet
    // For now, mapping the standard 10 gods.
    if (market === 'US') {
        const enKey = BAZI_TRANSLATIONS[structure];
        if (enKey && DECISION_MODELS_EN[enKey]) {
            return DECISION_MODELS_EN[enKey];
        }
        return DEFAULT_DECISION_MODEL_EN;
    }

    if (market === 'CN') {
        const key = Object.keys(DECISION_MODELS_CN).find(k => structure.includes(k));
        return key ? DECISION_MODELS_CN[key] : DEFAULT_DECISION_MODEL_CN;
    }

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

export function getElementColor(element: string | undefined) {
    if (!element) return ELEMENT_COLORS["土"]; // Default
    // Handle English Element Names for US market if passed directly
    if (element === 'Metal') return ELEMENT_COLORS['金'];
    if (element === 'Wood') return ELEMENT_COLORS['木'];
    if (element === 'Water') return ELEMENT_COLORS['水'];
    if (element === 'Fire') return ELEMENT_COLORS['火'];
    if (element === 'Earth') return ELEMENT_COLORS['土'];

    const key = Object.keys(ELEMENT_COLORS).find(k => element.includes(k));
    return key ? ELEMENT_COLORS[key] : ELEMENT_COLORS["土"];
}

export function parseFourPillars(fourPillars: any) {
    if (!fourPillars) return null;

    if (typeof fourPillars === 'object' && !Array.isArray(fourPillars)) {
        return {
            year: fourPillars.year || '?',
            month: fourPillars.month || '?',
            day: fourPillars.day || '?',
            hour: fourPillars.hour || '?'
        };
    }

    let parts: string[] = [];
    if (Array.isArray(fourPillars)) {
        parts = fourPillars;
    } else if (typeof fourPillars === 'string') {
        parts = fourPillars.trim().split(/\s+/);
    } else {
        return null;
    }

    if (parts.length < 4) return null;
    return {
        year: parts[0],
        month: parts[1],
        day: parts[2],
        hour: parts[3]
    };
}

// ===== AVATAR MAPPING =====

export function getAvatarPath(citizenId: string, age: number, gender: string, name?: string): string {
    const seed = name || citizenId;
    const style = 'micah';

    // Apply gender-based hair constraints to prevent visual mismatches
    // (e.g. Male with long hair, Female with boy-like short hair)
    let hairParam = '';
    const isMale = gender === 'Male' || gender === '男';
    const isFemale = gender === 'Female' || gender === '女';


    if (isMale) {
        // Short / masculine styles
        // Correct values: fonze, mrClean, dougFunny, dannyPhantom, mrT
        hairParam = '&hair=fonze,mrClean,dougFunny,dannyPhantom';
    } else if (isFemale) {
        // Long / feminine styles
        // 'full' is long hair, 'pixie' is short but feminine
        hairParam = '&hair=full,pixie';
    }

    return `https://api.dicebear.com/7.x/${style}/svg?seed=${encodeURIComponent(seed)}&backgroundColor=transparent${hairParam}`;
}

// ===== TRANSLATIONS =====
const GENDER_TRANSLATIONS: Record<string, Record<string, string>> = {
    "Male": { TW: "男", CN: "男", US: "Male" },
    "Female": { TW: "女", CN: "女", US: "Female" },
    "男": { TW: "男", CN: "男", US: "Male" },
    "女": { TW: "女", CN: "女", US: "Female" }
};

const MBTI_TRANSLATIONS: Record<string, Record<string, string>> = {
    "ENTJ": { TW: "指揮官", CN: "指挥官", US: "Commander" },
    "INTJ": { TW: "建築師", CN: "建筑师", US: "Architect" },
    "ENTP": { TW: "辯論家", CN: "辩论家", US: "Debater" },
    "INTP": { TW: "邏輯學家", CN: "逻辑学家", US: "Logician" },
    "ESTJ": { TW: "總經理", CN: "总经理", US: "Executive" },
    "ISTJ": { TW: "物流師", CN: "物流师", US: "Logistician" },
    "ESTP": { TW: "企業家", CN: "企业家", US: "Entrepreneur" },
    "ISTP": { TW: "鑑賞家", CN: "鉴赏家", US: "Virtuoso" },
    "ENFJ": { TW: "主人公", CN: "主人公", US: "Protagonist" },
    "INFJ": { TW: "提倡者", CN: "提倡者", US: "Advocate" },
    "ENFP": { TW: "競選者", CN: "竞选者", US: "Campaigner" },
    "INFP": { TW: "調停者", CN: "调停者", US: "Mediator" },
    "ESFJ": { TW: "執政官", CN: "执政官", US: "Consul" },
    "ISFJ": { TW: "守衛者", CN: "守卫者", US: "Defender" },
    "ESFP": { TW: "表演者", CN: "表演者", US: "Entertainer" },
    "ISFP": { TW: "探險家", CN: "探险家", US: "Adventurer" }
};

export function translateGender(gender: string, market: string) {
    if (!gender) return "";
    return GENDER_TRANSLATIONS[gender]?.[market] || gender;
}

export function translateMBTI(mbti: string, market: string) {
    if (!mbti) return mbti;
    const match = Object.keys(MBTI_TRANSLATIONS).find(k => mbti.includes(k));
    if (match) {
        return `${match} ${MBTI_TRANSLATIONS[match][market]}`;
    }
    return mbti;
}

const STEM_TRANSLATIONS: Record<string, string> = {
    "甲": "Yang Wood", "乙": "Yin Wood", "丙": "Yang Fire", "丁": "Yin Fire", "戊": "Yang Earth",
    "己": "Yin Earth", "庚": "Yang Metal", "辛": "Yin Metal", "壬": "Yang Water", "癸": "Yin Water"
};

const BRANCH_TRANSLATIONS: Record<string, string> = {
    "子": "Rat", "丑": "Ox", "寅": "Tiger", "卯": "Rabbit", "辰": "Dragon", "巳": "Snake",
    "午": "Horse", "未": "Sheep", "申": "Monkey", "酉": "Rooster", "戌": "Dog", "亥": "Pig"
};

const PINYIN_STEMS: Record<string, string> = {
    "jia": "甲", "yi": "乙", "bing": "丙", "ding": "丁", "wu": "戊",
    "ji": "己", "geng": "庚", "xin": "辛", "ren": "壬", "gui": "癸"
};
const PINYIN_BRANCHES: Record<string, string> = {
    "zi": "子", "chou": "丑", "yin": "寅", "mao": "卯", "chen": "辰", "si": "巳",
    "wu": "午", "wei": "未", "shen": "申", "you": "酉", "xu": "戌", "hai": "亥"
};

export const I18N = {
    TW: {
        id: "ID",
        occupation: "職業",
        gender: "性別",
        age: "歲",
        birth: "出生",
        date_format: (y: any, m: any, d: any, h: any = null) => `${y}年${m}月${d}日`,
        current_state: "當前狀態解讀",
        structure: "命理格局",
        strength: "能量強弱",
        favorable: "喜用五行",
        traits: "性格標籤",
        model_title: "決策思維模型",
        current_luck: "當前大運 / CURRENT LUCK",
        chart: "八字命盤",
        timeline: "10年大運時間軸",
        current_tag: "當前運勢 CURRENT",
        view_more: "查看完整運勢報告",
        view_less: "收合報告",
        unknown: "未知",
        none: "無",
        pillar_year: "年",
        pillar_month: "月",
        pillar_day: "日",
        pillar_hour: "時",
        prev_page: "上一頁",
        next_page: "下一頁",
        page: "頁"
    },
    US: {
        id: "ID",
        occupation: "Occupation",
        gender: "Gender",
        age: " y/o",
        birth: "Birth",
        date_format: (y: any, m: any, d: any, h: any = null) => {
            if (!y) return "Unknown";
            const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            const mStr = m ? monthNames[parseInt(m) - 1] : "";
            const dStr = d ? d + ", " : "";
            return mStr ? `${mStr} ${dStr}${y}` : `${y}`;
        },
        current_state: "Current State Analysis",
        structure: "Structure",
        strength: "Energy",
        favorable: "Lucky Elements",
        traits: "Traits",
        model_title: "Decision Model",
        current_luck: "Current Luck Cycle",
        chart: "Element Chart",
        timeline: "10-Year Luck Timeline",
        current_tag: "CURRENT",
        view_more: "View Full Report",
        view_less: "Collapse Report",
        unknown: "Unknown",
        none: "None",
        pillar_year: "Year",
        pillar_month: "Month",
        pillar_day: "Day",
        pillar_hour: "Hour",
        prev_page: "Previous",
        next_page: "Next",
        page: "Page"
    },
    CN: {
        id: "ID",
        occupation: "职业",
        gender: "性别",
        age: "岁",
        birth: "出生",
        date_format: (y: any, m: any, d: any, h: any = null) => `${y}年${m}月${d}日`,
        current_state: "当前状态解读",
        structure: "命理格局",
        strength: "能量强弱",
        favorable: "喜用五行",
        traits: "性格标签",
        model_title: "决策思维模型",
        current_luck: "当前大运",
        chart: "八字命盘",
        timeline: "10年大运时间轴",
        current_tag: "当前运势",
        view_more: "查看完整报告",
        view_less: "收起报告",
        unknown: "未知",
        none: "无",
        pillar_year: "年",
        pillar_month: "月",
        pillar_day: "日",
        pillar_hour: "时",
        prev_page: "上一页",
        next_page: "下一页",
        page: "页"
    }
};

const BAZI_TRANSLATIONS: Record<string, string> = {
    "正官格": "Director",
    "七殺格": "Challenger",
    "正財格": "Financier",
    "偏財格": "Entrepreneur",
    "正印格": "Mentor",
    "偏印格": "Strategist",
    "食神格": "Creator",
    "傷官格": "Innovator",
    "建祿格": "Builder",
    "羊刃格": "Commander",
    "身強": "Strong",
    "身弱": "Weak",
    "中和": "Balanced",
    "金": "Metal", "木": "Wood", "水": "Water", "火": "Fire", "土": "Earth"
};

export function translateBazi(text: string | undefined, market: string) {
    if (!text) return "";
    if (market === 'US') return BAZI_TRANSLATIONS[text] || text;
    if (market === 'CN') {
        const cn_mapping: Record<string, string> = {
            "身強": "身强", "身弱": "身弱", "中和": "中和", "極強": "极强", "極弱": "极弱",
            "比肩格": "比肩格", "劫財格": "劫财格", "食神格": "食神格", "傷官格": "伤官格",
            "偏財格": "偏财格", "正財格": "正财格", "七殺格": "七杀格", "正官格": "正官格",
            "偏印格": "偏印格", "正印格": "正印格", "建祿格": "建禄格", "羊刃格": "羊刃格",
            "從財格": "从财格", "從殺格": "从杀格", "從兒格": "从儿格", "專旺格": "专旺格", "從強格": "从强格",
            "金": "金", "木": "木", "水": "水", "火": "火", "土": "土"
        };
        return cn_mapping[text] || text;
    }
    return text;
}

function translatePillar(pillar: string, market: string) {
    if (!pillar || typeof pillar !== 'string') return "";

    if (pillar.includes('-')) {
        const [pStem, pBranch] = pillar.toLowerCase().split('-');
        const cnStem = PINYIN_STEMS[pStem];
        const cnBranch = PINYIN_BRANCHES[pBranch];

        if (cnStem && cnBranch) {
            const cnPillar = cnStem + cnBranch;
            if (market === 'US') {
                return translatePillar(cnPillar, market);
            }
            return cnPillar;
        }
        return pillar.split('-').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join('-');
    }

    if (market !== 'US') return pillar;

    const stem = pillar[0];
    const branch = pillar[1];
    const sEn = STEM_TRANSLATIONS[stem];
    const bEn = BRANCH_TRANSLATIONS[branch];

    if (sEn && bEn) {
        const element = sEn.split(' ')[1];
        return `${element} ${bEn}`;
    }
    return pillar;
}

const STRENGTH_MAP_FALLBACK: Record<string, Record<string, string>> = {
    "Weak": { "TW": "身弱", "CN": "身弱", "US": "Weak" },
    "Strong": { "TW": "身強", "CN": "身强", "US": "Strong" },
    "Balanced": { "TW": "中和", "CN": "中和", "US": "Balanced" }
};

const ELEMENT_MAP_FALLBACK: Record<string, Record<string, string>> = {
    "Wood": { "TW": "木", "CN": "木", "US": "Wood" },
    "Fire": { "TW": "火", "CN": "火", "US": "Fire" },
    "Earth": { "TW": "土", "CN": "土", "US": "Earth" },
    "Metal": { "TW": "金", "CN": "金", "US": "Metal" },
    "Water": { "TW": "水", "CN": "水", "US": "Water" }
};

export default function CitizenModal({ citizen, market, onClose }: { citizen: Citizen; market: 'TW' | 'US' | 'CN'; onClose: () => void }) {
    const [showDetails, setShowDetails] = useState(false);

    if (!citizen) return null;

    const activeProfile = citizen.profiles?.[market] || citizen.profiles?.['TW'];
    const rawJob = activeProfile?.job || citizen.occupation;
    const resolvedJob = (typeof rawJob === 'object' && rawJob !== null)
        ? (rawJob[market] || rawJob['TW'] || rawJob['US'] || "Unknown")
        : String(rawJob);

    const display = {
        name: activeProfile?.name || citizen.name,
        job: resolvedJob,
        city: activeProfile?.city || citizen.location
    };
    const t = I18N[market] || I18N['TW'];
    const decisionModel = getDecisionModel(citizen.bazi_profile?.structure, market);
    const bazi = (citizen.bazi_profile || {}) as any;
    const luckPillars = bazi.luck_timeline || bazi.luck_pillars || [];

    let currentLuck = null;
    if (bazi.current_luck && typeof bazi.current_luck === 'string') {
        const pillarStr = bazi.current_luck;
        const start = Math.floor(citizen.age / 10) * 10;
        const end = start + 9;
        currentLuck = {
            pillar: pillarStr,
            age_start: start,
            age_end: end,
            description: "Current 10-year cycle",
            localized_description: {}
        };
    } else {
        currentLuck = luckPillars.find((l: any) => citizen.age >= l.age_start && citizen.age <= l.age_end) || luckPillars[0];
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in fade-in duration-200" onClick={onClose}>
            <div className="relative bg-slate-900 border border-purple-500/30 rounded-3xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl shadow-purple-900/50" onClick={(e) => e.stopPropagation()}>

                <div className="p-6 border-b border-white/10 bg-slate-900/95 sticky top-0 z-10 flex justify-between items-start">
                    <div className="flex items-center gap-5">
                        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-950 flex items-center justify-center text-4xl shadow-xl border border-white/10">
                            {citizen.gender === 'Female' || citizen.gender === '女' ? '👩' : '👨'}
                        </div>
                        <div>
                            <div className="flex items-baseline gap-3">
                                <h2 className="text-3xl font-black text-white tracking-tight">{display.name}</h2>
                                <span className="text-xs font-mono text-slate-500 px-2 py-1 bg-white/5 rounded-full border border-white/5">{t.id}: {String(citizen.id).padStart(8, '0').slice(0, 8)}</span>
                            </div>
                            <div className="flex items-center gap-3 mt-2 text-sm">
                                <span className="bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30 font-bold">
                                    {display.job}
                                </span>
                                <span className="text-slate-400">•</span>
                                <span className="text-slate-300 font-medium">{translateGender(citizen.gender, market)}</span>
                                <span className="text-slate-400">•</span>
                                <span className="text-slate-300 font-medium">{citizen.age}{t.age}</span>
                                <span className="text-slate-400">•</span>
                                <span className="text-slate-400">{display.city}</span>
                            </div>
                            <div className="flex items-center gap-2 mt-2 text-xs text-slate-400 font-mono">
                                <span>📅</span>
                                <span>
                                    {(() => {
                                        const y = citizen.bazi_profile?.birth_year || (2026 - citizen.age);
                                        const m = citizen.bazi_profile?.birth_month || citizen.bazi_profile?.birth_info?.month;
                                        const d = citizen.bazi_profile?.birth_day || citizen.bazi_profile?.birth_info?.day;
                                        const h = citizen.bazi_profile?.birth_info?.hour;
                                        if (y && m) return t.date_format(y, m, d, h);
                                        return t.unknown;
                                    })()}
                                </span>
                            </div>
                        </div>
                    </div>
                    <button onClick={onClose} aria-label="Close" className="text-slate-500 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-full shrink-0">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div className="overflow-y-auto p-6 space-y-6 custom-scrollbar">
                    {/* Real Bazi Section */}
                    <section className="bg-slate-800/50 rounded-xl p-4 border border-white/5">
                        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">八字命盤 (Four Pillars)</h3>
                        <div className="grid grid-cols-4 gap-2 text-center">
                            <div className="p-2 bg-slate-900 rounded border border-white/10">
                                <div className="text-[10px] text-slate-500">Year</div>
                                <div className="text-lg font-bold text-white">{citizen.bazi_profile.four_pillars?.year}</div>
                            </div>
                            <div className="p-2 bg-slate-900 rounded border border-white/10">
                                <div className="text-[10px] text-slate-500">Month</div>
                                <div className="text-lg font-bold text-white">{citizen.bazi_profile.four_pillars?.month}</div>
                            </div>
                            <div className="p-2 bg-slate-900 rounded border border-white/10">
                                <div className="text-[10px] text-slate-500">Day</div>
                                <div className="text-lg font-bold text-purple-400">{citizen.bazi_profile.four_pillars?.day}</div>
                            </div>
                            <div className="p-2 bg-slate-900 rounded border border-white/10">
                                <div className="text-[10px] text-slate-500">Hour</div>
                                <div className="text-lg font-bold text-white">{citizen.bazi_profile.four_pillars?.hour}</div>
                            </div>
                        </div>
                        <div className="text-[10px] text-slate-500 mt-2 text-center font-mono">
                            Born: {citizen.bazi_profile.birth_year}-{String(citizen.bazi_profile.birth_month).padStart(2, '0')}-{String(citizen.bazi_profile.birth_day).padStart(2, '0')} {String(citizen.bazi_profile.birth_hour).padStart(2, '0')}:00
                        </div>
                    </section>

                    <section className="grid grid-cols-2 gap-4">
                        <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                            <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">{t.structure}</div>
                            <div className="text-xl font-black text-white">{translateBazi(citizen.bazi_profile.structure, market) || t.unknown}</div>
                        </div>
                        <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                            <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">{t.strength}</div>
                            <div className="text-xl font-black text-white">
                                {citizen.bazi_profile.localized_strength?.[market] ||
                                    STRENGTH_MAP_FALLBACK[citizen.bazi_profile.strength || ""]?.[market] ||
                                    translateBazi(citizen.bazi_profile.strength, market) ||
                                    t.unknown}
                            </div>
                        </div>
                        <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                            <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">{t.favorable}</div>
                            <div className="flex gap-1.5 flex-wrap">
                                {(citizen.bazi_profile.localized_favorable_elements?.[market] || citizen.bazi_profile.favorable_elements)?.map((e: string) => {
                                    const displayText = ELEMENT_MAP_FALLBACK[e]?.[market] || translateBazi(e, market);
                                    return <span key={e} className="text-sm font-bold text-emerald-400">{displayText}</span>
                                }) || <span className="text-slate-500">{t.none}</span>}
                            </div>
                        </div>
                        <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                            <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">{t.traits}</div>
                            <div className="text-xl font-black text-amber-400 truncate">
                                {translateMBTI(
                                    citizen.profiles?.[market]?.traits?.[0] ||
                                    activeProfile?.traits?.[0] ||
                                    citizen.traits?.[0] ||
                                    "MBTI",
                                    market
                                )}
                            </div>
                        </div>
                    </section>

                    {showDetails && (
                        <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
                            <section>
                                <div className="flex items-center gap-2 mb-3">
                                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                                    <h3 className="text-sm font-bold text-cyan-500 uppercase tracking-widest">{t.model_title}</h3>
                                </div>
                                <div className="p-5 rounded-2xl bg-slate-800/30 border border-cyan-500/20">
                                    <div className="text-lg font-bold text-white mb-2">{decisionModel.title}</div>
                                    <div className="text-slate-400 leading-relaxed text-sm">
                                        {decisionModel.desc}
                                    </div>
                                </div>
                            </section>

                            <div className="grid grid-cols-1 gap-6">
                                <section>
                                    <div className="flex items-center gap-2 mb-3">
                                        <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                                        <h3 className="text-sm font-bold text-amber-500 uppercase tracking-widest">{t.current_luck}</h3>
                                    </div>
                                    <div className="p-5 rounded-2xl bg-amber-500/5 border border-amber-500/20">
                                        <div className="text-xl font-bold text-amber-200 mb-2">
                                            {currentLuck ? `${translatePillar(currentLuck.pillar, market)} ${market === 'US' ? 'Cycle' : '運'} (${currentLuck.age_start}-${currentLuck.age_end}${t.age})` : t.unknown}
                                        </div>
                                        <div className="text-amber-100/80 leading-relaxed">
                                            {market === 'US' ? (
                                                <span className="text-slate-400 italic font-medium">
                                                    {currentLuck?.localized_description?.['US'] ||
                                                        (currentLuck?.ten_god ? `Luck Cycle: ${currentLuck.ten_god}` : "Analysis available in report.")}
                                                </span>
                                            ) : (
                                                currentLuck?.localized_description?.[market] ||
                                                currentLuck?.description ||
                                                (currentLuck?.pillar ? `${translatePillar(currentLuck.pillar, market)}運` : t.unknown)
                                            )}
                                        </div>
                                    </div>
                                </section>

                                <section>
                                    <div className="flex items-center gap-2 mb-3">
                                        <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
                                        <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest">{t.chart}</h3>
                                    </div>
                                    <div className="p-6 rounded-2xl bg-slate-950 border border-white/10 text-center font-mono text-xl md:text-2xl text-white tracking-widest shadow-inner">
                                        {(() => {
                                            const p = parseFourPillars(citizen.bazi_profile.four_pillars);
                                            if (!p) return generateMockPillars();
                                            if (market === 'US') {
                                                return `${translatePillar(p.year, market)} | ${translatePillar(p.month, market)} | ${translatePillar(p.day, market)} | ${translatePillar(p.hour, market)}`;
                                            }
                                            return `${p.year}  ${p.month}  ${p.day}  ${p.hour}`;
                                        })()}
                                    </div>
                                </section>
                            </div>

                            <section>
                                <div className="flex items-center gap-2 mb-3">
                                    <span className="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
                                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">{t.timeline}</h3>
                                </div>
                                <div className="space-y-3">

                                    {luckPillars.slice(0, 8).map((pillar: any, idx: number) => {
                                        let pObj = pillar;
                                        if (typeof pillar === 'string') {
                                            pObj = {
                                                pillar: pillar,
                                                age_start: idx * 10,
                                                age_end: (idx * 10) + 9
                                            };
                                        }

                                        const isCurrent = citizen.age >= pObj.age_start && citizen.age <= pObj.age_end;

                                        // Use rich description for current luck from the top-level bazi profile if available
                                        // This ensures the timeline description matches the detailed "Current Luck" section
                                        let description = pObj.localized_description?.[market] || pObj.description;
                                        if (isCurrent && bazi.current_luck && typeof bazi.current_luck === 'object') {
                                            const rich = bazi.current_luck.localized_description?.[market] || bazi.current_luck.description;
                                            if (rich) description = rich;
                                        }

                                        return (
                                            <div key={idx} className={`p-4 rounded-xl border transition-all ${isCurrent ? 'bg-purple-900/30 border-purple-500/50 shadow-[0_0_15px_rgba(168,85,247,0.1)]' : 'bg-slate-800/30 border-white/5 opacity-70 hover:opacity-100'}`}>
                                                <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-2">
                                                    <div className="flex items-center gap-3 min-w-[120px]">
                                                        <span className={`text-xs font-bold ${isCurrent ? 'text-purple-300' : 'text-slate-500'}`}>{pObj.age_start}-{pObj.age_end}{t.age}</span>
                                                        <span className={`text-lg font-bold ${isCurrent ? 'text-white' : 'text-slate-300'}`}>{translatePillar(pObj.pillar, market)}</span>
                                                    </div>
                                                    {isCurrent && <span className="text-[10px] bg-purple-500 text-white px-2 py-0.5 rounded-full font-bold tracking-wider">{t.current_tag}</span>}
                                                </div>
                                                {market !== 'US' && description && (
                                                    <div className={`text-sm leading-relaxed ${isCurrent ? 'text-purple-100' : 'text-slate-400'}`}>
                                                        {description}
                                                    </div>
                                                )}
                                            </div>
                                        )
                                    })}
                                </div>
                            </section>
                        </div>
                    )}

                    <button
                        onClick={() => setShowDetails(!showDetails)}
                        className="w-full py-4 rounded-xl bg-purple-500/10 border border-purple-500/30 text-base font-bold text-purple-300 hover:bg-purple-500/20 hover:border-purple-500/50 transition-all flex items-center justify-center gap-2 group"
                    >
                        {showDetails ? (
                            <> {t.view_less} <span className="group-hover:-translate-y-1 transition-transform">↑</span></>
                        ) : (
                            <> {t.view_more} <span className="group-hover:translate-y-1 transition-transform">↓</span></>
                        )}
                    </button>

                </div>
            </div >
        </div >
    );
}
