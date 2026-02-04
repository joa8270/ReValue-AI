# MIRRA Video Audit Implementation Plan

## 1. Backend
- Create `backend/app/services/video_analysis_service.py`
- Create `backend/app/api/video_audit.py`
- Register router in `backend/app/main.py`

## 2. Frontend
- Revert `frontend/app/page.tsx`
- Implement Double Entry Dashboard
- Create `frontend/app/video-audit/page.tsx`
- Update `Navbar` and `Translations`

## 3. Security
- Use `.env.local` for `GOOGLE_API_KEY`
- Audit and remove hardcoded keys
