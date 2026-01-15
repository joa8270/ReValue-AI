"use client"

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileText, Image as ImageIcon, Loader2, ArrowRight, X, Sparkles, Mic, Square } from 'lucide-react'

export default function SimulationForm() {
    const router = useRouter()
    const [mode, setMode] = useState<'image' | 'pdf'>('image')
    const [file, setFile] = useState<File | null>(null)
    const [loading, setLoading] = useState(false)
    const [aiLoading, setAiLoading] = useState(false)
    const [error, setError] = useState("")
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)

    // Recording State
    const [isRecording, setIsRecording] = useState(false)
    const [recordingTime, setRecordingTime] = useState(0)
    const mediaRecorderRef = useRef<MediaRecorder | null>(null)
    const audioChunksRef = useRef<Blob[]>([])
    const timerRef = useRef<NodeJS.Timeout | null>(null)

    useEffect(() => {
        if (!file || !file.type.startsWith('image/')) {
            setPreviewUrl(null)
            return
        }

        const objectUrl = URL.createObjectURL(file)
        setPreviewUrl(objectUrl)

        return () => URL.revokeObjectURL(objectUrl)
    }, [file])

    // Form Fields
    const [productName, setProductName] = useState("")
    const [price, setPrice] = useState("")
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

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0])
            setError("")
        }
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
                setFile(audioFile)
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
        if (!file || !productName) {
            setError("請先上傳圖片並輸入產品名稱")
            return
        }
        setAiLoading(true)
        setError("")

        try {
            const formData = new FormData()
            formData.append("file", file)
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

            // 這裡可以做一個簡單的 Modal 讓用戶選 A 或 B，目前先簡單接上
            setDescription(`${data.option_a}\n\n━━━━━━━━━━━━━━\n\n${data.option_b}`)

        } catch (err: any) {
            console.error(err)
            setError(err.message || "AI 生成失敗")
        }
        setAiLoading(false)
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!file) {
            setError("請先上傳檔案")
            return
        }

        setLoading(true)
        setError("")

        try {
            const formData = new FormData()
            formData.append("file", file)

            if (mode === 'image') {
                formData.append("product_name", productName)
                formData.append("price", price)
                formData.append("description", description)
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
        setFile(null)
        if (fileInputRef.current) {
            fileInputRef.current.value = ""
        }
    }

    return (
        <div className="w-full max-w-2xl mx-auto bg-slate-900/80 backdrop-blur-xl border border-purple-500/30 rounded-3xl p-6 shadow-2xl shadow-purple-900/20 overflow-hidden relative group">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-50" />

            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="p-2 bg-purple-500/20 rounded-lg text-purple-400">⚡</span>
                啟動「鏡界」預演
            </h2>

            {/* Tabs */}
            <div className="flex p-1 bg-slate-950/50 rounded-xl mb-6">
                <button
                    onClick={() => { setMode('image'); setFile(null); }}
                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all ${mode === 'image'
                        ? 'bg-purple-600 text-white shadow-lg'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                        }`}
                >
                    <ImageIcon className="w-4 h-4" />
                    產品圖片
                </button>
                <button
                    onClick={() => { setMode('pdf'); setFile(null); }}
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
                    className={`relative border-2 border-dashed rounded-2xl p-8 transition-all text-center cursor-pointer hover:border-purple-400/50 hover:bg-slate-800/50 ${file ? 'border-purple-500/50 bg-purple-900/10' : 'border-slate-700 bg-slate-950/30'
                        }`}
                    onClick={() => !file && fileInputRef.current?.click()}
                >
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        accept={mode === 'image' ? "image/*" : ".pdf,.docx,.pptx,.txt,.webm,.mp3,.wav,.m4a"}
                        onChange={handleFileChange}
                    />

                    {file ? (
                        <div className="flex flex-col items-center gap-2">
                            {mode === 'image' && previewUrl ? (
                                <div className="relative w-48 h-48 rounded-xl overflow-hidden mb-2 border-2 border-purple-500/50 shadow-lg shadow-purple-900/20">
                                    <img
                                        src={previewUrl}
                                        alt="Preview"
                                        className="w-full h-full object-cover"
                                    />
                                </div>
                            ) : (
                                <div className="p-3 bg-purple-500 rounded-full text-white mb-2">
                                    {mode === 'image' ? <ImageIcon className="w-6 h-6" /> : <FileText className="w-6 h-6" />}
                                </div>
                            )}
                            <p className="text-purple-400 font-bold">{file.name}</p>
                            <p className="text-slate-500 text-xs">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                            <button
                                type="button"
                                onClick={(e) => { e.stopPropagation(); clearFile(); }}
                                className="mt-2 px-3 py-1 bg-slate-800 text-slate-300 rounded-full text-xs hover:bg-red-500/20 hover:text-red-400 transition-colors flex items-center gap-1"
                            >
                                <X className="w-3 h-3" /> 移除檔案
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
                                    <label className="text-xs text-slate-400 ml-1">產品名稱</label>
                                    <input
                                        type="text"
                                        value={productName}
                                        onChange={(e) => setProductName(e.target.value)}
                                        placeholder="例：智能咖啡機"
                                        className="w-full px-4 py-3 bg-slate-950/50 border border-slate-700/50 rounded-xl focus:outline-none focus:border-purple-500/50 text-white placeholder-slate-600 transition-all"
                                    />
                                </div>
                                <div className="space-y-1">
                                    <label className="text-xs text-slate-400 ml-1">建議售價 (選填)</label>
                                    <input
                                        type="text"
                                        value={price}
                                        onChange={(e) => setPrice(e.target.value)}
                                        placeholder="例：2990"
                                        className="w-full px-4 py-3 bg-slate-950/50 border border-slate-700/50 rounded-xl focus:outline-none focus:border-purple-500/50 text-white placeholder-slate-600 transition-all"
                                    />
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
                                            disabled={aiLoading || !file || !productName}
                                            className={`text-[10px] px-2 py-1 rounded-full border flex items-center gap-1 transition-all ${aiLoading || !file || !productName
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
