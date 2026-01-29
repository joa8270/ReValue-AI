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
    four_pillars?: any // Can be string or object {year, month, day, hour}
    strength?: string
    structure?: string
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
    profiles?: {
        TW?: { name: string; city: string; job: string; pain: string }
        US?: { name: string; city: string; job: string; pain: string }
        CN?: { name: string; city: string; job: string; pain: string }
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

const CURRENT_STATE_EN: Record<string, string> = {
    "正官格": "The energy favors discipline, order, and career advancement. It is a good time for steady progress and adhering to established plans.",
    "七殺格": "You are facing a period of transformation and challenge. Decisive action and bold leadership are required to overcome obstacles.",
    "正財格": "Focus on stable income and practical financial management. A grounded approach will yield steady results.",
    "偏財格": "Opportunities for unexpected gains or business expansion are present. Be ready to seize chances but manage risks carefully.",
    "正印格": "A period favorable for learning, reputation, and seeking mentorship. Patience and long-term planning are beneficial.",
    "偏印格": "Unconventional ideas and deep insights are highlighted. You may feel solitary but your creativity is at its peak.",
    "食神格": "Creativity and enjoyment are favored. A good time for artistic pursuits, social connection, and expressing yourself naturally.",
    "傷官格": "You may feel a strong urge to break rules or innovate. Channel this rebellious energy into creative breakthroughs rather than conflict.",
    "建祿格": "Self-reliance and independence are key. You are building a strong foundation through your own efforts and confidence.",
    "羊刃格": "Intense competitive energy. You have the drive to achieve ambitious goals, but beware of being too aggressive or impulsive.",
    "從財格": "The energy flows with wealth trends. Adaptability to the market or environment will bring success.",
    "從殺格": "Power and influence are the focus. Aligning with strong leaders or organizations will prevent resistance.",
    "從兒格": "Intellectual flow is strong. Your talents and ideas are your greatest assets right now.",
    "專旺格": "Your personal strength is dominant. Stick to your principles and lead with confidence."
};

const HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"];
const EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];

function generateMockPillars() {
    const getPair = () => HEAVENLY_STEMS[Math.floor(Math.random() * 10)] + EARTHLY_BRANCHES[Math.floor(Math.random() * 12)];
    return `${getPair()}  ${getPair()}  ${getPair()}  ${getPair()}`;
}

// Fallback for unknown structures
const DEFAULT_DECISION_MODEL = { title: "多元策略型", desc: "能根據不同情境調整決策模式，兼具理性與感性。" };
const DEFAULT_DECISION_MODEL_EN = { title: "Adaptive Strategist", desc: "Adjusts decision modes based on context. Balances rationality and sensibility." };
const DEFAULT_DECISION_MODEL_CN = { title: "多元策略型", desc: "能根据不同情境调整决策模式，兼具理性与感性。" };

function getDecisionModel(structure: string | undefined, market: string = 'TW') {
    if (!structure) {
        if (market === 'US') return DEFAULT_DECISION_MODEL_EN;
        if (market === 'CN') return DEFAULT_DECISION_MODEL_CN;
        return DEFAULT_DECISION_MODEL;
    }

    // Check for "Follow" types or "Strong" types that might not be in basic EN map yet
    // For now, mapping the standard 10 gods.

    // If US, translate structure first to match EN keys
    if (market === 'US') {
        // We need to map "正官格" -> "Director (Officer)" to find it in DECISION_MODELS_EN
        const enKey = BAZI_TRANSLATIONS[structure];
        if (enKey && DECISION_MODELS_EN[enKey]) {
            return DECISION_MODELS_EN[enKey];
        }
        // Fallback if specific EN model not found
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

function getElementColor(element: string | undefined) {
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

function parseFourPillars(fourPillars: any) {
    if (!fourPillars) return null;

    // V6 Object Format
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

// ===== AVATAR MAPPING (使用 DiceBear API 動態生成頭像) =====
function getAvatarPath(citizenId: string, age: number, gender: string, name?: string): string {
    // 使用市民姓名或 ID 作為種子，確保同一人頭像一致
    const seed = name || citizenId;

    // 根據性別和年齡選擇適合的風格
    // micah 風格：Notion 風格，具備極高的現代感與差異度
    const style = 'micah';

    // 構建 DiceBear URL，添加性別和年齡相關參數
    // DiceBear 會根據 seed 生成一致的頭像
    return `https://api.dicebear.com/7.x/${style}/svg?seed=${encodeURIComponent(seed)}&backgroundColor=transparent`;
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

function translateGender(gender: string, market: string) {
    if (!gender) return "";
    return GENDER_TRANSLATIONS[gender]?.[market] || gender;
}

function translateMBTI(mbti: string, market: string) {
    if (!mbti) return mbti;
    // MBTI is usually the first trait
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

const I18N = {
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
        chart: "Element Chart", // Refined from 'Bazi Chart'
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
    "正官格": "Director", // Removed (Officer)
    "七殺格": "Challenger", // Replaced Pioneer (7-Killings)
    "正財格": "Financier", // Removed (Wealth)
    "偏財格": "Entrepreneur", // Removed (Windfall)
    "正印格": "Mentor", // Removed (Resource)
    "偏印格": "Strategist", // Removed (Owl)
    "食神格": "Creator", // Replaced Artist (Chef) -> Creator is better for "Eating God" concept of output/creation
    "傷官格": "Innovator", // Replaced Disruptor (Hurting)
    "建祿格": "Builder", // Removed (Prosperity)
    "羊刃格": "Commander", // Replaced Warrior (Blade) - Commander sounds more leadership focused
    "身強": "Strong",
    "身弱": "Weak",
    "中和": "Balanced",
    "金": "Metal", "木": "Wood", "水": "Water", "火": "Fire", "土": "Earth"
};

function translateBazi(text: string | undefined, market: string) {
    if (!text) return "";
    if (market === 'US') return BAZI_TRANSLATIONS[text] || text;
    if (market === 'CN') {
        const cn_mapping: Record<string, string> = {
            // Strength
            "身強": "身强", "身弱": "身弱", "中和": "中和", "極強": "极强", "極弱": "极弱",
            // Structures
            "比肩格": "比肩格", "劫財格": "劫财格", "食神格": "食神格", "傷官格": "伤官格",
            "偏財格": "偏财格", "正財格": "正财格", "七殺格": "七杀格", "正官格": "正官格",
            "偏印格": "偏印格", "正印格": "正印格", "建祿格": "建禄格", "羊刃格": "羊刃格",
            "從財格": "从财格", "從殺格": "从杀格", "從兒格": "从儿格", "專旺格": "专旺格", "從強格": "从强格",
            // Elements
            "金": "金", "木": "木", "水": "水", "火": "火", "土": "土"
        };
        return cn_mapping[text] || text;
    }
    return text;
}

function translatePillar(pillar: string, market: string) {
    if (!pillar) return "";
    if (market !== 'US') return pillar;

    // Attempt to split 2 chars
    const stem = pillar[0];
    const branch = pillar[1];

    const sEn = STEM_TRANSLATIONS[stem];
    const bEn = BRANCH_TRANSLATIONS[branch];

    if (sEn && bEn) {
        // Full translation: "Yang Wood Rat"
        // Or simplified: "Wood Rat" (The user asked for "Element Animal")
        // STEM_TRANSLATIONS has "Yang Wood". I will strip Yang/Yin for cleaner UI if desired?
        // User example was "Water Rooster", "Earth Sheep". So "Yang Wood" -> "Wood" is okay?
        // Actually "Yang Wood" is precise. "Wood Rat" is acceptably precise. 
        // Let's use the full one "Yang Wood Rat" or simplify to "Wood Rat"?
        // Current STEM_TRANSLATIONS has "Yang Wood".
        // Let's make it cleaner: just "Wood Rat"?
        // But "Yang/Yin" is important.
        // Let's try to detect if we want to shorten.
        // For now, return "Yang Wood Rat" - it sounds cool.
        // User example: "Water Rooster", "Earth Sheep". "Yang" is implied by the animal? No.
        // I'll stick to full "Yang Wood Rat" as it is very authentic but English.
        // Wait, user suggestion: "Earth Ox Phase". Just "Earth Ox". 
        // So I should probably strip polarity to be cleaner.
        const element = sEn.split(' ')[1]; // "Wood"
        return `${element} ${bEn}`;
    }
    return pillar;
}

// ===== COMPONENTS =====

function CitizenModal({ citizen, market, onClose }: { citizen: Citizen; market: 'TW' | 'US' | 'CN'; onClose: () => void }) {
    if (!citizen) return null;

    // Resolve Profile based on Market
    const activeProfile = citizen.profiles?.[market] || citizen.profiles?.['TW'];
    const display = {
        name: activeProfile?.name || citizen.name,
        job: activeProfile?.job || citizen.occupation,
        city: activeProfile?.city || citizen.location
    };
    const t = I18N[market] || I18N['TW'];

    const [showDetails, setShowDetails] = useState(false);
    const decisionModel = getDecisionModel(citizen.bazi_profile?.structure, market);
    const luckPillars = citizen.bazi_profile?.luck_pillars || [];
    const currentLuck = luckPillars.find(l => citizen.age >= l.age_start && citizen.age <= l.age_end) || luckPillars[0];

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
                    <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-full shrink-0">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div className="overflow-y-auto p-6 space-y-6 custom-scrollbar">
                    <section>
                        <div className="flex items-center gap-2 mb-3">
                            <span className="w-2 h-2 rounded-full bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.8)]"></span>
                            <h3 className="text-sm font-bold text-purple-400 uppercase tracking-widest">{t.current_state}</h3>
                        </div>
                        <div className="p-5 rounded-2xl bg-gradient-to-br from-purple-900/20 to-slate-900 border border-purple-500/30 text-slate-200 leading-relaxed text-lg shadow-inner">
                            {market === 'US' ? (
                                <span className="text-slate-300">
                                    {CURRENT_STATE_EN[citizen.bazi_profile.structure || ""] || "The analysis reflects a period of unique energy flow."}
                                </span>
                            ) : (
                                (citizen.bazi_profile as any).localized_state?.[market] || citizen.bazi_profile.current_state
                            )}
                        </div>
                    </section>

                    <section className="grid grid-cols-2 gap-4">
                        <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                            <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">{t.structure}</div>
                            <div className="text-xl font-black text-white">{translateBazi(citizen.bazi_profile.structure, market) || t.unknown}</div>
                        </div>
                        <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                            <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">{t.strength}</div>
                            <div className="text-xl font-black text-white">{translateBazi(citizen.bazi_profile.strength, market) || t.unknown}</div>
                        </div>
                        <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                            <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">{t.favorable}</div>
                            <div className="flex gap-1.5 flex-wrap">
                                {citizen.bazi_profile.favorable_elements?.map(e => (
                                    <span key={e} className="text-sm font-bold text-emerald-400">{translateBazi(e, market)}</span>
                                )) || <span className="text-slate-500">{t.none}</span>}
                            </div>
                        </div>
                        <div className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                            <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">{t.traits}</div>
                            <div className="text-xl font-black text-amber-400 truncate">{translateMBTI(citizen.traits?.[0] || "MBTI", market)}</div>
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
                                                <span className="text-slate-400 italic">Analysis available in report.</span>
                                            ) : (
                                                currentLuck?.localized_description?.[market] || currentLuck?.description || t.unknown
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
                                        const isCurrent = citizen.age >= pillar.age_start && citizen.age <= pillar.age_end;
                                        return (
                                            <div key={idx} className={`p-4 rounded-xl border transition-all ${isCurrent ? 'bg-purple-900/30 border-purple-500/50 shadow-[0_0_15px_rgba(168,85,247,0.1)]' : 'bg-slate-800/30 border-white/5 opacity-70 hover:opacity-100'}`}>
                                                <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-2">
                                                    <div className="flex items-center gap-3 min-w-[120px]">
                                                        <span className={`text-xs font-bold ${isCurrent ? 'text-purple-300' : 'text-slate-500'}`}>{pillar.age_start}-{pillar.age_end}{t.age}</span>
                                                        <span className={`text-lg font-bold ${isCurrent ? 'text-white' : 'text-slate-300'}`}>{translatePillar(pillar.pillar, market)}</span>
                                                    </div>
                                                    {isCurrent && <span className="text-[10px] bg-purple-500 text-white px-2 py-0.5 rounded-full font-bold tracking-wider">{t.current_tag}</span>}
                                                </div>
                                                {market !== 'US' && (pillar.localized_description?.[market] || pillar.description) && (
                                                    <div className={`text-sm leading-relaxed ${isCurrent ? 'text-purple-100' : 'text-slate-400'}`}>
                                                        {pillar.localized_description?.[market] || pillar.description}
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

    const [market, setMarket] = useState<'TW' | 'US' | 'CN'>('TW');

    const [debouncedSearch, setDebouncedSearch] = useState("")

    // Debounce search input
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(search)
            setPage(0) // Reset to page 0 when search changes
        }, 500)
        return () => clearTimeout(timer)
    }, [search])

    useEffect(() => {
        fetchCitizens()
    }, [page, debouncedSearch])

    const fetchCitizens = async () => {
        setLoading(true)
        try {
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const query = `limit=${limit}&offset=${page * limit}` + (debouncedSearch ? `&search=${encodeURIComponent(debouncedSearch)}` : "")
            const res = await fetch(`${API_BASE_URL}/citizens?${query}`)
            const data = await res.json()
            setCitizens(data.citizens || [])
            setTotal(data.total || 0)
        } catch (e) {
            console.error("Failed to fetch citizens:", e)
        }
        setLoading(false)
    }

    // Client-side filtering removed in favor of Server-side search
    const filteredCitizens = citizens

    // Helper to get active profile data
    const getProfile = (c: Citizen) => {
        // 優先讀取對應市場的 Profile，如果沒有則降級回原本的資料 (TW or root properties)
        const targetProfile = c.profiles?.[market];
        const fallbackProfile = c.profiles?.['TW'];

        // If explicitly TW market, return TW/Original
        if (market === 'TW') {
            return {
                name: fallbackProfile?.name || c.name,
                city: fallbackProfile?.city || c.location, // Note: User code used .city, my interface uses .city, root uses .location
                job: fallbackProfile?.job || c.occupation,
                pain: fallbackProfile?.pain
            }
        }

        // For US/CN, try target then fallback
        const active = targetProfile || fallbackProfile;

        return {
            name: active?.name || c.name,
            city: active?.city || c.location,
            job: active?.job || c.occupation,
            pain: active?.pain // Only target profile usually has relevant pain for that market, but fallback is ok
        }
    }

    const t = I18N[market] || I18N['TW'];

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
                                實時人口資料庫 • 總數: {total.toLocaleString()}
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
                        <div className="text-slate-500 font-mono text-sm">正在同步人口數據...</div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {filteredCitizens.map((citizen) => {
                            const pillars = parseFourPillars(citizen.bazi_profile.four_pillars || generateMockPillars());
                            const dayMasterElement = citizen.bazi_profile.element || "土";
                            const elementStyle = getElementColor(dayMasterElement);

                            // 🌍 Global Identity Context
                            const profile = getProfile(citizen);
                            const isReincarnated = market !== 'TW' && (citizen.profiles?.[market]?.name); // Check if data actually exists

                            return (
                                <div key={citizen.id} className="group relative bg-[#241a30] rounded-xl overflow-hidden border border-[#362b45] hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-purple-500/10">

                                    {/* Day Master Badge */}
                                    <div className="absolute top-3 right-3 z-20 flex flex-col items-end gap-1">
                                        <span className="text-[9px] text-gray-400 font-mono tracking-wider">日主</span>
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
                                                {citizen.age}歲
                                            </span>
                                        </div>
                                        <p className={`text-sm font-medium mb-1 uppercase tracking-wide ${elementStyle.text.replace('text-', 'text-').replace('-900', '-400')}`}>
                                            {profile.job}
                                        </p>

                                        {/* 🔥 Pain Point Badge with Tooltip Implementation */}
                                        {market !== 'TW' && profile.pain && (
                                            <div className="mt-3 group/tooltip relative">
                                                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-red-500/30 bg-red-500/10 text-[10px] font-bold text-red-300 cursor-help hover:bg-red-500/20 transition-colors">
                                                    <span>⚠️</span>
                                                    <span className="truncate max-w-[200px]">{profile.pain}</span>
                                                </div>

                                                {/* Custom Tooltip */}
                                                <div className="absolute bottom-full left-0 mb-2 w-48 p-2 bg-slate-900 border border-white/10 rounded-lg shadow-xl text-xs text-slate-300 opacity-0 group-hover/tooltip:opacity-100 transition-opacity pointer-events-none z-50">
                                                    <div className="font-bold text-white mb-1">此市民當前的核心焦慮</div>
                                                    {profile.pain}
                                                    <div className="absolute -bottom-1 left-4 w-2 h-2 bg-slate-900 border-b border-r border-white/10 rotate-45"></div>
                                                </div>
                                            </div>
                                        )}

                                        {/* Bazi Info (Only in TW Mode or if space allows) */}
                                        {market === 'TW' && (
                                            <p className="text-[10px] text-gray-500 mb-3">
                                                出生: {(() => {
                                                    const year = citizen.bazi_profile?.birth_year || (2026 - citizen.age);
                                                    const month = citizen.bazi_profile?.birth_month || citizen.bazi_profile?.birth_info?.month;
                                                    const day = citizen.bazi_profile?.birth_day || citizen.bazi_profile?.birth_info?.day;

                                                    if (year && month && day) {
                                                        return t.date_format(year, month, day);
                                                    }
                                                    return (year && month) ? `${year}年${month}月` : '未知';
                                                })()}
                                            </p>
                                        )}

                                        {/* Additional Info from Modal */}
                                        {citizen.bazi_profile.current_state && market === 'TW' && (
                                            <div className="mb-3 p-2 rounded-lg bg-purple-500/5 border border-purple-500/10">
                                                <div className="text-[9px] font-bold text-purple-400 uppercase tracking-widest mb-1">當前運勢</div>
                                                <div className="text-[11px] text-slate-300 line-clamp-2 leading-relaxed">
                                                    {citizen.bazi_profile.current_state}
                                                </div>
                                            </div>
                                        )}

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
                    </div>
                )}

                {/* Pagination */}
                <div className="mt-8 flex justify-center gap-4">
                    <button
                        onClick={() => setPage(p => Math.max(0, p - 1))}
                        disabled={page === 0}
                        className="px-4 py-2 bg-slate-800 rounded hover:bg-slate-700 disabled:opacity-50 text-sm"
                    >
                        {t.prev_page}
                    </button>
                    <span className="text-sm text-slate-500 py-2">
                        {t.page} {page + 1} / {Math.ceil(total / limit)}
                    </span>
                    <button
                        onClick={() => setPage(p => p + 1)}
                        disabled={(page + 1) * limit >= total}
                        className="px-4 py-2 bg-slate-800 rounded hover:bg-slate-700 disabled:opacity-50 text-sm"
                    >
                        {t.next_page}
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
