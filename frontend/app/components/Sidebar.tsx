'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    Home,
    PlusCircle,
    History,
    Settings,
    ChevronRight,
    User,
    LogOut
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}


export default function Sidebar() {
    const pathname = usePathname();

    return (
        <>
            {/* Import Material Symbols */}
            <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />

            <aside className="w-64 h-[calc(100vh-80px)] bg-[#111318] border-r border-white/5 flex flex-col fixed left-0 top-[80px] z-40">
                <div className="flex h-full flex-col justify-between p-4">
                    <div className="flex flex-col gap-8">
                        {/* Brand */}
                        <Link href="/dashboard" className="flex items-center gap-3 px-2 pt-2 hover:opacity-80 transition-opacity cursor-pointer">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 shadow-[0_0_15px_rgba(13,89,242,0.4)]">
                                <span className="material-symbols-outlined text-white">all_inclusive</span>
                            </div>
                            <div className="flex flex-col">
                                <h1 className="text-xl font-bold tracking-wider text-white">MIRRA</h1>
                                <p className="text-[10px] text-gray-500 font-medium">BEYOND REALITY</p>
                            </div>
                        </Link>

                        {/* Navigation */}
                        <nav className="flex flex-col gap-2">
                            {[
                                { name: '首頁', icon: 'grid_view', href: '/dashboard' },
                                { name: '建立新預演', icon: 'add_circle', href: '/#start' },
                                { name: '歷史紀錄', icon: 'history', href: '/dashboard?filter=history' },
                                { name: '設定', icon: 'settings', href: '/settings' },
                            ].map((item) => {
                                const isActive = pathname === item.href;
                                return (
                                    <Link
                                        key={item.name}
                                        href={item.href}
                                        className={cn(
                                            "group flex items-center gap-3 rounded-xl px-3 py-3 transition-all duration-200",
                                            isActive
                                                ? "bg-blue-600/10 text-blue-400 border border-blue-500/20"
                                                : "text-gray-400 hover:bg-white/5 hover:text-white"
                                        )}
                                    >
                                        <span className={cn(
                                            "material-symbols-outlined transition-transform group-hover:scale-110",
                                            isActive && "fill-[1]"
                                        )}>
                                            {item.icon}
                                        </span>
                                        <span className="text-sm font-medium">{item.name}</span>
                                        {isActive && (
                                            <div className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(37,99,235,0.6)]" />
                                        )}
                                    </Link>
                                );
                            })}
                        </nav>
                    </div>

                    {/* User Profile Area */}
                    <div className="flex flex-col gap-4 border-t border-white/5 pt-4">
                        {/* Quota Card */}
                        <div className="rounded-xl bg-gradient-to-r from-purple-900/10 to-blue-900/10 p-3 border border-white/5">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-[11px] font-medium text-gray-400">本月額度</span>
                                <span className="text-[11px] font-bold text-blue-400">85%</span>
                            </div>
                            <div className="h-1.5 w-full rounded-full bg-gray-800 overflow-hidden">
                                <div
                                    className="h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500 shadow-[0_0_10px_rgba(59,130,246,0.3)]"
                                    style={{ width: '85%' }}
                                />
                            </div>
                        </div>

                        {/* User Profile */}
                        <div className="flex items-center gap-3 rounded-xl p-2 transition-colors hover:bg-white/5 cursor-pointer group">
                            <div className="h-10 w-10 overflow-hidden rounded-full border border-white/10 bg-gray-800">
                                <img
                                    alt="User avatar"
                                    className="h-full w-full object-cover"
                                    src="https://api.dicebear.com/7.x/avataaars/svg?seed=Alex"
                                />
                            </div>
                            <div className="flex flex-col min-w-0 flex-1">
                                <span className="text-sm font-medium text-white truncate">Alex Chen</span>
                                <span className="text-[10px] text-gray-500 uppercase font-bold tracking-tight">Pro Plan</span>
                            </div>
                            <span className="material-symbols-outlined text-gray-500 group-hover:text-white transition-colors">
                                more_vert
                            </span>
                        </div>
                    </div>
                </div>
            </aside>
        </>
    );
}
