"""
Module 9 Router: Job Readiness Dashboard & Career Skill Profile API
Exposes endpoints for retrieving, recalculating, and summarizing the final Career Skill Profile.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.routers.auth import get_current_user_id
from backend.services.job_readiness_engine import get_career_skill_profile

router = APIRouter(prefix="/api/readiness", tags=["Module 9: Job Readiness Dashboard"])

class RecalculateRequest(BaseModel):
    target_role_id: Optional[str] = None

@router.get("/dashboard")
def get_dashboard(
    target_role_id: Optional[str] = None,
    user_id: int = Depends(get_current_user_id)
):
    """
    Returns the final CAREER SKILL PROFILE dashboard combining all project modules (1 through 8).
    Includes:
    - User Information (Name, Target Job Role, Preferred Domain, Career Goal)
    - Verified Skills (Skill, Verified Proficiency, Assessment Score)
    - Required Job Skills (Skill, Required Level, Job-Market Demand)
    - Skill Gaps (Skill, Current Level, Required Level, Gap, Priority)
    - Curriculum Progress (Completed Modules, Current Module, Remaining Modules, Overall Progress)
    - Micro-Credentials (Earned Credentials, In-Progress Credentials)
    - Job Readiness / Skill Coverage (Transparent percentage with non-employment disclaimer)
    - 6 Visualizations Datasets (Radar chart, Proficiency bars, Gap chart, Curriculum progress, Credential progress, Market demand)
    - Final Actionable Recommendations (Top gaps, Highest-priority skills, Recommended next module, Recommended retake)
    """
    try:
        profile = get_career_skill_profile(user_id=user_id, target_role_id=target_role_id)
        return {
            "success": True,
            "profile": profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Career Skill Profile: {str(e)}")

@router.get("/summary")
def get_summary(
    target_role_id: Optional[str] = None,
    user_id: int = Depends(get_current_user_id)
):
    """
    Quick executive summary of readiness metrics.
    """
    try:
        profile = get_career_skill_profile(user_id=user_id, target_role_id=target_role_id)
        jr = profile.get("job_readiness", {})
        recs = profile.get("final_recommendations", {})
        return {
            "success": True,
            "overall_skill_coverage": jr.get("overall_skill_coverage", 0.0),
            "coverage_band": jr.get("coverage_band", "Foundational"),
            "skills_fully_met": jr.get("skills_fully_met_count", 0),
            "skills_with_gaps": jr.get("skills_with_gaps_count", 0),
            "credentials_earned": profile.get("micro_credentials", {}).get("earned_count", 0),
            "curriculum_progress": profile.get("curriculum_progress", {}).get("overall_progress", 0.0),
            "recommended_next_module": recs.get("recommended_next_module", {}).get("title"),
            "disclaimer": jr.get("disclaimer")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recalculate")
def recalculate_readiness(
    req: Optional[RecalculateRequest] = None,
    user_id: int = Depends(get_current_user_id)
):
    """
    Forces recalculation of skill coverage and career skill profile metrics.
    """
    role_id = req.target_role_id if req else None
    try:
        profile = get_career_skill_profile(user_id=user_id, target_role_id=role_id)
        return {
            "success": True,
            "message": "Career Skill Profile & Job Readiness metrics recalculated successfully.",
            "profile": profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
