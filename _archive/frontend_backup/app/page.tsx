
import Link from 'next/link';

export default function Home() {
    return (
        <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-cyan-400 font-mono relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 z-0 opacity-20" style={{
                backgroundImage: 'linear-gradient(rgba(6,182,212,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(6,182,212,0.1) 1px, transparent 1px)',
                backgroundSize: '40px 40px'
            }}></div>

            <div className="relative z-10 max-w-3xl px-6 text-center space-y-8">
                {/* Logo / Header */}
                <div className="space-y-2">
                    <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500 drop-shadow-[0_0_15px_rgba(34,211,238,0.5)]">
                        MIRRA AI
                    </h1>
                    <p className="text-sm md:text-base text-cyan-300/70 tracking-[0.5em] uppercase">
                        Market Intelligence & Reality Rendering Agent
                    </p>
                </div>

                {/* Introduction Text */}
                <div className="p-8 border border-cyan-500/30 rounded-2xl bg-slate-900/60 backdrop-blur-sm shadow-2xl shadow-cyan-900/20">
                    <p className="text-lg md:text-xl leading-relaxed text-slate-300 mb-6 text-justify">
                        <strong className="text-white">MIRRA // 鏡界</strong> 是一個連接現實與平行世界的市場預演系統。
                    </p>
                    <p className="text-base md:text-lg leading-relaxed text-slate-400 text-justify">
                        在這裡，您可以將產品或商業計劃投入由 <span className="text-cyan-400">1,000+ 位 AI 虛擬市民</span> 構成的『鏡』像世『界』。
                        系統將透過大規模群體模擬，為您預先感知市場情緒、洞察潛在風險，甚至發現意想不到的商機。
                    </p>
                    <div className="mt-8 pt-6 border-t border-cyan-500/20 flex flex-col gap-3">
                        <p className="text-sm text-cyan-500/80 font-bold">
                            讓每一次決策，都經過未來的驗證。
                        </p>
                    </div>
                </div>

                {/* Call to Action */}
                <div className="space-y-4">
                    <div className="inline-block p-[2px] rounded-full bg-gradient-to-r from-cyan-500 to-purple-600">
                        <div className="px-6 py-3 rounded-full bg-slate-950 text-white text-sm font-bold tracking-wider flex items-center gap-2">
                            <span className="relative flex h-3 w-3">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
                            </span>
                            SYSTEM ONLINE // 請在 LINE 上傳圖片啟動戰情室
                        </div>
                    </div>

                    <div className="flex justify-center gap-4 text-xs text-slate-600">
                        <Link href="/citizens" className="hover:text-cyan-400 transition-colors">
                            查看市民資料庫
                        </Link>
                        <span>|</span>
                        <span>v1.0.5-stable</span>
                    </div>
                </div>
            </div>
        </div>
    )
}