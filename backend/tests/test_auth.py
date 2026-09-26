import os
import pytest
from unittest.mock import patch
import jwt
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def create_test_jwt(user_id: str, email: str, role: str) -> str:
    """Helper function to generate test JWT payloads."""
    payload = {
        "sub": user_id,
        "email": email,
        "user_metadata": {
            "role": role,
            "org_id": "org-test-123",
            "workspace_id": "ws-test-456",
        },
    }
    return jwt.encode(payload, "secret-key", algorithm="HS256")


def test_unauthenticated_request_fails():
    """Unauthenticated request must return 401 Unauthorized."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert "detail" in response.json()


def test_invalid_token_request_fails():
    """Request with invalid Authorization header format must return 401."""
    headers = {"Authorization": "Bearer invalid.token.value"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


def test_authenticated_user_profile():
    """Authenticated request returns user profile and workspace context."""
    user_id = "usr-12345678"
    token = create_test_jwt(user_id, "analyst@company.com", "ANALYST")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "analyst@company.com"
    assert data["role"] == "ANALYST"
    assert data["organization_id"] == "org-test-123"
    assert data["workspace_id"] == "ws-test-456"
    assert "token" not in data
    assert "secret" not in data


def test_analyst_role_access_to_admin_endpoint_forbidden():
    """ANALYST role accessing admin-only endpoint must return 403 Forbidden."""
    token = create_test_jwt("usr-analyst", "analyst@company.com", "ANALYST")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/admin/status", headers=headers)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_admin_role_access_to_admin_endpoint_success():
    """ADMIN role accessing admin-only endpoint must return 200 OK."""
    token = create_test_jwt("usr-admin", "admin@company.com", "ADMIN")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/admin/status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["access_granted"] is True
    assert data["admin_user_id"] == "usr-admin"


def test_production_jwt_valid_secret_accepted():
    """Verify production JWT with valid configured secret enables signature verification and accepts valid token."""
    prod_secret = "super-secret-production-key-value-12345"
    payload = {
        "sub": "usr-prod-1",
        "email": "prod@company.com",
        "user_metadata": {"role": "ADMIN", "workspace_id": "ws-prod-123"},
    }
    valid_token = jwt.encode(payload, prod_secret, algorithm="HS256")

    with patch.dict(os.environ, {"ENVIRONMENT": "production", "SUPABASE_JWT_SECRET": prod_secret}):
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == "usr-prod-1"
        assert response.json()["workspace_id"] == "ws-prod-123"


def test_production_jwt_missing_secret_rejected():
    """Verify production environment without JWT secret rejects authentication without falling back to unsigned decoding."""
    payload = {
        "sub": "usr-prod-2",
        "email": "prod2@company.com",
        "user_metadata": {"role": "ADMIN", "workspace_id": "ws-prod-123"},
    }
    token = jwt.encode(payload, "some-key", algorithm="HS256")

    env_mock = {"ENVIRONMENT": "production"}
    with patch.dict(os.environ, env_mock, clear=True):
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        assert "JWT secret configuration error in production" in response.json()["detail"]


def test_production_jwt_placeholder_secret_rejected():
    """Verify production environment with template placeholder secret rejects authentication."""
    payload = {
        "sub": "usr-prod-3",
        "email": "prod3@company.com",
        "user_metadata": {"role": "ADMIN", "workspace_id": "ws-prod-123"},
    }
    token = jwt.encode(payload, "your-supabase-jwt-secret", algorithm="HS256")

    with patch.dict(os.environ, {"ENVIRONMENT": "production", "SUPABASE_JWT_SECRET": "your-supabase-jwt-secret"}):
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        assert "JWT secret configuration error in production" in response.json()["detail"]


def test_invalid_jwt_signature_rejected():
    """Verify token signed with wrong secret is rejected."""
    prod_secret = "correct-secret-key-12345"
    wrong_secret = "wrong-secret-key-99999"
    payload = {
        "sub": "usr-prod-4",
        "email": "prod4@company.com",
        "user_metadata": {"role": "ADMIN", "workspace_id": "ws-prod-123"},
    }
    bad_token = jwt.encode(payload, wrong_secret, algorithm="HS256")

    with patch.dict(os.environ, {"ENVIRONMENT": "production", "SUPABASE_JWT_SECRET": prod_secret}):
        headers = {"Authorization": f"Bearer {bad_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        assert "Invalid authentication token" in response.json()["detail"]


def test_missing_workspace_id_rejected():
    """Verify JWT payload missing workspace_id is rejected with 401 Unauthorized without default fallback."""
    payload = {
        "sub": "usr-no-ws",
        "email": "nows@company.com",
        "user_metadata": {"role": "ANALYST"},
    }
    token = jwt.encode(payload, "secret-key", algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    assert "missing valid workspace_id claim" in response.json()["detail"]


def test_empty_workspace_id_rejected():
    """Verify JWT payload with blank/empty workspace_id is rejected with 401 Unauthorized."""
    payload = {
        "sub": "usr-empty-ws",
        "email": "emptyws@company.com",
        "user_metadata": {"role": "ANALYST", "workspace_id": "   "},
    }
    token = jwt.encode(payload, "secret-key", algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    assert "missing valid workspace_id claim" in response.json()["detail"]


def test_valid_workspace_id_accepted():
    """Verify token with valid explicit workspace_id is accepted and populates user context correctly."""
    payload = {
        "sub": "usr-valid-ws",
        "email": "validws@company.com",
        "user_metadata": {"role": "MANAGER", "workspace_id": "00000000-0000-4000-a000-000000000002"},
    }
    token = jwt.encode(payload, "secret-key", algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["workspace_id"] == "00000000-0000-4000-a000-000000000002"
    assert data["role"] == "MANAGER"
