'use client';

import React from 'react';
import Link from 'next/link';
import {
    MoreHorizontal,
    Clock,
    CheckCircle2,
    AlertCircle,
    TrendingUp,
    MapPin
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export interface ProjectData {
    sim_id: string;
    product_name: string;
    price?: string;
    status: 'processing' | 'done' | 'error';
    score?: number;
    summary?: string;
    timestamp?: string;
    category?: string;
}

interface ProjectCardProps {
    project: ProjectData;
}

export default function ProjectCard({ project }: ProjectCardProps) {
    const isDone = project.status === 'done';
    const isProcessing = project.status === 'processing';
    const isError = project.status === 'error';

    return (
        <div className="group relative bg-[#111113] border border-white/5 rounded-2xl overflow-hidden hover:border-purple-500/30 transition-all duration-300 shadow-xl shadow-black/20">
            {/* Card Header Illustration/Image */}
            <div className="relative h-40 bg-[#0a0a0b] overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-t from-[#111113] to-transparent z-10" />

                {/* Mock Graphic / Thumbnail */}
                <div className="absolute inset-0 opacity-40 group-hover:opacity-60 transition-opacity duration-500">
                    <div className="w-full h-full bg-[url('https://images.unsplash.com/photo-1639322537228-f710d846310a?w=400&q=80')] bg-cover bg-center grayscale group-hover:grayscale-0 transition-all duration-700" />
                </div>

                {/* Status Badge */}
                <div className="absolute top-4 right-4 z-20">
                    <div className={cn(
                        "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider backdrop-blur-md border",
                        isDone && "bg-green-500/10 text-green-400 border-green-500/20",
                        isProcessing && "bg-blue-500/10 text-blue-400 border-blue-500/20",
                        isError && "bg-red-500/10 text-red-500 border-red-500/20"
                    )}>
                        <div className={cn(
                            "w-1 h-1 rounded-full shadow-[0_0_5px_currentColor]",
                            isDone && "bg-green-400",
                            isProcessing && "bg-blue-400 animate-pulse",
                            isError && "bg-red-400"
                        )} />
                        {isDone ? '已完成' : isProcessing ? '運算中' : '錯誤'}
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="p-5 relative">
                <div className="flex justify-between items-start mb-1">
                    <h3 className="text-white font-bold text-lg leading-tight group-hover:text-purple-400 transition-colors truncate pr-4">
                        {project.product_name}
                    </h3>
                    {/* Score Indicator (Circular) */}
                    <div className="flex flex-col items-end shrink-0">
                        <div className="relative w-12 h-12 flex items-center justify-center">
                            <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                                <circle
                                    cx="18" cy="18" r="16"
                                    fill="none"
                                    className="stroke-gray-800"
                                    strokeWidth="3"
                                />
                                {isDone && (
                                    <circle
                                        cx="18" cy="18" r="16"
                                        fill="none"
                                        className="stroke-purple-500 drop-shadow-[0_0_5px_rgba(168,85,247,0.5)]"
                                        strokeWidth="3"
                                        strokeDasharray={`${project.score || 0}, 100`}
                                        strokeLinecap="round"
                                        style={{ transition: 'stroke-dasharray 1s ease-out' }}
                                    />
                                )}
                            </svg>
                            <span className="absolute text-[13px] font-black text-white">
                                {isDone ? project.score : '--'}
                            </span>
                        </div>
                        <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider mt-1">購買意願</span>
                    </div>
                </div>

                <div className="flex items-center gap-3 text-xs text-gray-500 mb-6 mt-[-10px]">
                    <span className="flex items-center gap-1">
                        <MapPin size={12} className="text-gray-600" /> 台灣市場
                    </span>
                    <span>•</span>
                    <span className="text-gray-400 font-medium">{project.price ? `NT$ ${project.price}` : '未提供售價'}</span>
                </div>

                <div className="flex items-center justify-between border-t border-white/5 pt-4">
                    {/* Persona Avatars Stack */}
                    <div className="flex -space-x-2">
                        {[...Array(3)].map((_, i) => (
                            <div
                                key={i}
                                className="w-7 h-7 rounded-full border-2 border-[#111113] bg-gray-800 flex items-center justify-center overflow-hidden"
                            >
                                <img
                                    src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${project.sim_id}_${i}`}
                                    alt="Persona"
                                    className="w-full h-full object-cover opacity-60"
                                />
                            </div>
                        ))}
                        <div className="w-7 h-7 rounded-full border-2 border-[#111113] bg-purple-900/40 flex items-center justify-center text-[10px] font-bold text-purple-300">
                            +8
                        </div>
                    </div>

                    <Link
                        href={`/watch/${project.sim_id}`}
                        className={cn(
                            "px-4 py-2 rounded-xl text-xs font-bold transition-all",
                            isDone
                                ? "bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-500/20"
                                : "bg-white/5 text-gray-500 border border-white/5 cursor-wait"
                        )}
                    >
                        {isDone ? '查看報告' : '運算中...'}
                    </Link>
                </div>
            </div>
            {/* Progress Line (for processing) */}
            {isProcessing && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500/20 overflow-hidden">
                    <div className="h-full bg-blue-400 w-1/3 animate-[progress_2s_infinite_linear]"
                        style={{
                            animationName: 'shimmer',
                            backgroundImage: 'linear-gradient(to right, transparent, rgba(96, 165, 250, 0.4), transparent)'
                        }}
                    />
                </div>
            )}
        </div>
    );
}
