"use client"

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useLanguage } from '../context/LanguageContext';
import { api } from '@/lib/api';
import { Skill, BaZiRequest } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Cpu, Calendar, Clock, Activity, X } from 'lucide-react';

export default function Dashboard() {
    const [skills, setSkills] = useState<Skill[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);

    // BaZi State
    const [baziResult, setBaziResult] = useState<any>(null);
    const [isCalculating, setIsCalculating] = useState(false);

    useEffect(() => {
        const loadSkills = async () => {
            const data = await api.getSkills();
            setSkills(data);
            setLoading(false);
        };
        loadSkills();
    }, []);

    const openSkill = (skill: Skill) => {
        setSelectedSkill(skill);
        setBaziResult(null);
    };

    const closeSkill = () => {
        setSelectedSkill(null);
        setBaziResult(null);
    };

    return (
        <div className="min-h-screen bg-[#141118] font-sans text-white p-6 md:p-12 relative overflow-hidden">
            {/* Background Glow */}
            <div className="fixed inset-0 bg-hero-glow pointer-events-none z-0 opacity-50" />

            {/* Header */}
            <div className="relative z-10 max-w-6xl mx-auto mb-10 flex items-center gap-4">
                <Link href="/" className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                    <ArrowLeft className="w-6 h-6 text-gray-400" />
                </Link>
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-400">
                        Skill Dashboard
                    </h1>
                    <p className="text-gray-400 text-sm mt-1">Manage and execute AI capabilities</p>
                </div>
            </div>

            {/* Grid */}
            <div className="relative z-10 max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {loading ? (
                    <div className="text-gray-500 animate-pulse">Loading skills...</div>
                ) : (
                    skills
                        .filter(skill => skill.slug !== 'bazi-calc')
                        .map(skill => (
                        <motion.div
                            key={skill.id}
                            layoutId={`card-${skill.id}`}
                            onClick={() => openSkill(skill)}
                            className="glass-panel p-6 rounded-xl border border-white/5 hover:border-purple-500/50 cursor-pointer transition-all hover:shadow-[0_0_20px_rgba(127,19,236,0.3)] group"
                            whileHover={{ scale: 1.02 }}
                        >
                            <div className="w-12 h-12 rounded-lg bg-purple-500/10 flex items-center justify-center mb-4 group-hover:bg-purple-500/20 transition-colors">
                                <Cpu className="w-6 h-6 text-purple-400" />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-2">{skill.name}</h3>
                            <p className="text-gray-400 text-sm mb-4 line-clamp-2">{skill.description}</p>
                            <div className="flex items-center justify-between text-xs text-gray-500">
                                <span className="px-2 py-1 rounded bg-white/5">v{skill.version}</span>
                                <span className="group-hover:text-purple-400 transition-colors">Execute &rarr;</span>
                            </div>
                        </motion.div>
                    ))
                )}
            </div>

            {/* Modal */}
            <AnimatePresence>
                {selectedSkill && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                        <motion.div
                            layoutId={`card-${selectedSkill.id}`}
                            className="w-full max-w-lg bg-[#1a1620] border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                        >
                            <div className="p-6 border-b border-white/5 flex justify-between items-center">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 rounded bg-purple-500/10">
                                        <Cpu className="w-5 h-5 text-purple-400" />
                                    </div>
                                    <h2 className="text-xl font-bold">{selectedSkill.name}</h2>
                                </div>
                                <button onClick={closeSkill} className="p-2 hover:bg-white/5 rounded-full text-gray-400 hover:text-white">
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <div className="p-6">
                                {selectedSkill.slug === 'bazi-calc' ? (
                                    <BaZiCalculator onBack={closeSkill} />
                                ) : (
                                    <div className="text-center py-10 text-gray-500">
                                        <p>Interface for {selectedSkill.name} is under construction.</p>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}

function BaZiCalculator({ onBack }: { onBack: () => void }) {
    const { t } = useLanguage();
    const [formData, setFormData] = useState<BaZiRequest>({
        year: 2000,
        month: 1,
        day: 1,
        hour: 12
    });
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const formatPillar = (pillar: string) => {
        if (!pillar) return '-';
        const parts = pillar.toLowerCase().split('-');
        if (parts.length !== 2) return pillar;
        
        const [stemKey, branchKey] = parts;
        const stem = t(`bazi.stems.${stemKey}`);
        const branch = t(`bazi.branches.${branchKey}`);
        
        const s = stem.startsWith('bazi.stems') ? stemKey : stem;
        const b = branch.startsWith('bazi.branches') ? branchKey : branch;
        
        return `${s}${b}`;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const res = await api.executeBaZiCalc(formData);
            setResult(res);
        } catch (err) {
            setError("Failed to calculate. Backend might be offline.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            {!result ? (
                <form onSubmit={handleSubmit} className="space-y-4">
                    <p className="text-sm text-gray-400 mb-4">Enter birth details to calculate the Four Pillars chart.</p>
                    
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-gray-400 uppercase">Year</label>
                            <div className="relative">
                                <Calendar className="absolute left-3 top-2.5 w-4 h-4 text-gray-500" />
                                <input
                                    type="number"
                                    min="1900"
                                    max="2030"
                                    value={formData.year}
                                    onChange={e => setFormData({ ...formData, year: parseInt(e.target.value) })}
                                    className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-purple-500 text-white"
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-gray-400 uppercase">Month</label>
                            <select
                                value={formData.month}
                                onChange={e => setFormData({ ...formData, month: parseInt(e.target.value) })}
                                className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-purple-500 text-white appearance-none"
                            >
                                {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
                                    <option key={m} value={m}>{m}月</option>
                                ))}
                            </select>
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-gray-400 uppercase">Day</label>
                            <input
                                type="number"
                                min="1"
                                max="31"
                                value={formData.day}
                                onChange={e => setFormData({ ...formData, day: parseInt(e.target.value) })}
                                className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-purple-500 text-white"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-gray-400 uppercase">Hour (0-23)</label>
                            <div className="relative">
                                <Clock className="absolute left-3 top-2.5 w-4 h-4 text-gray-500" />
                                <input
                                    type="number"
                                    min="0"
                                    max="23"
                                    value={formData.hour}
                                    onChange={e => setFormData({ ...formData, hour: parseInt(e.target.value) })}
                                    className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-purple-500 text-white"
                                />
                            </div>
                        </div>
                    </div>

                    {error && <p className="text-red-400 text-sm bg-red-500/10 p-2 rounded">{error}</p>}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2"
                    >
                        {loading ? <span className="animate-spin">🌀</span> : <Activity className="w-4 h-4" />}
                        {loading ? "Calculating..." : "Calculate Destiny"}
                    </button>
                </form>
            ) : (
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-lg text-center">
                        <h3 className="text-purple-300 text-sm uppercase tracking-widest font-bold mb-4">Four Pillars Chart</h3>
                        <div className="grid grid-cols-4 gap-2 text-center">
                            <div>
                                <div className="text-xs text-gray-500 mb-1">Year</div>
                                <div className="text-xl font-bold">{formatPillar(result.bazi?.year)}</div>
                            </div>
                            <div>
                                <div className="text-xs text-gray-500 mb-1">Month</div>
                                <div className="text-xl font-bold">{formatPillar(result.bazi?.month)}</div>
                            </div>
                            <div>
                                <div className="text-xs text-gray-500 mb-1">Day</div>
                                <div className="text-xl font-bold text-white bg-purple-500/20 rounded py-1">{formatPillar(result.bazi?.day)}</div>
                            </div>
                            <div>
                                <div className="text-xs text-gray-500 mb-1">Hour</div>
                                <div className="text-xl font-bold">{formatPillar(result.bazi?.hour)}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div className="bg-white/5 p-4 rounded-lg">
                        <pre className="text-xs text-gray-400 overflow-x-auto">
                            {JSON.stringify(result, null, 2)}
                        </pre>
                    </div>

                    <button
                        onClick={() => setResult(null)}
                        className="w-full py-2 bg-white/5 hover:bg-white/10 text-gray-300 font-medium rounded-lg transition-all"
                    >
                        Calculate Another
                    </button>
                </div>
            )}
        </div>
    );
}
