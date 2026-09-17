from typing import Any, Dict
from fastapi import APIRouter, Depends
from app.core.security import get_current_user, require_role

router = APIRouter()


@router.get("/auth/me", response_model=Dict[str, Any], tags=["Authentication"])
async def get_my_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Returns authenticated user's profile and workspace context.
    Requires valid Bearer JWT access token.
    """
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "role": current_user["role"],
        "organization_id": current_user["organization_id"],
        "workspace_id": current_user["workspace_id"],
    }


@router.get(
    "/admin/status",
    response_model=Dict[str, Any],
    tags=["Administration"],
    dependencies=[Depends(require_role(["ADMIN"]))],
)
async def get_admin_system_status(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Protected Admin Endpoint. Requires ADMIN role.
    """
    return {
        "status": "active",
        "admin_user_id": current_user["id"],
        "access_granted": True,
        "message": "Welcome to EMBIP System Administration",
    }
