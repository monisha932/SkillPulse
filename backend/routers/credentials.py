from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from backend.routers.auth import get_current_user_id
from backend.services.credential_engine import (
    get_user_credentials,
    sync_user_micro_credentials,
    get_credential_by_id,
    verify_credential_public,
    claim_credential as engine_claim_credential
)

router = APIRouter(prefix="/api/credentials", tags=["Module 7: Micro-Credential Generation"])

@router.get("")
def list_user_credentials(user_id: int = Depends(get_current_user_id)):
    """
    Retrieves candidate's earned and in-progress micro-credentials.
    """
    try:
        data = get_user_credentials(user_id)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
def generate_credentials(user_id: int = Depends(get_current_user_id)):
    """
    Synthesizes and updates micro-credentials from completed curriculum modules.
    """
    try:
        data = sync_user_micro_credentials(user_id)
        return {
            "success": True,
            "message": "Micro-credentials successfully synchronized from completed modules.",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify/{credential_id}")
def verify_credential(credential_id: str):
    """
    Public digital verification endpoint.
    No authentication required, enabling employer/evaluator verification.
    """
    try:
        result = verify_credential_public(credential_id)
        return {"success": True, "verification": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{credential_id}")
def get_credential_details(credential_id: str, user_id: int = Depends(get_current_user_id)):
    """
    Retrieves full details of a specific micro-credential record.
    """
    try:
        record = get_credential_by_id(credential_id)
        if not record:
            raise HTTPException(status_code=404, detail="Credential not found.")
        return {"success": True, "credential": record}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{credential_id}/claim")
def claim_user_credential(credential_id: str, user_id: int = Depends(get_current_user_id)):
    """
    Claims and issues an in-progress micro-credential when completion requirements are met.
    """
    try:
        record = engine_claim_credential(user_id, credential_id)
        return {
            "success": True,
            "message": f"Micro-credential '{record['title']}' claimed successfully!",
            "credential": record
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
