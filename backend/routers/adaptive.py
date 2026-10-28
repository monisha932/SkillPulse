from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from backend.routers.auth import get_current_user_id
from backend.models import (
    AdaptiveTriggerRequest,
    ReassessmentStartRequest,
    SimulateMarketShiftRequest,
    SimulateReassessmentRequest,
    SkillAssessmentStartRequest
)
from backend.services.adaptive_engine import (
    adapt_learning_path,
    get_assessment_comparison,
    get_latest_adaptation_log,
    simulate_reassessment as engine_simulate_reassessment,
    simulate_market_demand_shift as engine_simulate_market_shift
)
from backend.routers.assessment import start_assessment

router = APIRouter(prefix="/api/adaptive", tags=["Module 8: Adaptive Learning Path & Reassessment"])

@router.get("/learning-path")
def get_adaptive_learning_path(
    target_role_id: Optional[str] = None,
    user_id: int = Depends(get_current_user_id)
):
    """
    Module 8 Core:
    Retrieves the latest adapted learning path roadmap, including:
    - Banner: 'YOUR LEARNING PATH HAS BEEN UPDATED'
    - Explanations for why the path changed
    - Before vs After assessment comparisons
    - Removed beginner modules
    - Newly added job-market skills
    - Recommended next priority skills
    """
    try:
        adapted = adapt_learning_path(user_id=user_id, target_role_id=target_role_id, trigger_reason="view_load")
        return {"success": True, "adaptive_path": adapted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_assessment_history(user_id: int = Depends(get_current_user_id)):
    """
    Module 8 Reassessment Tracking:
    Returns chronological Before vs After assessment performance comparisons.
    Example:
      Python: Before = 45%, After = 78%
      SQL:    Before = 60%, After = 85%
    Guarantees no historical results are ever deleted.
    """
    try:
        comparisons = get_assessment_comparison(user_id=user_id)
        latest_log = get_latest_adaptation_log(user_id=user_id)
        return {
            "success": True,
            "comparisons": comparisons,
            "latest_adaptation": latest_log
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-adaptation")
def trigger_adaptation(
    req: Optional[AdaptiveTriggerRequest] = None,
    user_id: int = Depends(get_current_user_id)
):
    """
    Module 8:
    Recalculates skill gaps, updates curriculum, prunes redundant modules,
    and updates priorities based on user progress and shifting market demand.
    """
    role_id = req.target_role_id if req else None
    reason = req.trigger_reason if req and req.trigger_reason else "progress_update"
    try:
        adapted = adapt_learning_path(user_id=user_id, target_role_id=role_id, trigger_reason=reason)
        return {
            "success": True,
            "message": "YOUR LEARNING PATH HAS BEEN UPDATED",
            "adaptive_path": adapted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reassess/start")
def start_reassessment(
    req: ReassessmentStartRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    Module 8:
    Launches a timed reassessment for a skill. Closes any lingering inactive sessions
    and initializes a brand-new attempt so results are tracked incrementally in history.
    """
    try:
        # Start fresh assessment attempt
        start_req = SkillAssessmentStartRequest(skill_name=req.skill_name)
        res = start_assessment(start_req, user_id=user_id)
        return {
            "success": True,
            "is_reassessment": True,
            "skill_name": req.skill_name,
            "session": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate-reassessment")
def simulate_reassessment_route(
    req: SimulateReassessmentRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    Demonstration & Verification Endpoint:
    Simulates completing a reassessment (e.g. Python: Before = 45%, After = 78%),
    preserves historical results, and dynamically adapts the curriculum path.
    """
    try:
        res = engine_simulate_reassessment(
            user_id=user_id,
            skill_name=req.skill_name,
            new_score_pct=req.new_score_pct,
            new_proficiency_level=req.new_proficiency_level
        )
        return {
            "success": True,
            "message": "YOUR LEARNING PATH HAS BEEN UPDATED",
            "adaptive_path": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate-market-shift")
def simulate_market_shift_route(
    req: SimulateMarketShiftRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    Demonstration & Verification Endpoint:
    Simulates a newly surging market skill (e.g. Docker detected at 88% demand)
    and dynamically inserts it into the user's learning path.
    """
    try:
        shift_res = engine_simulate_market_shift(
            role_id=req.role_id or "fullstack-dev",
            new_skill=req.new_skill or "Docker",
            demand_percentage=req.demand_percentage or 88.0
        )
        # Adapt user learning path
        adapted = adapt_learning_path(
            user_id=user_id,
            target_role_id=req.role_id,
            trigger_reason="market_demand_shift"
        )
        return {
            "success": True,
            "message": "YOUR LEARNING PATH HAS BEEN UPDATED",
            "market_shift": shift_res,
            "adaptive_path": adapted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
