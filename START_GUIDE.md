# MIRRA 系統啟動指引 (快速開始)

本指引將協助您快速啟動 MIRRA 系統的本地開發環境。

## 1. 啟動後端服務 (Backend)
開啟一個終端機，確保您在 `MIRRA` 根目錄下，執行：
```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```
- **確認：** 看到 `Application startup complete` 表示成功。
- **連結：** [http://localhost:8000](http://localhost:8000)

## 2. 啟動前端介面 (Frontend)
開啟另一個終端機，切換到 `frontend` 目錄，執行：
```powershell
cd frontend
npm run dev
```
- **確認：** 看到 `Ready in ...` 表示成功。
- **連結：** [http://localhost:4000](http://localhost:4000)

## 3. 系統狀態驗證
- **戰情室連結：** [http://localhost:4000](http://localhost:4000)
- **API 測試：** [http://localhost:8000/citizens](http://localhost:8000/citizens)

---
💡 **提示：** 如果啟動過程中遇到 Gemini API 404 錯誤，請確認您的 `.env` 檔案中 `GOOGLE_API_KEY` 是否正確。系統目前已預設使用最新的 `gemini-2.5-pro` 模型。
