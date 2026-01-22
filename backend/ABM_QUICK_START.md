# ⚡ ABM整合快速啟用指南（5分鐘上手）

## 🎯 目標
將ABM引擎整合到現有的模擬流程中，讓AI市民真正互動。

---

## 🚀 方案A：最小改動啟用（推薦新手）

### Step 1: 創建ABM開關API

在 `backend/app/api/web.py` 的路由器中添加：

```python
# 在文件頂部添加導入
from app.services.abm_helpers import (
    infer_product_element_with_ai,
    extract_price_from_context
)
from app.core.abm_engine import ABMSimulation

# 在現有路由後添加新端點
@router.post("/simulate-abm/{sim_id}")
async def run_abm_simulation(
    sim_id: str,
    request: Request,
    file: UploadFile = File(None)
):
    """
    ABM增強版模擬（實驗性功能）
    
    使用方式：POST /api/simulate-abm/{sim_id}
    Body: { "text_context": "產品名稱：XXX，售價：$500" }
    File: 產品圖片
    """
    try:
        # 1. 讀取圖片
        image_bytes = await file.read() if file else None
        body = await request.json()
        text_context = body.get("text_context", "")
        
        # 2. 準備圖片格式
        image_parts = []
        if image_bytes:
            import base64
            img_b64 = base64.b64encode(image_bytes).decode('utf-8')
            image_parts.append({"inline_data": {"mime_type": "image/jpeg", "data": img_b64}})
        
        # 3. 抽取市民
        from app.core.database import get_random_citizens
        citizens = get_random_citizens(sample_size=30)
        
        # 4. 執行ABM模擬
        ## 4.1 判斷產品五行（簡化版：直接用Fire）
        product_element = "Fire"  # TODO: 整合AI判斷
        
        ## 4.2 提取價格
        price_info = extract_price_from_context(text_context)
        
        product_info = {
            "element": product_element,
            "price": price_info["price"],
            "market_price": price_info["market_price"]
        }
        
        ## 4.3 運行ABM
        abm_sim = ABMSimulation(citizens, product_info)
        abm_sim.build_social_network("element_based")
        abm_sim.initialize_opinions()
        abm_sim.run_iterations(num_iterations=5)
        abm_sim.identify_opinion_leaders(top_n=5)
        
        ## 4.4 收集結果
        emergence = abm_sim.analyze_emergence()
        comments = abm_sim.get_final_comments(num_comments=10)
        
        # 5. 返回結果
        return {
            "status": "completed",
            "score": emergence["average_opinion"],
            "abm_analytics": emergence,
            "comments": comments
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}
```

### Step 2: 前端測試

在瀏覽器控制台測試：

```javascript
// 測試ABM模擬API
const formData = new FormData();
formData.append('text_context', '產品名稱：無線耳機，售價：$1500');

fetch('http://localhost:8000/api/simulate-abm/test-001', {
    method: 'POST',
    body: JSON.stringify({ text_context: '產品名稱：無線耳機，售價：$1500' }),
    headers: { 'Content-Type': 'application/json' }
})
.then(r => r.json())
.then(console.log);
```

---

## 🔧 方案B：環境變數切換（推薦進階）

### Step 1: 在 `.env` 添加開關

```bash
# backend/.env
ENABLE_ABM=true
```

### Step 2: 修改現有模擬函數

在 `line_bot_service.py` 的 `run_simulation_with_image_data` 函數中添加：

```python
async def run_simulation_with_image_data(self, image_data_input, sim_id, text_context=None, language="zh-TW"):
    """核心圖文分析邏輯 (ABM-Enhanced)"""
    import os
    
    # 檢查是否啟用ABM
    use_abm = os.getenv("ENABLE_ABM", "false").lower() == "true"
    
    if use_abm:
        print(f"🧬 [ABM] ABM模式已啟用")
        # 調用ABM增強邏輯
        return await self._run_simulation_with_abm(image_data_input, sim_id, text_context, language)
    else:
        # 原本的流程
        print(f"🔄 [LEGACY] 使用傳統AI角色扮演模式")
        # ... 原本的代碼 ...
```

### Step 3: 實現ABM分支

```python
async def _run_simulation_with_abm(self, image_data_input, sim_id, text_context, language):
    """ABM增強版模擬邏輯"""
    from app.core.abm_engine import ABMSimulation
    from app.services.abm_helpers import extract_price_from_context
    from fastapi.concurrency import run_in_threadpool
    from app.core.database import get_random_citizens
    
    # 1. 處理圖片
    image_bytes_list = image_data_input if isinstance(image_data_input, list) else [image_data_input]
    image_parts = []
    for img_bytes in image_bytes_list:
        import base64
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        image_parts.append({"inline_data": {"mime_type": "image/jpeg", "data": img_b64}})
    
    # 2. 抽取市民
    citizens = await run_in_threadpool(get_random_citizens, sample_size=30)
    
    # 3. 產品資訊（簡化版）
    price_info = extract_price_from_context(text_context)
    product_info = {
        "element": "Fire",  # 簡化：預設火
        "price": price_info["price"],
        "market_price": price_info["market_price"]
    }
    
    # 4. 執行ABM
    abm_sim = ABMSimulation(citizens, product_info)
    abm_sim.build_social_network("element_based")
    abm_sim.initialize_opinions()
    abm_sim.run_iterations(num_iterations=3)  # 快速版：3輪
    emergence = abm_sim.analyze_emergence()
    abm_comments = abm_sim.get_final_comments(num_comments=10)
    
    # 5. 讓AI基於ABM結果生成文字
    # （這裡可以保留原本的AI調用，但prompt改成基於ABM結果）
    
    # 6. 組裝結果
    result = {
        "status": "completed",
        "score": emergence["average_opinion"],
        "summary": f"基於ABM模擬，群體平均購買意圖為 {emergence['average_opinion']:.1f} 分...",
        "comments": abm_comments,
        "abm_analytics": emergence
    }
    
    # 7. 更新資料庫
    from app.core.database import update_simulation
    update_simulation(sim_id, "completed", result)
    
    return result
```

---

## 📊 方案C：A/B測試（推薦生產環境）

### 隨機分配流量

```python
import random

async def run_simulation_with_image_data(self, ...):
    # 20%機率使用ABM，80%使用舊方法
    use_abm = random.random() < 0.2
    
    if use_abm:
        print("🧬 [A/B] 使用ABM模式")
        # ABM邏輯
    else:
        print("🔄 [A/B] 使用傳統模式")
        # 原本邏輯
    
    # 記錄使用的方法
    result["ab_test_variant"] = "ABM" if use_abm else "Legacy"
```

---

## 🎨 前端展示ABM結果

### 在報告頁面添加ABM指標

```typescript
// frontend/app/watch/[id]/page.tsx

{data.abm_analytics && (
  <div className="abm-insights">
    <h3>🧬 ABM 社會動力學分析</h3>
    
    <div className="metrics">
      <div className="metric">
        <label>共識度</label>
        <div className="value">{(data.abm_analytics.consensus * 100).toFixed(0)}%</div>
      </div>
      
      <div className="metric">
        <label>從眾效應</label>
        <div className="value">{data.abm_analytics.herding_strength.toFixed(1)}分</div>
      </div>
      
      <div className="metric">
        <label>極化程度</label>
        <div className="value">{(data.abm_analytics.polarization * 100).toFixed(0)}%</div>
      </div>
    </div>
    
    <p className="explanation">
      {data.abm_analytics.consensus > 0.7 
        ? "✅ 市場反應一致，共識度高"
        : "⚠️ 市場意見分歧，需關注不同族群"}
    </p>
  </div>
)}
```

---

## ✅ 驗證清單

啟用ABM後，請檢查：

- [ ] ABM模擬能正常運行（無錯誤）
- [ ] 意見有演化（初始值 ≠ 最終值）
- [ ] 識別出意見領袖（3-5位）
- [ ] 突現行為指標合理（共識度0-1，極化0-1）
- [ ] 評論提到「受影響」或「意見改變」
- [ ] 前端正確顯示ABM分析結果
- [ ] 模擬時間控制在10秒內

---

## 🐛 常見問題

### Q1: ABM模擬太慢怎麼辦？
**A**: 減少迭代次數和樣本量
```python
abm_sim.run_iterations(num_iterations=3)  # 5 → 3
citizens = get_random_citizens(sample_size=20)  # 30 → 20
```

### Q2: 如何關閉ABM？
**A**: 設置環境變數
```bash
ENABLE_ABM=false
```

### Q3: 評論還是模板化？
**A**: 確認AI prompt有使用ABM上下文
```python
# 錯誤：沒用ABM數據
prompt = "請扮演這些市民..."

# 正確：基於ABM結果
prompt = f"""
這些市民已經過5輪互動，意見從{initial}變成{final}...
請基於這些演化數據生成評論...
"""
```

---

## 🎓 學習資源

- **ABM理論**: 閱讀 `app/core/ABM_INTEGRATION_GUIDE.md`
- **測試範例**: 運行 `python backend/test_abm_engine.py`
- **完整報告**: 查看 `backend/ABM_INTEGRATION_COMPLETE.md`

---

## 🚀 準備好了嗎？

選擇一個方案開始整合：

1. **保守派**：方案A（獨立API，不動現有代碼）
2. **實用派**：方案B（環境變數切換）
3. **數據派**：方案C（A/B測試，收集數據）

**建議流程**：
```
本地測試（方案A） → 小流量驗證（方案C, 20%） → 全面啟用（方案B）
```

祝整合順利！🎉
