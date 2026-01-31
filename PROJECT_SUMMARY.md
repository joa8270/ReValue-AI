# 專案總結 (Project Summary)

本文件自動生成，概述專案的依賴套件與結構。

## 1. 依賴套件 (Dependencies)

### Python (Backend)
主要用於後端 API、資料庫與 AI 邏輯處理：
*   **Web Framework:** `fastapi`, `uvicorn`
*   **Database:** `sqlalchemy`, `asyncpg`, `psycopg2-binary`
*   **Validation & Settings:** `pydantic`, `pydantic-settings`
*   **AI & Logic:** `google-generativeai`, `numpy`, `faker`
*   **Integrations:** `line-bot-sdk`, `requests`
*   **Utilities:** `python-dotenv`, `python-multipart`, `jinja2`, `uuid`

### Next.js (Frontend)
主要用於前端介面與使用者互動：
*   **Core:** `next` (v14.2.0), `react`, `react-dom`
*   **Styling & UI:** `tailwindcss`, `framer-motion`, `clsx`, `tailwind-merge`, `lucide-react`
*   **Utilities:** `@react-pdf/renderer`, `html2canvas`
*   **Language:** `typescript`

## 2. 專案結構 (Project Structure)

專案分為前後端分離架構，根目錄包含啟動腳本與文件。

*   **根目錄 (Root):**
    *   存放專案文件 (e.g., `MIRRA_BLUEPRINT.md`, `README_QUICKSTART.md`)。
    *   包含系統啟動與測試腳本 (e.g., `start_system.py`, `run.py`)。
    *   日誌檔案 (e.g., `*.log`)。

*   **後端 (backend/):**
    *   `app/`: 核心應用程式邏輯 (FastAPI)。
    *   `data/`: 資料儲存或暫存。
    *   `scripts/`: 工具腳本。
    *   `tests/`: 測試代碼。
    *   包含大量的檢查 (`check_*.py`) 與除錯 (`debug_*.py`) 腳本，用於資料庫與邏輯驗證。
    *   `requirements.txt`: Python 依賴列表。

*   **前端 (frontend/):**
    *   `app/`: Next.js 應用程式路由與頁面。
    *   `lib/`: 共用函式庫與工具。
    *   `public/`: 靜態資源。
    *   `package.json`: Node.js 依賴與設定。
    *   設定檔: `tailwind.config.ts`, `tsconfig.json` 等。
