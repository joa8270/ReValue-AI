"use client"

import { useState } from "react"
import Link from "next/link"

export default function Navbar() {
    const [isMenuOpen, setIsMenuOpen] = useState(false)

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-[#141118]/95 backdrop-blur-md border-b border-white/5">
            <div className="max-w-[1400px] mx-auto px-4 md:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                        <span className="text-purple-500 text-2xl">∞</span>
                        <h2 className="text-white text-lg font-bold tracking-wider">MIRRA</h2>
                    </Link>

                    {/* Desktop Menu */}
                    <div className="hidden md:flex items-center gap-6">
                        <Link href="/#how-it-works" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
                            運作方式
                        </Link>
                        <Link href="/#why-bazi" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
                            八字基礎
                        </Link>
                        <Link href="/#pricing" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
                            方案定價
                        </Link>
                        <Link href="/citizens" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
                            瀏覽市民
                        </Link>
                        <Link
                            href="/#start"
                            className="flex items-center justify-center rounded-lg h-9 px-4 bg-purple-600 hover:bg-purple-500 text-white text-sm font-bold transition-all shadow-[0_0_15px_rgba(127,19,236,0.3)]"
                        >
                            立即預演
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
            <div className={`md:hidden overflow-hidden transition-all duration-300 ${isMenuOpen ? 'max-h-96' : 'max-h-0'}`}>
                <div className="px-4 py-6 bg-[#0f0c12] border-t border-white/5 flex flex-col gap-4">
                    <Link
                        href="/#how-it-works"
                        className="text-gray-400 hover:text-white transition-colors text-sm font-medium py-2"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        運作方式
                    </Link>
                    <Link
                        href="/#why-bazi"
                        className="text-gray-400 hover:text-white transition-colors text-sm font-medium py-2"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        八字基礎
                    </Link>
                    <Link
                        href="/#pricing"
                        className="text-gray-400 hover:text-white transition-colors text-sm font-medium py-2"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        方案定價
                    </Link>
                    <Link
                        href="/citizens"
                        className="text-gray-400 hover:text-white transition-colors text-sm font-medium py-2"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        瀏覽市民
                    </Link>
                    <Link
                        href="/#start"
                        className="mt-2 flex items-center justify-center rounded-lg h-10 px-4 bg-purple-600 hover:bg-purple-500 text-white text-sm font-bold transition-all"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        立即預演
                    </Link>
                </div>
            </div>
        </nav>
    )
}
