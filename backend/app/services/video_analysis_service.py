"""
MIRRA // 全真視覺分析引擎 (True Vision Engine)
===============================================
使用 Gemini Native Multimodal 能力進行視頻審片
支援時間戳識別、視覺風格分析、社會模擬
"""
import google.generativeai as genai
import os
import time
import json
import random
import requests
import hashlib
import yt_dlp
import tempfile
import asyncio
import subprocess
import numpy as np
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.core.database import get_random_citizens
from app.core.abm_engine import ABMSimulation


class VideoAnalysisService:
    """
    全真視覺分析引擎
    - 下載網路視頻到本地 (支援核心 Token 授權)
    - 上傳至 Gemini File API
    - 使用原生多模態能力進行分析
    - 執行社會模擬並生成結果
    """
    
    # 平台特定配置 (封裝 Header、Token 與 模擬行為)
    PLATFORM_CONFIGS = {
        'dynadrama.com': {
            'referer': 'http://www.dynadrama.com/',
            'origin': 'http://www.dynadrama.com',
            'name': 'Dynadrama',
            'use_browser': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMTQyIiwiaWF0IjoxNzcwMTkyNTI5LCJleHAiOjE3NzA3OTczMjl9.8DXxVHt_kq1omvUyc6XpLcYuuNWY1LWcbBEkhOTjPN2onz0rCYkeOPhSrearMYZvQBAz0fb5t_8KqLV215dYUg'
        },
    }

    def __init__(self):
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model_name = "gemini-1.5-pro-latest"
        print(f"[VideoEngine] Ready with: {self.model_name}", flush=True)

    def download_video_robust(self, url: str) -> Optional[str]:
        try:
            temp_dir = tempfile.mkdtemp()
            parsed_url = url.lower()
            platform_config = self.PLATFORM_CONFIGS.get('dynadrama.com') if 'dynadrama' in parsed_url else None
            
            if not platform_config:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                base = f"{parsed.scheme}://{parsed.netloc}"
                platform_config = {'referer': base+'/', 'origin': base, 'name': parsed.netloc}

            if platform_config.get('use_browser'):
                print(f"[VideoEngine] 啟動瀏覽器嗅探: {url}", flush=True)
                stream_url = self._download_with_browser_sync(url)
                if stream_url: url = stream_url

            output_file = os.path.join(temp_dir, "video.mp4")
            token = platform_config.get('token')
            ua = platform_config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
            
            headers_str = f"Referer: {platform_config['referer']}\r\nUser-Agent: {ua}\r\nOrigin: {platform_config['origin']}\r\n"
            if token: headers_str += f"Token: {token}\r\n"
            
            ffmpeg_cmd = ['ffmpeg', '-y', '-headers', headers_str, '-i', url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', '-movflags', '+faststart', output_file]
            print(f"[VideoEngine] 執行授權下載...", flush=True)
            try:
                res = subprocess.run(ffmpeg_cmd, capture_output=True, timeout=180)
                if res.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 100*1024:
                    return output_file
            except: pass

            # Fallback
            ydl_opts = {'outtmpl': os.path.join(temp_dir, 'yt_video.%(ext)s'), 'quiet': True, 'nocheckcertificate': True, 'http_headers': {'Referer': platform_config['referer'], 'Origin': platform_config['origin'], 'User-Agent': ua, 'Token': token or ""}}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
            except: pass

            for f in os.listdir(temp_dir):
                fp = os.path.join(temp_dir, f)
                if (f.endswith('.mp4') or f.endswith('.part')) and os.path.getsize(fp) > 50*1024:
                    if f.endswith('.part'):
                        nf = fp.replace('.part', '.mp4')
                        if os.path.exists(nf): os.unlink(nf)
                        os.rename(fp, nf); fp = nf
                    return fp
            return None
        except Exception as e:
            print(f"[VideoEngine] Download Error: {e}", flush=True)
            return None

    def analyze_video_content(self, video_url: str) -> Dict[str, Any]:
        """[Brain] Gemini AI 視覺分析實施"""
        print(f"[VideoEngine] 🧠 啟動 AI 觀察: {video_url}", flush=True)
        video_path = self.download_video_robust(video_url)
        if not video_path: return {"error": "VIDEO_DOWNLOAD_FAILED"}
        
        try:
            model = genai.GenerativeModel(model_name=self.model_name)
            video_file = genai.upload_file(path=video_path)
            while video_file.state.name == "PROCESSING": time.sleep(2)
            
            prompt = """請深入觀察這段影片，提供：1. 視覺風格 2. 敘事分析 3. 市民簡報（約200字）。回覆 JSON 格式。"""
            response = model.generate_content([prompt, video_file])
            text = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(text)
            genai.delete_file(video_file.name)
            return data
        except Exception as e:
            print(f"[VideoEngine] Processing Error: {e}", flush=True)
            # 災難恢復：若 AI 失敗，回報基本資訊確保流程不中斷
            return {
                "visual_summary": {"style_tags": ["影視感"], "aesthetics_score": 7},
                "narrative_analysis": {"pacing": "流暢", "emotional_impact": 6},
                "citizen_briefing": "這是一段關於市場趨勢的視覺呈現...",
                "error_fallback": True
            }

    def run_market_simulation(self, report_data: dict, video_url: str, **kwargs) -> Dict[str, Any]:
        """[Brain] ABM 市民仿真實施 - 修正傳參錯誤造成的崩潰"""
        try:
            print(f"[VideoEngine] 🧬 正在執行仿真辯論...", flush=True)
            seed = kwargs.get("seed_salt", 0)
            
            # 取得市民
            citizens = get_random_citizens(limit=100, seed=seed)
            if not citizens: return {"error": "DATABASE_EMPTY"}
            
            # 建立產品資訊 (ABMSimulation 需要此字典)
            product_info = {
                "name": kwargs.get("product_name") or "短劇影片",
                "price": float(kwargs.get("price") or 100),
                "market_price": 100.0,
                "element": "Fire" # 影音產品通常屬火
            }
            
            # 執行 ABM
            abm = ABMSimulation(citizens, product_info, is_pure_content=True)
            abm.initialize_opinions()
            abm.build_social_network()
            abm.run_iterations(num_iterations=5)
            
            # 取得結果
            analytics = abm.analyze_emergence()
            final_score = int(analytics.get("average_opinion", 70))
            
            # 提取評論
            raw_comments = abm.get_final_comments(num_comments=10)
            top_reviews = []
            for c in raw_comments:
                top_reviews.append({
                    "citizen_id": c["citizen_id"],
                    "name": c["name"],
                    "text": c["text"],
                    "score": int(c["opinion_score"]),
                    "sentiment": c["sentiment"],
                    "is_leader": c["is_leader"]
                })

            return {
                "score": final_score,
                "decision": "值得推廣" if final_score > 75 else "具備潛力",
                "top_reviews": top_reviews,
                "simulation_logs": abm.logs
            }
        except Exception as e:
            print(f"[VideoEngine] Simulation Crash: {e}", flush=True)
            return {"error": "SIMULATION_FAILED", "message": str(e)}

    def _download_with_browser_sync(self, url: str) -> Optional[str]:
        try:
            import nest_asyncio
            nest_asyncio.apply()
            return asyncio.run(self._download_with_browser_async(url))
        except: return None

    async def _download_with_browser_async(self, url: str) -> Optional[str]:
        from playwright.async_api import async_playwright
        detected_video_url = None
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            config = self.PLATFORM_CONFIGS['dynadrama.com']
            context = await browser.new_context(
                user_agent=config['user_agent'],
                extra_http_headers={"Token": config['token'], "Origin": config['origin'], "Referer": config['referer']}
            )
            page = await context.new_page()
            async def handle_request(request):
                nonlocal detected_video_url
                if (".m3u8" in request.url or ".ts" in request.url) and not detected_video_url:
                    detected_video_url = request.url
            page.on("request", handle_request)
            try:
                await page.goto("http://www.dynadrama.com/", wait_until="networkidle", timeout=30000)
                if "id=" in url:
                    vid = url.split("id=")[1].split("&")[0]
                    await page.evaluate(f"window.location.hash = '#/me/detail/detail?id={vid}'")
                    await page.wait_for_timeout(7000)
                    for s in ["video", ".vjs-big-play-button"]:
                        try:
                            el = await page.query_selector(s)
                            if el: await el.click()
                        except: pass
                    if not detected_video_url: await page.wait_for_timeout(5000)
            except: pass
            finally: await browser.close()
        return detected_video_url

video_analysis_service = VideoAnalysisService()
