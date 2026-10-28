from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional
from backend.routers.auth import get_current_user_id
from backend.services.gap_engine import calculate_skill_gaps

router = APIRouter(prefix="/api/skills", tags=["Skill Gap Analysis & Benchmark Engine"])

class GapAnalysisTriggerRequest(BaseModel):
    target_role_id: Optional[str] = None

@router.post("/gap-analysis")
def compute_gap_analysis(req: Optional[GapAnalysisTriggerRequest] = None, user_id: int = Depends(get_current_user_id)):
    """
    Module 5 Core:
    Compares strictly VERIFIED user skills with target job role requirements.
    Calculates mathematical skill gap vectors, priority tiers, and radar/bar coordinates.
    """
    role_id = req.target_role_id if req and req.target_role_id else None
    try:
        results = calculate_skill_gaps(user_id=user_id, target_role_id=role_id)
        return {"success": True, "gap_analysis": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill gap calculation error: {str(e)}")

@router.get("/gap-analysis")
def get_user_gap_analysis(
    role_id: Optional[str] = None,
    target_role_id: Optional[str] = None,
    user_id: int = Depends(get_current_user_id)
):
    """
    Retrieves skill gap analysis comparing verified candidate proficiencies
    against required job market skills for specified role.
    """
    selected_role = target_role_id or role_id
    if not isinstance(selected_role, str) or not selected_role.strip():
        selected_role = None
    try:
        results = calculate_skill_gaps(user_id=user_id, target_role_id=selected_role)
        return {"success": True, "gap_analysis": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve skill gaps: {str(e)}")
