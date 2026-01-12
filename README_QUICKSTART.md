# MIRRA - System Launch Quickstart

歡迎來到 **MIRRA (鏡界)** - 您的 AI 消費者模擬引擎。
請按照以下步驟啟動系統。

## 1. 環境設定 (Environment Setup)

請在專案根目錄建立一個 `.env` 檔案，並填入以下資訊：

```ini
# .env

# Google Gemini API (Visual Analysis & Infographic)
GOOGLE_API_KEY=your_google_api_key_here

# LINE Messaging API
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret

# Optional: Run locally without real APIs (Mock Mode)
# UseMock=True
```

## 2. 啟動系統 (System Launch)

我們提供了一個一鍵啟動腳本，會同時開啟 Backend (FastAPI) 與 Frontend (Next.js)。

```bash
# 確保您已安裝 Python 依賴 (requirements.txt) 與 Node 依賴 (npm install)

python start_system.py
```

啟動後：
- **Backend API**: `http://localhost:8000`
- **Frontend UI**: `http://localhost:3000`

## 3. 設定 LINE Webhook (Exposure)

由於 LINE 需要一個公開的 HTTPS 網址才能傳送 Webhook，請使用 `ngrok` 將本地 8000 Port 暴露出去。

1. 安裝並執行 ngrok:
   ```bash
   ngrok http 8000
   ```
2. 複製 ngrok 產生的 HTTPS網址 (例如 `https://abcd-1234.ngrok-free.app`)。
3. 前往 [LINE Developers Console](https://developers.line.biz/)。
4. 設定 **Webhook URL** 為：
   ```
   https://abcd-1234.ngrok-free.app/api/line/callback
   ```
   (記得開啟 "Use Webhook" 開關)

## 4. 這要怎麼玩？

1. 加你的 LINE Bot 為好友。
2. 傳送一張產品照片給它。
3. 收到「👁️ 鏡界連結中...」回覆。
4. 等待幾秒，收到分析報告與「即時戰情室」連結。
5. 點擊連結，在瀏覽器看到 1000 個虛擬人對你的產品品頭論足！

Enjoy MIRRA!
