'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar';
import ProjectCard, { ProjectData } from '../components/ProjectCard';
import { Search, Filter, Plus, LayoutGrid, List as ListIcon, Calendar, ArrowUpDown } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
    const [projects, setProjects] = useState<ProjectData[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        async function fetchProjects() {
            try {
                const response = await fetch('http://localhost:8000/api/simulations');
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                setProjects(data);
            } catch (error) {
                console.error('Failed to fetch projects:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchProjects();
    }, []);

    const filteredProjects = projects.filter(p =>
        p.product_name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="min-h-screen bg-[#0f1115] text-white flex font-sans">
            {/* Sidebar Navigation */}
            <Sidebar />

            {/* Main Content Area */}
            <main className="flex-1 ml-64 min-h-screen relative overflow-hidden pt-[100px]">
                {/* Subtle Background Pattern */}
                <div className="absolute inset-0 pointer-events-none opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)', backgroundSize: '32px 32px' }} />

                <div className="max-w-[1400px] mx-auto p-8 lg:p-10 relative z-10">

                    {/* Header */}
                    <header className="flex flex-col md:flex-row justify-between items-end gap-6 mb-10">
                        <div className="space-y-1">
                            <h1 className="text-3xl font-black tracking-tight text-white mb-1">專案儀表板</h1>
                            <p className="text-gray-400 font-light">管理您的平行世界模擬歷程與洞察分析</p>
                        </div>

                        <Link
                            href="/#start"
                            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-500 transition-all hover:scale-[1.02] shadow-lg shadow-blue-500/25 active:scale-95"
                        >
                            <Plus size={20} />
                            建立新預演
                        </Link>
                    </header>

                    {/* Controls: Search & Filter */}
                    <div className="mb-8 grid gap-4 md:grid-cols-[1fr_auto]">
                        {/* Search Box */}
                        <div className="relative group">
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-blue-500 transition-colors">
                                <Search size={20} />
                            </div>
                            <input
                                type="text"
                                placeholder="搜尋專案名稱、關鍵字..."
                                className="w-full bg-[#181b21] border border-white/10 rounded-xl py-3.5 pl-12 pr-6 focus:outline-none focus:border-blue-500/50 transition-all text-sm group-focus-within:bg-[#1c212b] group-focus-within:ring-1 group-focus-within:ring-blue-500/50"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>

                        {/* Quick Actions / Filters */}
                        <div className="flex items-center gap-3">
                            <div className="flex items-center gap-2 bg-[#181b21] border border-white/10 p-1 rounded-xl">
                                <button className="flex items-center gap-2 px-3 py-2 bg-white/10 rounded-lg text-sm font-medium text-white shadow-sm transition-all hover:bg-white/15">
                                    <Calendar size={16} className="text-blue-400" />
                                    最新日期
                                </button>
                                <button className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-400 hover:bg-white/5 hover:text-gray-200 transition-all">
                                    <ArrowUpDown size={14} />
                                    評分高低
                                </button>
                            </div>
                            <button className="w-12 h-12 flex items-center justify-center bg-[#181b21] border border-white/10 rounded-xl text-gray-400 hover:border-white/20 hover:text-white transition-colors">
                                <Filter size={20} />
                            </button>
                        </div>
                    </div>

                    {/* Project Grid */}
                    {loading ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {[...Array(8)].map((_, i) => (
                                <div key={i} className="h-[340px] bg-white/5 rounded-2xl animate-pulse border border-white/5" />
                            ))}
                        </div>
                    ) : filteredProjects.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {filteredProjects.map((project) => (
                                <ProjectCard key={project.sim_id} project={project} />
                            ))}

                            {/* "Create New" Placeholder */}
                            <Link
                                href="/#start"
                                className="group relative flex flex-col items-center justify-center rounded-2xl border border-dashed border-white/20 bg-white/5 p-8 transition-all hover:border-blue-500/50 hover:bg-blue-500/[0.03] min-h-[340px]"
                            >
                                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-white/5 text-gray-500 transition-all group-hover:bg-blue-600 group-hover:text-white group-hover:shadow-[0_0_20px_rgba(37,99,235,0.4)]">
                                    <Plus size={32} />
                                </div>
                                <h3 className="text-lg font-bold text-white group-hover:text-blue-400">建立新預演專案</h3>
                                <p className="mt-2 text-center text-sm text-gray-500 px-4">開始探索另一個平行時空的市場可能性</p>
                            </Link>
                        </div>
                    ) : (
                        <div className="py-32 flex flex-col items-center justify-center bg-[#111113]/50 rounded-3xl border border-white/5 border-dashed">
                            <div className="bg-white/5 p-6 rounded-full mb-6 text-gray-700">
                                <LayoutGrid size={64} />
                            </div>
                            <h3 className="text-2xl font-black mb-2 tracking-tight">查無相關專案</h3>
                            <p className="text-gray-500 mb-10 max-w-sm text-center font-light">
                                目前沒有匹配 "{searchQuery}" 的預演。嘗試更換關鍵字，或者立即發起一個新的市場預演。
                            </p>
                            <Link
                                href="/#start"
                                className="px-10 py-4 bg-white text-black font-black rounded-xl hover:bg-gray-200 transition-all shadow-xl shadow-white/5"
                            >
                                發起新預演
                            </Link>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
