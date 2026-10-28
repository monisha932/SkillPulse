import hashlib
import json
import secrets
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from backend.database import get_db_connection
from backend.models import (
    UserRegisterRequest,
    UserLoginRequest,
    CareerProfileRequest,
    UserResponse
)

router = APIRouter(prefix="/api", tags=["Authentication & Career Profile"])

SALT = "s5_micro_credential_salt"

def hash_password(password: str) -> str:
    return hashlib.sha256((SALT + password).encode("utf-8")).hexdigest()

# Simple in-memory session token mapping for seamless local college demo
# session_token -> user_id
ACTIVE_SESSIONS = {}

def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    """Extracts user ID from Bearer token or Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header.")
    
    token = authorization.replace("Bearer ", "").strip()
    user_id = ACTIVE_SESSIONS.get(token)
    if not user_id:
        # Check SQLite user_auth_tokens table for persistent session across reloads
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id FROM user_auth_tokens WHERE token = ?", (token,))
            row = cursor.fetchone()
            if row:
                user_id = row["user_id"]
                ACTIVE_SESSIONS[token] = user_id
        except Exception:
            pass
        finally:
            conn.close()

    if not user_id:
        # Check if token is directly an integer user ID for simple testing
        if token.isdigit():
            user_id = int(token)
        else:
            raise HTTPException(status_code=401, detail="Invalid or expired session token.")
    return user_id

@router.post("/auth/register")
def register_user(req: UserRegisterRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (req.email.lower().strip(),))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    
    pwd_hash = hash_password(req.password)
    cursor.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'student')",
        (req.name.strip(), req.email.lower().strip(), pwd_hash)
    )
    user_id = cursor.lastrowid
    token = secrets.token_hex(16)
    cursor.execute("INSERT OR REPLACE INTO user_auth_tokens (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    conn.close()
    
    ACTIVE_SESSIONS[token] = user_id
    
    return {
        "success": True,
        "message": "Account registered successfully.",
        "token": token,
        "user": {
            "id": user_id,
            "name": req.name.strip(),
            "email": req.email.lower().strip(),
            "role": "student"
        }
    }

@router.post("/auth/login")
def login_user(req: UserLoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, email, password_hash, role FROM users WHERE email = ?", (req.email.lower().strip(),))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    
    pwd_hash = hash_password(req.password)
    if user["password_hash"] != pwd_hash:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    
    token = secrets.token_hex(16)
    cursor.execute("INSERT OR REPLACE INTO user_auth_tokens (token, user_id) VALUES (?, ?)", (token, user["id"]))
    conn.commit()
    conn.close()

    ACTIVE_SESSIONS[token] = user["id"]
    
    return {
        "success": True,
        "message": "Login successful.",
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@router.get("/auth/me")
def get_me(user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"]
    }

@router.get("/market/roles")
def get_available_roles():
    """Returns all available target job roles and their real-time market demand metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_roles ORDER BY market_demand_index DESC")
    roles = [dict(row) for row in cursor.fetchall()]
    
    for r in roles:
        cursor.execute("""
        SELECT skill_name, category, importance_weight, trend_status, min_proficiency 
        FROM role_skills WHERE role_id = ?
        """, (r["role_id"],))
        r["skills"] = [dict(sk) for sk in cursor.fetchall()]
    
    conn.close()
    return {"roles": roles}

@router.post("/profile")
def save_career_profile(req: CareerProfileRequest, user_id: int = Depends(get_current_user_id)):
    """Workflow Step 2 & 3: Save user's target career role and self-declared skills."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify role_id exists
    cursor.execute("SELECT role_id FROM job_roles WHERE role_id = ?", (req.target_role_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail=f"Target role '{req.target_role_id}' does not exist.")
    
    declared_skills_list = [item.dict() for item in req.declared_skills]
    skills_json = json.dumps(declared_skills_list)
    
    cursor.execute("SELECT id FROM career_profiles WHERE user_id = ?", (user_id,))
    existing_profile = cursor.fetchone()
    
    if existing_profile:
        cursor.execute("""
        UPDATE career_profiles 
        SET target_role_id = ?, experience_level = ?, education = ?, declared_skills_json = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
        """, (req.target_role_id, req.experience_level, req.education, skills_json, user_id))
    else:
        cursor.execute("""
        INSERT INTO career_profiles (user_id, target_role_id, experience_level, education, declared_skills_json)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, req.target_role_id, req.experience_level, req.education, skills_json))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": "Career profile & declared skills saved successfully.",
        "profile": {
            "user_id": user_id,
            "target_role_id": req.target_role_id,
            "experience_level": req.experience_level,
            "education": req.education,
            "declared_skills": declared_skills_list
        }
    }

@router.get("/profile")
def get_career_profile(user_id: int = Depends(get_current_user_id)):
    """Fetches user's saved career profile, declared skills, and verified skills."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT cp.*, jr.role_title, jr.domain, jr.market_demand_index, jr.demand_status, jr.avg_salary
    FROM career_profiles cp
    JOIN job_roles jr ON cp.target_role_id = jr.role_id
    WHERE cp.user_id = ?
    """, (user_id,))
    profile_row = cursor.fetchone()
    
    if not profile_row:
        conn.close()
        return {"has_profile": False, "profile": None}
    
    profile_dict = dict(profile_row)
    profile_dict["declared_skills"] = json.loads(profile_dict.get("declared_skills_json", "[]"))
    del profile_dict["declared_skills_json"]

    # Query verified skills for this user
    cursor.execute("""
    SELECT skill_name, score_pct, proficiency_level, declared_level, comparison_status, verified_at
    FROM verified_skills
    WHERE user_id = ?
    ORDER BY verified_at DESC
    """, (user_id,))
    v_rows = cursor.fetchall()
    profile_dict["verified_skills"] = [dict(v) for v in v_rows]
    conn.close()
    
    return {"has_profile": True, "profile": profile_dict}
