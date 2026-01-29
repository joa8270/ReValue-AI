"use client"

import Link from 'next/link';
import { Suspense } from 'react';
import SimulationForm from './components/SimulationForm';
import { useLanguage } from './context/LanguageContext';

export default function Home() {
    const { t, language } = useLanguage();

    return (
        <div className="min-h-screen bg-[#141118] font-sans antialiased text-white overflow-x-hidden">
            {/* Background Glow */}
            <div className="fixed inset-0 bg-hero-glow pointer-events-none z-0" />

            {/* Hero Section */}
            <section className="pt-32 md:pt-40 px-4 md:px-40 flex justify-center relative">
                <div className="max-w-[1200px] w-full">
                    <div className="flex min-h-[500px] flex-col gap-6 md:gap-10 items-start justify-center p-8 relative overflow-hidden rounded-xl"
                        style={{
                            backgroundImage: 'linear-gradient(rgba(20, 17, 24, 0.7) 0%, rgba(20, 17, 24, 0.9) 100%), url("https://images.unsplash.com/photo-1639322537228-f710d846310a?w=1200&q=80")',
                            backgroundSize: 'cover',
                            backgroundPosition: 'center'
                        }}>
                        {/* Noise Overlay */}
                        <div className="absolute inset-0 noise-overlay" />

                        <div className="flex flex-col gap-4 text-left max-w-[900px] z-10">
                            {/* Status Badge */}
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-purple-500/30 bg-purple-500/10 mb-2 w-fit">
                                <span className="relative flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-500 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span>
                                </span>
                                <span className="text-xs font-medium text-purple-400 uppercase tracking-widest">{t('hero.status')}</span>
                            </div>

                            {/* Main Title */}
                            {/* RWD Note: using text-xl on mobile to accommodate longer text */}
                            <h1 className="text-glow text-xl sm:text-3xl md:text-5xl font-black leading-[1.5] tracking-tight mb-4 break-words">
                                {t('hero.title_prefix')}<span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-purple-300 mx-1">{t('hero.title_highlight')}</span>{t('hero.title_suffix')}
                            </h1>

                            {/* Subtitle */}
                            <h2 className="text-gray-300 text-base md:text-lg font-light leading-relaxed max-w-[700px]">
                                {t('hero.subtitle')}
                            </h2>

                            {/* Trust Anchor */}
                            <a
                                href="https://en.wikipedia.org/wiki/Agent-based_model"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 text-xs md:text-sm text-blue-400/80 hover:text-blue-300 hover:underline transition-colors mt-2"
                            >
                                <span>🧠</span>
                                {t('hero.trust_anchor')}
                                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            </a>
                        </div>

                        {/* CTA Buttons */}
                        <div className="flex flex-wrap gap-4 justify-start z-10 mt-4">
                            <a href="#start" className="flex min-w-[140px] cursor-pointer items-center justify-center rounded-lg h-12 px-6 bg-purple-600 hover:bg-purple-500 transition-all hover:scale-105 text-white text-base font-bold shadow-[0_0_20px_rgba(127,19,236,0.4)]">
                                {t('hero.cta_primary')}
                            </a>
                            <Link href="/citizens" className="flex min-w-[140px] cursor-pointer items-center justify-center rounded-lg h-12 px-6 bg-white/5 hover:bg-white/10 border border-white/10 backdrop-blur-sm transition-all text-white text-base font-bold">
                                <span className="mr-2">👥</span>
                                {t('hero.cta_secondary')}
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
                                    <p className="text-gray-400 text-xs uppercase tracking-wider font-medium">{t('stats.active_citizens')}</p>
                                    <p className="text-white text-2xl font-bold leading-tight tabular-nums">1,000</p>
                                </div>
                            </div>
                            {/* Stat 2 */}
                            <div className="flex flex-1 items-center gap-4 p-6 hover:bg-white/5 transition-colors group">
                                <div className="p-3 rounded-lg bg-blue-500/20 text-blue-400 group-hover:scale-110 transition-transform">
                                    <span className="text-2xl">🔄</span>
                                </div>
                                <div className="flex flex-col">
                                    <p className="text-gray-400 text-xs uppercase tracking-wider font-medium">{t('stats.running_simulations')}</p>
                                    <p className="text-white text-2xl font-bold leading-tight tabular-nums">124</p>
                                </div>
                            </div>
                            {/* Stat 3 */}
                            <div className="flex flex-1 items-center gap-4 p-6 hover:bg-white/5 transition-colors group">
                                <div className="p-3 rounded-lg bg-emerald-500/20 text-emerald-400 group-hover:scale-110 transition-transform">
                                    <span className="text-2xl">📈</span>
                                </div>
                                <div className="flex flex-col">
                                    <p className="text-gray-400 text-xs uppercase tracking-wider font-medium">{t('stats.accuracy')}</p>
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
                        <div className="flex flex-col gap-4 text-left items-start">
                            <h2 className="text-white tracking-tight text-3xl md:text-4xl font-bold leading-tight max-w-[720px]">
                                {t('how_it_works.title')}
                            </h2>
                            <p className="text-gray-400 text-base md:text-lg font-light leading-relaxed max-w-[600px]">
                                {t('how_it_works.subtitle')}
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
                                    <h3 className="text-white text-xl font-bold leading-tight">{t('how_it_works.step1_title')}</h3>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        {t('how_it_works.step1_desc')}
                                    </p>
                                </div>
                            </div>

                            {/* Step 2 */}
                            <div className="glass-panel group p-6 rounded-xl border border-white/5 hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1">
                                <div className="mb-6 inline-flex items-center justify-center w-12 h-12 rounded-lg bg-[#2a2435] text-white group-hover:bg-purple-600 group-hover:shadow-[0_0_15px_rgba(127,19,236,0.6)] transition-all duration-300">
                                    <span className="text-xl">🤖</span>
                                </div>
                                <div className="flex flex-col gap-3">
                                    <h3 className="text-white text-xl font-bold leading-tight">{t('how_it_works.step2_title')}</h3>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        {t('how_it_works.step2_desc')}
                                    </p>
                                </div>
                            </div>

                            {/* Step 3 */}
                            <div className="glass-panel group p-6 rounded-xl border border-white/5 hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1">
                                <div className="mb-6 inline-flex items-center justify-center w-12 h-12 rounded-lg bg-[#2a2435] text-white group-hover:bg-purple-600 group-hover:shadow-[0_0_15px_rgba(127,19,236,0.6)] transition-all duration-300">
                                    <span className="text-xl">📊</span>
                                </div>
                                <div className="flex flex-col gap-3">
                                    <h3 className="text-white text-xl font-bold leading-tight">{t('how_it_works.step3_title')}</h3>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        {t('how_it_works.step3_desc')}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Scientific Basis Section */}
            <section id="why-bazi" className="px-4 md:px-40 flex justify-center py-16 md:py-24 relative overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-gradient-to-b from-purple-500/5 to-transparent rounded-full blur-[100px] pointer-events-none" />
                <div className="max-w-[960px] w-full z-10">
                    <div className="flex flex-col gap-12 px-4">
                        {/* Section Header */}
                        <div className="flex flex-col gap-4 text-left items-start">
                            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-purple-500/30 bg-purple-500/10 mb-2">
                                <span className="text-purple-400">⚡</span>
                                <span className="text-xs font-bold text-purple-400 uppercase tracking-widest">{t('scientific_basis.badge')}</span>
                            </div>
                            <h2 className="text-white tracking-tight text-3xl md:text-4xl font-bold leading-tight max-w-[720px]">
                                {t('scientific_basis.title_prefix')}<span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">{t('scientific_basis.title_highlight')}</span>{t('scientific_basis.title_suffix')}
                            </h2>
                            <p className="text-gray-400 text-base md:text-lg font-light leading-relaxed max-w-[650px]">
                                {t('scientific_basis.subtitle')}
                            </p>
                        </div>




                        {/* Content Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Card 1 */}
                            <div className="glass-panel p-6 rounded-xl border border-blue-500/20 hover:border-blue-500/40 transition-all duration-300">
                                <div className="flex flex-col gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center text-2xl">
                                        🌐
                                    </div>
                                    <h3 className="text-white text-lg font-bold">{t('scientific_basis.card1_title')}</h3>
                                    <p className="text-blue-400 font-mono text-xs uppercase tracking-wider mb-1">{t('scientific_basis.card1_subtitle')}</p>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        {t('scientific_basis.card1_desc')}
                                    </p>
                                    <a href="https://en.wikipedia.org/wiki/Agent-based_model" target="_blank" className="text-xs text-blue-400/70 hover:text-blue-400 hover:underline mt-2">{t('scientific_basis.card1_link')}</a>
                                </div>
                            </div>

                            {/* Card 2 */}
                            <div className="glass-panel p-6 rounded-xl border border-amber-500/20 hover:border-amber-500/40 transition-all duration-300">
                                <div className="flex flex-col gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-amber-500/10 flex items-center justify-center text-2xl">
                                        🧠
                                    </div>
                                    <h3 className="text-white text-lg font-bold">{t('scientific_basis.card2_title')}</h3>
                                    <p className="text-amber-400 font-mono text-xs uppercase tracking-wider mb-1">{t('scientific_basis.card2_subtitle')}</p>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        {t('scientific_basis.card2_desc_p1')}
                                        <a
                                            href={language === 'zh-CN' ? 'https://baike.baidu.com/item/八字' : 'https://zh.wikipedia.org/zh-tw/八字'}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-amber-400/80 hover:text-amber-300 underline decoration-amber-500/30 hover:decoration-amber-300 transition-colors"
                                        >
                                            {t('scientific_basis.card2_desc_link1')}
                                        </a>
                                        {t('scientific_basis.card2_desc_p2')}
                                        <a
                                            href={language === 'zh-CN' ? 'https://baike.baidu.com/item/MBTI' : 'https://zh.wikipedia.org/zh-tw/邁爾斯-布里格斯性格分類法'}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-amber-400/80 hover:text-amber-300 underline decoration-amber-500/30 hover:decoration-amber-300 transition-colors"
                                        >
                                            {t('scientific_basis.card2_desc_link2')}
                                        </a>
                                        {t('scientific_basis.card2_desc_p3')}
                                    </p>
                                </div>
                            </div>

                            {/* Card 3 */}
                            <div className="glass-panel p-6 rounded-xl border border-emerald-500/20 hover:border-emerald-500/40 transition-all duration-300">
                                <div className="flex flex-col gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-emerald-500/10 flex items-center justify-center text-2xl">
                                        📈
                                    </div>
                                    <h3 className="text-white text-lg font-bold">{t('scientific_basis.card3_title')}</h3>
                                    <p className="text-emerald-400 font-mono text-xs uppercase tracking-wider mb-1">{t('scientific_basis.card3_subtitle')}</p>
                                    <p className="text-gray-400 text-sm leading-relaxed">
                                        {t('scientific_basis.card3_desc')}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Bottom Link */}
                        <div className="text-left md:text-center">
                            <a href="https://en.wikipedia.org/wiki/Computational_social_science" target="_blank" className="text-slate-500 text-sm hover:text-purple-400 transition-colors border-b border-transparent hover:border-purple-400">
                                {t('scientific_basis.footer_link')}
                            </a>
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
                        <div className="flex flex-col gap-4 text-left items-start">
                            <h2 className="text-white tracking-tight text-3xl md:text-4xl font-bold leading-tight">
                                {t('pricing.title')}
                            </h2>
                            <p className="text-gray-400 text-base md:text-lg font-light leading-relaxed max-w-[600px]">
                                {t('pricing.subtitle')}
                            </p>
                        </div>

                        {/* Pricing Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Free Tier */}
                            <div className="glass-panel p-6 rounded-xl border border-white/5 hover:border-purple-500/30 transition-all duration-300">
                                <div className="flex flex-col gap-4">
                                    <div>
                                        <h3 className="text-white text-xl font-bold">{t('pricing.free_title')}</h3>
                                        <p className="text-gray-400 text-sm">{t('pricing.free_desc')}</p>
                                    </div>
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-white text-4xl font-bold">{t('pricing.free_price')}</span>
                                        <span className="text-gray-500 text-sm">/mo</span>
                                    </div>
                                    <ul className="flex flex-col gap-2 text-sm text-gray-400">
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> {t('pricing.features.monthly_3')}</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> {t('pricing.features.report_basic')}</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> {t('pricing.features.citizens_100')}</li>
                                        <li className="flex items-center gap-2 text-gray-600"><span>✗</span> {t('pricing.features.no_advanced')}</li>
                                    </ul>
                                    <a href="#start" className="mt-4 w-full py-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-white text-center font-bold transition-all">
                                        {t('pricing.cta_free')}
                                    </a>
                                </div>
                            </div>

                            {/* Pro Tier */}
                            <div className="glass-panel p-6 rounded-xl border-2 border-purple-500 transition-all duration-300 relative">
                                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-purple-600 text-white text-xs font-bold rounded-full">
                                    {t('pricing.pro_badge')}
                                </div>
                                <div className="flex flex-col gap-4">
                                    <div>
                                        <h3 className="text-white text-xl font-bold">{t('pricing.pro_title')}</h3>
                                        <p className="text-gray-400 text-sm">{t('pricing.pro_desc')}</p>
                                    </div>
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-white text-4xl font-bold">{t('pricing.pro_price')}</span>
                                        <span className="text-gray-500 text-sm">/mo</span>
                                    </div>
                                    <ul className="flex flex-col gap-2 text-sm text-gray-400">
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> {t('pricing.features.monthly_50')}</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> {t('pricing.features.report_full')}</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> {t('pricing.features.citizens_1000')}</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> {t('pricing.features.history_dashboard')}</li>
                                    </ul>
                                    <a href="#start" className="mt-4 w-full py-3 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-center font-bold transition-all shadow-[0_0_15px_rgba(127,19,236,0.4)]">
                                        {t('pricing.cta_pro')}
                                    </a>
                                </div>
                            </div>

                            {/* Enterprise Tier */}
                            <div className="glass-panel p-6 rounded-xl border border-white/5 hover:border-purple-500/30 transition-all duration-300">
                                <div className="flex flex-col gap-4">
                                    <div>
                                        <h3 className="text-white text-xl font-bold">{t('pricing.enterprise_title')}</h3>
                                        <p className="text-gray-400 text-sm">{t('pricing.enterprise_desc')}</p>
                                    </div>
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-white text-4xl font-bold">{t('pricing.enterprise_price')}</span>
                                    </div>
                                    <ul className="flex flex-col gap-2 text-sm text-gray-400">
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> {t('pricing.features.unlimited')}</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> {t('pricing.features.account_manager')}</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> {t('pricing.features.custom_citizens')}</li>
                                        <li className="flex items-center gap-2"><span className="text-emerald-400">✓</span> {t('pricing.features.api_support')}</li>
                                    </ul>
                                    <a href="mailto:contact@mirra.ai" className="mt-4 w-full py-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-white text-center font-bold transition-all">
                                        {t('pricing.cta_enterprise')}
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="px-4 md:px-40 flex justify-center py-5 mt-auto border-t border-white/5 bg-[#0f0c12]">
                <div className="max-w-[1200px] w-full">
                    <div className="flex flex-col gap-8 px-5 py-10 text-center md:text-left">
                        <div className="flex flex-col md:flex-row justify-between items-center md:items-start gap-8">
                            <div className="flex flex-col gap-4 items-center md:items-start">
                                <div className="flex items-center gap-2 text-white">
                                    <span className="text-purple-500 text-xl">∞</span>
                                    <h2 className="text-lg font-bold">MIRRA</h2>
                                </div>
                                <p className="text-gray-500 text-sm max-w-[300px]">{t('footer.vision')}</p>
                            </div>
                            <div className="flex flex-wrap items-center justify-center gap-6 md:gap-10">
                                <div className="flex items-center gap-1">
                                    <a className="text-gray-400 hover:text-purple-400 transition-colors text-sm font-medium" href="#">{t('footer.docs')}</a>
                                    <span className="text-[10px] px-1.5 py-0.5 bg-purple-500/20 text-purple-400 rounded-full">{t('footer.coming_soon')}</span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <a className="text-gray-400 hover:text-purple-400 transition-colors text-sm font-medium" href="#">{t('footer.api')}</a>
                                    <span className="text-[10px] px-1.5 py-0.5 bg-purple-500/20 text-purple-400 rounded-full">{t('footer.coming_soon')}</span>
                                </div>
                                <a className="text-gray-400 hover:text-purple-400 transition-colors text-sm font-medium" href="#">{t('footer.terms')}</a>
                            </div>
                        </div>
                        <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
                            <p className="text-gray-600 text-xs">{t('footer.copyright')}</p>
                            <p className="text-gray-600 text-xs">v2.0-scientific-i18n</p>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    )
}