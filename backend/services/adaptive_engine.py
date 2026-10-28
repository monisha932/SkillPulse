import json
import math
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.database import get_db_connection
from backend.services.gap_engine import (
    calculate_skill_gaps,
    PROFICIENCY_SCALE,
    REVERSE_PROFICIENCY_SCALE
)
from backend.services.market_analyzer import analyze_target_role_skills
from backend.services.curriculum_engine import (
    MODULE_KNOWLEDGE_BASE,
    topological_sort_modules,
    get_capstone_module_definition
)

def record_assessment_attempt(
    user_id: int,
    skill_name: str,
    attempt_id: int,
    score_pct: float,
    proficiency_level: str,
    mcq_score: float = 0.0,
    programming_score: float = 0.0
) -> Dict[str, Any]:
    """
    Module 8 Core:
    Records an assessment attempt into skill_assessment_history without deleting any past attempts.
    Calculates attempt number incrementally for empirical before-vs-after comparison.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*) as attempt_count
    FROM skill_assessment_history
    WHERE user_id = ? AND LOWER(skill_name) = LOWER(?)
    """, (user_id, skill_name))
    cnt_row = cursor.fetchone()
    attempt_number = (cnt_row["attempt_count"] if cnt_row else 0) + 1

    cursor.execute("""
    INSERT INTO skill_assessment_history (
        user_id, skill_name, attempt_id, attempt_number,
        score_pct, proficiency_level, mcq_score, programming_score, evaluated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        user_id, skill_name, attempt_id, attempt_number,
        round(score_pct, 1), proficiency_level, mcq_score, programming_score
    ))

    conn.commit()
    conn.close()

    return {
        "user_id": user_id,
        "skill_name": skill_name,
        "attempt_number": attempt_number,
        "score_pct": score_pct,
        "proficiency_level": proficiency_level
    }

def get_assessment_comparison(user_id: int) -> List[Dict[str, Any]]:
    """
    Module 8 Core Requirement:
    Compares 'Before assessment vs After assessment' results across candidate attempts.
    Example:
      Python: Before = 45%, After = 78%
      SQL:    Before = 60%, After = 85%
    Returns rich comparison metadata for each evaluated technical skill.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query all historical attempts ordered chronologically
    cursor.execute("""
    SELECT sah.*, aa.session_token
    FROM skill_assessment_history sah
    LEFT JOIN assessment_attempts aa ON sah.attempt_id = aa.id
    WHERE sah.user_id = ?
    ORDER BY sah.skill_name ASC, sah.attempt_number ASC, sah.id ASC
    """, (user_id,))
    rows = [dict(r) for r in cursor.fetchall()]

    # If skill_assessment_history is empty, check assessment_results table as fallback
    if not rows:
        cursor.execute("""
        SELECT ar.id, ar.user_id, ar.skill_name, ar.attempt_id,
               ar.percentage as score_pct, ar.proficiency_level,
               ar.mcq_score, ar.programming_score, ar.evaluated_at,
               ROW_NUMBER() OVER (PARTITION BY ar.skill_name ORDER BY ar.id ASC) as attempt_number
        FROM assessment_results ar
        WHERE ar.user_id = ?
        ORDER BY ar.skill_name ASC, ar.id ASC
        """, (user_id,))
        rows = [dict(r) for r in cursor.fetchall()]

    conn.close()

    # Group by skill name
    skill_groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        s_name = r["skill_name"]
        if s_name not in skill_groups:
            skill_groups[s_name] = []
        skill_groups[s_name].append(r)

    comparisons: List[Dict[str, Any]] = []

    for s_name, attempts in skill_groups.items():
        total_attempts = len(attempts)
        if total_attempts == 1:
            # Baseline single attempt
            first = attempts[0]
            comparisons.append({
                "skill": s_name,
                "skill_name": s_name,
                "has_reassessment": False,
                "total_attempts": 1,
                "before_score": None,
                "before_level": None,
                "before_date": None,
                "after_score": first["score_pct"],
                "after_level": first["proficiency_level"],
                "after_date": first["evaluated_at"],
                "score_change": 0.0,
                "score_diff": 0.0,
                "level_improved": False,
                "status": "Baseline Assessed",
                "display_text": f"{s_name}: Initial verified score = {first['score_pct']}% ({first['proficiency_level']})"
            })
        else:
            # Multiple attempts: compare earliest baseline vs latest attempt
            baseline = attempts[0]
            latest = attempts[-1]
            diff = round(latest["score_pct"] - baseline["score_pct"], 1)

            base_lvl_num = PROFICIENCY_SCALE.get(baseline["proficiency_level"], 1)
            late_lvl_num = PROFICIENCY_SCALE.get(latest["proficiency_level"], 1)
            level_improved = late_lvl_num > base_lvl_num

            if diff > 15.0 or level_improved:
                status_label = "Significantly Improved"
            elif diff > 0:
                status_label = "Improved"
            elif diff == 0:
                status_label = "Maintained"
            else:
                status_label = "Needs Review"

            comparisons.append({
                "skill": s_name,
                "skill_name": s_name,
                "has_reassessment": True,
                "total_attempts": total_attempts,
                "before_score": baseline["score_pct"],
                "before_level": baseline["proficiency_level"],
                "before_date": baseline["evaluated_at"],
                "after_score": latest["score_pct"],
                "after_level": latest["proficiency_level"],
                "after_date": latest["evaluated_at"],
                "score_change": diff,
                "score_diff": diff,
                "level_improved": level_improved,
                "status": status_label,
                "display_text": f"{s_name}: Before = {baseline['score_pct']}%, After = {latest['score_pct']}% ({baseline['proficiency_level']} -> {latest['proficiency_level']})"
            })

    return comparisons

def adapt_learning_path(
    user_id: int,
    target_role_id: Optional[str] = None,
    trigger_reason: str = "reassessment"
) -> Dict[str, Any]:
    """
    Module 8 Core:
    Dynamically recalculates and adapts the candidate's learning path.
    Triggers when:
      - User progress advances / modules completed
      - New assessment or reassessment results recorded
      - Job-market demand shifts or new skills detected
      - Skill proficiency increases

    Key adaptations:
      1. Demonstrates sufficient proficiency (e.g. Python): Removes unnecessary beginner modules.
      2. Job-market analysis detects newly important skill: Adds new skill module.
      3. Recalculates skill gaps and priority ranks.
      4. Marks completed/mastered skills.
      5. Recommends next immediate priority skills.
      6. Formulates clear explanations ('Why the curriculum changed').
      7. Displays banner 'YOUR LEARNING PATH HAS BEEN UPDATED'.
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

    role_id = role_info["role_id"]
    role_title = role_info["role_title"]

    # 2. Get User Verified Skills (Module 3) & Reassessment Comparisons
    cursor.execute("SELECT * FROM verified_skills WHERE user_id = ?", (user_id,))
    verified_rows = [dict(r) for r in cursor.fetchall()]
    verified_map = {r["skill_name"].lower(): r for r in verified_rows}

    comparisons = get_assessment_comparison(user_id)
    comparison_map = {c["skill_name"].lower(): c for c in comparisons}

    # 3. Recalculate Live Skill Gaps (Module 5)
    gap_data = calculate_skill_gaps(user_id=user_id, target_role_id=role_id)
    live_gaps = gap_data.get("gaps", [])
    gap_map = {g["skill_name"].lower(): g for g in live_gaps}

    # 4. Check Current Modules & Completed Module States
    cursor.execute("""
    SELECT uc.id as curr_id, uc.adaptation_version
    FROM user_curriculums uc
    WHERE uc.user_id = ? AND LOWER(uc.role_id) = LOWER(?)
    ORDER BY uc.id DESC LIMIT 1
    """, (user_id, role_id))
    curr_row = cursor.fetchone()
    curr_id = curr_row["curr_id"] if curr_row else None
    current_version = (curr_row["adaptation_version"] if curr_row else 0) + 1

    completed_modules = set()
    existing_curriculum_skills = set()
    if curr_id:
        cursor.execute("""
        SELECT skill_name, title, status FROM curriculum_modules
        WHERE curriculum_id = ?
        """, (curr_id,))
        for cm in cursor.fetchall():
            if cm["status"] == 'completed':
                completed_modules.add(cm["title"].lower())
                if cm["skill_name"]:
                    completed_modules.add(cm["skill_name"].lower())
            if cm["skill_name"]:
                existing_curriculum_skills.add(cm["skill_name"].lower())

    # 5. Explanations List ("Why the curriculum changed")
    explanations: List[str] = []
    pruned_modules: List[Dict[str, Any]] = []
    added_modules: List[Dict[str, Any]] = []
    completed_skills: List[str] = []

    # 6. Evaluate Proficiency Changes & Prune Unnecessary Beginner Modules
    # E.g.: If user demonstrates sufficient Python proficiency (score >= 60% or Level >= Intermediate):
    # Remove beginner Python modules (e.g., Python Basics, Python Functions).
    beginner_module_tags = {
        "python": ["python basics", "python functions"],
        "sql": ["sql basics", "sql fundamentals"],
        "javascript": ["javascript basics", "html/css basics"]
    }

    # Track skills with sufficient proficiency
    sufficient_skills = set()
    for s_lower, v_info in verified_map.items():
        v_level = v_info["proficiency_level"]
        v_score = v_info["score_pct"]
        v_level_num = PROFICIENCY_SCALE.get(v_level, 1)

        # Check comparison if retaken
        comp = comparison_map.get(s_lower)
        if comp and comp.get("has_reassessment"):
            before_score = comp["before_score"]
            after_score = comp["after_score"]
            before_level = comp["before_level"]
            after_level = comp["after_level"]

            if comp["score_change"] > 0:
                explanations.append(
                    f"{v_info['skill_name']}: Verified proficiency increased from {before_level} ({before_score}%) to {after_level} ({after_score}%)."
                )

        # Check against role requirement
        g_info = gap_map.get(s_lower)
        req_level_num = g_info["required_level_num"] if g_info else 3
        req_level_name = g_info["required_level"] if g_info else "Intermediate"

        if v_level_num >= req_level_num or v_score >= 70.0:
            sufficient_skills.add(s_lower)
            completed_skills.append(v_info["skill_name"])
            if g_info and g_info.get("gap_num", 0) <= 0:
                explanations.append(
                    f"{v_info['skill_name']} is no longer a high-priority gap because your verified proficiency reached {v_level} ({v_score}%), fulfilling the {req_level_name} requirement."
                )

        # Check for beginner module pruning
        if v_level_num >= 3 or v_score >= 60.0:
            tags_to_prune = beginner_module_tags.get(s_lower, [])
            for tag in tags_to_prune:
                pruned_modules.append({
                    "skill_name": v_info["skill_name"],
                    "module_title": MODULE_KNOWLEDGE_BASE.get(tag, {}).get("title", tag.title()),
                    "reason": f"Verified proficiency reached {v_score}% ({v_level}), making beginner {v_info['skill_name']} drills redundant."
                })
                explanations.append(
                    f"Removed unnecessary beginner {v_info['skill_name']} module because your verified proficiency reached {v_score}% ({v_level})."
                )

    # 7. Check Job-Market Demand for Newly Important Skills
    # If job market analysis detects a newly important skill, add it to the path
    market_analytics = analyze_target_role_skills(role_id)
    top_market_skills = market_analytics.get("top_skills", [])

    # Identify candidate skills to include in learning path
    active_skills_in_path = set()
    for g in live_gaps:
        active_skills_in_path.add(g["skill_name"].lower())

    # Check trending role_skills in database
    cursor.execute("SELECT * FROM role_skills WHERE LOWER(role_id) = LOWER(?) AND (LOWER(trend_status) = 'surging' OR importance_weight >= 0.85)", (role_id,))
    trending_role_skills = [dict(r) for r in cursor.fetchall()]
    for trs in trending_role_skills:
        s_name = trs["skill_name"]
        s_lower = s_name.lower()
        demand_pct = round(trs["importance_weight"] * 100.0, 1) if trs["importance_weight"] <= 1.0 else trs["importance_weight"]

        # If not in existing curriculum or marked surging, it was introduced by market demand
        if s_lower not in existing_curriculum_skills or trs.get("trend_status") == "surging":
            if not any(a["skill_name"].lower() == s_lower for a in added_modules):
                added_modules.append({
                    "skill_name": s_name,
                    "demand_pct": demand_pct,
                    "reason": f"Real-time job-market demand surge ({demand_pct}% employer postings in {role_title})."
                })
                explanations.append(
                    f"Added {s_name} to your learning path based on newly analyzed job-market demand (+{demand_pct}% in active postings)."
                )

        if s_lower not in active_skills_in_path:
            live_gaps.append({
                "skill_name": s_name,
                "category": trs.get("category", "Trending Tech"),
                "required_level": trs.get("min_proficiency", "Intermediate"),
                "required_level_num": PROFICIENCY_SCALE.get(trs.get("min_proficiency", "Intermediate"), 3),
                "verified_level": "Not Assessed",
                "verified_level_num": 0,
                "gap": "Medium Gap",
                "gap_num": 3,
                "job_demand_percentage": demand_pct,
                "importance_weight": trs.get("importance_weight", 0.85),
                "priority": "High",
                "priority_badge_class": "badge-primary"
            })
            active_skills_in_path.add(s_lower)

    for ms in top_market_skills:
        ms_name = ms["skill_name"]
        ms_lower = ms_name.lower()
        ms_demand = ms.get("demand_score_pct", 75.0)

        # If trending or high demand and not currently in previous curriculum:
        if (ms.get("is_trending") or ms_demand >= 70.0) and (s_lower not in existing_curriculum_skills or ms_lower not in active_skills_in_path):
            if not any(a["skill_name"].lower() == ms_lower for a in added_modules):
                added_modules.append({
                    "skill_name": ms_name,
                    "demand_pct": ms_demand,
                    "reason": f"Real-time job-market demand surge ({ms_demand}% employer postings in {role_title})."
                })
                explanations.append(
                    f"Added {ms_name} to your learning path based on newly analyzed job-market demand ({ms_demand}% in active postings)."
                )

        if ms_lower not in active_skills_in_path:
            # Add to gaps for synthesis
            live_gaps.append({
                "skill_name": ms_name,
                "category": ms.get("category", "Trending Tech"),
                "required_level": "Intermediate",
                "required_level_num": 3,
                "verified_level": "Not Assessed",
                "verified_level_num": 0,
                "gap": "Medium Gap",
                "gap_num": 3,
                "job_demand_percentage": ms_demand,
                "importance_weight": 0.85,
                "priority": "High",
                "priority_badge_class": "badge-primary"
            })
            active_skills_in_path.add(ms_lower)

    # 8. Synthesize Adapted Modules Sequence
    adapted_raw_modules = []
    pruned_module_titles = set(m["module_title"].lower() for m in pruned_modules)

    for g in live_gaps:
        s_name = g["skill_name"]
        s_lower = s_name.lower()

        # Check if already completed or sufficient
        is_skill_mastered = s_lower in sufficient_skills or s_lower in completed_modules

        # Template lookup
        template = MODULE_KNOWLEDGE_BASE.get(s_lower)
        if not template:
            # Fallback template
            template = {
                "title": f"{s_name} Engineering Mastery",
                "category": g.get("category", "Core Technical"),
                "default_hours": 10,
                "difficulty": "Intermediate" if g["required_level_num"] <= 3 else "Advanced",
                "learning_objective": f"Develop production-level proficiency in {s_name} to bridge competency gaps.",
                "prerequisites": [],
                "topics": [
                    f"Core Concepts & Architecture in {s_name}",
                    f"Production Best Practices for {s_name}",
                    f"Testing, Debugging and Automation in {s_name}"
                ],
                "learning_resources": [
                    {"title": f"Official {s_name} Documentation", "type": "Documentation", "url": "https://devdocs.io"}
                ],
                "practice_activities": [
                    f"Complete production engineering exercises in {s_name}"
                ],
                "assessment": f"15 {s_name} technical MCQs + 1 practical challenge.",
                "project_task": f"Build and deliver an end-to-end {s_name} component."
            }

        # Check if this module title was pruned
        if template.get("title", "").lower() in pruned_module_titles:
            continue

        # Adjust hours based on current gap
        gap_hours = max(6, g["gap_num"] * 4 + 2) if g["gap_num"] > 0 else template.get("default_hours", 8)
        if is_skill_mastered:
            gap_hours = max(4, int(gap_hours * 0.5))

        status = "completed" if is_skill_mastered else ("in_progress" if g["gap_num"] == 1 else "pending")
        progress = 100 if is_skill_mastered else (45 if g["gap_num"] == 1 else 0)

        adapted_raw_modules.append({
            "skill_name": s_name,
            "title": template["title"],
            "category": template.get("category", g.get("category", "Technical")),
            "current_proficiency": g["verified_level"],
            "current_proficiency_num": g["verified_level_num"],
            "required_proficiency": g["required_level"],
            "required_proficiency_num": g["required_level_num"],
            "gap": g["gap"],
            "gap_num": 0 if is_skill_mastered else g["gap_num"],
            "job_demand_percentage": g.get("job_demand_percentage", 75.0),
            "importance_weight": g.get("importance_weight", 0.85),
            "priority": "None" if is_skill_mastered else g["priority"],
            "priority_badge_class": "badge-secondary" if is_skill_mastered else g.get("priority_badge_class", "badge-primary"),
            "learning_objective": template["learning_objective"],
            "prerequisites": template.get("prerequisites", []),
            "topics": template.get("topics", []),
            "difficulty": template.get("difficulty", "Intermediate"),
            "hours": gap_hours,
            "estimated_duration": f"{gap_hours} Hours",
            "learning_resources": template.get("learning_resources", []),
            "practice_activities": template.get("practice_activities", []),
            "assessment": template.get("assessment", ""),
            "project_task": template.get("project_task", ""),
            "status": status,
            "progress_pct": progress,
            "is_unlocked": True
        })

    # 9. Prerequisite Topological Sorting
    sequenced_modules = topological_sort_modules(adapted_raw_modules)

    # 10. Append Final Capstone Project
    capstone_def = get_capstone_module_definition(role_title)
    all_incomplete_pre = [m for m in sequenced_modules if m["status"] != "completed"]

    sequenced_modules.append({
        "skill_name": capstone_def["skill_name"],
        "title": capstone_def["title"],
        "category": capstone_def["category"],
        "current_proficiency": "Ready to Synthesize" if not all_incomplete_pre else "In Progress",
        "current_proficiency_num": 0,
        "required_proficiency": capstone_def["required_proficiency"],
        "required_proficiency_num": 5,
        "gap": "Integration Capstone",
        "gap_num": 1,
        "job_demand_percentage": 100.0,
        "importance_weight": 1.0,
        "priority": "Critical",
        "priority_badge_class": "badge-danger",
        "learning_objective": capstone_def["learning_objective"],
        "prerequisites": [m["skill_name"] for m in sequenced_modules],
        "topics": capstone_def["topics"],
        "difficulty": capstone_def["difficulty"],
        "hours": capstone_def["hours"],
        "estimated_duration": f"{capstone_def['hours']} Hours",
        "learning_resources": capstone_def["learning_resources"],
        "practice_activities": capstone_def["practice_activities"],
        "assessment": capstone_def["assessment"],
        "project_task": capstone_def["project_task"],
        "status": "pending",
        "progress_pct": 0,
        "is_unlocked": len(all_incomplete_pre) == 0
    })

    # 11. Determine Unlocking & Next Recommended Skills
    mastered_skill_names = set(m["skill_name"].lower() for m in sequenced_modules if m["status"] == "completed")
    recommended_next_skills: List[Dict[str, Any]] = []

    for idx, m in enumerate(sequenced_modules):
        m["module_order"] = idx + 1
        prereqs = m.get("prerequisites", [])

        is_unlocked = False
        if m["status"] == "completed":
            is_unlocked = True
        elif idx == 0:
            is_unlocked = True
        elif not prereqs or all(p.lower() in mastered_skill_names for p in prereqs):
            is_unlocked = True

        m["is_unlocked"] = is_unlocked

        if is_unlocked and m["status"] != "completed" and len(recommended_next_skills) < 3:
            recommended_next_skills.append({
                "module_id": None, # Will be set upon db persist
                "skill_name": m["skill_name"],
                "title": m["title"],
                "hours": m["hours"],
                "priority": m["priority"],
                "learning_objective": m["learning_objective"]
            })

    # Add default explanation if list is empty
    if not explanations:
        explanations.append("Curriculum dynamically recalibrated against current verified competencies and live market requirements.")

    # 12. Persist Adapted Curriculum in Database
    curriculum_title = f"Adaptive Learning Pathway: {role_title}"
    total_hours = sum(m["hours"] for m in sequenced_modules)
    completed_cnt = sum(1 for m in sequenced_modules if m["status"] == "completed")

    if curr_id:
        cursor.execute("""
        UPDATE user_curriculums
        SET title = ?, status = 'active', total_modules = ?, completed_modules = ?,
            adaptation_version = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """, (curriculum_title, len(sequenced_modules), completed_cnt, current_version, curr_id))
        cursor.execute("DELETE FROM curriculum_modules WHERE curriculum_id = ?", (curr_id,))
    else:
        cursor.execute("""
        INSERT INTO user_curriculums (
            user_id, role_id, title, status, total_modules, completed_modules,
            adaptation_version, weekly_hours, preferred_difficulty,
            learning_preferences, estimated_weeks
        ) VALUES (?, ?, ?, 'active', ?, ?, ?, 10, 'Adaptive', 'Hands-on Projects', 6)
        """, (user_id, role_id, curriculum_title, len(sequenced_modules), completed_cnt, current_version))
        curr_id = cursor.lastrowid

    # Persist updated modules
    for m in sequenced_modules:
        cursor.execute("""
        INSERT INTO curriculum_modules (
            curriculum_id, module_order, title, hours, status, progress_pct,
            skill_name, current_proficiency, required_proficiency, difficulty,
            learning_objective, prerequisites_json, topics_json, resources_json,
            practice_json, assessment_info, project_task, details_json, is_unlocked
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            curr_id, m["module_order"], m["title"], m["hours"], m["status"], m["progress_pct"],
            m["skill_name"], m["current_proficiency"], m["required_proficiency"], m["difficulty"],
            m["learning_objective"], json.dumps(m["prerequisites"]), json.dumps(m["topics"]),
            json.dumps(m["learning_resources"]), json.dumps(m["practice_activities"]),
            m["assessment"], m["project_task"], json.dumps(m), 1 if m["is_unlocked"] else 0
        ))
        m["module_id"] = cursor.lastrowid

    # Update module IDs in recommended list
    for rec in recommended_next_skills:
        for m in sequenced_modules:
            if m["skill_name"] == rec["skill_name"]:
                rec["module_id"] = m["module_id"]
                break

    # 13. Persist Adaptation Audit Log (Module 8)
    banner_message = "YOUR LEARNING PATH HAS BEEN UPDATED"
    cursor.execute("""
    INSERT INTO learning_path_adaptations (
        user_id, role_id, curriculum_id, version, trigger_reason,
        banner_message, explanations_json, before_vs_after_json,
        pruned_modules_json, added_modules_json, completed_skills_json,
        recommended_next_json, adapted_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        user_id, role_id, curr_id, current_version, trigger_reason,
        banner_message, json.dumps(explanations), json.dumps(comparisons),
        json.dumps(pruned_modules), json.dumps(added_modules),
        json.dumps(completed_skills), json.dumps(recommended_next_skills)
    ))
    adaptation_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "adaptation_id": adaptation_id,
        "curriculum_id": curr_id,
        "user_id": user_id,
        "target_role_id": role_id,
        "target_role_title": role_title,
        "banner": banner_message,
        "banner_message": banner_message,
        "is_updated": True,
        "adaptation_version": current_version,
        "trigger_reason": trigger_reason,
        "explanations": explanations,
        "before_vs_after": comparisons,
        "pruned_modules": pruned_modules,
        "added_modules": added_modules,
        "completed_skills": completed_skills,
        "recommended_next_skills": recommended_next_skills,
        "total_modules": len(sequenced_modules),
        "completed_modules": completed_cnt,
        "overall_progress_pct": round((completed_cnt / max(1, len(sequenced_modules))) * 100.0, 1),
        "modules": sequenced_modules
    }

def get_latest_adaptation_log(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves the latest adaptation state and explanations for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM learning_path_adaptations
    WHERE user_id = ?
    ORDER BY id DESC LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "role_id": row["role_id"],
        "version": row["version"],
        "trigger_reason": row["trigger_reason"],
        "banner_message": row["banner_message"],
        "explanations": json.loads(row["explanations_json"]),
        "before_vs_after": json.loads(row["before_vs_after_json"]),
        "pruned_modules": json.loads(row["pruned_modules_json"]),
        "added_modules": json.loads(row["added_modules_json"]),
        "completed_skills": json.loads(row["completed_skills_json"]),
        "recommended_next_skills": json.loads(row["recommended_next_json"]),
        "adapted_at": row["adapted_at"]
    }

def simulate_reassessment(
    user_id: int,
    skill_name: str,
    new_score_pct: float,
    new_proficiency_level: Optional[str] = None
) -> Dict[str, Any]:
    """
    Simulation & Testing Helper:
    Simulates a completed reassessment (e.g. Python increasing from 45% to 78%),
    records the attempt into history WITHOUT deleting past attempts,
    updates verified_skills, and triggers live adaptive learning path recalculation.
    """
    if not new_proficiency_level:
        if new_score_pct >= 90:
            new_proficiency_level = "Expert"
        elif new_score_pct >= 75:
            new_proficiency_level = "Advanced"
        elif new_score_pct >= 60:
            new_proficiency_level = "Intermediate"
        elif new_score_pct >= 40:
            new_proficiency_level = "Basic"
        else:
            new_proficiency_level = "Beginner"

    conn = get_db_connection()
    cursor = conn.cursor()

    # Create distinct attempt record in assessment_attempts
    import secrets
    token = f"sim_{secrets.token_hex(8)}"
    cursor.execute("""
    INSERT INTO assessment_attempts (
        session_token, user_id, skill_name, start_time, end_time,
        duration_minutes, is_completed, mcq_score, programming_score,
        total_score, percentage, status
    ) VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 90, 1, ?, ?, ?, ?, 'completed')
    """, (token, user_id, skill_name, new_score_pct * 0.7, new_score_pct * 0.3, new_score_pct, new_score_pct))
    attempt_id = cursor.lastrowid

    # Create assessment_result record (NEVER deleted)
    cursor.execute("""
    INSERT INTO assessment_results (
        attempt_id, user_id, skill_name, mcq_score, mcq_max,
        programming_score, programming_max, total_score, total_max,
        percentage, proficiency_level, topic_scores_json,
        difficulty_scores_json, programming_details_json, evaluated_at
    ) VALUES (?, ?, ?, ?, 50.0, ?, 20.0, ?, 100.0, ?, ?, '{}', '{}', '[]', CURRENT_TIMESTAMP)
    """, (
        attempt_id, user_id, skill_name,
        round(new_score_pct * 0.5, 1), round(new_score_pct * 0.2, 1),
        new_score_pct, new_score_pct, new_proficiency_level
    ))

    # Update active verified_skills (Module 3 handoff table)
    cursor.execute("DELETE FROM verified_skills WHERE user_id = ? AND LOWER(skill_name) = LOWER(?)", (user_id, skill_name))
    cursor.execute("""
    INSERT INTO verified_skills (
        user_id, attempt_id, skill_name, category, score_pct,
        proficiency_level, mcq_score, programming_score, comparison_status, verified_at
    ) VALUES (?, ?, ?, 'Technical Skill', ?, ?, ?, ?, 'matched', CURRENT_TIMESTAMP)
    """, (
        user_id, attempt_id, skill_name,
        new_score_pct, new_proficiency_level,
        round(new_score_pct * 0.5, 1), round(new_score_pct * 0.2, 1)
    ))

    conn.commit()
    conn.close()

    # Record in history (preserving all previous attempts)
    record_assessment_attempt(
        user_id=user_id,
        skill_name=skill_name,
        attempt_id=attempt_id,
        score_pct=new_score_pct,
        proficiency_level=new_proficiency_level,
        mcq_score=round(new_score_pct * 0.5, 1),
        programming_score=round(new_score_pct * 0.2, 1)
    )

    # Immediately trigger adaptive path recalculation
    adapted = adapt_learning_path(user_id=user_id, trigger_reason="reassessment")
    return adapted

def simulate_market_demand_shift(
    role_id: str,
    new_skill: str,
    demand_percentage: float = 88.0
) -> Dict[str, Any]:
    """
    Simulation & Testing Helper:
    Simulates a newly surging market skill demand (e.g. Docker surging to 88% demand),
    and triggers curriculum adaptation.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert or update job posting requiring new_skill
    cursor.execute("""
    INSERT INTO job_postings (
        job_title, target_role_id, company, industry, location,
        required_skills_json, experience_level, posting_date, data_source
    ) VALUES (
        ?, ?, 'Market Intelligence Labs', 'Technology / Cloud', 'Remote',
        ?, 'Mid-Level (2-4 yrs)', date('now'), 'Real-Time Job Aggregator'
    )
    """, (
        f"Senior {role_id.title()} with {new_skill}",
        role_id,
        json.dumps([new_skill, "Git", "REST API"])
    ))

    # Also update role_skills with surging trend
    cursor.execute("SELECT id FROM role_skills WHERE LOWER(role_id) = LOWER(?) AND LOWER(skill_name) = LOWER(?)", (role_id, new_skill))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO role_skills (role_id, skill_name, category, importance_weight, trend_status, min_proficiency)
        VALUES (?, ?, 'Cloud / DevOps', 0.90, 'surging', 'Intermediate')
        """, (role_id, new_skill))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Simulated market demand shift for {new_skill} in role {role_id} (Demand: {demand_percentage}%)",
        "new_skill": new_skill,
        "demand_percentage": demand_percentage
    }
