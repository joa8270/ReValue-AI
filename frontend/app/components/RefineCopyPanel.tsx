"use client"

import { useState } from "react"

interface RefineCopyPanelProps {
    simId: string
    currentCopy: string
    productName: string
    arenaComments: any[]
    style?: string
    sourceType?: string
}

export default function RefineCopyPanel({ simId, currentCopy, productName, arenaComments, style = "professional", sourceType = "image" }: RefineCopyPanelProps) {
    const [isRefining, setIsRefining] = useState(false)
    const [refineResult, setRefineResult] = useState<{ pain_points: string, refined_copy: string | any, marketing_copy?: string | any } | null>(null)

    // Helper to format content as plain text, even if it's an object/JSON
    const formatContent = (content: any): string => {
        if (!content) return "";
        if (typeof content === 'string') {
            // Check if string is actually a JSON string
            if (content.trim().startsWith('{') || content.trim().startsWith('[')) {
                try {
                    const parsed = JSON.parse(content);
                    return formatContent(parsed); // Recurse
                } catch (e) {
                    return content; // Not valid JSON, return as is
                }
            }
            return content;
        }
        if (typeof content === 'object') {
            // Flatten object values into a single string
            let text = "";
            // Common keys to prioritize
            const order = ['headline', 'title', 'body', 'content', 'call_to_action', 'cta', 'hashtags'];

            // First add prioritized keys
            order.forEach(key => {
                if (content[key]) {
                    text += content[key] + "\n\n";
                }
            });

            // Then add any other string values not in priority list
            Object.keys(content).forEach(key => {
                if (!order.includes(key) && typeof content[key] === 'string') {
                    // specific exclusion for internal keys if any
                    text += `【${key}】 ${content[key]}\n\n`;
                }
            });

            return text.trim() || JSON.stringify(content, null, 2); // Fallback if empty
        }
        return String(content);
    }

    const handleRefineCopy = async () => {
        if (!arenaComments || arenaComments.length === 0) {
            alert("暫無市民評論，無法進行優化")
            return
        }

        setIsRefining(true)
        try {
            // Use the exact API endpoint confirmed in web.py
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/web/refine-copy`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    sim_id: simId,
                    current_copy: currentCopy,
                    product_name: productName,
                    style: style,
                    source_type: sourceType
                })
            })

            if (!res.ok) throw new Error("API Request Failed")

            const result = await res.json()
            if (result.refined_copy) {
                setRefineResult(result)
            } else {
                alert("優化結果為空，請稍後再試")
            }
        } catch (e) {
            console.error("Refine Error", e)
            alert("優化失敗，請檢查後端日誌")
        } finally {
            setIsRefining(false)
        }
    }

    return (
        <div className="bg-[#1a1a1f] border border-[#7f13ec] rounded-2xl p-6 relative overflow-hidden group shadow-[0_0_20px_rgba(127,19,236,0.2)] mb-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-bold flex items-center gap-2">
                    <span className="material-symbols-outlined text-[#7f13ec]">auto_fix_high</span>
                    AI 文案優化
                </h3>
                {isRefining && <span className="text-xs text-[#7f13ec] animate-pulse">優化運算中...</span>}
            </div>

            {!refineResult ? (
                <button
                    onClick={handleRefineCopy}
                    disabled={isRefining}
                    className="w-full py-3 bg-[#7f13ec] hover:bg-[#6b10c6] text-white rounded-xl font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                    {isRefining ? '正在分析市民反饋...' : '根據反饋優化文案'}
                </button>
            ) : (
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4">
                    <div className="bg-rose-500/10 border border-rose-500/20 rounded-lg p-3">
                        <p className="text-xs text-rose-400 font-bold mb-1">發現痛點 / PAIN POINTS</p>
                        <p className="text-xs text-gray-300 leading-relaxed">{refineResult.pain_points}</p>
                    </div>
                    <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3 relative group">
                        <p className="text-xs text-emerald-400 font-bold mb-1 flex items-center gap-2">
                            <span className="material-symbols-outlined text-sm">lightbulb</span>
                            優化策略 / STRATEGIC ADVICE
                        </p>
                        <p className="text-xs text-gray-300 leading-relaxed whitespace-pre-wrap">{formatContent(refineResult.refined_copy)}</p>
                        <button
                            onClick={() => navigator.clipboard.writeText(formatContent(refineResult.refined_copy) || "")}
                            className="absolute top-2 right-2 p-1.5 bg-emerald-500/20 hover:bg-emerald-500 text-emerald-400 hover:text-white rounded-md transition-colors opacity-0 group-hover:opacity-100"
                            title="複製策略"
                        >
                            <span className="material-symbols-outlined text-sm">content_copy</span>
                        </button>
                    </div>

                    {/* 🌟 New Block: Ready-to-Use Marketing Copy */}
                    {refineResult.marketing_copy && (
                        <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-3 relative group mt-4">
                            <p className="text-xs text-purple-400 font-bold mb-1 flex items-center gap-2">
                                <span className="material-symbols-outlined text-sm">post_add</span>
                                實戰文案 / READY-TO-USE COPY
                            </p>
                            <div className="relative">
                                <p className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap font-medium">
                                    {formatContent(refineResult.marketing_copy)}
                                </p>
                                <button
                                    onClick={() => navigator.clipboard.writeText(formatContent(refineResult.marketing_copy) || "")}
                                    className="absolute top-0 right-0 p-1.5 bg-purple-500/20 hover:bg-purple-500 text-purple-400 hover:text-white rounded-md transition-colors opacity-0 group-hover:opacity-100"
                                    title="複製文案"
                                >
                                    <span className="material-symbols-outlined text-sm">content_copy</span>
                                </button>
                            </div>
                        </div>
                    )}
                    <button
                        onClick={() => setRefineResult(null)}
                        className="w-full text-xs text-gray-500 hover:text-white py-2 transition-colors"
                    >
                        重新優化
                    </button>
                </div>
            )}
        </div>
    )
}
