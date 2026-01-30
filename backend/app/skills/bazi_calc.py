from .base import BaseSkill
from typing import Dict, Any
from datetime import datetime

class BaZiCalcSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "BaZi Calculator"

    @property
    def description(self) -> str:
        return "Calculates the Four Pillars (BaZi) based on birth date and time."

    @property
    def slug(self) -> str:
        return "bazi-calc"

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        簡易八字排盤邏輯 (模擬版)
        輸入參數: year, month, day, hour (皆為整數)
        """
        try:
            year = int(context.get("year", 2000))
            month = int(context.get("month", 1))
            day = int(context.get("day", 1))
            hour = int(context.get("hour", 12))
            
            # 天干地支表 (Pinyin Keys - Lowercase for standardization)
            heavenly_stems = ["jia", "yi", "bing", "ding", "wu", "ji", "geng", "xin", "ren", "gui"]
            earthly_branches = ["zi", "chou", "yin", "mao", "chen", "si", "wu", "wei", "shen", "you", "xu", "hai"]
            
            # --- 年柱計算 (Year Pillar) ---
            # 簡單算法：(年 - 4) % 10 = 天干, (年 - 4) % 12 = 地支
            year_stem_idx = (year - 4) % 10
            year_branch_idx = (year - 4) % 12
            year_pillar = f"{heavenly_stems[year_stem_idx]}-{earthly_branches[year_branch_idx]}"
            
            # --- 月柱計算 (Month Pillar) ---
            # 簡化版：僅根據年干與月令推算 (實際需要節氣)
            # 年上起月法: 甲己之年丙作首...
            month_start_lookup = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}
            month_stem_start = month_start_lookup[year_stem_idx]
            
            # 假設月份從立春(寅月)開始，對應 index 2
            # 這裡做一個非常簡化的對應: 1月=丑, 2月=寅... (這是不準確的，僅供Demo)
            # 正確做法需要 Solar Term (節氣) 計算
            
            # 修正：直接假設輸入月份對應地支 (1月->寅, 2月->卯...)
            month_branch_idx = (month + 1) % 12
            month_stem_idx = (month_stem_start + (month - 1)) % 10
            
            month_pillar = f"{heavenly_stems[month_stem_idx]}-{earthly_branches[month_branch_idx]}"
            
            # --- 日柱計算 (Day Pillar) ---
            # 日柱需要萬年曆公式或查表，這裡僅回傳一個模擬值
            # 根據 1900/1/1 是甲戌日推算 (簡化模擬)
            base_date = datetime(1900, 1, 1)
            target_date = datetime(year, month, day)
            delta_days = (target_date - base_date).days
            
            # 1900/1/1 甲(0)戌(10)
            day_stem_idx = (0 + delta_days) % 10
            day_branch_idx = (10 + delta_days) % 12
            day_pillar = f"{heavenly_stems[day_stem_idx]}-{earthly_branches[day_branch_idx]}"
            
            # --- 時柱計算 (Hour Pillar) ---
            # 日上起時法: 甲己還加甲...
            hour_start_lookup = {0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8}
            hour_stem_start = hour_start_lookup[day_stem_idx]
            
            # 時支: 子(23-1), 丑(1-3)...
            hour_branch_idx = 0
            if hour >= 23 or hour < 1: hour_branch_idx = 0 # Zi
            elif hour < 3: hour_branch_idx = 1 # Chou
            elif hour < 5: hour_branch_idx = 2 # Yin
            else: hour_branch_idx = (hour + 1) // 2 % 12
            
            # 時干推算: 從子時開始數
            # 子時對應 index 0
            steps_from_zi = hour_branch_idx
            hour_stem_idx = (hour_stem_start + steps_from_zi) % 10
            
            hour_pillar = f"{heavenly_stems[hour_stem_idx]}-{earthly_branches[hour_branch_idx]}"

            return {
                "status": "success",
                "input_date": f"{year}-{month}-{day} {hour}:00",
                "bazi": {
                    "year": year_pillar,
                    "month": month_pillar,
                    "day": day_pillar,
                    "hour": hour_pillar
                },
                "note": "Simplified calculation for demonstration purposes."
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
