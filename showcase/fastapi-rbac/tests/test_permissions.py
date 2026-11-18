"""Security regression tests for the public FastAPI demo."""
from __future__ import annotations

import os
import time

import jwt
from fastapi.testclient import TestClient

from app.main import app, documents

TEST_SECRET = "TEST-ONLY-not-a-production-key-change-me-before-use"
os.environ["APP_JWT_SECRET"] = TEST_SECRET
client = TestClient(app)


def token(tenant: str, role: str = "viewer", **overrides: object) -> str:
    now = int(time.time())
    claims: dict[str, object] = {
        "sub": "sample-user",
        "tenant_id": tenant,
        "role": role,
        "iss": "portfolio-demo",
        "aud": "tenant-api",
        "iat": now,
        "exp": now + 600,
    }
    claims.update(overrides)
    return jwt.encode(claims, TEST_SECRET, algorithm="HS256")


def headers(tenant: str, role: str = "viewer", **overrides: object) -> dict[str, str]:
    return {"Authorization": f"Bearer {token(tenant, role, **overrides)}"}


def test_missing_token_is_rejected() -> None:
    response = client.get("/documents")
    assert response.status_code == 401


def test_invalid_signature_is_rejected() -> None:
    response = client.get("/documents", headers={"Authorization": "Bearer invalid.token.value"})
    assert response.status_code == 401


def test_expired_token_is_rejected() -> None:
    response = client.get("/documents", headers=headers("tenant-a", exp=int(time.time()) - 60))
    assert response.status_code == 401


def test_only_own_tenant_records_are_listed() -> None:
    response = client.get("/documents", headers=headers("tenant-a"))
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["demo-a"]


def test_cross_tenant_document_is_not_disclosed() -> None:
    response = client.get("/documents/demo-b", headers=headers("tenant-a", "admin"))
    assert response.status_code == 404


def test_viewer_cannot_create_or_update() -> None:
    payload = {"title": "Demo", "body": "For local testing"}
    assert client.post("/documents", headers=headers("tenant-a"), json=payload).status_code == 403
    assert client.patch("/documents/demo-a", headers=headers("tenant-a"), json=payload).status_code == 403


def test_editor_create_is_scoped_to_claimed_tenant() -> None:
    payload = {"title": "New record", "body": "Demo only"}
    response = client.post("/documents", headers=headers("tenant-b", "editor"), json=payload)
    assert response.status_code == 201
    doc = response.json()
    assert doc["tenant_id"] == "tenant-b"
    assert client.get(f"/documents/{doc['id']}", headers=headers("tenant-a", "admin")).status_code == 404
    # Reset mutable demo storage to keep tests deterministic.
    documents.pop(doc["id"], None)


def test_admin_can_update_same_tenant() -> None:
    payload = {"title": "Reviewed record", "body": "Updated text"}
    original = documents["demo-a"]
    try:
        response = client.patch("/documents/demo-a", headers=headers("tenant-a", "admin"), json=payload)
        assert response.status_code == 200
        assert response.json()["title"] == "Reviewed record"
    finally:
        documents["demo-a"] = original


def test_patch_preserves_omitted_fields() -> None:
    original = documents["demo-a"]
    try:
        response = client.patch(
            "/documents/demo-a",
            headers=headers("tenant-a", "editor"),
            json={"title": "Updated title only"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated title only"
        assert response.json()["body"] == original.body
    finally:
        documents["demo-a"] = original


def test_patch_rejects_null_field() -> None:
    response = client.patch(
        "/documents/demo-a",
        headers=headers("tenant-a", "editor"),
        json={"body": None},
    )
    assert response.status_code == 422


def test_caller_cannot_override_tenant_with_request_body() -> None:
    response = client.post(
        "/documents",
        headers=headers("tenant-a", "editor"),
        json={"title": "Scoped", "body": "Example", "tenant_id": "tenant-b"},
    )
    assert response.status_code == 201
    doc = response.json()
    assert doc["tenant_id"] == "tenant-a"
    documents.pop(doc["id"], None)
