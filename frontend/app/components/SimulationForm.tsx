"use client"

import { useState, useRef, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileText, Image as ImageIcon, Loader2, ArrowRight, X, Sparkles, Mic, Square } from 'lucide-react'

export default function SimulationForm() {
    const router = useRouter()
    const [mode, setMode] = useState<'image' | 'pdf'>('image')
    const [files, setFiles] = useState<File[]>([])
    const [loading, setLoading] = useState(false)
    const [aiLoading, setAiLoading] = useState(false)
    const [nameLoading, setNameLoading] = useState(false) // AI 識別產品名稱的加載狀態
    const [error, setError] = useState("")
    const [previewUrls, setPreviewUrls] = useState<string[]>([])
    const [iterationAlert, setIterationAlert] = useState<{ type: 'pivot' | 'scale'; message: string } | null>(null)
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
                    message: "上一輪表現優異！建議上傳不同風格的素材進行 A/B 測試，擴大勝果 (Scale)。"
                })
            } else {
                // Pivot or Restart match
                setIterationAlert({
                    type: 'pivot',
                    message: "建議根據分析結果微調定價或產品描述，嘗試新的市場切入點 (Pivot)。"
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
        { value: "professional", label: "專業穩重", desc: "正式、專業的商務風格" },
        { value: "friendly", label: "親切活潑", desc: "輕鬆、有親和力的風格" },
        { value: "luxury", label: "高端奢華", desc: "精緻、高質感的品牌調性" },
        { value: "minimalist", label: "簡約清爽", desc: "簡潔有力、重點突出" },
        { value: "storytelling", label: "故事敘述", desc: "用故事帶入產品情境" },
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
                alert("✅ 資料庫初始化成功！\n現在您可以開始進行模擬分析。")
            } else {
                const txt = await res.text()
                alert(`❌ 初始化失敗: ${txt}`)
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
                setPrice(data.estimated_price.toString())
            }
            // 設置價格來源說明
            if (data.price_source) {
                setPriceSource(`💡 ${data.price_source}${data.price_range ? ` (價格範圍: ${data.price_range})` : ''}`)
            }
            // 🔍 存儲市場比價資料
            if (data.market_prices) {
                setMarketPrices(data.market_prices)
                // 如果有成功取得市場比價，更新價格來源顯示
                if (data.market_prices.success && data.market_prices.sources_count > 0) {
                    setPriceSource(`📊 已比對 ${data.market_prices.sources_count} 個電商平台：${data.market_prices.search_summary}`)
                }
            }
        } catch (err) {
            console.error("Product identification failed:", err)
            setError("識別失敗，請稍後再試或手動輸入")
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
            setError("無法啟動麥克風，請確認瀏覽器權限")
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
            setError("請先上傳圖片並輸入產品名稱")
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
        if (files.length === 0) {
            setError("請先上傳檔案")
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
            }

            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const res = await fetch(`${API_BASE_URL}/api/web/trigger`, {
                method: "POST",
                body: formData,
            })

            if (!res.ok) {
                throw new Error("上傳失敗，請檢查後端連線")
            }

            const data = await res.json()
            if (data.sim_id) {
                router.push(`/watch/${data.sim_id}`)
            } else {
                throw new Error("無法取得 Simulation ID")
            }

        } catch (err: any) {
            console.error(err)
            setError(err.message || "發生未知錯誤")
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
                            {iterationAlert.type === 'scale' ? '準備擴大規模 (Scale)' : '啟動迭代優化 (Pivot)'}
                        </h3>
                        <p className="text-xs opacity-90 leading-relaxed">
                            {iterationAlert.message}
                        </p>
                    </div>
                </motion.div>
            )}

            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="p-2 bg-purple-500/20 rounded-lg text-purple-400">⚡</span>
                {iterationAlert ? '延續預演迭代' : '啟動「鏡界」預演'}
            </h2>

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
                    產品圖片
                </button>
                <button
                    onClick={() => { setMode('pdf'); setFiles([]); }}
                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all ${mode === 'pdf'
                        ? 'bg-purple-600 text-white shadow-lg'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                        }`}
                >
                    <FileText className="w-4 h-4" />
                    商業計劃 / 想法
                </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">

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
                                {files.length === 1 ? files[0].name : `已選擇 ${files.length} 個檔案`}
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
                                <X className="w-3 h-3" /> 移除全部
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
                            <p className="font-bold text-lg">錄音中...</p>
                            <p className="text-2xl font-mono">{formatTime(recordingTime)}</p>
                            <button
                                type="button"
                                onClick={(e) => { e.stopPropagation(); stopRecording(); }}
                                className="px-6 py-2 bg-red-500 text-white rounded-full font-bold flex items-center gap-2 hover:bg-red-600 transition-colors"
                            >
                                <Square className="w-4 h-4" /> 停止錄音
                            </button>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center gap-3 text-slate-400">
                            <Upload className="w-8 h-8 mb-1 opacity-50" />
                            <p className="font-bold">點擊上傳 {mode === 'image' ? '產品圖片' : '商業計劃文件'}</p>
                            <p className="text-xs opacity-60">
                                {mode === 'image' ? '支援 JPG, PNG, WEBP' : '支援 PDF, Word, PPT, TXT, 錄音檔'}
                            </p>
                            {/* Live Recording Button (PDF mode only) */}
                            {mode === 'pdf' && (
                                <div className="mt-3 pt-3 border-t border-slate-700/50 w-full flex flex-col items-center gap-2">
                                    <p className="text-xs text-slate-500">或者用語音分享您的想法</p>
                                    <button
                                        type="button"
                                        onClick={(e) => { e.stopPropagation(); startRecording(); }}
                                        className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full font-bold flex items-center gap-2 hover:shadow-lg hover:shadow-purple-500/30 transition-all"
                                    >
                                        <Mic className="w-4 h-4" /> 開始錄音
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
                                    AI 正在分析產品...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-4 h-4" />
                                    AI 識別品名與估價
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
                                        產品名稱
                                        {nameLoading && <Loader2 className="w-3 h-3 animate-spin text-purple-400" />}
                                    </label>
                                    <input
                                        type="text"
                                        value={productName}
                                        onChange={(e) => setProductName(e.target.value)}
                                        placeholder={nameLoading ? "AI 識別中..." : "例：智能咖啡機"}
                                        disabled={nameLoading}
                                        className={`w-full px-4 py-3 bg-slate-950/50 border border-slate-700/50 rounded-xl focus:outline-none focus:border-purple-500/50 text-white placeholder-slate-600 transition-all ${nameLoading ? 'animate-pulse' : ''}`}
                                    />
                                </div>
                                <div className="space-y-1">
                                    <label className="text-xs text-slate-400 ml-1 flex items-center gap-2">
                                        建議售價 (TWD)
                                        {nameLoading && <Loader2 className="w-3 h-3 animate-spin text-purple-400" />}
                                    </label>
                                    <input
                                        ref={priceInputRef}
                                        type="text"
                                        value={price}
                                        onChange={(e) => { setPrice(e.target.value); setPriceSource(""); }}
                                        placeholder={nameLoading ? "AI 估價中..." : "例：2990"}
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
                                    <label className="text-xs text-slate-400 ml-1">產品描述與特色 (選填)</label>
                                    <div className="flex items-center gap-2">
                                        {/* Style Dropdown */}
                                        <select
                                            value={selectedStyle}
                                            onChange={(e) => setSelectedStyle(e.target.value)}
                                            className="text-[10px] px-2 py-1 rounded-full border border-slate-700 bg-slate-950/50 text-slate-300 focus:outline-none focus:border-purple-500/50 cursor-pointer"
                                        >
                                            {styleOptions.map((opt) => (
                                                <option key={opt.value} value={opt.value}>
                                                    {opt.label}
                                                </option>
                                            ))}
                                        </select>
                                        <button
                                            type="button"
                                            onClick={handleAiGenerate}
                                            disabled={aiLoading || files.length === 0 || !productName}
                                            className={`text-[10px] px-2 py-1 rounded-full border flex items-center gap-1 transition-all ${aiLoading || files.length === 0 || !productName
                                                ? 'text-slate-600 border-slate-700 cursor-not-allowed'
                                                : 'text-purple-400 border-purple-500/50 hover:bg-purple-500/20 hover:border-purple-400 animate-pulse shadow-[0_0_10px_rgba(168,85,247,0.5)]'
                                                }`}
                                        >
                                            <Sparkles className="w-3 h-3" />
                                            {aiLoading ? 'AI 構思中...' : '讓 AI 幫寫'}
                                        </button>
                                    </div>
                                </div>
                                <textarea
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    placeholder={aiLoading ? "AI 正在觀察您的圖片並撰寫文案..." : "輸入產品特色，讓 AI 更精準分析..."}
                                    rows={5}
                                    className={`w-full px-4 py-3 bg-slate-950/50 border border-slate-700/50 rounded-xl focus:outline-none focus:border-purple-500/50 text-white placeholder-slate-600 transition-all resize-none ${aiLoading ? 'animate-pulse' : ''
                                        }`}
                                />
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Error Message */}
                {error && (
                    <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm text-center">
                        {error}
                    </div>
                )}

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={loading || aiLoading}
                    className={`w-full py-4 rounded-xl font-bold text-lg tracking-widest transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] shadow-lg ${loading || aiLoading
                        ? "bg-slate-700 text-slate-400 cursor-not-allowed"
                        : "bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400 text-white shadow-purple-500/30"
                        }`}
                >
                    {loading ? (
                        <span className="flex items-center justify-center gap-2">
                            <span className="animate-spin text-xl">⚡</span> 正在開啟鏡像世界...
                        </span>
                    ) : (
                        <span className="flex items-center justify-center gap-2">
                            啟動 MIRRA 預演
                        </span>
                    )}
                </button>

                <p className="flex items-center gap-2 text-xs text-slate-500 mt-4 justify-center">
                    <Sparkles className="w-3 h-3 text-[#d8b4fe]" />
                    系統將自動召喚 1,000+ 位虛擬市民進行即時推演
                </p>

                <div className="mt-8 pt-4 border-t border-white/5 flex flex-col items-center gap-2">
                    <button
                        type="button"
                        onClick={handleResetDB}
                        disabled={isResetting}
                        className="text-[10px] text-slate-600 hover:text-red-400 disabled:opacity-50 transition-colors flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-white/5 group"
                    >
                        {isResetting ? <Loader2 className="w-3 h-3 animate-spin" /> : <span className="material-symbols-outlined text-[14px]">database</span>}
                        {isResetting ? "正在初始化..." : "初始化資料庫 (Admin)"}
                    </button>
                </div>
            </form>
        </div >
    )
}
