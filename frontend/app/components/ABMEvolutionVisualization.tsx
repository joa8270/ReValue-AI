"use client"

import { motion } from "framer-motion"
import { useState } from "react"
import { useLanguage } from "@/app/context/LanguageContext"

interface ABMEvolutionProps {
    data: {
        rounds: number[]
        average_scores: number[]
        logs: string[]
        product_element?: string
        price_ratio?: number
    }
    analytics?: {
        consensus: number
        polarization: number
        herding_strength: number
        network_density: number
        element_preferences?: { [key: string]: number }
        element_initial_preferences?: { [key: string]: number }
        structure_preferences?: { [key: string]: number }
    }
}

export default function ABMEvolutionVisualization({ data, analytics }: ABMEvolutionProps) {
    const [selectedRound, setSelectedRound] = useState<number | null>(null)
    const { t } = useLanguage()

    if (!data || !data.rounds || data.rounds.length === 0) {
        return null
    }

    const maxScore = Math.max(...data.average_scores, 100)
    const minScore = Math.min(...data.average_scores, 0)
    const scoreRange = maxScore - minScore

    // 五行座標定義 (雷達圖)
    const elements = ["Wood", "Fire", "Earth", "Metal", "Water"]
    const getRadarPoints = (prefs: { [key: string]: number } | undefined) => {
        if (!prefs) return ""
        return elements.map((el, i) => {
            const score = prefs[el] || 50
            const angle = (i * 2 * Math.PI) / 5 - Math.PI / 2
            const r = (score / 100) * 40 // 半徑最大 40
            const x = 50 + r * Math.cos(angle)
            const y = 50 + r * Math.sin(angle)
            return `${x},${y}`
        }).join(" ")
    }

    return (
        <div className="bg-gradient-to-br from-slate-950 via-purple-950/20 to-slate-950 rounded-3xl p-8 border border-purple-500/20 shadow-2xl shadow-purple-900/20 space-y-10">
            {/* 標題 */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <div className="w-3 h-3 rounded-full bg-purple-500 shadow-[0_0_15px_rgba(168,85,247,0.8)] animate-pulse"></div>
                    <h3 className="text-2xl font-black text-white tracking-tight">
                        🧬 {t('report.abm.title')}
                    </h3>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-xs text-purple-400 bg-purple-500/10 px-3 py-1 rounded-full border border-purple-500/30 font-mono">
                        Agent-Based Modeling
                    </span>
                    <span className="text-xs text-cyan-400 bg-cyan-500/10 px-3 py-1 rounded-full border border-cyan-500/30 font-mono">
                        Bazi Integrated
                    </span>
                </div>
            </div>

            <p className="text-slate-300 text-sm leading-relaxed max-w-3xl">
                {t('report.abm.subtitle')}
            </p>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* 左側：演化趨勢圖 */}
                <div className="space-y-4">
                    <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                        <span className="w-4 h-[1px] bg-purple-500"></span>
                        {t('report.abm.evolution_log')}
                    </h4>
                    <div className="relative h-64 bg-slate-900/50 rounded-2xl p-6 border border-white/5">
                        {/* Y軸標籤 */}
                        <div className="absolute left-2 top-6 bottom-6 flex flex-col justify-between text-[10px] text-slate-500 font-mono">
                            <span>{maxScore.toFixed(0)}</span>
                            <span>{minScore.toFixed(0)}</span>
                        </div>

                        {/* 圖表區域 */}
                        <svg className="absolute left-10 top-6 right-6 bottom-8 w-[calc(100%-64px)] h-[calc(100%-56px)]" viewBox="0 0 100 100" preserveAspectRatio="none">
                            <line x1="0" y1="50" x2="100" y2="50" stroke="rgba(255,255,255,0.05)" strokeWidth="0.5" />

                            <motion.path
                                d={data.average_scores.map((score, i) => {
                                    const x = (i / (data.average_scores.length - 1)) * 100
                                    const y = 100 - ((score - minScore) / (scoreRange || 1)) * 100
                                    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
                                }).join(' ')}
                                fill="none"
                                stroke="url(#lineGradient)"
                                strokeWidth="3"
                                initial={{ pathLength: 0 }}
                                animate={{ pathLength: 1 }}
                                transition={{ duration: 2, ease: "easeInOut" }}
                            />
                            <defs>
                                <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stopColor="#a855f7" />
                                    <stop offset="100%" stopColor="#06b6d4" />
                                </linearGradient>
                            </defs>
                        </svg>

                        {/* 演化日誌滾動區 */}
                        <div className="absolute left-6 right-6 bottom-4 h-24 overflow-y-auto custom-scrollbar space-y-2 pr-2">
                            {data.logs.map((log, i) => (
                                <div key={i} className="text-sm text-slate-300 border-l-2 border-purple-500/50 pl-3 py-1.5 bg-white/5 rounded-r leading-relaxed">
                                    <span className="text-purple-400 mr-2 font-bold">[{i + 1}]</span> {log}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* 右側：五行契合度雷達圖 */}
                <div className="space-y-4">
                    <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                        <span className="w-4 h-[1px] bg-cyan-500"></span>
                        {t('report.abm.element_radar_title')}
                    </h4>
                    <div className="relative h-64 bg-slate-900/50 rounded-2xl flex items-center justify-center border border-white/5">
                        <div className="absolute top-4 left-6 text-xs text-slate-400 max-w-[200px] leading-relaxed">
                            {t('report.abm.element_radar_desc')}
                        </div>

                        <svg className="w-48 h-48" viewBox="0 0 100 100">
                            {/* 背景網格 */}
                            {[20, 40].map((r) => (
                                <circle key={r} cx="50" cy="50" r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="0.5" />
                            ))}
                            {elements.map((_, i) => {
                                const angle = (i * 2 * Math.PI) / 5 - Math.PI / 2
                                return (
                                    <line key={i} x1="50" y1="50" x2={50 + 40 * Math.cos(angle)} y2={50 + 40 * Math.sin(angle)} stroke="rgba(255,255,255,0.05)" strokeWidth="0.5" />
                                )
                            })}

                            {/* 初始契合度 (底部填充) */}
                            {analytics?.element_initial_preferences && (
                                <motion.polygon
                                    points={getRadarPoints(analytics.element_initial_preferences)}
                                    fill="rgba(168, 85, 247, 0.2)"
                                    stroke="rgba(168, 85, 247, 0.4)"
                                    strokeWidth="1"
                                    strokeDasharray="2,2"
                                />
                            )}

                            {/* 最終共鳴分數 (主填充) */}
                            {analytics?.element_preferences && (
                                <motion.polygon
                                    points={getRadarPoints(analytics.element_preferences)}
                                    fill="rgba(6, 182, 212, 0.3)"
                                    stroke="#06b6d4"
                                    strokeWidth="2"
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ duration: 1, delay: 0.5 }}
                                />
                            )}

                            {/* 標籤 */}
                            {elements.map((el, i) => {
                                const angle = (i * 2 * Math.PI) / 5 - Math.PI / 2
                                const x = 50 + 48 * Math.cos(angle)
                                const y = 50 + 48 * Math.sin(angle)
                                return (
                                    <text key={el} x={x} y={y} textAnchor="middle" dominantBaseline="middle" className="fill-slate-500 text-[6px] font-bold">
                                        {t(`report.elements.${el}.word`)}
                                    </text>
                                )
                            })}
                        </svg>

                        {/* 圖例 */}
                        <div className="absolute bottom-4 right-6 flex flex-col gap-1.5">
                            <div className="flex items-center gap-2 text-xs text-slate-300">
                                <span className="w-3 h-3 rounded-full bg-purple-500/40 border border-purple-500/60"></span>
                                {t('report.abm.initial_affinity')}
                            </div>
                            <div className="flex items-center gap-2 text-xs text-slate-300">
                                <span className="w-3 h-3 rounded-full bg-cyan-500 border border-cyan-400"></span>
                                {t('report.abm.final_resonance')}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* 格局分布圖 */}
            {analytics?.structure_preferences && (
                <div className="space-y-4">
                    <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                        <span className="w-4 h-[1px] bg-amber-500"></span>
                        {t('report.abm.structure_dist_title')}
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        {Object.entries(analytics.structure_preferences)
                            .sort((a, b) => b[1] - a[1]) // 由高到低排序
                            .slice(0, 10) // 最多顯示 10 個
                            .map(([struct, score]) => (
                                <div key={struct} className="bg-slate-900/40 p-4 rounded-xl border border-white/5 space-y-2">
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="text-slate-300 truncate max-w-[100px] font-medium">{struct}</span>
                                        <span className="text-amber-400 font-mono font-bold">{score.toFixed(0)}</span>
                                    </div>
                                    <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${score}%` }}
                                            className="h-full bg-gradient-to-r from-amber-600 to-amber-400"
                                        />
                                    </div>
                                </div>
                            ))}
                    </div>
                </div>
            )}

            {/* 突現行為分析指標 */}
            {analytics && (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 pt-8 border-t border-white/5">
                    {[
                        {
                            label: 'consensus', val: (analytics.consensus * 100).toFixed(0) + '%', color: 'cyan',
                            desc: analytics.consensus > 0.7 ? 'consensus_high' : analytics.consensus > 0.5 ? 'consensus_mid' : 'consensus_low'
                        },
                        {
                            label: 'polarization', val: (analytics.polarization * 100).toFixed(0) + '%', color: 'amber',
                            desc: analytics.polarization < 0.3 ? 'polarization_low' : analytics.polarization < 0.6 ? 'polarization_mid' : 'polarization_high'
                        },
                        {
                            label: 'herding_strength', val: analytics.herding_strength.toFixed(1), color: 'purple',
                            desc: analytics.herding_strength > 10 ? 'herding_strong' : analytics.herding_strength > 5 ? 'herding_mid' : 'herding_weak'
                        },
                        {
                            label: 'network_density', val: (analytics.network_density * 100).toFixed(1) + '%', color: 'slate',
                            desc: 'network_label'
                        }
                    ].map((item) => (
                        <div key={item.label} className={`p-5 rounded-2xl bg-${item.color}-500/5 border border-${item.color}-500/20`}>
                            <div className={`text-xs text-${item.color}-400 font-bold uppercase mb-2`}>{t(`report.abm.${item.label}`)}</div>
                            <div className="text-3xl font-black text-white">{item.val}</div>
                            <div className="text-sm text-slate-400 mt-2 leading-relaxed">{t(`report.abm.${item.desc}`)}</div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
