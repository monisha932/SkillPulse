from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from backend.routers.auth import get_current_user_id
from backend.services.curriculum_engine import (
    generate_personalized_curriculum,
    get_active_user_curriculum,
    update_module_progress as engine_update_progress
)

router = APIRouter(prefix="/api/curriculum", tags=["Micro-Credential Curriculum & Learning Pathways"])

class CurriculumRequest(BaseModel):
    target_role_id: Optional[str] = None
    weekly_hours: Optional[int] = 10
    preferred_difficulty: Optional[str] = "Adaptive"
    learning_preferences: Optional[str] = "Hands-on Projects & Coding"

class ModuleProgressUpdate(BaseModel):
    module_id: int
    progress_pct: int
    status: str # 'pending', 'in_progress', 'completed'

@router.post("/generate")
def create_curriculum(req: Optional[CurriculumRequest] = None, user_id: int = Depends(get_current_user_id)):
    """Workflow Step 14 & 15: Synthesizes personalized micro-credential curriculum."""
    role_id = req.target_role_id if req else None
    weekly_hours = req.weekly_hours if req and req.weekly_hours else 10
    preferred_difficulty = req.preferred_difficulty if req and req.preferred_difficulty else "Adaptive"
    learning_preferences = req.learning_preferences if req and req.learning_preferences else "Hands-on Projects & Coding"
    try:
        curriculum = generate_personalized_curriculum(
            user_id=user_id,
            target_role_id=role_id,
            weekly_hours=weekly_hours,
            preferred_difficulty=preferred_difficulty,
            learning_preferences=learning_preferences
        )
        return {"success": True, "curriculum": curriculum}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def get_user_curriculum(target_role_id: Optional[str] = None, user_id: int = Depends(get_current_user_id)):
    """Retrieves active curriculum or generates one if not yet synthesized."""
    try:
        curriculum = get_active_user_curriculum(user_id=user_id, target_role_id=target_role_id)
        return {"success": True, "curriculum": curriculum}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/module/progress")
def update_progress(req: ModuleProgressUpdate, user_id: int = Depends(get_current_user_id)):
    """Workflow Step 16: Updates candidate learning progress on a curriculum module and auto-unlocks dependent modules."""
    try:
        res = engine_update_progress(
            user_id=user_id,
            module_id=req.module_id,
            progress_pct=req.progress_pct,
            status=req.status
        )
        return {"success": True, "module_id": res["module_id"], "status": res["status"], "progress_pct": res["progress_pct"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adapt")
def adapt_curriculum(req: Optional[CurriculumRequest] = None, user_id: int = Depends(get_current_user_id)):
    """Workflow Step 17: Adapts the curriculum roadmap dynamically based on progress and shifting market demand."""
    role_id = req.target_role_id if req else None
    weekly_hours = req.weekly_hours if req and req.weekly_hours else 10
    preferred_difficulty = req.preferred_difficulty if req and req.preferred_difficulty else "Adaptive"
    learning_preferences = req.learning_preferences if req and req.learning_preferences else "Hands-on Projects & Coding"
    try:
        adapted_curr = generate_personalized_curriculum(
            user_id=user_id,
            target_role_id=role_id,
            weekly_hours=weekly_hours,
            preferred_difficulty=preferred_difficulty,
            learning_preferences=learning_preferences
        )
        return {
            "success": True,
            "message": "Curriculum dynamically adapted to reflect latest learning progress and market demand signals!",
            "curriculum": adapted_curr
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
