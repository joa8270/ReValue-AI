"use client"

import { useState } from "react"
import Link from "next/link"
import { useLanguage } from "../context/LanguageContext"
import { Language } from "../lib/translations"

export default function Navbar() {
    const [isMenuOpen, setIsMenuOpen] = useState(false)
    const [isLangMenuOpen, setIsLangMenuOpen] = useState(false)
    const { t, language, setLanguage } = useLanguage()

    const handleLangChange = (lang: Language) => {
        setLanguage(lang)
        setIsLangMenuOpen(false)
    }

    const languages: { code: Language; label: string }[] = [
        { code: 'zh-TW', label: '繁體中文' },
        { code: 'zh-CN', label: '简体中文' },
        { code: 'en', label: 'English' },
    ]

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-[#141118]/95 backdrop-blur-md border-b border-white/5">
            <div className="max-w-[1400px] mx-auto px-4 md:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                        <span className="text-purple-500 text-2xl">∞</span>
                        <h2 className="text-white text-lg font-bold tracking-wider">MIRRA // 鏡界</h2>
                    </Link>

                    {/* Desktop Menu */}
                    <div className="hidden md:flex items-center gap-6">
                        <Link href="/#how-it-works" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
                            {t('navbar.process')}
                        </Link>
                        <Link href="/#why-bazi" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
                            {t('navbar.algorithm')}
                        </Link>
                        <Link href="/#pricing" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
                            {t('navbar.pricing')}
                        </Link>
                        <Link href="/citizens" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
                            {t('navbar.citizens')}
                        </Link>


                        {/* Language Switcher */}
                        <div className="relative">
                            <button
                                onClick={() => setIsLangMenuOpen(!isLangMenuOpen)}
                                className="flex items-center gap-1.5 text-gray-400 hover:text-white transition-colors text-sm font-medium px-2 py-1.5 rounded-md hover:bg-white/5"
                            >
                                <span className="text-lg">🌐</span>
                                <span className="uppercase">{language === 'zh-TW' ? '繁' : language === 'zh-CN' ? '简' : 'EN'}</span>
                            </button>

                            {/* Dropdown */}
                            {isLangMenuOpen && (
                                <div className="absolute top-full right-0 mt-2 w-32 bg-[#1e1a24] border border-white/10 rounded-lg shadow-xl overflow-hidden py-1">
                                    {languages.map((lang) => (
                                        <button
                                            key={lang.code}
                                            onClick={() => handleLangChange(lang.code)}
                                            className={`block w-full text-left px-4 py-2 text-sm transition-colors ${language === lang.code
                                                ? 'bg-purple-600/20 text-purple-400'
                                                : 'text-gray-400 hover:bg-white/5 hover:text-white'
                                                }`}
                                        >
                                            {lang.label}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        <Link
                            href="/#start"
                            className="flex items-center justify-center rounded-lg h-9 px-4 bg-purple-600 hover:bg-purple-500 text-white text-sm font-bold transition-all shadow-[0_0_15px_rgba(127,19,236,0.3)]"
                        >
                            {t('navbar.start')}
                        </Link>
                    </div>

                    {/* Mobile Hamburger */}
                    <button
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        className="md:hidden flex items-center justify-center w-10 h-10 rounded-lg hover:bg-white/5 transition-colors"
                        aria-label="Toggle menu"
                    >
                        <div className="flex flex-col gap-1.5 w-5">
                            <span className={`h-0.5 w-full bg-white transition-all duration-300 ${isMenuOpen ? 'rotate-45 translate-y-2' : ''}`} />
                            <span className={`h-0.5 w-full bg-white transition-all duration-300 ${isMenuOpen ? 'opacity-0' : ''}`} />
                            <span className={`h-0.5 w-full bg-white transition-all duration-300 ${isMenuOpen ? '-rotate-45 -translate-y-2' : ''}`} />
                        </div>
                    </button>
                </div>
            </div>

            {/* Mobile Menu Dropdown */}
            <div className={`md:hidden transition-all duration-300 ${isMenuOpen ? 'max-h-[85vh] overflow-y-auto' : 'max-h-0 overflow-hidden'}`}>
                <div className="px-4 py-6 bg-[#0f0c12] border-t border-white/5 flex flex-col gap-4">
                    <Link
                        href="/#how-it-works"
                        className="text-gray-400 hover:text-white transition-colors text-sm font-medium py-2"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        {t('navbar.process')}
                    </Link>
                    <Link
                        href="/#why-bazi"
                        className="text-gray-400 hover:text-white transition-colors text-sm font-medium py-2"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        {t('navbar.algorithm')}
                    </Link>
                    <Link
                        href="/#pricing"
                        className="text-gray-400 hover:text-white transition-colors text-sm font-medium py-2"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        {t('navbar.pricing')}
                    </Link>
                    <Link
                        href="/citizens"
                        className="text-gray-400 hover:text-white transition-colors text-sm font-medium py-2"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        {t('navbar.citizens')}
                    </Link>


                    <div className="py-2 border-t border-white/5 mt-2">
                        <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Language</p>
                        <div className="flex flex-col gap-2">
                            {languages.map((lang) => (
                                <button
                                    key={lang.code}
                                    onClick={() => handleLangChange(lang.code)}
                                    className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium border transition-colors ${language === lang.code
                                        ? 'bg-purple-600 border-purple-600 text-white'
                                        : 'border-white/10 text-gray-400 hover:border-white/30'
                                        }`}
                                >
                                    {lang.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <Link
                        href="/#start"
                        className="mt-2 flex items-center justify-center rounded-lg h-10 px-4 bg-purple-600 hover:bg-purple-500 text-white text-sm font-bold transition-all"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        {t('navbar.start')}
                    </Link>
                </div>
            </div>
        </nav>
    )
}
