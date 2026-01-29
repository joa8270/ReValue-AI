"use client"

import { useState, useRef, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileText, Image as ImageIcon, Loader2, ArrowRight, X, Sparkles, Mic, Square, User, Target, TrendingUp, Users, ShieldAlert, ShoppingBag, Briefcase, Globe, Dices } from 'lucide-react'

// 🌍 市場配置常數 (Chameleon Architecture)
const MARKET_CONFIG = {
    TW: { basePop: 18600000, currency: 'TWD', flag: '🇹🇼', labelKey: 'step2_market_tw' },
    US: { basePop: 335000000, currency: 'USD', flag: '🇺🇸', labelKey: 'step2_market_us' },
    CN: { basePop: 1400000000, currency: 'CNY', flag: '🇨🇳', labelKey: 'step2_market_cn' }
} as const;
type MarketKey = keyof typeof MARKET_CONFIG;
import { useLanguage } from '../context/LanguageContext'

export default function SimulationForm() {
    const router = useRouter()
    const { t, language } = useLanguage()
    const [mode, setMode] = useState<'image' | 'pdf'>('image')
    const [files, setFiles] = useState<File[]>([])
    const [loading, setLoading] = useState(false)
    const [aiLoading, setAiLoading] = useState(false)
    const [nameLoading, setNameLoading] = useState(false) // AI 識別產品名稱的加載狀態
    const [error, setError] = useState("")
    const [previewUrls, setPreviewUrls] = useState<string[]>([])
    const [iterationAlert, setIterationAlert] = useState<{ type: 'pivot' | 'scale'; message: string } | null>(null)
    const [step, setStep] = useState(1) // Step 1: Upload/Identify, Step 2: Targeting
    // Targeting State
    const [targetAge, setTargetAge] = useState<[number, number]>([20, 60])
    const [targetGender, setTargetGender] = useState<'all' | 'male' | 'female'>('all')
    const [targetOccupations, setTargetOccupations] = useState<string[]>([])
    const [expertMode, setExpertMode] = useState(false)
    const [forceRandom, setForceRandom] = useState(false) // [New] Force Random Mode
    const [tam, setTam] = useState(18600000) // Initial TAM (Taiwan Active Internet Users / Labor Force)
    // Scenario State
    const [analysisScenario, setAnalysisScenario] = useState<'b2c' | 'b2b'>('b2c')
    // 🌍 目標市場狀態 (Globalization)
    const [targetMarket, setTargetMarket] = useState<MarketKey>('TW')

    // Auto-calculate TAM with Fermi Logic (連動市場選擇)
    useEffect(() => {
        // 🌍 根據選擇的市場取得基礎人口
        let base = MARKET_CONFIG[targetMarket].basePop

        // Age impact (Rough estimate)
        const ageRange = targetAge[1] - targetAge[0]
        const ageFactor = Math.min(1, ageRange / 60)
        base = base * ageFactor

        // Gender impact
        if (targetGender !== 'all') base = base * 0.52

        // Occupation impact
        if (targetOccupations.length > 0) {
            // Suppose each selected specific group reduces scope
            // But multiple selections add up. 
            // Simplified: 0.15 per group, max 1.0
            const occFactor = Math.min(1, targetOccupations.length * 0.15)
            base = base * occFactor
        }

        // 加入隨機雜訊，讓尾數看起來不那麼整齊，增加真實感
        const noise = Math.floor(Math.random() * 5000)
        setTam(Math.floor(base) + noise)
    }, [targetAge, targetGender, targetOccupations, targetMarket])

    const searchParams = useSearchParams()

    // Refs
    const priceInputRef = useRef<HTMLInputElement>(null)

    // Recording State
    const [isRecording, setIsRecording] = useState(false)
    const [recordingTime, setRecordingTime] = useState(0)
    const mediaRecorderRef = useRef<MediaRecorder | null>(null)
    const audioChunksRef = useRef<Blob[]>([])
    const timerRef = useRef<NodeJS.Timeout | null>(null)

    useEffect(() => {
        if (files.length === 0) {
            setPreviewUrls([])
            return
        }

        const urls: string[] = []
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                urls.push(URL.createObjectURL(file))
            }
        })
        setPreviewUrls(urls)

        return () => {
            urls.forEach(url => URL.revokeObjectURL(url))
        }
    }, [files])

    // Handle Context Carry-over (Iteration Mode)
    useEffect(() => {
        const modeParam = searchParams.get('mode')
        const action = searchParams.get('action') || 'Pivot'
        const refName = searchParams.get('product_name')
        const refPrice = searchParams.get('price')
        const refDesc = searchParams.get('description')
        // const refScore = searchParams.get('ref_score')

        if (modeParam === 'iteration') {
            // Pre-fill data
            if (refName) setProductName(decodeURIComponent(refName))
            if (refPrice && refPrice !== 'undefined') setPrice(refPrice)
            if (refDesc && refDesc !== 'undefined') setDescription(decodeURIComponent(refDesc))

            // Visual Feedback
            if (action === 'Scale') {
                setIterationAlert({
                    type: 'scale',
                    message: t('simulation_form.iteration_alert_scale_desc')
                })
            } else {
                // Pivot or Restart match
                setIterationAlert({
                    type: 'pivot',
                    message: t('simulation_form.iteration_alert_pivot_desc')
                })
                // Focus on price if Pivot
                setTimeout(() => {
                    priceInputRef.current?.focus()
                }, 800)
            }
        }
    }, [searchParams])

    // Form Fields
    const [productName, setProductName] = useState("")
    const [price, setPrice] = useState("")
    const [priceSource, setPriceSource] = useState("") // 價格來源說明
    const [marketPrices, setMarketPrices] = useState<{
        success: boolean;
        prices: Array<{ platform: string; price: number; note: string }>;
        min_price: number;
        max_price: number;
        sources_count: number;
        search_summary: string;
    } | null>(null) // 市場比價資料
    const [description, setDescription] = useState("")

    // AI Writing Style Options
    const [selectedStyle, setSelectedStyle] = useState("professional")
    const styleOptions = [
        { value: "professional", label: t('simulation_form.style_professional'), desc: t('simulation_form.style_professional') },
        { value: "friendly", label: t('simulation_form.style_friendly'), desc: t('simulation_form.style_friendly') },
        { value: "luxury", label: t('simulation_form.style_luxury'), desc: t('simulation_form.style_luxury') },
        { value: "minimalist", label: t('simulation_form.style_minimalist'), desc: t('simulation_form.style_minimalist') },
        { value: "storytelling", label: t('simulation_form.style_storytelling'), desc: t('simulation_form.style_storytelling') },
    ]

    // Admin Tools
    const [isResetting, setIsResetting] = useState(false)
    const handleResetDB = async () => {
        if (!confirm("⚠️ 確定要重置並初始化市民資料庫嗎？\n此操作將生成 1,000 位新市民，耗時約 30 秒。\n請確保目前沒有模擬正在進行中。")) return;

        setIsResetting(true)
        try {
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const res = await fetch(`${API_BASE_URL}/api/web/admin/reset-citizens?count=1000`, { method: "POST" })
            if (res.ok) {
                alert("✅ Database initialized successfully!")
            } else {
                const txt = await res.text()
                alert(`❌ Initialization failed: ${txt}`)
            }
        } catch (e) {
            alert(`❌ 請求錯誤: ${e}`)
        } finally {
            setIsResetting(false)
        }
    }

    const fileInputRef = useRef<HTMLInputElement>(null)

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            const newFiles = Array.from(e.target.files)

            // Append mode: Add new files to existing ones, avoiding duplicates (by name + size)
            setFiles(prevFiles => {
                const combined = [...prevFiles]
                newFiles.forEach(newFile => {
                    // Check for duplicate
                    if (!combined.some(existing => existing.name === newFile.name && existing.size === newFile.size)) {
                        combined.push(newFile)
                    }
                })
                return combined
            })

            setError("")

            // Clear input value so selecting the same file again (if user wants to for some reason, though we filter duplicates) or selecting others works reliably
            if (fileInputRef.current) fileInputRef.current.value = ""
        }
    }

    const handleIdentifyProduct = async () => {
        if (files.length === 0) return

        setNameLoading(true)
        try {
            const formData = new FormData()
            files.forEach(f => formData.append("files", f))
            formData.append("language", language)

            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const res = await fetch(`${API_BASE_URL}/api/web/identify-product`, {
                method: "POST",
                body: formData,
            })

            const data = await res.json()
            // 支援多圖判斷結結果
            // if (data.is_same_product === false) { alert("注意：AI 檢測到這些圖片可能屬於不同產品，分析將以最顯著的產品為主。") }

            if (data.product_name) {
                setProductName(data.product_name)
            }
            // 填入估算價格
            if (data.estimated_price) {
                const currency = data.currency || ''
                setPrice(`${data.estimated_price} ${currency}`.trim())
            }
            // 設置價格來源說明
            if (data.price_source) {
                const rangeText = data.price_range ? t('simulation_form.format_price_range').replace('{range}', data.price_range) : ''
                setPriceSource(`💡 ${data.price_source}${rangeText}`)
            }
            // 🔍 存儲市場比價資料
            if (data.market_prices) {
                setMarketPrices(data.market_prices)
                // 如果有成功取得市場比價，更新價格來源顯示
                if (data.market_prices.success && data.market_prices.sources_count > 0) {
                    setPriceSource(t('simulation_form.format_market_compare')
                        .replace('{count}', data.market_prices.sources_count.toString())
                        .replace('{summary}', data.market_prices.search_summary)
                    )
                }
            }
        } catch (err) {
            console.error("Product identification failed:", err)
            setError(t('simulation_form.error_identify_fail'))
        }
        setNameLoading(false)
    }

    // Recording Controls
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
            mediaRecorderRef.current = mediaRecorder
            audioChunksRef.current = []

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data)
                }
            }

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
                const audioFile = new File([audioBlob], `recording_${Date.now()}.webm`, { type: 'audio/webm' })
                setFiles([audioFile]) // Set as single file
                stream.getTracks().forEach(track => track.stop())
            }

            mediaRecorder.start(100) // Collect data every 100ms
            setIsRecording(true)
            setRecordingTime(0)

            // Start timer
            timerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1)
            }, 1000)

        } catch (err) {
            console.error('Recording failed:', err)
            setError(t('simulation_form.error_mic_fail'))
        }
    }

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop()
            setIsRecording(false)
            if (timerRef.current) {
                clearInterval(timerRef.current)
                timerRef.current = null
            }
        }
    }

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    const handleAiGenerate = async () => {
        if (files.length === 0 || !productName) {
            setError(t('simulation_form.error_ai_write_fail'))
            return
        }
        setAiLoading(true)
        setError("")

        try {
            const formData = new FormData()
            // 傳送所有圖片
            if (files.length > 0) {
                files.forEach(f => formData.append("files", f))
            }

            formData.append("product_name", productName)
            formData.append("price", price || "未定")
            formData.append("style", selectedStyle)
            formData.append("language", language)

            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const res = await fetch(`${API_BASE_URL}/api/web/generate-description`, {
                method: "POST",
                body: formData,
            })

            const data = await res.json()
            if (data.error) throw new Error(data.error)

            // 後端現在只返回單篇文案
            if (data.copy_content) {
                setDescription(data.copy_content)
            } else if (data.option_a) {
                // 向後兼容舊格式
                setDescription(`${data.option_a}\n\n━━━━━━━━━━━━━━\n\n${data.option_b}`)
            }

        } catch (err: any) {
            console.error(err)
            setError(err.message || "AI 生成失敗")
        }
        setAiLoading(false)
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        // Guard: Only allow submit on Step 2
        if (step !== 2) {
            return
        }

        if (files.length === 0) {
            setError(t('simulation_form.error_no_file'))
            return
        }

        setLoading(true)
        setError("")

        try {
            const formData = new FormData()
            files.forEach(f => formData.append("files", f))

            if (mode === 'image') {
                formData.append("product_name", productName)
                formData.append("price", price)
                formData.append("description", description)
                // 🔍 傳遞市場比價資料
                if (marketPrices) {
                    formData.append("market_prices", JSON.stringify(marketPrices))
                }
                formData.append("style", selectedStyle)
                formData.append("language", language)
            }

            // Add Scenario Mode
            formData.append("analysis_scenario", analysisScenario)

            // Add Targeting Params (含市場選擇)
            const targetingData = {
                age_range: targetAge,
                gender: targetGender,
                occupations: targetOccupations,
                tam: tam,  // 傳遞計算後的 TAM 值
                target_market: targetMarket  // 🌍 傳遞目標市場
            }
            formData.append("targeting", JSON.stringify(targetingData))
            formData.append("expert_mode", expertMode.toString())
            formData.append("force_random", forceRandom.toString()) // [New] Pass force_random flag

            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const res = await fetch(`${API_BASE_URL}/api/web/trigger`, {
                method: "POST",
                body: formData,
            })

            if (!res.ok) {
                throw new Error("Upload failed, please check backend connection")
            }

            const data = await res.json()
            if (data.sim_id) {
                router.push(`/watch/${data.sim_id}`)
            } else {
                throw new Error("Failed to get Simulation ID")
            }

        } catch (err: any) {
            console.error(err)
            setError(err.message || "Unknown Error")
            setLoading(false)
        }
    }


    const clearFile = () => {
        setFiles([])
        if (fileInputRef.current) {
            fileInputRef.current.value = ""
        }
    }

    return (
        <div className="w-full max-w-2xl mx-auto bg-slate-900/80 backdrop-blur-xl border border-purple-500/30 rounded-3xl p-6 shadow-2xl shadow-purple-900/20 overflow-hidden relative group">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-50" />


            {/* Iteration Alert Banner */}
            {iterationAlert && (
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`mb-6 p-4 rounded-xl border flex items-start gap-3 ${iterationAlert.type === 'scale'
                        ? 'bg-green-500/10 border-green-500/30 text-green-300'
                        : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                        }`}
                >
                    <span className="text-xl">
                        {iterationAlert.type === 'scale' ? '🚀' : '💡'}
                    </span>
                    <div>
                        <h3 className="font-bold text-sm mb-1">
                            {iterationAlert.type === 'scale' ? t('simulation_form.iteration_alert_scale_title') : t('simulation_form.iteration_alert_pivot_title')}
                        </h3>
                        <p className="text-xs opacity-90 leading-relaxed">
                            {iterationAlert.message}
                        </p>
                    </div>
                </motion.div>
            )}

            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="p-2 bg-purple-500/20 rounded-lg text-purple-400">⚡</span>
                {iterationAlert ? t('simulation_form.title_iteration') : t('simulation_form.title_default')}
            </h2>

            {/* Scenario Switch */}
            <div className="mb-6 bg-slate-950/50 p-1.5 rounded-xl flex gap-2">
                <button
                    onClick={() => setAnalysisScenario('b2c')}
                    className={`flex-1 flex flex-col items-center justify-center py-3 rounded-lg border-2 transition-all gap-1 ${analysisScenario === 'b2c'
                        ? 'bg-purple-900/30 border-purple-500 text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.3)]'
                        : 'bg-transparent border-transparent text-slate-500 hover:bg-slate-800'
                        }`}
                >
                    <div className="flex items-center gap-2">
                        <ShoppingBag className="w-5 h-5" />
                        <span className="font-bold">{t('simulation_form.analysis_mode.b2c')}</span>
                    </div>
                    <span className="text-[10px] opacity-70">{t('simulation_form.analysis_mode.b2c_desc')}</span>
                </button>
                <button
                    onClick={() => setAnalysisScenario('b2b')}
                    className={`flex-1 flex flex-col items-center justify-center py-3 rounded-lg border-2 transition-all gap-1 ${analysisScenario === 'b2b'
                        ? 'bg-blue-900/30 border-blue-500 text-blue-300 shadow-[0_0_15px_rgba(59,130,246,0.3)]'
                        : 'bg-transparent border-transparent text-slate-500 hover:bg-slate-800'
                        }`}
                >
                    <div className="flex items-center gap-2">
                        <Briefcase className="w-5 h-5" />
                        <span className="font-bold">{t('simulation_form.analysis_mode.b2b')}</span>
                    </div>
                    <span className="text-[10px] opacity-70">{t('simulation_form.analysis_mode.b2b_desc')}</span>
                </button>
            </div>

            {/* Tabs */}
            <div className="flex p-1 bg-slate-950/50 rounded-xl mb-6">
                <button
                    onClick={() => { setMode('image'); setFiles([]); }}
                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all ${mode === 'image'
                        ? 'bg-purple-600 text-white shadow-lg'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                        }`}
                >
                    <ImageIcon className="w-4 h-4" />
                    {t('simulation_form.tab_image')}
                </button>
                <button
                    onClick={() => { setMode('pdf'); setFiles([]); }}
                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all ${mode === 'pdf'
                        ? 'bg-purple-600 text-white shadow-lg'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                        }`}
                >
                    <FileText className="w-4 h-4" />
                    {t('simulation_form.tab_pdf')}
                </button>
            </div>



            <form onSubmit={handleSubmit} className="space-y-6">

                {/* Step 1: Product & Copy */}
                {step === 1 && (
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="space-y-6"
                    >
                        {/* File Upload Area */}
                        <div
                            className={`relative border-2 border-dashed rounded-2xl p-8 transition-all text-center cursor-pointer hover:border-purple-400/50 hover:bg-slate-800/50 ${files.length > 0 ? 'border-purple-500/50 bg-purple-900/10' : 'border-slate-700 bg-slate-950/30'
                                }`}
                            onClick={() => files.length === 0 && fileInputRef.current?.click()}
                        >
                            <input
                                type="file"
                                ref={fileInputRef}
                                className="hidden"
                                multiple // Support multiple files
                                accept={mode === 'image' ? "image/*" : ".pdf,.docx,.pptx,.txt,.webm,.mp3,.wav,.m4a"}
                                onChange={handleFileChange}
                            />

                            {files.length > 0 ? (
                                <div className="flex flex-col items-center gap-2 w-full">
                                    {mode === 'image' && previewUrls.length > 0 ? (
                                        <div className="flex flex-wrap justify-center gap-3 w-full">
                                            {previewUrls.map((url, index) => (
                                                <div key={index} className="relative w-24 h-24 rounded-lg overflow-hidden border border-purple-500/30 shadow-sm group/img">
                                                    <img
                                                        src={url}
                                                        alt={`Preview ${index}`}
                                                        className="w-full h-full object-cover"
                                                    />
                                                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover/img:opacity-100 transition-opacity flex items-center justify-center text-xs text-white">
                                                        {index + 1}
                                                    </div>
                                                    <button
                                                        type="button"
                                                        className="absolute top-1 right-1 p-1 bg-red-500/80 text-white rounded-full opacity-0 group-hover/img:opacity-100 transition-opacity hover:bg-red-600"
                                                        onClick={(e) => {
                                                            e.stopPropagation()
                                                            setFiles(prev => prev.filter((_, i) => i !== index))
                                                        }}
                                                    >
                                                        <X className="w-3 h-3" />
                                                    </button>
                                                </div>
                                            ))}
                                            {/* Add More Button */}
                                            <div
                                                onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
                                                className="w-24 h-24 rounded-lg border-2 border-dashed border-purple-500/30 flex items-center justify-center cursor-pointer hover:bg-purple-500/10 hover:border-purple-500/50 transition-all group/add"
                                            >
                                                <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center group-hover/add:bg-purple-500/40">
                                                    <span className="text-xl text-purple-400 font-bold">+</span>
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="p-3 bg-purple-500 rounded-full text-white mb-2">
                                            {mode === 'image' ? <ImageIcon className="w-6 h-6" /> : <FileText className="w-6 h-6" />}
                                        </div>
                                    )}
                                    <p className="text-purple-400 font-bold mt-2">
                                        {files.length === 1 ? files[0].name : t('simulation_form.files_selected').replace('{count}', files.length.toString())}
                                    </p>
                                    <p className="text-slate-500 text-xs">
                                        {files.length === 1
                                            ? (files[0].size / 1024 / 1024).toFixed(2) + " MB"
                                            : `總計 ${(files.reduce((acc, f) => acc + f.size, 0) / 1024 / 1024).toFixed(2)} MB`}
                                    </p>
                                    <button
                                        type="button"
                                        onClick={(e) => { e.stopPropagation(); clearFile(); }}
                                        className="mt-2 px-3 py-1 bg-slate-800 text-slate-300 rounded-full text-xs hover:bg-red-500/20 hover:text-red-400 transition-colors flex items-center gap-1"
                                    >
                                        <X className="w-3 h-3" /> {t('simulation_form.remove_all')}
                                    </button>
                                </div>
                            ) : isRecording ? (
                                /* Recording in progress UI */
                                <div className="flex flex-col items-center gap-4 text-red-400">
                                    <div className="relative">
                                        <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center animate-pulse">
                                            <div className="w-3 h-3 rounded-full bg-red-500 animate-ping"></div>
                                        </div>
                                    </div>
                                    <p className="font-bold text-lg">{t('simulation_form.recording_in_progress')}</p>
                                    <p className="text-2xl font-mono">{formatTime(recordingTime)}</p>
                                    <button
                                        type="button"
                                        onClick={(e) => { e.stopPropagation(); stopRecording(); }}
                                        className="px-6 py-2 bg-red-500 text-white rounded-full font-bold flex items-center gap-2 hover:bg-red-600 transition-colors"
                                    >
                                        <Square className="w-4 h-4" /> {t('simulation_form.stop_recording')}
                                    </button>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-3 text-slate-400">
                                    <Upload className="w-8 h-8 mb-1 opacity-50" />
                                    <p className="font-bold">{mode === 'image' ? t('simulation_form.upload_placeholder_image') : t('simulation_form.upload_placeholder_pdf')}</p>
                                    <p className="text-xs opacity-60">
                                        {mode === 'image' ? t('simulation_form.upload_support_image') : t('simulation_form.upload_support_pdf')}
                                    </p>
                                    {/* Live Recording Button (PDF mode only) */}
                                    {mode === 'pdf' && (
                                        <div className="mt-3 pt-3 border-t border-slate-700/50 w-full flex flex-col items-center gap-2">
                                            <p className="text-xs text-slate-500">{t('simulation_form.or_voice_share')}</p>
                                            <button
                                                type="button"
                                                onClick={(e) => { e.stopPropagation(); startRecording(); }}
                                                className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full font-bold flex items-center gap-2 hover:shadow-lg hover:shadow-purple-500/30 transition-all"
                                            >
                                                <Mic className="w-4 h-4" /> {t('simulation_form.start_recording')}
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Manual Identification Button */}
                            {mode === 'image' && files.length > 0 && (
                                <button
                                    type="button"
                                    onClick={(e) => { e.stopPropagation(); handleIdentifyProduct(); }}
                                    disabled={nameLoading}
                                    className={`mt-4 w-full py-2.5 rounded-xl flex items-center justify-center gap-2 font-bold transition-all ${nameLoading
                                        ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                                        : 'bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 hover:scale-[1.02] border border-purple-500/30'
                                        }`}
                                >
                                    {nameLoading ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            {t('simulation_form.btn_identifying')}
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles className="w-4 h-4" />
                                            {t('simulation_form.btn_identify')}
                                        </>
                                    )}
                                </button>
                            )}
                        </div>

                        {/* Form Inputs (Image Mode Only) */}
                        <AnimatePresence>
                            {mode === 'image' && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="space-y-4"
                                >
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-1">
                                            <label className="text-xs text-slate-400 ml-1 flex items-center gap-2">
                                                {t('simulation_form.label_product_name')}
                                                {nameLoading && <Loader2 className="w-3 h-3 animate-spin text-purple-400" />}
                                            </label>
                                            <input
                                                type="text"
                                                value={productName}
                                                onChange={(e) => setProductName(e.target.value)}
                                                placeholder={nameLoading ? t('simulation_form.placeholder_product_name_loading') : t('simulation_form.placeholder_product_name')}
                                                disabled={nameLoading}
                                                className={`w-full px-4 py-3 bg-slate-950/50 border border-slate-700/50 rounded-xl focus:outline-none focus:border-purple-500/50 text-white placeholder-slate-600 transition-all ${nameLoading ? 'animate-pulse' : ''}`}
                                            />
                                        </div>
                                        <div className="space-y-1">
                                            <label className="text-xs text-slate-400 ml-1 flex items-center gap-2">
                                                {t('simulation_form.label_price')}
                                                {nameLoading && <Loader2 className="w-3 h-3 animate-spin text-purple-400" />}
                                            </label>
                                            <input
                                                ref={priceInputRef}
                                                type="text"
                                                value={price}
                                                onChange={(e) => { setPrice(e.target.value); setPriceSource(""); }}
                                                placeholder={nameLoading ? t('simulation_form.placeholder_price_loading') : t('simulation_form.placeholder_price')}
                                                disabled={nameLoading}
                                                className={`w-full px-4 py-3 bg-slate-950/50 border border-slate-700/50 rounded-xl focus:outline-none focus:border-purple-500/50 text-white placeholder-slate-600 transition-all ${nameLoading ? 'animate-pulse' : ''} ${iterationAlert?.type === 'pivot' ? 'ring-2 ring-amber-500/50' : ''}`}
                                            />
                                            {priceSource && (
                                                <p className="text-[10px] text-purple-400/80 ml-1 mt-1">{priceSource}</p>
                                            )}
                                        </div>
                                    </div>
                                    <div className="space-y-1 relative">
                                        <div className="flex justify-between items-center flex-wrap gap-2">
                                            <label className="text-xs text-slate-400 ml-1">{t('simulation_form.label_desc')}</label>
                                            <div className="flex items-center gap-3">
                                                {/* Style Dropdown with Label */}
                                                <div className="flex items-center gap-2">
                                                    <label className="text-xs text-slate-400 whitespace-nowrap">{t('simulation_form.label_style')}</label>
                                                    <select
                                                        value={selectedStyle}
                                                        onChange={(e) => setSelectedStyle(e.target.value)}
                                                        className="text-sm px-3 py-2 rounded-lg border border-slate-700 bg-slate-950/50 text-slate-300 focus:outline-none focus:border-purple-500/50 cursor-pointer hover:bg-slate-800/50 transition-colors min-w-[120px]"
                                                    >
                                                        {styleOptions.map((opt) => (
                                                            <option key={opt.value} value={opt.value}>
                                                                {opt.label}
                                                            </option>
                                                        ))}
                                                    </select>
                                                </div>
                                                {/* AI Write Button */}
                                                <button
                                                    type="button"
                                                    onClick={handleAiGenerate}
                                                    disabled={aiLoading || files.length === 0 || !productName}
                                                    className={`text-sm px-4 py-2 rounded-lg border flex items-center gap-2 transition-all font-medium ${aiLoading || files.length === 0 || !productName
                                                        ? 'text-slate-600 border-slate-700 cursor-not-allowed bg-slate-900'
                                                        : 'text-purple-400 border-purple-500/50 hover:bg-purple-500/20 hover:border-purple-400 animate-pulse shadow-[0_0_15px_rgba(168,85,247,0.6)] hover:shadow-[0_0_20px_rgba(168,85,247,0.8)]'
                                                        }`}
                                                >
                                                    <Sparkles className="w-4 h-4" />
                                                    {aiLoading ? t('simulation_form.btn_ai_writing') : t('simulation_form.btn_ai_write')}
                                                </button>
                                            </div>
                                        </div>
                                        <textarea
                                            value={description}
                                            onChange={(e) => setDescription(e.target.value)}
                                            placeholder={aiLoading ? t('simulation_form.placeholder_desc_loading') : t('simulation_form.placeholder_desc')}
                                            rows={5}
                                            className={`w-full px-4 py-3 bg-slate-950/50 border border-slate-700/50 rounded-xl focus:outline-none focus:border-purple-500/50 text-white placeholder-slate-600 transition-all resize-none ${aiLoading ? 'animate-pulse' : ''
                                                }`}
                                        />
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>
                )}

                {/* Step 2: Targeting & Expert Mode */}
                {step === 2 && (
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        className="space-y-6"
                    >
                        {/* 🌍 Market Selector (Chameleon Architecture) */}
                        <div className="space-y-3">
                            <label className="text-sm font-bold text-slate-300 flex items-center gap-2">
                                <Globe className="w-4 h-4 text-blue-400" />
                                {t('simulation_form.step2_market_label')}
                            </label>
                            <div className="flex gap-2">
                                {(Object.keys(MARKET_CONFIG) as MarketKey[]).map((key) => {
                                    const config = MARKET_CONFIG[key];
                                    return (
                                        <button
                                            key={key}
                                            type="button"
                                            onClick={() => setTargetMarket(key)}
                                            className={`flex-1 py-3 rounded-xl border-2 transition-all flex flex-col items-center gap-1 ${targetMarket === key
                                                ? 'bg-blue-900/30 border-blue-500 text-blue-300 shadow-[0_0_15px_rgba(59,130,246,0.3)]'
                                                : 'bg-slate-900 border-slate-700 text-slate-500 hover:border-slate-500'
                                                }`}
                                        >
                                            <span className="text-2xl">{config.flag}</span>
                                            <span className="text-sm font-bold">{t(`simulation_form.${config.labelKey}`)}</span>
                                            <span className="text-[10px] opacity-70">{config.currency}</span>
                                        </button>
                                    );
                                })}
                            </div>
                            {/* ⚠️ 貨幣提示防呆 (Currency Unit Warning) */}
                            {targetMarket !== 'TW' && (
                                <p className="text-xs text-amber-400/80 bg-amber-500/10 border border-amber-500/20 rounded-lg px-3 py-2 flex items-start gap-2">
                                    <span>⚠️</span>
                                    <span>{t(`simulation_form.step2_market_currency_warning_${targetMarket.toLowerCase()}`)}</span>
                                </p>
                            )}
                        </div>

                        {/* Fermi Panel (Stats) */}
                        <div className="bg-slate-950/50 rounded-xl p-6 border border-slate-800 space-y-4">
                            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                <TrendingUp className="w-4 h-4 text-emerald-400" />
                                {t('simulation_form.step2_fermi_title')}
                            </h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 rounded-lg bg-slate-900 border border-slate-800">
                                    <p className="text-xs text-slate-500 mb-1">{t('simulation_form.step2_fermi_tam')}</p>
                                    <p className="text-base sm:text-xl lg:text-2xl font-bold text-white tabular-nums">
                                        {new Intl.NumberFormat('en-US').format(tam)}
                                    </p>
                                    <p className="text-[10px] text-slate-600 mt-1">{t('simulation_form.step2_fermi_tam_desc')}</p>
                                </div>
                                <div className="p-4 rounded-lg bg-slate-900 border border-slate-800 relative group">
                                    <p className="text-xs text-slate-500 mb-1">{t('simulation_form.step2_fermi_sample')}</p>
                                    <p className="text-lg sm:text-xl lg:text-2xl font-bold text-purple-400 tabular-nums">1,000</p>
                                    <p className="text-[10px] text-slate-600 mt-1">{t('simulation_form.step2_fermi_sample_desc')}</p>
                                    {/* Tooltip */}
                                    <div className="absolute -top-12 left-1/2 -translate-x-1/2 bg-slate-800 text-slate-300 text-xs p-2 rounded shadow-xl opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                                        {t('simulation_form.step2_fermi_tooltip')}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Controls */}
                        <div className="space-y-6">
                            {/* Age Slider */}
                            <div className="space-y-3">
                                <label className="text-sm font-bold text-slate-300 flex justify-between">
                                    <span>{t('simulation_form.step2_age_label')}</span>
                                    <span className="text-purple-400">{targetAge[0]} - {targetAge[1] === 60 ? '60+' : targetAge[1]} {t('simulation_form.step2_age_unit')}</span>
                                </label>
                                <input
                                    type="range"
                                    min="20"
                                    max="60"
                                    step="5"
                                    value={targetAge[1]}
                                    onChange={(e) => {
                                        const val = parseInt(e.target.value)
                                        if (val > targetAge[0]) setTargetAge([targetAge[0], val])
                                    }}
                                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
                                />
                                <div className="flex justify-between text-xs text-slate-600 font-mono">
                                    <span>20</span>
                                    <span>30</span>
                                    <span>40</span>
                                    <span>50</span>
                                    <span>60+</span>
                                </div>
                            </div>

                            {/* Gender Switch */}
                            <div className="space-y-3">
                                <label className="text-sm font-bold text-slate-300">{t('simulation_form.step2_gender_label')}</label>
                                <div className="flex bg-slate-950 rounded-lg p-1 border border-slate-800">
                                    {['all', 'male', 'female'].map((g) => (
                                        <button
                                            key={g}
                                            type="button"
                                            onClick={() => setTargetGender(g as any)}
                                            className={`flex-1 py-2 rounded-md text-sm font-medium transition-all ${targetGender === g ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-500 hover:text-slate-300'
                                                }`}
                                        >
                                            {g === 'all' ? t('simulation_form.step2_gender_all') : g === 'male' ? t('simulation_form.step2_gender_male') : t('simulation_form.step2_gender_female')}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Occupation Tags */}
                            <div className="space-y-3">
                                <label className="text-sm font-bold text-slate-300">{t('simulation_form.step2_occupation_label')}</label>
                                <div className="flex flex-wrap gap-2">
                                    {[
                                        { id: 'student', labelKey: 'step2_occ_student' },
                                        { id: 'office_worker', labelKey: 'step2_occ_office' },
                                        { id: 'executive', labelKey: 'step2_occ_executive' },
                                        { id: 'entrepreneur', labelKey: 'step2_occ_entrepreneur' }
                                    ].map((occ) => (
                                        <button
                                            key={occ.id}
                                            type="button"
                                            onClick={() => {
                                                if (targetOccupations.includes(occ.id)) {
                                                    setTargetOccupations(prev => prev.filter(x => x !== occ.id))
                                                } else {
                                                    setTargetOccupations(prev => [...prev, occ.id])
                                                }
                                            }}
                                            className={`px-3 py-1.5 rounded-full text-xs font-bold border transition-all ${targetOccupations.includes(occ.id)
                                                ? 'bg-purple-500/20 border-purple-500 text-purple-300'
                                                : 'bg-slate-900 border-slate-700 text-slate-500 hover:border-slate-500'
                                                }`}
                                        >
                                            {t(`simulation_form.${occ.labelKey}`)}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Expert Mode */}
                            <div className="pt-4 border-t border-slate-800">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className={`p-2 rounded-lg transition-colors ${expertMode ? 'bg-red-500/20 text-red-500' : 'bg-slate-800 text-slate-500'}`}>
                                            <ShieldAlert className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <h4 className={`font-bold text-sm ${expertMode ? 'text-red-400' : 'text-slate-400'}`}>{t('simulation_form.expert_mode_title')}</h4>
                                            <p className="text-xs text-slate-500">{t('simulation_form.expert_mode_desc')}</p>
                                        </div>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => setExpertMode(!expertMode)}
                                        aria-label={t('simulation_form.expert_mode_title')}
                                        className={`w-12 h-6 rounded-full relative transition-colors ${expertMode ? 'bg-red-500' : 'bg-slate-700'}`}
                                    >
                                        <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${expertMode ? 'left-7' : 'left-1'}`} />
                                    </button>
                                </div>
                                {/* Expert Mode Detail Explanation */}
                                {expertMode && (
                                    <p className="mt-3 text-xs text-red-400/80 bg-red-500/5 border border-red-500/20 rounded-lg p-3">
                                        {t('simulation_form.expert_mode_detail')}
                                    </p>
                                )}
                            </div>

                            {/* Force Random Mode (New) */}
                            <div className="pt-4 border-t border-slate-800">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className={`p-2 rounded-lg transition-colors ${forceRandom ? 'bg-purple-500/20 text-purple-500' : 'bg-slate-800 text-slate-500'}`}>
                                            <Dices className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <h4 className={`font-bold text-sm ${forceRandom ? 'text-purple-400' : 'text-slate-400'}`}>
                                                {t('simulation_form.force_random_title') || "隨機重抽 (True Randomness)"}
                                            </h4>
                                            <p className="text-xs text-slate-500">
                                                {t('simulation_form.force_random_desc') || "開啟後將忽略檔案快取，強制重新隨機抽取每一位市民。"}
                                            </p>
                                        </div>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => setForceRandom(!forceRandom)}
                                        aria-label={t('simulation_form.force_random_title')}
                                        className={`w-12 h-6 rounded-full relative transition-colors ${forceRandom ? 'bg-purple-600' : 'bg-slate-700'}`}
                                    >
                                        <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${forceRandom ? 'left-7' : 'left-1'}`} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* Error Message */}
                {error && (
                    <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm text-center">
                        {error}
                    </div>
                )}

                {/* Submit / Next Button */}
                <div className="flex gap-3">
                    {step === 2 && (
                        <button
                            type="button"
                            onClick={() => setStep(1)}
                            disabled={loading}
                            className="px-6 py-4 rounded-xl font-bold text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                        >
                            {t('simulation_form.step2_back')}
                        </button>
                    )}

                    {step === 1 ? (
                        <button
                            type="button"
                            onClick={(e) => {
                                e.preventDefault()
                                e.stopPropagation()
                                if (files.length === 0) {
                                    setError(t('simulation_form.error_no_file'))
                                    return
                                }
                                setStep(2)
                            }}
                            className="flex-1 py-4 rounded-xl font-bold text-lg tracking-widest bg-slate-800 hover:bg-slate-700 text-white transition-all shadow-lg flex items-center justify-center gap-2 group"
                        >
                            {t('simulation_form.step2_next')} <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                        </button>
                    ) : (
                        <button
                            type="submit"
                            disabled={loading || aiLoading}
                            className={`flex-1 py-4 rounded-xl font-bold text-lg tracking-widest transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] shadow-lg ${loading || aiLoading
                                ? "bg-slate-700 text-slate-400 cursor-not-allowed"
                                : expertMode
                                    ? "bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 text-white shadow-red-500/30"
                                    : "bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400 text-white shadow-purple-500/30"
                                }`}
                        >
                            {loading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <span className="animate-spin text-xl">⚡</span> {t('simulation_form.submit_btn_loading')}
                                </span>
                            ) : (
                                <span className="flex items-center justify-center gap-2">
                                    {expertMode ? '🔥 啟動專家級預演' : t('simulation_form.submit_btn')}
                                </span>
                            )}
                        </button>
                    )}
                </div>

                <p className="flex items-center gap-2 text-xs text-slate-500 mt-4 justify-center">
                    <Sparkles className="w-3 h-3 text-[#d8b4fe]" />
                    {t('simulation_form.footer_note')}
                </p>

                <div className="mt-8 pt-4 border-t border-white/5 flex flex-col items-center gap-2">
                    <button
                        type="button"
                        onClick={handleResetDB}
                        disabled={isResetting}
                        className="text-[10px] text-slate-600 hover:text-red-400 disabled:opacity-50 transition-colors flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-white/5 group"
                    >
                        {isResetting ? <Loader2 className="w-3 h-3 animate-spin" /> : <span className="material-symbols-outlined text-[14px]">database</span>}
                        {isResetting ? t('simulation_form.admin_init_loading') : t('simulation_form.admin_init')}
                    </button>
                </div>
            </form>
        </div >
    )
}
