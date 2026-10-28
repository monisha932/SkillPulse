import json
from collections import Counter
from typing import Dict, Any, List, Optional
from backend.database import get_db_connection
from backend.services.market_analyzer import analyze_target_role_skills

# Configurable 1–5 Proficiency Scale (as specified in Module 5)
PROFICIENCY_SCALE: Dict[str, int] = {
    "Not Assessed": 0,
    "Not Verified": 0,
    "Unassessed": 0,
    "Beginner": 1,
    "Novice": 1,
    "Basic": 2,
    "Intermediate": 3,
    "Competent": 3,
    "Advanced": 4,
    "Proficient": 4,
    "Expert": 5
}
PROFICIENCY_MAP = PROFICIENCY_SCALE

REVERSE_PROFICIENCY_SCALE: Dict[int, str] = {
    0: "Not Assessed",
    1: "Beginner",
    2: "Basic",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert"
}

# Skill Prerequisites Mapping for Priority Calculation
SKILL_PREREQUISITES: Dict[str, List[str]] = {
    "React": ["JavaScript", "HTML/CSS"],
    "Next.js": ["React", "JavaScript"],
    "Node.js": ["JavaScript"],
    "Spring Boot": ["Java"],
    "Django": ["Python"],
    "FastAPI": ["Python"],
    "REST API": ["JavaScript", "Java", "Python"],
    "Docker": ["Git"],
    "Kubernetes": ["Docker"],
    "PyTorch": ["Python", "Algorithms"],
    "TensorFlow": ["Python", "Algorithms"]
}

def get_gap_category(gap_num: int) -> str:
    """
    Configurable Gap Categories:
    <= 0 -> No Gap
    1    -> Low Gap
    2    -> Medium Gap
    3    -> High Gap
    4+   -> Critical Gap
    """
    if gap_num <= 0:
        return "No Gap"
    elif gap_num == 1:
        return "Low Gap"
    elif gap_num == 2:
        return "Medium Gap"
    elif gap_num == 3:
        return "High Gap"
    else:
        return "Critical Gap"

def calculate_skill_priority(
    gap_num: int,
    market_demand_pct: float,
    importance_weight: float,
    skill_name: str,
    all_required_skills: List[str]
) -> Dict[str, Any]:
    """
    Multi-Factor Priority Calculation:
    - Skill gap magnitude (0 to 4+)
    - Job-market demand percentage (0 to 100%)
    - Skill importance weight (0.0 to 1.0)
    - Prerequisites (boosts foundational skills needed by downstream tools)
    """
    if gap_num <= 0:
        return {
            "priority": "None",
            "priority_score": 0.0,
            "badge_class": "badge-secondary"
        }

    # 1. Gap factor: 0 - 100
    gap_score = gap_num * 25.0

    # 2. Market demand factor: 0 - 35
    demand_score = (market_demand_pct / 100.0) * 35.0

    # 3. Importance factor: 0 - 25
    importance_score = importance_weight * 25.0

    # 4. Prerequisite factor: +15 if this skill is required by any other skill in target role
    prereq_score = 0.0
    for other_skill in all_required_skills:
        needed_prereqs = SKILL_PREREQUISITES.get(other_skill, [])
        if skill_name in needed_prereqs:
            prereq_score = 15.0
            break

    total_score = round(gap_score + demand_score + importance_score + prereq_score, 1)

    if total_score >= 85 or gap_num >= 4:
        priority = "Critical"
        badge_class = "badge-danger"
    elif total_score >= 60 or gap_num >= 3:
        priority = "High"
        badge_class = "badge-warning"
    elif total_score >= 40 or gap_num == 2:
        priority = "Medium"
        badge_class = "badge-primary"
    else:
        priority = "Low"
        badge_class = "badge-secondary"

    return {
        "priority": priority,
        "priority_score": total_score,
        "badge_class": badge_class
    }

def calculate_skill_gaps(user_id: int, target_role_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Module 5 Core Analytical Service:
    Compares strictly VERIFIED USER SKILLS (from Module 3) against
    REQUIRED JOB-MARKET SKILLS (from Module 4).
    Does NOT compare self-declared skills directly.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Resolve Target Role
    if not target_role_id:
        cursor.execute("SELECT target_role_id FROM career_profiles WHERE user_id = ?", (user_id,))
        p_row = cursor.fetchone()
        target_role_id = p_row["target_role_id"] if p_row and p_row["target_role_id"] else "fullstack-dev"

    cursor.execute("SELECT * FROM job_roles WHERE LOWER(role_id) = LOWER(?)", (target_role_id,))
    role_info = cursor.fetchone()
    if not role_info:
        cursor.execute("SELECT * FROM job_roles WHERE role_id = 'fullstack-dev'")
        role_info = cursor.fetchone()
        target_role_id = "fullstack-dev"

    # 2. Get Module 4 Job-Market Skill Demands & Postings Analytics
    market_data = analyze_target_role_skills(target_role_id)
    market_skills_map = {s["skill_name"].lower(): s for s in market_data.get("skills", [])}

    # 3. Get Role Required Skills specification
    cursor.execute("SELECT * FROM role_skills WHERE LOWER(role_id) = LOWER(?)", (target_role_id,))
    db_role_skills = cursor.fetchall()

    # Build comprehensive required skills inventory
    required_skills_dict = {}
    for rs in db_role_skills:
        s_name = rs["skill_name"]
        required_skills_dict[s_name.lower()] = {
            "skill_name": s_name,
            "category": rs["category"] or "Technical",
            "min_proficiency": rs["min_proficiency"],
            "importance_weight": rs["importance_weight"],
            "trend_status": rs["trend_status"]
        }

    # If any top market skill is not yet in role_skills, synthesize standard defaults
    for s_obj in market_data.get("top_skills", [])[:8]:
        s_name = s_obj["skill_name"]
        if s_name.lower() not in required_skills_dict:
            required_skills_dict[s_name.lower()] = {
                "skill_name": s_name,
                "category": s_obj.get("category", "Core Technical"),
                "min_proficiency": "Intermediate",
                "importance_weight": 0.85,
                "trend_status": "surging" if s_obj.get("is_trending") else "high"
            }

    # 4. Strictly Retrieve VERIFIED USER SKILLS from Module 3 (verified_skills table)
    cursor.execute("SELECT * FROM verified_skills WHERE user_id = ?", (user_id,))
    verified_rows = cursor.fetchall()
    verified_skills_map = {r["skill_name"].lower(): dict(r) for r in verified_rows}

    # Also fetch user's self-declared skills strictly for informational display (NEVER used in gap calculation)
    cursor.execute("SELECT declared_skills_json FROM career_profiles WHERE user_id = ?", (user_id,))
    cp_row = cursor.fetchone()
    declared_skills_map = {}
    if cp_row and cp_row["declared_skills_json"]:
        try:
            decl_list = json.loads(cp_row["declared_skills_json"])
            for d in decl_list:
                declared_skills_map[d.get("skill_name", "").lower()] = d.get("self_rating", "Intermediate")
        except Exception:
            pass

    # 5. Clear previous gaps for this user and role
    cursor.execute("DELETE FROM skill_gaps WHERE user_id = ? AND LOWER(role_id) = LOWER(?)", (user_id, target_role_id))

    gaps_list = []
    radar_categories = []
    radar_required = []
    radar_verified = []
    radar_declared = []

    all_req_names = [s["skill_name"] for s in required_skills_dict.values()]

    total_potential_weight = 0.0
    achieved_weight = 0.0

    for s_lower, r_info in required_skills_dict.items():
        skill_name = r_info["skill_name"]
        category = r_info["category"]
        req_prof_name = r_info["min_proficiency"]
        importance = r_info["importance_weight"]
        trend = r_info["trend_status"]

        # 1-5 Numerical Required Level
        req_level_num = PROFICIENCY_SCALE.get(req_prof_name, 3)

        # Retrieve VERIFIED User Skill (Module 3 only)
        ver_entry = verified_skills_map.get(s_lower)
        if ver_entry:
            ver_prof_name = ver_entry["proficiency_level"]
            user_level_num = PROFICIENCY_SCALE.get(ver_prof_name, 1)
            verified_score_pct = ver_entry["score_pct"]
            is_verified = True
        else:
            ver_prof_name = "Not Assessed"
            user_level_num = 0  # 0 indicates unassessed/unverified
            verified_score_pct = 0.0
            is_verified = False

        # Calculate exact mathematical gap: Required Level - User Verified Level
        raw_gap_num = max(0, req_level_num - user_level_num)
        gap_category = get_gap_category(raw_gap_num)

        # Job-market demand data from Module 4
        m_info = market_skills_map.get(s_lower)
        if m_info:
            market_demand_pct = m_info.get("demand_percentage", 50.0)
            market_frequency = m_info.get("frequency", 0)
        else:
            market_demand_pct = round(importance * 80.0, 1)
            market_frequency = 10

        # Calculate multi-factor priority
        p_data = calculate_skill_priority(
            gap_num=raw_gap_num,
            market_demand_pct=market_demand_pct,
            importance_weight=importance,
            skill_name=skill_name,
            all_required_skills=all_req_names
        )

        # Weighted gap score for sorting and DB persistence
        weighted_gap_score = round(raw_gap_num * importance, 2)

        # Informational self-declared level (NOT used in calculation)
        declared_level_str = declared_skills_map.get(s_lower, "Not Declared")

        # Persist to database
        cursor.execute("""
        INSERT INTO skill_gaps (
            user_id, role_id, skill_name, category, required_level, verified_level,
            declared_level, trend_status, required_weight, verified_weight, gap_score, priority
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, target_role_id, skill_name, category, req_prof_name, ver_prof_name,
            declared_level_str, trend, req_level_num, user_level_num, weighted_gap_score, p_data["priority"]
        ))

        gap_item = {
            "skill_name": skill_name,
            "category": category,
            "trend_status": trend,
            "required_level": req_prof_name,
            "required_level_num": req_level_num,
            "required_proficiency": req_prof_name,
            "verified_level": ver_prof_name,
            "verified_level_num": user_level_num,
            "verified_proficiency": ver_prof_name,
            "is_verified": is_verified,
            "verified_score_pct": verified_score_pct,
            "declared_level": declared_level_str,
            "gap": gap_category,
            "gap_num": raw_gap_num,
            "gap_score": weighted_gap_score,
            "job_demand_percentage": market_demand_pct,
            "job_demand_frequency": market_frequency,
            "importance_weight": importance,
            "priority": p_data["priority"],
            "priority_score": p_data["priority_score"],
            "priority_badge_class": p_data["badge_class"],
            "status": "Proficiency Met" if raw_gap_num == 0 else f"{gap_category} (+{raw_gap_num} levels)"
        }
        gaps_list.append(gap_item)

        # Vector coordinates for radar and comparative bar charts
        radar_categories.append(skill_name)
        radar_required.append(req_level_num)
        radar_verified.append(user_level_num)
        radar_declared.append(PROFICIENCY_SCALE.get(declared_level_str, 0))

        # Match weight accumulation
        total_potential_weight += (req_level_num * importance)
        achieved_weight += (min(user_level_num, req_level_num) * importance)

    # Sort gaps by priority order: Critical -> High -> Medium -> Low -> None
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "None": 4}
    gaps_list.sort(key=lambda x: (priority_order.get(x["priority"], 5), -x["gap_num"], -x["job_demand_percentage"]))

    role_match_pct = round((achieved_weight / total_potential_weight) * 100.0, 1) if total_potential_weight > 0 else 0.0

    conn.commit()
    conn.close()

    return {
        "user_id": user_id,
        "target_role": {
            "role_id": role_info["role_id"],
            "role_title": role_info["role_title"],
            "domain": role_info["domain"],
            "market_demand_index": role_info["market_demand_index"],
            "demand_status": role_info["demand_status"],
            "avg_salary": role_info["avg_salary"],
            "description": role_info["description"]
        },
        "role_match_percentage": role_match_pct,
        "total_skills_evaluated": len(gaps_list),
        "critical_gaps_count": sum(1 for g in gaps_list if g["priority"] == "Critical"),
        "high_gaps_count": sum(1 for g in gaps_list if g["priority"] == "High"),
        "medium_gaps_count": sum(1 for g in gaps_list if g["priority"] == "Medium"),
        "low_gaps_count": sum(1 for g in gaps_list if g["priority"] == "Low"),
        "mastered_count": sum(1 for g in gaps_list if g["gap_num"] == 0),
        "gaps": gaps_list,
        "chart_data": {
            "categories": radar_categories,
            "required_series": radar_required,
            "verified_series": radar_verified,
            "declared_series": radar_declared
        },
        "radar_chart_data": {
            "categories": radar_categories,
            "required_series": radar_required,
            "verified_series": radar_verified,
            "declared_series": radar_declared
        },
        "market_data_source": market_data.get("data_sources", ["Verified Tech Dataset 2026"])
    }
