from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any

# Authentication Models
class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6)

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

# Career Profile Models
class DeclaredSkillItem(BaseModel):
    skill_name: str
    self_rating: str = "Intermediate" # Beginner, Intermediate, Advanced

class CareerProfileRequest(BaseModel):
    target_role_id: str
    experience_level: str = "Fresher"
    education: str = "B.E. Computer Science & Engineering"
    declared_skills: List[DeclaredSkillItem] = []

# Module 2 Assessment Models
class SkillAssessmentStartRequest(BaseModel):
    skill_name: Optional[str] = "Python"

class AssessmentStartRequest(BaseModel):
    user_id: Optional[int] = None
    skill_name: Optional[str] = "Python"

class SaveAnswerRequest(BaseModel):
    session_token: str
    question_num: int
    selected_option: Optional[int] = None
    submitted_code: Optional[str] = None

class SubmitAnswerRequest(BaseModel):
    session_token: str
    question_id: Optional[int] = None
    question_num: Optional[int] = None
    question_type: Optional[str] = None # 'mcq' or 'coding'
    selected_option: Optional[int] = None
    submitted_code: Optional[str] = None

class RunCodeRequest(BaseModel):
    session_token: str
    question_num: int
    code: str

class CodeRunRequest(BaseModel):
    code: str
    function_name: str
    test_cases: List[Dict[str, Any]]

class ViolationReportRequest(BaseModel):
    session_token: str
    violation_type: str # 'tab_switch', 'window_blur', 'copy_attempt', 'paste_attempt', 'context_menu'
    details: Optional[str] = None

class ViolationRequest(BaseModel):
    session_token: str
    violation_type: str
    details: Optional[str] = None

class AssessmentCompleteRequest(BaseModel):
    session_token: str

CompleteAssessmentRequest = AssessmentCompleteRequest

# Skill Gap & Curriculum Models
class SkillGapRequest(BaseModel):
    user_id: int
    target_role_id: str

class CurriculumGenerateRequest(BaseModel):
    user_id: int
    target_role_id: str

class ModuleProgressUpdateRequest(BaseModel):
    module_id: int
    progress_pct: int
    status: str # 'pending', 'in_progress', 'completed'

class CurriculumAdaptRequest(BaseModel):
    user_id: int
    target_role_id: str

# Module 8: Adaptive Learning Path Models
class ReassessmentStartRequest(BaseModel):
    skill_name: str
    force_new: Optional[bool] = True

class AdaptiveTriggerRequest(BaseModel):
    target_role_id: Optional[str] = None
    trigger_reason: Optional[str] = "manual_trigger" # 'reassessment', 'module_completed', 'market_demand_shift', 'proficiency_change'

class SimulateMarketShiftRequest(BaseModel):
    role_id: Optional[str] = "fullstack-dev"
    new_skill: Optional[str] = "Docker"
    demand_percentage: Optional[float] = 88.0

class SimulateReassessmentRequest(BaseModel):
    skill_name: str = "Python"
    new_score_pct: float = 78.0
    new_proficiency_level: Optional[str] = None # Auto-derived if None
