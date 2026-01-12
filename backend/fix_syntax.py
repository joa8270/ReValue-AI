"""修復 line_bot_service.py 語法錯誤"""
import re

with open('app/services/line_bot_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 尋找損壞的字串並修復
# 原本是 "📝 請直接輸入文字即可。\n💡 若不補充..." 中間的 \n 變成了真正的換行
old_text = '"📝 請直接輸入文字即可。\n💡'
new_text = '"📝 請直接輸入文字即可。\\n"\n                "💡'

if old_text in content:
    content = content.replace(old_text, new_text)
    with open('app/services/line_bot_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 已修復語法錯誤")
else:
    # 嘗試其他方式
    # 找到有問題的行號並直接替換
    lines = content.split('\n')
    fixed = False
    for i, line in enumerate(lines):
        if '請直接輸入文字即可。' in line and not line.rstrip().endswith('"'):
            # 這行有問題
            lines[i] = '                "📝 請直接輸入文字即可。\\n"'
            if i+1 < len(lines) and '若不補充' in lines[i+1]:
                lines[i+1] = '                "💡 若不補充，請輸入「**略過**」或「**skip**」直接開始分析。"'
            fixed = True
            print(f"✅ 修復行 {i+1}")
            break
    
    if fixed:
        with open('app/services/line_bot_service.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    else:
        print("未找到需要修復的內容，請手動檢查")

print("完成")
