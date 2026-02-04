"""
ABM-Enhanced Simulation Function
用於替換 line_bot_service.py 中的 run_simulation_with_image_data
"""

async def run_simulation_with_image_data_abm(self, image_data_input, sim_id, text_context=None, language="zh-TW", use_abm=True):
    """
    核心圖文分析邏輯 (ABM-Enhanced Version)
    
    Args:
        use_abm: 是否使用ABM引擎（True=新方法，False=舊方法）
    """
    import traceback
    try:
        with open("debug_image.log", "w", encoding="utf-8") as f: 
            f.write(f"[{sim_id}] STARTING ABM-Enhanced Simulation (USE_ABM={use_abm}, Lang: {language})\n")
        
        # 1. Process Images (Single or List)
        image_bytes_list = image_data_input if isinstance(image_data_input, list) else [image_data_input]
        image_parts = []
        
        for idx, img_bytes in enumerate(image_bytes_list):
            mime_type = "image/jpeg"
            if img_bytes.startswith(b'\x89PNG'):
                mime_type = "image/png"
            elif img_bytes.startswith(b'GIF8'):
                mime_type = "image/gif"
            elif img_bytes.startswith(b'RIFF') and img_bytes[8:12] == b'WEBP':
                mime_type = "image/webp"
            
            import base64
            img_b64 = base64.b64encode(img_bytes).decode('utf-8')
            image_parts.append({"inline_data": {"mime_type": mime_type, "data": img_b64}})
        
        print(f"[ABM] Processed {len(image_parts)} images")
        
        # 2. 從資料庫隨機抽取市民
        from fastapi.concurrency import run_in_threadpool
        from app.core.database import get_random_citizens
        
        sampled_citizens = await run_in_threadpool(get_random_citizens, sample_size=30)
        
        if not sampled_citizens:
            print("[ABM] No citizens sampled from DB!")
            raise Exception("No citizens available")
        
        print(f"[ABM] Sampled {len(sampled_citizens)} citizens")
        
        # 3. 【NEW】執行ABM模擬（如果啟用）
        abm_data = None
        emergence_data = None
        
        if use_abm:
            try:
                from app.core.abm_engine import ABMSimulation
                from app.services.abm_helpers import (
                    infer_product_element_with_ai, 
                    extract_price_from_context
                )
                
                # 3.1 判斷產品五行屬性
                product_element = await infer_product_element_with_ai(self, image_parts, text_context)
                
                # 3.2 提取價格資訊
                price_info = extract_price_from_context(text_context)
                
                product_info = {
                    "element": product_element,
                    "price": price_info.get("price", 100),
                    "market_price": price_info.get("market_price", 100)
                }
                
                print(f"[ABM] Product Info: {product_info}")
                
                # 3.3 執行ABM模擬
                abm_sim = ABMSimulation(sampled_citizens, product_info)
                abm_sim.build_social_network("element_based")
                abm_sim.initialize_opinions()
                abm_sim.run_iterations(num_iterations=5, convergence_rate=0.3)
                abm_sim.identify_opinion_leaders(top_n=5)
                
                # 3.4 收集ABM分析結果
                emergence_data = abm_sim.analyze_emergence()
                abm_comments_raw = abm_sim.get_final_comments(num_comments=10)
                
                print(f"[ABM] Simulation completed. Avg opinion: {emergence_data['average_opinion']:.1f}")
                
                # 將ABM結果儲存供AI使用
                abm_data = {
                    "emergence": emergence_data,
                    "comments": abm_comments_raw
                }
                
            except Exception as e:
                print(f"[ABM] ABM simulation failed: {e}")
                traceback.print_exc()
                use_abm = False  # 降級為舊方法
        
        # 4. 構建AI Prompt（根據是否使用ABM調整）
        import json
        from app.core.config import settings
        
        if use_abm and abm_data:
            # 【NEW PROMPT】基於ABM結果生成
            abm_comments_json = json.dumps(abm_data['comments'], ensure_ascii=False, indent=2)
            
            prompt = f"""
你是 MIRRA 系統的策略分析師。我們已經完成了一次 **Agent-Based Modeling (ABM) 模擬**，
以下是真實的模擬結果。請基於這些資料生成深度分析報告與市民評論。

📊 **ABM 模擬結果摘要**：
- 群體平均購買意圖：{emergence_data['average_opinion']:.1f} 分
- 意見標準差：{emergence_data['opinion_std']:.1f}
- 極化程度：{emergence_data['polarization']:.2f} (0=高度共識, 1=兩極分化)
- 從眾效應強度：{emergence_data['herding_strength']:.1f}

📋 **市民行為詳情** (10位代表性市民)：
{abm_comments_json}

⚠️ **重要說明**：
- 這些市民經過5輪互動，意見已經演化（initial_opinion → final_opinion）
- `opinion_change` 顯示受社交影響的程度（正值=變樂觀，負值=變悲觀）
- `is_leader=true` 代表意見領袖，其評論影響了多位市民
- 請基於 `abm_context` 中的數據撰寫評論

🎯 **任務**：
1. 為每位市民生成「符合其ABM行為邏輯」的詳細評論（繁體中文，至少60字）
   - 🔴 **嚴格指令：必須使用提供的 `age` (年齡) 與 `occupation` (職業)，嚴禁自行編造或修改身份。**
   - 如果 opinion_change 很大（>15），評論應提到「受鄰居/朋友影響」
   - 如果是意見領袖，評論應展現說服力與影響力
   - 評論應反映最終意見分數 (final_opinion)
   
2. 生成戰略分析報告（500字以上）
   - [解析] 基於ABM結果解讀產品的市場接受度
   - [優化] 根據極化程度、從眾效應提出策略
   - [戰略] 針對意見領袖與關鍵族群的行銷建議

請回傳JSON格式：
{{
    "result": {{
        "score": {emergence_data['average_opinion']},
        "summary": "標題\\n\\n[解析] ...\\n\\n[優化] ...\\n\\n[戰略] ...",
        "objections": [
            {{"reason": "質疑點", "percentage": 30}}
        ],
        "suggestions": [
            {{
                "target": "具體目標客群",
                "advice": "具體建議...",
                "execution_plan": ["步驟1", "步驟2", "步驟3", "步驟4", "步驟5"]
            }}
        ]
    }},
    "comments": [
        {{
            "citizen_id": "市民ID",
            "sentiment": "positive/negative/neutral",
            "text": "基於ABM行為的評論..."
        }}
    ],
    "abm_analytics": {{
        "polarization": {emergence_data['polarization']},
        "consensus": {emergence_data['consensus']},
        "herding_strength": {emergence_data['herding_strength']}
    }}
}}
"""
        else:
            # 【舊PROMPT】AI角色扮演
            citizens_for_prompt = []
            for c in sampled_citizens[:10]:
                bazi = c.get("bazi_profile") or {}
                citizens_for_prompt.append({
                    "id": str(c.get("id", "0")),
                    "name": c.get("name", "AI市民"),
                    "age": c.get("age", 30),
                    "element": bazi.get("element", "未知"),
                    "structure": bazi.get("structure", "未知"),
                    "occupation": c.get("occupation", "自由業"),
                })
            
            citizens_json = json.dumps(citizens_for_prompt, ensure_ascii=False)
            product_context = f"產品資訊：\n{text_context}" if text_context else ""
            
            prompt = f"""
你是 MIRRA 鏡界系統的核心 AI 策略顧問。請分析產品圖片，並「扮演」以下10位市民模擬反應。

{product_context}

市民資料：
{citizens_json}

請回傳JSON格式：
{{
    "result": {{
        "score": 75,
        "summary": "分析報告...",
        "suggestions": []
    }},
    "comments": [
        {{"citizen_id": "ID", "sentiment": "positive", "text": "評論..."}}
    ]
}}
"""
        
        # 5. 調用AI生成
        api_key = settings.GOOGLE_API_KEY
        ai_text, last_error = await self._call_gemini_rest(api_key, prompt, image_parts=image_parts)
        
        if ai_text is None:
            print(f"[ABM] Gemini failed: {last_error}")
            ai_text = "{}"
        
        # 6. 解析AI回應
        data = self._clean_and_parse_json(ai_text)
        
        # 🛡️ GHOST CITIZEN PROTECTION (Image Flow)
        raw_comments = data.get("comments", [])
        valid_map = {c["name"]: c for c in sampled_citizens}
        used_names = set()
        sanitized_comments = []
        
        # Collect used real names first
        for c in raw_comments:
            if not isinstance(c, dict): continue
            # Check citizen_name or name or look up by ID?
            # AI often returns "name" or just "citizen_id"
            c_name = c.get("name")
            if not c_name and c.get("citizen_id") in valid_map: 
                 # Maybe ID is name? No, ID is UUID.
                 # Need map by ID too
                 pass
            
            # Let's map by ID and Name to be safe
            pass 

        # Simplified Logic:
        # We need to ensure 'citizen_id' (or name) in comment matches a real citizen.
        # If not, replace with unused one.
        
        # Map by ID (primary) and Name (secondary)
        citizen_id_map = {str(c["id"]): c for c in sampled_citizens}
        citizen_name_map = {c["name"]: c for c in sampled_citizens}
        
        unused_citizens_img = [c for c in sampled_citizens] # copy
        
        for c in raw_comments:
            if not isinstance(c, dict): continue
            
            real_c = None
            cid = str(c.get("citizen_id", ""))
            cname = c.get("name", "")
            
            if cid in citizen_id_map:
                real_c = citizen_id_map[cid]
            elif cname in citizen_name_map:
                real_c = citizen_name_map[cname]
                
            if real_c:
                # Valid citizen
                c["citizen_id"] = str(real_c["id"])
                c["name"] = real_c["name"] # Enforce name
                if real_c in unused_citizens_img:
                    unused_citizens_img.remove(real_c)
            else:
                # GHOST! Replace.
                if unused_citizens_img:
                    real_c = unused_citizens_img.pop(0)
                    c["citizen_id"] = str(real_c["id"])
                    c["name"] = real_c["name"]
                    c["occupation"] = real_c.get("occupation", "未知")
                    # logger.warning(f"👻 [ABM-Image] Replaced ghost with {real_c['name']}")
                else:
                    continue # Should not happen if we sampled 30
            
            sanitized_comments.append(c)
            
        data["comments"] = sanitized_comments
        
        # 7. 合併ABM數據與AI生成結果
        if use_abm and abm_data:
            from app.services.abm_helpers import merge_abm_and_ai_comments
            
            # 合併評論
            ai_comments = data.get("comments", [])
            final_comments = merge_abm_and_ai_comments(abm_data['comments'], {"comments": ai_comments})
            data["comments"] = final_comments
            
            # 添加ABM分析數據
            if "result" not in data:
                data["result"] = {}
            data["result"]["abm_analytics"] = {
                "polarization": emergence_data['polarization'],
                "consensus": emergence_data['consensus'],
                "herding_strength": emergence_data['herding_strength'],
                "element_preferences": emergence_data['element_preferences'],
                "network_density": emergence_data['network_density']
            }
        
        # 8. 後續處理（與舊流程相同）
        # ... (原本的 comments 處理、personas 構建等邏輯)
        
        # 9. 更新資料庫
        from app.core.database import update_simulation
        
        final_result = {
            "status": "completed",
            "score": data.get("result", {}).get("score", 75),
            "summary": data.get("result", {}).get("summary", "分析完成"),
            "comments": data.get("comments", []),
            "abm_enabled": use_abm,
            **data
        }
        
        update_simulation(sim_id, "completed", final_result)
        print(f"[ABM] Simulation completed (ABM={use_abm})")
        
    except Exception as e:
        print(f"[ABM] Fatal error: {e}")
        traceback.print_exc()
        from app.core.database import update_simulation
        update_simulation(sim_id, "error", {"error": str(e)})
