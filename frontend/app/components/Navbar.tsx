import React from 'react';
import Link from 'next/link';

export default function Navbar() {
    return (
        <nav className="fixed top-0 left-0 right-0 z-[100] px-4 pt-4 lg:px-40 flex justify-center pointer-events-none">
            <header className="glass-panel rounded-full flex items-center justify-between whitespace-nowrap px-6 py-3 w-full max-w-[960px] shadow-lg shadow-purple-500/5 pointer-events-auto">
                <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                    <span className="text-purple-500 text-2xl">∞</span>
                    <h2 className="text-white text-xl font-bold leading-tight tracking-tight">MIRRA</h2>
                </Link>
                <div className="hidden md:flex items-center gap-8">
                    <Link className="text-gray-300 hover:text-white transition-colors text-sm font-medium" href="/#how-it-works">運作原理</Link>
                    <Link className="text-gray-300 hover:text-white transition-colors text-sm font-medium" href="/#why-bazi">八字科學</Link>
                    <Link className="text-gray-300 hover:text-white transition-colors text-sm font-medium" href="/dashboard">儀表板</Link>
                    <Link className="text-gray-300 hover:text-white transition-colors text-sm font-medium" href="/citizens">市民</Link>
                    <Link className="text-gray-300 hover:text-white transition-colors text-sm font-medium" href="/#pricing">定價</Link>
                </div>
                <Link href="/#start" className="hidden md:flex min-w-[84px] cursor-pointer items-center justify-center rounded-full h-9 px-5 bg-purple-600 hover:bg-purple-500 transition-all text-white text-sm font-bold shadow-[0_0_15px_rgba(127,19,236,0.5)]">
                    預演未來
                </Link>
                {/* Mobile Menu Button - can implement functionality later if needed */}
                <button className="md:hidden text-white text-2xl">☰</button>
            </header>
        </nav>
    );
}
