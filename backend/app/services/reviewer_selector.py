
import random
import time

def select_reviewers(candidates: list[dict], plan_id: str, mode: str = "Normal", refresh_flag: bool = False, target_count: int = 10) -> list[dict]:
    """
    從候選人名單中，根據 Plan ID 與模式，決定性地 (Deterministic) 選出評論者。
    
    Args:
        candidates: 候選人列表 (dicts)
        plan_id: 商業計劃 ID (sim_id)
        mode: "Expert" 或 "Normal"
        refresh_flag: 是否強制刷新 (True = 換一批)
        target_count: 目標選取人數 (Default 10)
        
    Returns:
        Selected reviewers list
    """
    # 步驟 1: 建立候選池 (Strict Filtering)
    filtered_candidates = []
    
    # 定義專家關鍵字 (包含繁體/簡體/英文)
    # P0 Requirement: 嚴格篩選，排除 Tier 3
    EXPERT_KEYWORDS = [
        'CEO', 'Founder', 'Co-Founder', 'Director', 'Manager', 'Investor', 
        'Doctor', 'Lawyer', 'Professor', 'Architect', 'Engineer', 'Consultant',
        'Chief', 'Head', 'VP', 'President', 'Specialist', 'Analyst',
        '總經理', '創辦人', '總監', '經理', '投資人', '醫師', '律師', 
        '教授', '建築師', '工程師', '顧問', '總裁', '董座', '負責人',
        '分析師', '專家', 'Master', 'Expert'
    ]
    
    # 排除關鍵字 (Blacklist) - 避免誤判 (e.g. "Manager of Sanition") - though current DB is simpler
    BLACKLIST_KEYWORDS = ['Assistant', 'Intern', 'Clerk', 'Student', 'Worker', 'Driver', '工讀生', '助理', '實習', '司機']

    if mode == 'Expert':
        # 嚴格篩選：只留職稱匹配者
        for c in candidates:
            # Check occupation field (usually string in TW locale from database.py)
            job_title = str(c.get('occupation', '')).lower()
            
            # Check Full Object if available
            if c.get('occupation_full'):
                # Combine all languages to check
                full_jobs = " ".join([str(v) for v in c['occupation_full'].values()]).lower()
                job_title += " " + full_jobs
            
            # 1. Must have Expert Keyword
            has_keyword = any(k.lower() in job_title for k in EXPERT_KEYWORDS)
            
            # 2. Must NOT have Blacklist Keyword (unless clearly overridden by high rank)
            has_black = any(b.lower() in job_title for b in BLACKLIST_KEYWORDS)
            
            if has_keyword and not has_black:
                filtered_candidates.append(c)
        
        # Fallback: If too few experts, relax slightly (but warn)
        if len(filtered_candidates) < target_count:
            print(f"⚠️ [ReviewerSelector] Expert pool too small ({len(filtered_candidates)}), selecting from top social tiers.")
            # Fallback to social tier 1 & 2 if available
            filtered_candidates = [c for c in candidates if c.get('social_tier', 3) <= 2]
            
    else:
        filtered_candidates = list(candidates) # Copy

    # 步驟 2: 穩定排序 (CRITICAL FIX for Consistency)
    # 這是解決 "4個人跑票" 的關鍵：在抽籤前，先把名單按 ID 排序，確保每次順序一樣
    # Ensure ID is string for sorting
    filtered_candidates.sort(key=lambda x: str(x['id']))

    # 步驟 3: 設定種子 (Seeding)
    if refresh_flag:
        seed_value = str(time.time()) # 換一批
    else:
        seed_value = str(plan_id) + str(mode) # 鎖定結果

    # 步驟 4: 決定性抽選
    rnd = random.Random(seed_value)
    
    # 安全檢查：候選人夠不夠抽？
    k = min(len(filtered_candidates), target_count)
    if k == 0:
        return []
        
    selected_reviewers = rnd.sample(filtered_candidates, k=k)
    
    # Sort selected reviewers by ID again for consistent display order (optional but good)
    selected_reviewers.sort(key=lambda x: str(x['id']))

    return selected_reviewers
