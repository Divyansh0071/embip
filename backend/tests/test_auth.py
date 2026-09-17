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
