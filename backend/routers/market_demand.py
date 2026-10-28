import json
from typing import Optional, List, Union
from fastapi import APIRouter, HTTPException, Query, Header, Depends, UploadFile, File, Form
from pydantic import BaseModel
from backend.database import get_db_connection
from backend.routers.auth import get_current_user_id
from backend.services.nlp_demand import extract_and_analyze_market_skills
from backend.services.market_analyzer import (
    analyze_target_role_skills,
    get_market_filters,
    import_job_postings,
    import_csv_postings,
    seed_default_job_postings_if_empty
)

router = APIRouter(prefix="/api/market", tags=["Job Market Skill Demands & NLP Analytics"])

# Pydantic Schemas
class JobPostingCreate(BaseModel):
    job_title: str
    target_role_id: str
    company: str
    industry: Optional[str] = "Technology"
    location: Optional[str] = "Remote"
    required_skills: Union[List[str], str]
    experience_level: Optional[str] = "Mid Level"
    posting_date: Optional[str] = None
    data_source: Optional[str] = "API Ingestion"

class JsonImportRequest(BaseModel):
    postings: List[Union[JobPostingCreate, dict]]
    data_source: Optional[str] = "JSON Batch Import"

class CsvImportRequest(BaseModel):
    csv_content: str
    data_source: Optional[str] = "CSV Batch Import"

def get_optional_user_id(authorization: Optional[str] = Header(None)) -> Optional[int]:
    if not authorization:
        return None
    try:
        return get_current_user_id(authorization)
    except HTTPException:
        return None

@router.get("/analytics")
def get_market_analytics(role_id: Optional[str] = Query(None)):
    """Workflow Step 10: Live NLP skill extraction, frequency scoring, and market demand analytics."""
    try:
        analytics = extract_and_analyze_market_skills(role_id)
        return {"success": True, "analytics": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skill-demand")
def get_skill_demand(
    target_role_id: Optional[str] = None,
    industry: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    user_id: Optional[int] = Depends(get_optional_user_id)
):
    """
    Module 4 Core Endpoint:
    Returns comprehensive job-market skill requirements for target role:
    - Most frequently requested skills & exact frequencies
    - Skill demand percentages
    - Industry, location, experience distributions
    - Trending skills & authentic data sources
    """
    try:
        resolved_role_id = target_role_id if isinstance(target_role_id, str) and target_role_id.strip() else None
        resolved_industry = industry if isinstance(industry, str) and industry.strip() else None
        resolved_location = location if isinstance(location, str) and location.strip() else None
        resolved_exp = experience_level if isinstance(experience_level, str) and experience_level.strip() else None

        if not resolved_role_id and user_id:
            # Look up target role in career_profiles
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT target_role_id FROM career_profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row and row["target_role_id"]:
                resolved_role_id = row["target_role_id"]

        if not resolved_role_id:
            resolved_role_id = "fullstack-dev"

        data = analyze_target_role_skills(
            target_role_id=resolved_role_id,
            industry=resolved_industry,
            location=resolved_location,
            experience_level=resolved_exp
        )
        return {
            "success": True,
            **data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze market demand: {str(e)}")

@router.get("/filters")
def get_filters(target_role_id: Optional[str] = None):
    """Returns available industries, locations, and experience levels for filtering."""
    try:
        role_param = target_role_id if isinstance(target_role_id, str) else None
        filters = get_market_filters(role_param)
        return {"success": True, "filters": filters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch filters: {str(e)}")

@router.post("/jobs")
def create_job_posting(posting: JobPostingCreate):
    """Ingests a single job posting into the market demand analyzer."""
    try:
        p_dict = posting.model_dump() if hasattr(posting, "model_dump") else posting.dict()
        result = import_job_postings([p_dict], data_source=posting.data_source or "API Ingestion")
        if not result["success"]:
            raise HTTPException(status_code=400, detail="Failed to import job posting.")
        return {"success": True, "message": "Job posting imported successfully.", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-json")
def import_json_data(req: Union[JsonImportRequest, List[dict]]):
    """Batch imports job postings via JSON."""
    try:
        if isinstance(req, list):
            postings = req
            source = "JSON Batch Import"
        else:
            postings = [
                p.model_dump() if hasattr(p, "model_dump") else p.dict() if hasattr(p, "dict") else p
                for p in req.postings
            ]
            source = req.data_source or "JSON Batch Import"

        result = import_job_postings(postings, data_source=source)
        return {
            "success": result["success"],
            "imported_count": result["imported_count"],
            "failed_count": result.get("failed_count", 0),
            "errors": result.get("errors", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-csv")
def import_csv_data(req: CsvImportRequest):
    """Batch imports job postings from CSV content."""
    try:
        result = import_csv_postings(req.csv_content, data_source=req.data_source or "CSV Batch Import")
        return {
            "success": result["success"],
            "imported_count": result["imported_count"],
            "failed_count": result.get("failed_count", 0),
            "errors": result.get("errors", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_job_market_file(
    file: UploadFile = File(...),
    data_source: Optional[str] = Form(None)
):
    """Admin upload endpoint supporting CSV and JSON datasets."""
    filename = file.filename.lower()
    content_bytes = await file.read()
    try:
        content_str = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content_str = content_bytes.decode("latin-1")

    source_label = data_source or f"Uploaded File ({file.filename})"

    if filename.endswith(".csv"):
        result = import_csv_postings(content_str, data_source=source_label)
    elif filename.endswith(".json"):
        try:
            parsed = json.loads(content_str)
            if isinstance(parsed, list):
                postings = parsed
            elif isinstance(parsed, dict) and "postings" in parsed:
                postings = parsed["postings"]
            else:
                postings = [parsed]
            result = import_job_postings(postings, data_source=source_label)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON file format: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a .csv or .json file.")

    return {
        "success": result["success"],
        "filename": file.filename,
        "imported_count": result["imported_count"],
        "failed_count": result.get("failed_count", 0),
        "errors": result.get("errors", [])
    }
