"use client"

import { motion, AnimatePresence } from "framer-motion"
import { X, Brain, Activity, Database, Sparkles, Compass, Scroll } from "lucide-react"

interface MethodologyModalProps {
    isOpen: boolean
    onClose: () => void
}

export default function MethodologyModal({ isOpen, onClose }: MethodologyModalProps) {
    if (!isOpen) return null

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
                {/* Backdrop */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-black/80 backdrop-blur-md"
                />

                {/* Modal Content */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 20 }}
                    className="relative w-full max-w-4xl bg-[#130f1a] border border-[#302839] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
                >
                    {/* Header */}
                    <div className="flex items-center justify-between p-6 border-b border-white/5 bg-[#1a1423]">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-purple-500/20 rounded-lg">
                                <Brain className="w-5 h-5 text-purple-400" />
                            </div>
                            <h2 className="text-xl font-bold text-white">東方命理 x 西方科學：雙軌驗證架構</h2>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Body */}
                    <div className="flex-1 overflow-y-auto p-6 md:p-8">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
                            {/* Center Divider styling (Desktop) */}
                            <div className="hidden md:block absolute left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-white/10 to-transparent -translate-x-1/2" />

                            {/* Left Column: Western Science */}
                            <div className="space-y-6">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="px-2 py-1 rounded bg-cyan-500/10 text-cyan-400 text-xs font-bold uppercase tracking-wider">Track A</span>
                                    <h3 className="text-lg font-bold text-white">西方科學 (Western Science)</h3>
                                </div>

                                <div className="p-5 rounded-xl bg-cyan-950/20 border border-cyan-500/20 space-y-4">
                                    <div className="flex gap-4">
                                        <div className="mt-1 p-2 bg-cyan-500/10 rounded-lg h-fit">
                                            <Activity className="w-5 h-5 text-cyan-400" />
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-cyan-100">Agent-Based Modeling (ABM)</h4>
                                            <p className="text-sm text-gray-400 mt-1 leading-relaxed">
                                                建構 1,000 個獨立決策的 AI 代理人，模擬複雜市場互動。當樣本數大於 1,000 時，我們能在 <span className="text-cyan-400">95% 信賴區間</span> 內精準預測群體行為。
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex gap-4">
                                        <div className="mt-1 p-2 bg-cyan-500/10 rounded-lg h-fit">
                                            <Database className="w-5 h-5 text-cyan-400" />
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-cyan-100">扎根理論 (Grounded Theory)</h4>
                                            <p className="text-sm text-gray-400 mt-1 leading-relaxed">
                                                不預設成見，讓資料「自己說話」。透過對海量模擬對話進行編碼與歸納，挖掘出顯著的市場模式 (Patterns) 與關鍵洞察。
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Right Column: Eastern Metaphysics */}
                            <div className="space-y-6">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="px-2 py-1 rounded bg-amber-500/10 text-amber-400 text-xs font-bold uppercase tracking-wider">Track B</span>
                                    <h3 className="text-lg font-bold text-white">東方八字科學 (Science)</h3>
                                </div>

                                <div className="p-5 rounded-xl bg-amber-950/20 border border-amber-500/20 space-y-4">
                                    <div className="flex gap-4">
                                        <div className="mt-1 p-2 bg-amber-500/10 rounded-lg h-fit">
                                            <Compass className="w-5 h-5 text-amber-400" />
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-amber-100">八字人格模型 (Bazi Personality)</h4>
                                            <p className="text-sm text-gray-400 mt-1 leading-relaxed">
                                                利用千年統計學構建 <span className="text-amber-400">10 種人格原型 (格局)</span>，比 MBTI 更精準地模擬消費者的深層價值觀與決策邏輯。
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex gap-4">
                                        <div className="mt-1 p-2 bg-amber-500/10 rounded-lg h-fit">
                                            <Scroll className="w-5 h-5 text-amber-400" />
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-amber-100">流年大運 (Time Cycles)</h4>
                                            <p className="text-sm text-gray-400 mt-1 leading-relaxed">
                                                引入「時間」變數。同一個人在不同大運（Luck Cycle）下，對同一產品的反應會截然不同，模擬真實市場的動態性。
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Synthesis Section */}
                        <div className="mt-8 pt-8 border-t border-white/5">
                            <div className="bg-gradient-to-r from-purple-900/40 to-indigo-900/40 border border-purple-500/30 p-6 rounded-xl flex flex-col md:flex-row items-center gap-6 text-center md:text-left">
                                <div className="p-4 bg-purple-500 rounded-full shadow-[0_0_20px_rgba(168,85,247,0.4)]">
                                    <Sparkles className="w-8 h-8 text-white" />
                                </div>
                                <div className="flex-1">
                                    <h4 className="text-lg font-bold text-white mb-2">MIRRA 下一代預演引擎</h4>
                                    <p className="text-gray-300 text-sm leading-relaxed">
                                        這不是玄學，而是將<span className="text-white font-bold">「人性算力化」</span>。我們將古老的命理結構轉譯為現代 AI 的 Prompt Engineering 參數，<strong className="text-white">融合西方「方法論」的快速迭代邏輯，建立「假設 — 驗證 — 修正」的科學閉環。</strong>透過這種循環強化商業週期，創造出具有真實靈魂與偏好的虛擬市民群體。
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    )
}
