import Link from 'next/link';
import { Suspense } from 'react';
import SimulationForm from './components/SimulationForm';

export default function Home() {
    return (
        <div className="min-h-screen bg-[#141118] font-sans antialiased text-white overflow-x-hidden">
            {/* Background Glow */}
            <div className="fixed inset-0 bg-hero-glow pointer-events-none z-0" />



            {/* Hero Section */}
            <section className="pt-32 md:pt-40 px-4 md:px-40 flex justify-center relative">
                <div className="max-w-[960px] w-full">
                    <div className="flex min-h-[420px] flex-col gap-6 md:gap-10 items-center justify-center p-8 relative overflow-hidden rounded-xl"
                        style={{
                            backgroundImage: 'linear-gradient(rgba(20, 17, 24, 0.7) 0%, rgba(20, 17, 24, 0.9) 100%), url("https://images.unsplash.com/photo-1639322537228-f710d846310a?w=1200&q=80")',
                            backgroundSize: 'cover',
                            backgroundPosition: 'center'
                        }}>
                        {/* Noise Overlay */}
                        <div className="absolute inset-0 noise-overlay" />

                        <div className="flex flex-col gap-4 text-center max-w-[800px] z-10">
                            {/* Status Badge */}
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-purple-500/30 bg-purple-500/10 mx-auto w-fit mb-2">
                                <span className="relative flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-500 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span>
                                </span>
                                <span className="text-xs font-medium text-purple-400 uppercase tracking-widest">系統上線</span>
                            </div>

                            {/* Main Title */}
                            <h1 className="text-glow text-4xl sm:text-5xl md:text-7xl font-black leading-[1.1] tracking-tight">
                                在<span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-purple-300">平行世界</span>中預演您的商業未來
                            </h1>

                            {/* Subtitle */}
                            <h2 className="text-gray-300 text-base md:text-lg font-light leading-relaxed max-w-[600px] mx-auto">
                                將您的產品部署給 1000 名自主 AI 市民。從未來獲取今日的市場回饋。
                            </h2>
                        </div>

                        {/* CTA Buttons */}
                        <div className="flex flex-wrap gap-4 justify-center z-10 mt-4">
                            <a href="#start" className="flex min-w-[140px] cursor-pointer items-center justify-center rounded-lg h-12 px-6 bg-purple-600 hover:bg-purple-500 transition-all hover:scale-105 text-white text-base font-bold shadow-[0_0_20px_rgba(127,19,236,0.4)]">
                                預演未來
                            </a>
                            <Link href="/citizens" className="flex min-w-[140px] cursor-pointer items-center justify-center rounded-lg h-12 px-6 bg-white/5 hover:bg-white/10 border border-white/10 backdrop-blur-sm transition-all text-white text-base font-bold">
                                <span className="mr-2">👥</span>
                                瀏覽市民
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats Panel */}
            <section className="px-4 md:px-40 flex justify-center py-5 -mt-10 relative z-20">
                <div className="max-w-[960px] w-full">
                    <div className="glass-panel rounded-xl p-1 mx-4 md:mx-8 shadow-2xl shadow-black/50">
                        <div className="flex flex-wrap md:flex-nowrap divide-y md:divide-y-0 md:divide-x divide-white/10">
                            {/* Stat 1 */}
                            <div className="flex flex-1 items-center gap-4 p-6 hover:bg-white/5 transition-colors group">
                                <div className="p-3 rounded-lg bg-purple-500/20 text-purple-400 group-hover:scale-110 transition-transform">
                                    <span className="text-2xl">👥</span>
                                </div>
                                <div className="flex flex-col">
                                    <p className="text-gray-400 text-xs uppercase tracking-wider font-medium">活躍市民</p>
                                    <p className="text-white text-2xl font-bold leading-tight tabular-nums">1,000</p>
                                </div>
                            </div>
                            {/* Stat 2 */}
                            <div className="flex flex-1 items-center gap-4 p-6 hover:bg-white/5 transition-colors group">
                                <div className="p-3 rounded-lg bg-blue-500/20 text-blue-400 group-hover:scale-110 transition-transform">
                                    <span className="text-2xl">🔄</span>
                                </div>
                                <div className="flex flex-col">
                                    <p className="text-gray-400 text-xs uppercase tracking-wider font-medium">預演運行中</p>
                                    <p className="text-white text-2xl font-bold leading-tight tabular-nums">124</p>
                                </div>
                            </div>
                            {/* Stat 3 */}
                            <div className="flex flex-1 items-center gap-4 p-6 hover:bg-white/5 transition-colors group">
                                <div className="p-3 rounded-lg bg-emerald-500/20 text-emerald-400 group-hover:scale-110 transition-transform">
                                    <span className="text-2xl">📈</span>
                                </div>
                                <div className="flex flex-col">
                                    <p className="text-gray-400 text-xs uppercase tracking-wider font-medium">預演準確度</p>
                                    <p className="text-white text-2xl font-bold leading-tight tabular-nums">98%</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Simulation Form Section */}
            <section id="start" className="px-4 md:px-40 flex justify-center py-16 relative z-10">
                <div className="max-w-[960px] w-full">
                    <Suspense fallback={<div className="h-[600px] flex items-center justify-center text-white"><span className="animate-spin text-4xl">🌀</span></div>}>
                        <SimulationForm />
                    </Suspense>
                </div>
            </section>

            {/* How It Works Section */}
            <section id="how-it-works" className="px-4 md:px-40 flex justify-center py-16 md:py-24 relative overflow-hidden">
                <div className="absolute top-1/2 left-0 w-64 h-64 bg-purple-500/10 rounded-full blur-[100px] pointer-events-none" />
                <div className="max-w-[960px] w-full z-10">
                    <div className="flex flex-col gap-12 px-4">
                        {/* Section Header */}
                        <div className="flex flex-col gap-4 text-center items-center">
                            <h2 className="text-white tracking-tight text-3xl md:text-4xl font-bold leading-tight max-w-[720px]">
                                預演如何運作
                            </h2>
                            <p className="text-gray-400 text-base md:text-lg font-light leading-relaxed max-w-[600px]">
                                3個簡單步驟，即可在平行世界中預言您的產品/商業計畫成敗。
                            </p>
                        </div>

                        {/* Steps Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Step 1 */}
                            <div className="glass-panel group p-6 rounded-xl border border-white/5 hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1">
                                <div className="mb-6 inline-flex items-center justify-center w-12 h-12 rounded-lg bg-[#2a2435] text-white group-hover:bg-purple-600 group-hover:shadow-[0_0_15px_rgba(127,19,236,0.6)] transition-all duration-300">
                                    <span className="text-xl">⚙️</span>
                                </div>
                                <div className="flex flex-col gap-3">
                                    <h3 className="text-white text-xl font-bold leading-tight">1. 上傳產品</h3>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        只需上傳產品圖片或商業計畫書，AI 會自動理解您的產品特性與定位。
                                    </p>
                                </div>
                            </div>

                            {/* Step 2 */}
                            <div className="glass-panel group p-6 rounded-xl border border-white/5 hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1">
                                <div className="mb-6 inline-flex items-center justify-center w-12 h-12 rounded-lg bg-[#2a2435] text-white group-hover:bg-purple-600 group-hover:shadow-[0_0_15px_rgba(127,19,236,0.6)] transition-all duration-300">
                                    <span className="text-xl">🤖</span>
                                </div>
                                <div className="flex flex-col gap-3">
                                    <h3 className="text-white text-xl font-bold leading-tight">2. 八字科學取樣</h3>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        從 1000 位具有八字命理性格的 AI 市民中，隨機抽取代表進行預演評估。
                                    </p>
                                </div>
                            </div>

                            {/* Step 3 */}
                            <div className="glass-panel group p-6 rounded-xl border border-white/5 hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1">
                                <div className="mb-6 inline-flex items-center justify-center w-12 h-12 rounded-lg bg-[#2a2435] text-white group-hover:bg-purple-600 group-hover:shadow-[0_0_15px_rgba(127,19,236,0.6)] transition-all duration-300">
                                    <span className="text-xl">📊</span>
                                </div>
                                <div className="flex flex-col gap-3">
                                    <h3 className="text-white text-xl font-bold leading-tight">3. 戰情分析</h3>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        即時獲得購買意願分數、消費者心聲，以及針對不同性格族群的行銷建議。
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Why Bazi Section */}
            <section id="why-bazi" className="px-4 md:px-40 flex justify-center py-16 md:py-24 relative overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-gradient-to-b from-purple-500/5 to-transparent rounded-full blur-[100px] pointer-events-none" />
                <div className="max-w-[960px] w-full z-10">
                    <div className="flex flex-col gap-12 px-4">
                        {/* Section Header */}
                        <div className="flex flex-col gap-4 text-center items-center">
                            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-amber-500/30 bg-amber-500/10 mb-2">
                                <span className="text-amber-400">☯️</span>
                                <span className="text-xs font-bold text-amber-400 uppercase tracking-widest">科學基礎</span>
                            </div>
                            <h2 className="text-white tracking-tight text-3xl md:text-4xl font-bold leading-tight max-w-[720px]">
                                為什麼選擇「<span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-400">八字</span>」作為人格模型？
                            </h2>
                            <p className="text-gray-400 text-base md:text-lg font-light leading-relaxed max-w-[650px]">
                                這不是迷信，而是人類最古老的行為統計學。
                            </p>
                        </div>

                        {/* Content Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Card 1: Statistical Evidence */}
                            <div className="glass-panel p-6 rounded-xl border border-amber-500/20 hover:border-amber-500/40 transition-all duration-300">
                                <div className="flex flex-col gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-amber-500/10 flex items-center justify-center text-2xl">
                                        📊
                                    </div>
                                    <h3 className="text-white text-lg font-bold">千年統計實證</h3>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        八字系統是中華文化<span className="text-amber-400 font-medium">數千年</span>對出生時間、性格、行為模式的觀察與歸納。如同西方心理學的 <span className="text-cyan-400">MBTI</span> 或 <span className="text-cyan-400">Big Five</span> 人格理論，只是樣本量更大、時間跨度更長。
                                    </p>
                                </div>
                            </div>

                            {/* Card 2: Time Dimension */}
                            <div className="glass-panel p-6 rounded-xl border border-purple-500/20 hover:border-purple-500/40 transition-all duration-300">
                                <div className="flex flex-col gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-purple-500/10 flex items-center justify-center text-2xl">
                                        ⏳
                                    </div>
                                    <h3 className="text-white text-lg font-bold">時間維度的人格變化</h3>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        八字獨特之處在於「<span className="text-purple-400 font-medium">大運</span>」系統——人的性格、決策模式會隨<span className="text-purple-400 font-medium">年齡階段</span>產生可預測的變化。這是 MBTI 等靜態模型所欠缺的動態維度。
                                    </p>
                                </div>
                            </div>

                            {/* Card 3: Consumer Behavior */}
                            <div className="glass-panel p-6 rounded-xl border border-cyan-500/20 hover:border-cyan-500/40 transition-all duration-300">
                                <div className="flex flex-col gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-cyan-500/10 flex items-center justify-center text-2xl">
                                        🛒
                                    </div>
                                    <h3 className="text-white text-lg font-bold">消費決策的行為模式</h3>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        不同「格局」的人在購買決策時，有統計上可辨識的偏好：<span className="text-emerald-400">正財格</span>重視 CP 值、<span className="text-rose-400">傷官格</span>追求獨特、<span className="text-amber-400">食神格</span>注重體驗感受。
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Bottom Quote */}
                        <div className="text-center">
                            <p className="text-slate-500 text-sm italic max-w-[600px] mx-auto">
                                「八字不預測命運，而是描繪<span className="text-slate-400">性格傾向</span>——我們用它來預演<span className="text-slate-400">一千種不同的消費人格</span>如何看待您的產品。」
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="px-4 md:px-40 flex justify-center py-16 md:py-24 relative overflow-hidden">
                <div className="absolute top-1/2 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-[100px] pointer-events-none" />
                <div className="max-w-[960px] w-full z-10">
                    <div className="flex flex-col gap-12 px-4">
                        {/* Section Header */}
                        <div className="flex flex-col gap-4 text-center items-center">
                            <h2 className="text-white tracking-tight text-3xl md:text-4xl font-bold leading-tight">
                                選擇適合您的方案
                            </h2>
                            <p className="text-gray-400 text-base md:text-lg font-light leading-relaxed max-w-[600px]">
                                從免費體驗開始，隨時升級以獲得更多功能與預演次數。
                            </p>
                        </div>

                        {/* Pricing Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Free Tier */}
                            <div className="glass-panel p-6 rounded-xl border border-white/5 hover:border-purple-500/30 transition-all duration-300">
                                <div className="flex flex-col gap-4">
                                    <div>
                                        <h3 className="text-white text-xl font-bold">免費體驗</h3>
                                        <p className="text-gray-400 text-sm">適合初次探索</p>
                                    </div>
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-white text-4xl font-bold">NT$0</span>
                                        <span className="text-gray-500 text-sm">/月</span>
                                    </div>
                                    <ul className="flex flex-col gap-2 text-sm text-gray-400">
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> 每月 3 次預演</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> 基礎報告分析</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> 100 位 AI 市民</li>
                                        <li className="flex items-center gap-2 text-gray-600"><span>✗</span> 進階洞察</li>
                                    </ul>
                                    <a href="#start" className="mt-4 w-full py-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-white text-center font-bold transition-all">
                                        開始免費試用
                                    </a>
                                </div>
                            </div>

                            {/* Pro Tier */}
                            <div className="glass-panel p-6 rounded-xl border-2 border-purple-500 transition-all duration-300 relative">
                                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-purple-600 text-white text-xs font-bold rounded-full">
                                    最受歡迎
                                </div>
                                <div className="flex flex-col gap-4">
                                    <div>
                                        <h3 className="text-white text-xl font-bold">專業版 Pro</h3>
                                        <p className="text-gray-400 text-sm">適合創業者與小型團隊</p>
                                    </div>
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-white text-4xl font-bold">NT$299</span>
                                        <span className="text-gray-500 text-sm">/月</span>
                                    </div>
                                    <ul className="flex flex-col gap-2 text-sm text-gray-400">
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> 每月 50 次預演</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> 完整報告 + AI 建議</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> 1,000 位 AI 市民</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> 歷史紀錄儀表板</li>
                                    </ul>
                                    <a href="#start" className="mt-4 w-full py-3 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-center font-bold transition-all shadow-[0_0_15px_rgba(127,19,236,0.4)]">
                                        升級 Pro
                                    </a>
                                </div>
                            </div>

                            {/* Enterprise Tier */}
                            <div className="glass-panel p-6 rounded-xl border border-white/5 hover:border-purple-500/30 transition-all duration-300">
                                <div className="flex flex-col gap-4">
                                    <div>
                                        <h3 className="text-white text-xl font-bold">企業版 Enterprise</h3>
                                        <p className="text-gray-400 text-sm">適合大型組織</p>
                                    </div>
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-white text-4xl font-bold">聯繫我們</span>
                                    </div>
                                    <ul className="flex flex-col gap-2 text-sm text-gray-400">
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> 無限次預演</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> 專屬客戶經理</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> 自訂 AI 市民人數</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> API 整合支援</li>
                                    </ul>
                                    <a href="mailto:contact@mirra.ai" className="mt-4 w-full py-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-white text-center font-bold transition-all">
                                        聯繫銷售團隊
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="px-4 md:px-40 flex justify-center py-5 mt-auto border-t border-white/5 bg-[#0f0c12]">
                <div className="max-w-[960px] w-full">
                    <div className="flex flex-col gap-8 px-5 py-10 text-center md:text-left">
                        <div className="flex flex-col md:flex-row justify-between items-center md:items-start gap-8">
                            <div className="flex flex-col gap-4 items-center md:items-start">
                                <div className="flex items-center gap-2 text-white">
                                    <span className="text-purple-500 text-xl">∞</span>
                                    <h2 className="text-lg font-bold">MIRRA</h2>
                                </div>
                                <p className="text-gray-500 text-sm max-w-[300px]">預演未來，為今日做出更好的決策。</p>
                            </div>
                            <div className="flex flex-wrap items-center justify-center gap-6 md:gap-10">
                                <div className="flex items-center gap-1">
                                    <a className="text-gray-400 hover:text-purple-400 transition-colors text-sm font-medium" href="#">文件</a>
                                    <span className="text-[10px] px-1.5 py-0.5 bg-purple-500/20 text-purple-400 rounded-full">即將推出</span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <a className="text-gray-400 hover:text-purple-400 transition-colors text-sm font-medium" href="#">API 存取</a>
                                    <span className="text-[10px] px-1.5 py-0.5 bg-purple-500/20 text-purple-400 rounded-full">即將推出</span>
                                </div>
                                <a className="text-gray-400 hover:text-purple-400 transition-colors text-sm font-medium" href="#">服務條款</a>
                            </div>
                        </div>
                        <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
                            <p className="text-gray-600 text-xs">© 2026 MIRRA AI. 保留所有權利。</p>
                            <p className="text-gray-600 text-xs">v1.0.5-stable</p>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    )
}