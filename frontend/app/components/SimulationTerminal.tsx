"use client"

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface SimulationLog {
    tick: number
    type: 'SYSTEM' | 'CITIZEN'
    tier?: number
    agent_name: string
    message: string
    sentiment?: 'positive' | 'negative' | 'neutral'
}

interface SimulationTerminalProps {
    logs: SimulationLog[]
    onComplete?: () => void
}

export default function SimulationTerminal({ logs, onComplete }: SimulationTerminalProps) {
    const [visibleLogs, setVisibleLogs] = useState<SimulationLog[]>([])
    const [sessionHex, setSessionHex] = useState("")
    const [mounted, setMounted] = useState(false)
    const terminalRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        setMounted(true)
        setSessionHex(Math.random().toString(16).slice(2, 10).toUpperCase())
    }, [])

    useEffect(() => {
        if (!mounted || !logs || logs.length === 0) return

        setVisibleLogs([]) // Reset if logs change
        let currentIndex = 0
        
        const interval = setInterval(() => {
            if (currentIndex < logs.length) {
                const nextLog = logs[currentIndex];
                if (nextLog) {
                    setVisibleLogs(prev => [...prev, nextLog])
                }
                currentIndex++
            } else {
                clearInterval(interval)
                if (onComplete) onComplete()
            }
        }, 500) // 500ms per line for better readability

        return () => clearInterval(interval)
    }, [logs, mounted, onComplete])

    // Auto scroll to bottom
    useEffect(() => {
        if (terminalRef.current) {
            terminalRef.current.scrollTop = terminalRef.current.scrollHeight
        }
    }, [visibleLogs])

    if (!mounted) return <div className="h-[400px] md:h-[600px] bg-black/90 rounded-3xl border border-white/10" />

    return (
        <div className="glass-panel rounded-3xl border border-white/10 bg-black/90 overflow-hidden flex flex-col h-[450px] md:h-[600px] shadow-2xl relative font-mono text-xs md:text-sm selection:bg-[#00ff00] selection:text-black">
            {/* Header */}
            <div className="flex items-center justify-between px-4 md:px-6 py-3 border-b border-white/5 bg-slate-900/80">
                <div className="flex items-center gap-3">
                    <div className="hidden md:flex gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" />
                        <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
                        <div className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
                    </div>
                    <span className="text-[8px] md:text-[10px] font-bold text-gray-500 uppercase tracking-[0.2em]">
                        MIRRA // MATRIX_CORE_v4.2.0
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-1 md:w-1.5 h-1 md:h-1.5 rounded-full bg-[#00ff00] animate-pulse shadow-[0_0_8px_#00ff00]" />
                    <span className="text-[8px] md:text-[10px] text-[#00ff00]/80">STREAMING</span>
                </div>
            </div>

            {/* Content Area */}
            <div 
                ref={terminalRef}
                className="flex-1 overflow-y-auto p-4 md:p-6 space-y-3 md:space-y-4 custom-scrollbar relative bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] bg-fixed"
            >
                {visibleLogs.length === 0 && (
                    <div className="flex items-center gap-2 text-[#00ff00]/50 animate-pulse">
                        <span className="text-lg md:text-xl">{'>'}</span>
                        <span className="text-[10px] md:text-xs uppercase tracking-[0.3em]">Establishing secure link...</span>
                    </div>
                )}

                {visibleLogs.map((log, idx) => {
                    if (!log) return null;
                    return (
                        <motion.div
                            key={`log-${idx}-${log.tick || 0}`}
                            initial={{ opacity: 0, y: 5 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex gap-4 items-start group"
                        >
                            <span className="text-gray-600 shrink-0 select-none font-mono text-xs pt-0.5">
                                {String(log.tick || 0).padStart(3, '0')}
                            </span>
                            
                            <div className="flex flex-col flex-1">
                                <div className="flex items-center gap-2">
                                    {(log.type === 'SYSTEM' || !log.type) ? (
                                        <span className="text-[#00ff00] font-black uppercase text-[10px] bg-[#00ff00]/10 border border-[#00ff00]/20 px-1.5 py-0.5 rounded shadow-[0_0_10px_rgba(0,255,0,0.2)]">
                                            SYSTEM
                                        </span>
                                    ) : (
                                        <span className={`font-black text-xs tracking-tight ${
                                            (log.tier === 1 || log.agent?.includes('1')) ? 'text-[#ffd700] drop-shadow-[0_0_5px_rgba(255,215,0,0.4)]' : 'text-[#00ffff] drop-shadow-[0_0_5px_rgba(0,255,255,0.4)]'
                                        }`}>
                                            {log.agent_name || log.agent || 'Unknown Agent'}{' '}T{log.tier || (log.agent?.includes('1') ? 1 : 3)}:
                                        </span>
                                    )}
                                </div>
                                <p className={`mt-1 leading-relaxed text-[13px] md:text-[14px] ${
                                    (log.type === 'SYSTEM' || !log.type) ? 'text-[#00ff00] italic font-medium' : 
                                    log.sentiment === 'positive' ? 'text-gray-100' :
                                    log.sentiment === 'negative' ? 'text-rose-400' :
                                    'text-gray-300'
                                }`}>
                                    {log.message || log.text || '...'}
                                </p>
                            </div>
                        </motion.div>
                    );
                })}

                {/* Blinking Cursor */}
                <div className="flex items-center gap-2 text-[#00ff00] mt-4 pt-2 border-t border-[#00ff00]/5">
                    <span className="animate-pulse font-black text-lg">{'>'}</span>
                    <span className="w-2 h-5 bg-[#00ff00] animate-[blink_1s_steps(2)_infinite] shadow-[0_0_10px_#00ff00]" />
                </div>
            </div>

            {/* Footer Stats */}
            <div className="px-6 py-2 border-t border-white/5 bg-black/40 flex justify-between items-center text-[10px] font-mono text-gray-500 tracking-widest">
                <div className="flex gap-6 uppercase">
                    <span className="flex items-center gap-1"><span className="w-1 h-1 bg-green-500 rounded-full" /> Link: Stable</span>
                    <span className="flex items-center gap-1"><span className="w-1 h-1 bg-blue-500 rounded-full" /> Buffer: 0ms</span>
                </div>
                <div className="text-[#00ff00]/40">
                    SID: 0x{sessionHex}
                </div>
            </div>

            {/* Matrix Scanline & Interlace Effect */}
            <div className="absolute inset-0 pointer-events-none opacity-[0.05] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%]" />
            <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-transparent via-white/[0.01] to-transparent h-20 w-full animate-[scan_4s_linear_infinite]" />
            
            <style jsx>{`
                @keyframes blink {
                    50% { opacity: 0; }
                }
                @keyframes scan {
                    0% { transform: translateY(-100%); }
                    100% { transform: translateY(600px); }
                }
                .custom-scrollbar::-webkit-scrollbar {
                    width: 4px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: transparent;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: rgba(0, 255, 0, 0.1);
                    border-radius: 10px;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: rgba(0, 255, 0, 0.3);
                }
            `}</style>
        </div>
    )
}
