"""
Module 9: Job Readiness Dashboard & Career Skill Profile Engine
Combines all project modules (Modules 1 through 8) into an executive Career Skill Profile.
Provides:
- User Information (Name, Target Job Role, Preferred Domain, Career Goal)
- Verified Skills (Skill, Verified Proficiency, Assessment Score)
- Required Job Skills (Skill, Required Level, Job-Market Demand)
- Skill Gaps (Skill, Current Level, Required Level, Gap, Priority)
- Curriculum Progress (Completed Modules, Current Module, Remaining Modules, Overall Progress)
- Micro-Credentials (Earned Credentials, In-Progress Credentials)
- Job Readiness / Skill Coverage (Transparent percentage calculation with non-employment disclaimer)
- 6 Visualizations Datasets (Radar chart, Proficiency bars, Gap chart, Curriculum progress, Credential progress, Market demand chart)
- Final Actionable Recommendations (Top gaps, Highest-priority skills, Next module, Assessment retake)
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.database import get_db_connection
from backend.services.gap_engine import calculate_skill_gaps, PROFICIENCY_SCALE
from backend.services.curriculum_engine import get_active_user_curriculum
from backend.services.credential_engine import get_user_credentials
from backend.services.market_analyzer import analyze_target_role_skills

NON_EMPLOYMENT_DISCLAIMER = (
    "Disclaimer: This metric represents an objective technical skill coverage percentage benchmarked "
    "against verified competencies and current job-market requirements. It is a technical readiness index "
    "and does NOT represent or guarantee a probability, promise, or offer of employment or job placement."
)

def get_career_skill_profile(user_id: int, target_role_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Module 9 Master Aggregator:
    Synthesizes candidate profile data across all modules into an executive Career Skill Profile.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. USER INFORMATION & CAREER PROFILE
    cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    candidate_name = user_row["name"] if user_row else "Candidate"
    candidate_email = user_row["email"] if user_row else "student@example.com"

    cursor.execute("SELECT * FROM career_profiles WHERE user_id = ?", (user_id,))
    profile_row = cursor.fetchone()

    resolved_role_id = target_role_id
    if not resolved_role_id:
        if profile_row and profile_row["target_role_id"]:
            resolved_role_id = profile_row["target_role_id"]
        else:
            resolved_role_id = "fullstack-dev"

    cursor.execute("SELECT * FROM job_roles WHERE LOWER(role_id) = LOWER(?)", (resolved_role_id,))
    role_row = cursor.fetchone()
    if not role_row:
        cursor.execute("SELECT * FROM job_roles WHERE role_id = 'fullstack-dev'")
        role_row = cursor.fetchone()

    role_title = role_row["role_title"] if role_row else "Full-Stack Software Engineer"
    role_domain = role_row["domain"] if role_row else "Software Engineering"
    active_role_id = role_row["role_id"] if role_row else resolved_role_id

    exp_level = profile_row["experience_level"] if profile_row and profile_row["experience_level"] else "Fresher"
    education = profile_row["education"] if profile_row and profile_row["education"] else "Undergraduate"

    # Formulate contextual career goal
    career_goal = f"Achieve industry-grade competency as a {role_title} in {role_domain} by mastering high-demand skills."

    # 2. VERIFIED SKILLS (Modules 2 & 3)
    cursor.execute("""
    SELECT skill_name, category, score_pct, proficiency_level, mcq_score, mcq_max,
           programming_score, programming_max, strengths_json, weaknesses_json,
           comparison_status, verified_at
    FROM verified_skills
    WHERE user_id = ?
    ORDER BY score_pct DESC, verified_at DESC
    """, (user_id,))
    v_rows = cursor.fetchall()

    verified_skills: List[Dict[str, Any]] = []
    seen_skills = set()
    for row in v_rows:
        s_name = row["skill_name"]
        if s_name.lower() in seen_skills:
            continue
        seen_skills.add(s_name.lower())
        verified_skills.append({
            "skill": s_name,
            "skill_name": s_name,
            "category": row["category"] or "Technical Skill",
            "verified_proficiency": row["proficiency_level"],
            "assessment_score": round(float(row["score_pct"]), 1),
            "mcq_score": round(float(row["mcq_score"] or 0), 1),
            "mcq_max": round(float(row["mcq_max"] or 50), 1),
            "programming_score": round(float(row["programming_score"] or 0), 1),
            "programming_max": round(float(row["programming_max"] or 20), 1),
            "verified_at": str(row["verified_at"])[:19] if row["verified_at"] else None
        })

    # If verified_skills is empty, check skill_assessment_history for recent completions
    if not verified_skills:
        cursor.execute("""
        SELECT skill_name, score_pct, proficiency_level, evaluated_at, mcq_score, programming_score
        FROM skill_assessment_history
        WHERE user_id = ?
        ORDER BY evaluated_at DESC
        """, (user_id,))
        hist_rows = cursor.fetchall()
        for hr in hist_rows:
            s_name = hr["skill_name"]
            if s_name.lower() in seen_skills:
                continue
            seen_skills.add(s_name.lower())
            verified_skills.append({
                "skill": s_name,
                "skill_name": s_name,
                "category": "Technical Skill",
                "verified_proficiency": hr["proficiency_level"],
                "assessment_score": round(float(hr["score_pct"]), 1),
                "mcq_score": round(float(hr["mcq_score"] or 0), 1),
                "mcq_max": 50.0,
                "programming_score": round(float(hr["programming_score"] or 0), 1),
                "programming_max": 20.0,
                "verified_at": str(hr["evaluated_at"])[:19] if hr["evaluated_at"] else None
            })

    # 3. SKILL GAPS & REQUIRED JOB SKILLS (Modules 4 & 5)
    gap_data = calculate_skill_gaps(user_id=user_id, target_role_id=active_role_id)
    gaps_list = gap_data.get("gaps", [])

    required_job_skills: List[Dict[str, Any]] = []
    skill_gaps: List[Dict[str, Any]] = []

    for g in gaps_list:
        required_job_skills.append({
            "skill": g["skill_name"],
            "skill_name": g["skill_name"],
            "required_level": g["required_level"],
            "job_market_demand": round(float(g["job_demand_percentage"]), 1),
            "importance_weight": round(float(g["importance_weight"]), 2),
            "trend_status": g["trend_status"],
            "category": g["category"]
        })

        skill_gaps.append({
            "skill": g["skill_name"],
            "skill_name": g["skill_name"],
            "current_level": g["verified_level"],
            "required_level": g["required_level"],
            "gap": g["gap"],
            "gap_num": g["gap_num"],
            "priority": g["priority"],
            "priority_score": g["priority_score"],
            "priority_badge_class": g["priority_badge_class"],
            "job_market_demand": round(float(g["job_demand_percentage"]), 1),
            "status": g["status"]
        })

    # 4. CURRICULUM PROGRESS (Module 6)
    curriculum_data = get_active_user_curriculum(user_id=user_id, target_role_id=active_role_id)
    modules_list = curriculum_data.get("modules", [])

    completed_modules = [m for m in modules_list if m.get("status") == "completed"]
    in_progress_modules = [m for m in modules_list if m.get("status") == "in_progress"]
    remaining_modules = [m for m in modules_list if m.get("status") != "completed"]

    # Identify current active module
    current_module = None
    if in_progress_modules:
        current_module = in_progress_modules[0]
    elif remaining_modules:
        # First unlocked remaining module
        unlocked = [m for m in remaining_modules if m.get("is_unlocked", True)]
        current_module = unlocked[0] if unlocked else remaining_modules[0]

    total_modules_count = len(modules_list)
    completed_modules_count = len(completed_modules)
    remaining_modules_count = len(remaining_modules)
    overall_progress_pct = (
        round((completed_modules_count / total_modules_count) * 100.0, 1)
        if total_modules_count > 0 else 0.0
    )

    curriculum_progress = {
        "curriculum_id": curriculum_data.get("id"),
        "curriculum_title": curriculum_data.get("title", f"{role_title} Micro-Credential Curriculum"),
        "completed_modules": [
            {
                "module_id": m.get("module_id") or m.get("id"),
                "title": m.get("title"),
                "skill_name": m.get("skill_name"),
                "hours": m.get("hours", 4),
                "status": "completed",
                "progress_pct": 100
            }
            for m in completed_modules
        ],
        "completed_count": completed_modules_count,
        "current_module": {
            "module_id": current_module.get("module_id") or current_module.get("id"),
            "title": current_module.get("title"),
            "skill_name": current_module.get("skill_name"),
            "hours": current_module.get("hours", 4),
            "status": current_module.get("status", "pending"),
            "progress_pct": current_module.get("progress_pct", 0),
            "learning_objective": current_module.get("learning_objective")
        } if current_module else None,
        "remaining_modules": [
            {
                "module_id": m.get("module_id") or m.get("id"),
                "title": m.get("title"),
                "skill_name": m.get("skill_name"),
                "hours": m.get("hours", 4),
                "status": m.get("status", "pending"),
                "is_unlocked": m.get("is_unlocked", False)
            }
            for m in remaining_modules
        ],
        "remaining_count": remaining_modules_count,
        "total_modules": total_modules_count,
        "overall_progress": overall_progress_pct,
        "overall_progress_formatted": f"{overall_progress_pct}%",
        "adaptation_version": curriculum_data.get("adaptation_version", 1)
    }

    # 5. MICRO-CREDENTIALS (Module 7)
    credentials_data = get_user_credentials(user_id=user_id)
    earned_creds = credentials_data.get("earned_credentials") or credentials_data.get("earned") or []
    in_progress_creds = credentials_data.get("in_progress_credentials") or credentials_data.get("in_progress") or []

    micro_credentials = {
        "earned_credentials": earned_creds,
        "earned": earned_creds,
        "earned_count": len(earned_creds),
        "in_progress_credentials": in_progress_creds,
        "in_progress": in_progress_creds,
        "in_progress_count": len(in_progress_creds),
        "total_credentials": len(earned_creds) + len(in_progress_creds)
    }

    # 6. JOB READINESS / SKILL COVERAGE CALCULATION
    # Transparent formula:
    # Coverage % = sum(min(verified_level_num, req_level_num) * importance) / sum(req_level_num * importance) * 100
    total_potential_weight = sum(g["required_level_num"] * g["importance_weight"] for g in gaps_list)
    achieved_weight = sum(min(g["verified_level_num"], g["required_level_num"]) * g["importance_weight"] for g in gaps_list)

    overall_skill_coverage = (
        round((achieved_weight / total_potential_weight) * 100.0, 1)
        if total_potential_weight > 0 else 0.0
    )

    fully_met_count = sum(1 for g in gaps_list if g["gap_num"] == 0)
    with_gaps_count = sum(1 for g in gaps_list if g["gap_num"] > 0)
    total_skills_count = len(gaps_list)

    if overall_skill_coverage >= 90:
        coverage_band = "Benchmark Ready"
        coverage_color = "#10b981"
    elif overall_skill_coverage >= 70:
        coverage_band = "High Alignment"
        coverage_color = "#38bdf8"
    elif overall_skill_coverage >= 45:
        coverage_band = "Moderate Alignment"
        coverage_color = "#f59e0b"
    else:
        coverage_band = "Foundational Alignment"
        coverage_color = "#ef4444"

    job_readiness = {
        "overall_skill_coverage": overall_skill_coverage,
        "overall_skill_coverage_display": f"Overall Skill Coverage: {overall_skill_coverage}%",
        "coverage_percentage": overall_skill_coverage,
        "coverage_band": coverage_band,
        "coverage_color": coverage_color,
        "skills_fully_met_count": fully_met_count,
        "skills_with_gaps_count": with_gaps_count,
        "total_skills_evaluated": total_skills_count,
        "calculation_method": (
            "Transparent multi-variable index: [Sum of min(Verified Proficiency, Required Level) * Importance Weight] "
            "/ [Sum of Required Level * Importance Weight] * 100%"
        ),
        "achieved_weight": round(achieved_weight, 2),
        "total_weight": round(total_potential_weight, 2),
        "disclaimer": NON_EMPLOYMENT_DISCLAIMER
    }

    # 7. VISUALIZATIONS DATASETS
    # Visual 1: Skill Radar Chart
    radar_labels = [g["skill_name"] for g in gaps_list]
    radar_verified = [g["verified_level_num"] for g in gaps_list]
    radar_required = [g["required_level_num"] for g in gaps_list]

    # Visual 2: Skill Proficiency Bars
    proficiency_bars = []
    for s in verified_skills:
        lvl_num = PROFICIENCY_SCALE.get(s["verified_proficiency"], 2)
        proficiency_bars.append({
            "skill": s["skill"],
            "score_pct": s["assessment_score"],
            "proficiency_level": s["verified_proficiency"],
            "level_num": lvl_num,
            "max_level": 5
        })

    # Visual 3: Skill Gap Chart
    skill_gap_chart = []
    for g in gaps_list:
        skill_gap_chart.append({
            "skill": g["skill_name"],
            "verified_level": g["verified_level"],
            "verified_level_num": g["verified_level_num"],
            "required_level": g["required_level"],
            "required_level_num": g["required_level_num"],
            "gap_num": g["gap_num"],
            "gap_category": g["gap"],
            "priority": g["priority"]
        })

    # Visual 4: Curriculum Progress Chart
    curriculum_progress_chart = {
        "completed": completed_modules_count,
        "in_progress": 1 if in_progress_modules else 0,
        "pending": max(0, total_modules_count - completed_modules_count - (1 if in_progress_modules else 0)),
        "total": total_modules_count,
        "percentage": overall_progress_pct
    }

    # Visual 5: Credential Progress Chart
    credential_progress_chart = {
        "earned": len(earned_creds),
        "in_progress": len(in_progress_creds),
        "total": len(earned_creds) + len(in_progress_creds),
        "completion_rate": (
            round((len(earned_creds) / (len(earned_creds) + len(in_progress_creds))) * 100.0, 1)
            if (len(earned_creds) + len(in_progress_creds)) > 0 else 0.0
        )
    }

    # Visual 6: Job-Market Demand Chart
    market_demand_chart = [
        {
            "skill": g["skill_name"],
            "demand_percentage": round(float(g["job_demand_percentage"]), 1),
            "importance_weight": round(float(g["importance_weight"]), 2),
            "trend_status": g["trend_status"]
        }
        for g in sorted(gaps_list, key=lambda x: -x["job_demand_percentage"])
    ]

    visualizations = {
        "skill_radar_chart": {
            "labels": radar_labels,
            "verified_series": radar_verified,
            "required_series": radar_required,
            "max_scale": 5
        },
        "skill_proficiency_bars": proficiency_bars,
        "skill_gap_chart": skill_gap_chart,
        "curriculum_progress": curriculum_progress_chart,
        "credential_progress": credential_progress_chart,
        "job_market_demand_chart": market_demand_chart
    }

    # 8. FINAL ACTIONABLE RECOMMENDATIONS
    # Top remaining skill gaps
    remaining_gaps = [g for g in gaps_list if g["gap_num"] > 0]
    # Sorted by priority and gap magnitude
    p_rank = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "None": 4}
    remaining_gaps.sort(key=lambda x: (p_rank.get(x["priority"], 5), -x["gap_num"], -x["job_demand_percentage"]))

    top_remaining_gaps = [
        {
            "skill": g["skill_name"],
            "current_level": g["verified_level"],
            "required_level": g["required_level"],
            "gap": g["gap"],
            "gap_num": g["gap_num"],
            "priority": g["priority"],
            "job_demand": round(float(g["job_demand_percentage"]), 1),
            "reason": f"Required proficiency is {g['required_level']} but verified level is {g['verified_level']}."
        }
        for g in remaining_gaps[:3]
    ]

    # Highest-priority skills
    high_priority_skills = [
        {
            "skill": g["skill_name"],
            "priority": g["priority"],
            "job_demand": round(float(g["job_demand_percentage"]), 1),
            "gap_num": g["gap_num"],
            "action": f"Focus immediately on {g['skill_name']} to eliminate a {g['gap']} with high market demand."
        }
        for g in gaps_list if g["priority"] in ["Critical", "High"]
    ]
    if not high_priority_skills and remaining_gaps:
        high_priority_skills = [
            {
                "skill": remaining_gaps[0]["skill_name"],
                "priority": remaining_gaps[0]["priority"],
                "job_demand": round(float(remaining_gaps[0]["job_demand_percentage"]), 1),
                "gap_num": remaining_gaps[0]["gap_num"],
                "action": f"Focus on {remaining_gaps[0]['skill_name']} to elevate skill coverage."
            }
        ]

    # Recommended next module
    if current_module:
        recommended_next_module = {
            "module_id": current_module.get("module_id") or current_module.get("id"),
            "title": current_module.get("title"),
            "skill": current_module.get("skill_name"),
            "duration": f"{current_module.get('hours', 4)} Hours",
            "learning_objective": current_module.get("learning_objective"),
            "action_text": f"Continue learning: {current_module.get('title')}"
        }
    else:
        recommended_next_module = {
            "module_id": None,
            "title": "All Modules Completed",
            "skill": "Full Stack Mastery",
            "duration": "Complete",
            "learning_objective": "All synthesized modules have been successfully completed.",
            "action_text": "Explore advanced project challenges or retake assessments to elevate verified scores."
        }

    # Recommended assessment/retake
    # Check if there is an unassessed skill or a skill where reassessment would yield high ROI
    recommended_retake = None
    unassessed_skills = [g for g in gaps_list if g["verified_level_num"] == 0 and g["job_demand_percentage"] >= 60]
    if unassessed_skills:
        target = unassessed_skills[0]
        recommended_retake = {
            "skill": target["skill_name"],
            "type": "Initial Assessment",
            "current_status": "Unassessed",
            "target_level": target["required_level"],
            "rationale": (
                f"Taking the {target['skill_name']} timed assessment can immediately boost your Overall Skill Coverage "
                f"by up to {round(target['required_level_num'] * target['importance_weight'] / total_potential_weight * 100, 1)}%."
            )
        }
    else:
        # Check verified skills with score < 80%
        improvable = [s for s in verified_skills if s["assessment_score"] < 80.0]
        if improvable:
            target = improvable[0]
            recommended_retake = {
                "skill": target["skill"],
                "type": "Reassessment / Retake",
                "current_status": f"{target['verified_proficiency']} ({target['assessment_score']}%)",
                "target_level": "Advanced (80%+)",
                "rationale": (
                    f"Retake the {target['skill']} assessment after completing curriculum modules to demonstrate "
                    f"advanced verified proficiency and upgrade historical results."
                )
            }
        elif verified_skills:
            target = verified_skills[0]
            recommended_retake = {
                "skill": target["skill"],
                "type": "Proficiency Reassessment",
                "current_status": f"{target['verified_proficiency']} ({target['assessment_score']}%)",
                "target_level": "Expert (90%+)",
                "rationale": f"Retake the {target['skill']} assessment to pursue Expert certification."
            }
        else:
            recommended_retake = {
                "skill": "Python",
                "type": "Initial Assessment",
                "current_status": "Unassessed",
                "target_level": "Intermediate",
                "rationale": "Launch initial technical assessment to verify core programming competency."
            }

    final_recommendations = {
        "top_remaining_skill_gaps": top_remaining_gaps,
        "highest_priority_skills": high_priority_skills,
        "recommended_next_module": recommended_next_module,
        "recommended_assessment_retake": recommended_retake
    }

    # 9. PERSIST SYNCHRONIZED SNAPSHOT TO job_readiness TABLE
    try:
        cursor.execute("SELECT id FROM job_readiness WHERE user_id = ?", (user_id,))
        existing_jr = cursor.fetchone()
        if existing_jr:
            cursor.execute("""
            UPDATE job_readiness
            SET role_id = ?, overall_readiness_pct = ?, role_match_pct = ?,
                gap_coverage_pct = ?, credentials_earned = ?, last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """, (
                active_role_id,
                overall_skill_coverage,
                overall_skill_coverage,
                overall_skill_coverage,
                len(earned_creds),
                user_id
            ))
        else:
            cursor.execute("""
            INSERT INTO job_readiness (
                user_id, role_id, overall_readiness_pct, role_match_pct,
                gap_coverage_pct, credentials_earned, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                user_id,
                active_role_id,
                overall_skill_coverage,
                overall_skill_coverage,
                overall_skill_coverage,
                len(earned_creds)
            ))
        conn.commit()
    except Exception as e:
        print(f"Warning: Failed to update job_readiness snapshot: {e}")
    finally:
        conn.close()

    return {
        "title": "CAREER SKILL PROFILE",
        "generated_at": datetime.now().isoformat(),
        "user_information": {
            "name": candidate_name,
            "email": candidate_email,
            "target_job_role": role_title,
            "target_role_id": active_role_id,
            "preferred_domain": role_domain,
            "career_goal": career_goal,
            "experience_level": exp_level,
            "education": education
        },
        "verified_skills": verified_skills,
        "required_job_skills": required_job_skills,
        "skill_gaps": skill_gaps,
        "curriculum_progress": curriculum_progress,
        "micro_credentials": micro_credentials,
        "job_readiness": job_readiness,
        "visualizations": visualizations,
        "final_recommendations": final_recommendations
    }
