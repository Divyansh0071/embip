import os
from typing import Any, Dict, List, Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings

# HTTP Bearer Scheme
security_scheme = HTTPBearer(auto_error=False)


def decode_supabase_jwt(token: str) -> Dict[str, Any]:
    """
    Decodes and verifies a Supabase / Application JWT token.
    Enforces signature verification in production environments when secret key is configured,
    and checks token expiration (exp) and subject claims (sub).
    """
    env = (os.getenv("ENVIRONMENT") or getattr(settings, "ENVIRONMENT", "development")).lower()
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET") or os.getenv("SECRET_KEY") or getattr(settings, "SECRET_KEY", None)

    is_placeholder = bool(
        not jwt_secret
        or "your-" in jwt_secret
        or jwt_secret == "sk-proj-placeholder"
    )

    if env == "production":
        if is_placeholder:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: JWT secret configuration error in production.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            payload = jwt.decode(
                token,
                key=jwt_secret,
                algorithms=["HS256", "RS256"],
                options={"verify_signature": True, "verify_exp": True},
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Development / Testing mode fallback
    try:
        if not is_placeholder:
            payload = jwt.decode(
                token,
                key=jwt_secret,
                algorithms=["HS256", "RS256"],
                options={"verify_signature": True, "verify_exp": True},
            )
        else:
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": True},
                algorithms=["HS256", "RS256"],
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Dict[str, Any]:
    """
    FastAPI dependency that extracts and validates the Bearer access token.
    Returns authenticated user context dict.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_supabase_jwt(token)

    user_id = payload.get("sub")
    email = payload.get("email") or payload.get("user_metadata", {}).get("email")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing valid user subject ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract role from metadata, app_metadata, or custom claims
    user_metadata = payload.get("user_metadata", {})
    app_metadata = payload.get("app_metadata", {})

    role = (
        user_metadata.get("role")
        or app_metadata.get("role")
        or payload.get("role")
        or "Analyst"
    )

    org_id = (
        user_metadata.get("org_id")
        or app_metadata.get("org_id")
        or payload.get("org_id")
        or "default-org-id"
    )

    # Require explicit workspace_id claim from trusted JWT context
    workspace_id = (
        user_metadata.get("workspace_id")
        or app_metadata.get("workspace_id")
        or payload.get("workspace_id")
    )

    if not workspace_id or not str(workspace_id).strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing valid workspace_id claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": user_id,
        "email": email or f"user_{user_id[:8]}@embip.internal",
        "role": str(role).upper(),
        "organization_id": org_id,
        "workspace_id": str(workspace_id).strip(),
    }


def require_role(allowed_roles: List[str]):
    """
    FastAPI dependency factory enforcing RBAC roles.
    Raises 403 Forbidden if user's role is not in allowed_roles.
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get("role", "").upper()
        allowed_uppercase = [r.upper() for r in allowed_roles]

        if user_role not in allowed_uppercase:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {allowed_roles}. Your role is '{user_role}'.",
            )
        return current_user

    return role_checker
