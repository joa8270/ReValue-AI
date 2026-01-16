---
description: 部署 MIRRA 應用程式到 Vercel 和 Render
---

# 部署流程

## 前置確認
1. 確保所有修改已保存
2. 確保本地測試通過

## 部署步驟

// turbo
1. 檢查 git 狀態
```bash
git status
```

2. 添加修改的檔案
```bash
git add -A
```

3. 提交變更（請輸入有意義的 commit message）
```bash
git commit -m "feat: 你的修改描述"
```

// turbo
4. 推送到 GitHub
```bash
git push origin main
```

5. 確認部署狀態：
   - 前端 (Vercel): https://vercel.com/joa8270s-projects/mirra-ai
   - 後端 (Render): https://dashboard.render.com/web/srv-d5d8fon5r7bs73bq857g/events

## 完成
部署通常需要 2-5 分鐘完成，可以在上述連結查看進度。
