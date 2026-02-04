from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks
from typing import List
from app.core.database import create_simulation, insert_citizens_batch, get_citizens_count, clear_citizens, get_citizen_by_id, update_simulation
import uuid
from app.services.video_analysis_service import video_analysis_service

import sys
import os
import json

print("[WEB] Module web.py loaded!", flush=True)

# 確保可以導入 create_citizens
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from create_citizens import generate_citizen

router = APIRouter()

# 🔧 Debug wrapper to catch background task exceptions
async def safe_run_pdf_task(line_service, *args, **kwargs):
    """Wrapper to catch and log any exceptions from PDF background task"""
    try:
        with open("debug_trace.log", "a", encoding="utf-8") as f:
            f.write(f"[WRAPPER] Starting PDF task with {len(args)} args, {len(kwargs)} kwargs\n")
        await line_service.run_simulation_with_pdf_data(*args, **kwargs)
    except Exception as e:
        import traceback
        error_msg = f"[WRAPPER] PDF Task Failed: {e}\n{traceback.format_exc()}"
        print(error_msg, flush=True)
        with open("debug_trace.log", "a", encoding="utf-8") as f:
            f.write(error_msg + "\n")
        with open("last_error.txt", "w", encoding="utf-8") as f:
            f.write(error_msg)
        
        # 🛡️ Update DB to error state so frontend knows it failed
        try:
            # Assuming sim_id is the first argument in args
            if args:
                sim_id = args[0]
                update_simulation(sim_id, "error", {
                    "status": "error",
                    "summary": f"系統錯誤: {str(e)}",
                    "score": 0,
                    "intent": "Error",
                    "genesis": {"total_population": 0, "sample_size": 0, "personas": []},
                    "comments": []
                })
        except:
            pass

async def run_video_audit_task(
    sim_id: str, 
    video_url: str, 
    product_name: str = None, 
    price: str = None,
    description: str = None,
    style: str = "專業穩重",
    language: str = "zh-TW",
    targeting_data: dict = None,
    is_expert_mode: bool = False,
    is_force_random: bool = False,
    analysis_scenario: str = "b2c",
    seed_salt: int = 0
):
    """Background task for video analysis and simulation with full params"""
    try:
        print(f">> [Task] Starting video audit for {video_url} (ID: {sim_id})")
        
        # ⏬ 階段 1：開始下載視頻
        update_simulation(sim_id, "processing", {
            "status": "processing",
            "summary": "📥 正在下載視頻（限制前60秒）...",
            "score": 0,
            "intent": "Processing..."
        })
        
        # 1. AI 視覺審片
        report_data = video_analysis_service.analyze_video_content(video_url)
        
        # [CRITICAL FIX] 完整錯誤攔截（包含 None 和 error 字段）
        # 避免使用錯誤的 citizen_briefing 進行市民模擬
        if not report_data or report_data.get("error"):
            error_type = report_data.get("error", "UNKNOWN_ERROR") if report_data else "NO_RESPONSE"
            error_msg = report_data.get("message", "AI 審片失敗") if report_data else "無回應"
            
            # 根據錯誤類型提供針對性建議
            suggestion_map = {
                "VIDEO_DOWNLOAD_FAILED": "影片下載失敗。請確認：1.連結是否有效 2.是否有防盜鏈限制 3.嘗試上傳本地 MP4 檔案",
                "VIDEO_UNREADABLE": "AI 無法識別影片內容。可能是下載了非影片文件（如 HTML 錯誤頁面）。請更換連結。",
                "UPLOAD_FAILED": "影片上傳至 AI 服務失敗。請稍後重試。",
                "PROCESSING_FAILED": "AI 處理影片時發生錯誤。請嘗試較短或較小的影片。",
            }
            suggestion = suggestion_map.get(error_type, "請嘗試：1.更換有效的影片連結 2.確保連結可直接下載 3.上傳本地 MP4 檔案")
            
            update_simulation(sim_id, "error", {
                "status": "error",
                "summary": f"[{error_type}] {error_msg}",
                "score": 0,
                "intent": "Error",
                "genesis": {"total_population": 0, "sample_size": 0, "personas": []},
                "comments": [],
                "error_details": {
                    "type": error_type,
                    "message": error_msg,
                    "suggestion": suggestion
                }
            })
            print(f">> [Task] Video audit BLOCKED due to error: {error_type} - {error_msg}")
            return
        
        # ⏬ 階段 2：AI 分析完成，開始市民模擬
        update_simulation(sim_id, "processing", {
            "status": "processing",
            "summary": "🤖 AI 視覺分析完成，正在召喚 1,000 位市民進行評估...",
            "score": 0,
            "intent": "Processing..."
        })
             
        # 2. 市民市場模擬 (傳入完整產品資訊與目標市場參數)
        sim_result = video_analysis_service.run_market_simulation(
            report_data, 
            video_url, 
            product_name=product_name, 
            price=price,
            description=description,
            style=style,
            language=language,
            targeting_data=targeting_data,
            is_expert_mode=is_expert_mode,
            is_force_random=is_force_random,
            analysis_scenario=analysis_scenario,
            seed_salt=seed_salt
        )
        
        # 3. 組合最終結果
        final_data = {
            "status": "completed",
            "report": report_data,
            "simulation": sim_result,
            "simulation_logs": sim_result.get("simulation_logs", []),
            # 前端相容性轉換
            "score": sim_result["score"],
            "summary": report_data.get("citizen_briefing", ""),
            "intent": sim_result["decision"],
            "comments": sim_result["top_reviews"],
            "genesis": {
                "total_population": 1000,
                "sample_size": len(sim_result["top_reviews"]),
                "personas": sim_result["top_reviews"]
            }
