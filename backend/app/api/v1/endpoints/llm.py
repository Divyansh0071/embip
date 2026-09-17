"""
FastAPI Endpoint for LLM Service Health & Configuration Diagnostics.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends
from app.ai.llm.service import llm_service
from app.core.security import get_current_user

router = APIRouter(prefix="/llm", tags=["LLM Service"])


@router.get("/status", response_model=Dict[str, Any])
async def get_llm_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get safe LLM service configuration diagnostics.
    Does NOT return secret keys or consume external API credits.
    """
    diagnostics = llm_service.get_diagnostics()
    return {
        "status": diagnostics["status"],
        "provider": diagnostics["provider"],
        "default_model": diagnostics["default_model"],
        "api_key_configured": diagnostics["api_key_configured"],
        "registered_providers": diagnostics["registered_providers"],
        "max_retries": diagnostics["max_retries"],
        "timeout_seconds": diagnostics["timeout_seconds"],
    }
