"use client"

import { useEffect } from 'react'

/**
 * 後端喚醒元件
 * 在頁面載入時自動發送請求到後端，防止 Render 免費方案的服務休眠
 * Render 免費方案會在 15 分鐘無活動後進入休眠狀態
 */
export default function BackendWakeup() {
    useEffect(() => {
        const wakeUpBackend = async () => {
            try {
                const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
                // 發送靜默請求喚醒後端，不阻塞 UI
                await fetch(API_BASE_URL, {
                    method: 'GET',
                    // 設定較短的超時，避免影響使用者體驗
                    signal: AbortSignal.timeout(10000)
                })
                console.log("✅ Backend wake-up request sent successfully")
            } catch (error) {
                // 靜默處理錯誤，不影響使用者體驗
                console.log("ℹ️ Backend wake-up: ", error instanceof Error ? error.message : "Request sent")
            }
        }

        // 頁面載入後立即發送喚醒請求
        wakeUpBackend()
    }, [])

    // 此元件不渲染任何 UI
    return null
}
