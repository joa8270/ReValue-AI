# LINE Bot 多圖處理輔助函數
# 這些函數將被集成到 line_bot_service.py 中

async def _identify_from_multiple_images(self, user_id):
    """
    從 session 中的多張圖片進行 AI 識別與市場比價
    """
    session = self.user_session.get(user_id)
    if not session or not session.get("images"):
        self._push_text(user_id, "❌ 找不到圖片，請重新上傳")
        return
    
    images = session["images"]
    image_count = len(images)
    
    try:
        # 1. AI 產品識別（使用第一張圖片）
        print(f"🔍 [Multi-Image] 開始識別 {image_count} 張圖片...")
        ai_name, ai_price = await self.identify_product_from_image(images[0])
        
        # 2. 市場比價查詢（如果有產品名稱）
        market_prices = {}
        if ai_name and ai_name != "未知產品":
            from app.services.price_search import search_market_prices_sync
            try:
                print(f"💰 [Market] 查詢市場價格: {ai_name}")
                market_result = search_market_prices_sync(ai_name)
                if market_result.get("success"):
                    market_prices = market_result
                    print(f"💰 [Market] 找到 {len(market_result.get('prices', []))} 筆價格資料")
            except Exception as e:
                print(f"⚠️ [Market] 比價查詢失敗: {e}")
        
        # 3. 更新 session
        session["image_bytes"] = images[0]  # 兼容性：保留第一張做為主圖
        session["product_name"] = ai_name or ""
        session["product_price"] = ai_price or "未定"  
        session["market_prices"] = market_prices
        session["stage"] = "waiting_for_name_confirmation"
        
        print(f"✅ [Multi-Image] 識別完成: {ai_name} / {ai_price}")
        
        # 4. 構建回覆訊息（包含市場比價資料）
        confirm_msg = f"👁️ **AI 視覺分析結果**（{image_count} 張圖片）\n\n"
        confirm_msg += f"📦 產品：{ai_name or '未知'}\n"
        
        # 顯示市場比價
        if market_prices.get("success"):
            prices = market_prices.get("prices", [])
            if prices:
                min_price = market_prices.get("min_price", ai_price)
                max_price = market_prices.get("max_price", ai_price)
                confirm_msg += f"💰 市場價格區間：${min_price} - ${max_price}\n"
                confirm_msg += f"📊 已比對 {len(prices)} 個平台\n"
            else:
                confirm_msg += f"💰 估價：{ai_price or '未知'}\n"
        else:
            confirm_msg += f"💰 估價：{ai_price or '未知'}\n"
        
        confirm_msg += "\n━━━━━━━━━━━━━━\n"
        confirm_msg += "✅ 若資料正確，請回覆「**Y**」\n"
        confirm_msg += "✏️ 若需修改，請直接輸入「**名稱 / 售價**」"
        
        self._push_text(user_id, confirm_msg)
        
    except Exception as e:
        print(f"❌ [Multi-Image] 識別失敗: {e}")
        import traceback
        traceback.print_exc()
        self._push_text(user_id, "❌ AI 識別失敗，請重新上傳圖片")
        # 重置 session
        if user_id in self.user_session:
            del self.user_session[user_id]


async def _handle_upload_complete(self, user_id):
    """
    處理用戶點選「完成上傳」後的邏輯
    """
    session = self.user_session.get(user_id)
    if not session:
        self._push_text(user_id, "❌ 找不到上傳的圖片，請重新開始")
        return
    
    images = session.get("images", [])
    if not images:
        self._push_text(user_id, "❌ 尚未上傳任何圖片，請先上傳產品圖片")
        return
    
    # 開始識別
    await self._identify_from_multiple_images(user_id)
