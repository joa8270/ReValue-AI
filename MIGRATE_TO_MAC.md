# 🍎 MIRRA Mac 遷移指南 (Migration Guide)

本指南將協助您將專案從 Windows 遷移至 Mac 繼續開發。

## 1. 檔案複製準備 (打包)

在 Windows 上複製專案資料夾前，建議**刪除或排除**以下資料夾，以節省複製時間並避免相容性問題：

*   `node_modules` (位於 `frontend/` 內) - **必須刪除** (Windows 與 Mac 版本不同)
*   `.next` (位於 `frontend/` 內) - 建議刪除 (快取檔案)
*   `venv` 或 `.venv` - **必須刪除** (Python 虛擬環境不跨平台)
*   `__pycache__` (分散在各處) - 建議刪除

確保保留以下重要檔案：
*   ✅ `.env` (包含您的 API Key，**非常重要**)
*   ✅ `run.py`
*   ✅ `frontend/package.json`
*   ✅ `backend/requirements.txt`

---

## 2. Mac 環境設定

將檔案複製到 Mac 並解壓縮後，請開啟終端機 (Terminal) 依序執行以下步驟：

### 步驟 A: 安裝 Python 依賴

1.  進入專案根目錄 (`MIRRA`)。
2.  建立虛擬環境：
    ```bash
    python3 -m venv venv
    ```
3.  啟動虛擬環境：
    ```bash
    source venv/bin/activate
    ```
4.  安裝套件：
    ```bash
    pip install -r backend/requirements.txt
    ```

### 步驟 B: 安裝前端依賴

1.  進入前端目錄：
    ```bash
    cd frontend
    ```
2.  安裝 Node.js 套件：
    ```bash
    npm install
    ```
3.  回到根目錄：
    ```bash
    cd ..
    ```

---

## 3. 啟動專案

確認 `.env` 檔案存在於根目錄後，執行：

```bash
# 確保虛擬環境已啟動 ((venv) 顯示在開頭)
python run.py
```

系統應會自動開啟：
*   Backend: http://localhost:8000
*   Frontend: http://localhost:4000

---

## 常見問題

*   **Python 版本**：建議使用 Python 3.10 以上版本。
*   **Port 佔用**：如果啟動失敗，請檢查 Port 4000 或 8000 是否被佔用。
*   **權限問題**：若遇到 `Permission denied`，試著在指令前加 `sudo` (不建議用於 pip/npm) 或檢查資料夾權限。
