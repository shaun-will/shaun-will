"""Original portfolio example of JWT-backed tenant isolation and RBAC."""
from __future__ import annotations

import os
from typing import Literal
from uuid import uuid4

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pydantic import BaseModel, Field, ValidationError, field_validator

app = FastAPI(title="Tenant-safe document API (demo)", version="0.1.0")
bearer = HTTPBearer(auto_error=False)

Role = Literal["viewer", "editor", "admin"]


class Principal(BaseModel):
    sub: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    role: Role


class DocumentInput(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=5000)


class Document(DocumentInput):
    id: str
    tenant_id: str


class DocumentPatch(BaseModel):
    """Partial changes: omitted fields remain unchanged; explicit null is rejected."""
    title: str | None = Field(default=None, min_length=1, max_length=120)
    body: str | None = Field(default=None, min_length=1, max_length=5000)

    @field_validator("title", "body")
    @classmethod
    def reject_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("A provided field cannot be null")
        return value


# Illustrative in-memory records. Do not use an in-memory store for production.
documents: dict[str, Document] = {
    "demo-a": Document(id="demo-a", tenant_id="tenant-a", title="Sample A", body="Fictional record"),
    "demo-b": Document(id="demo-b", tenant_id="tenant-b", title="Sample B", body="Fictional record"),
}


def invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Principal:
    if credentials is None:
        raise invalid_credentials()

    secret = os.getenv("APP_JWT_SECRET")
    if not secret:
        # A missing secret is a configuration failure, never a reason to skip authentication.
        raise RuntimeError("APP_JWT_SECRET must be configured before serving requests")

    try:
        claims = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=["HS256"],
            issuer="portfolio-demo",
            audience="tenant-api",
            options={"require": ["sub", "tenant_id", "role", "exp", "iat", "iss", "aud"]},
        )
        return Principal.model_validate(claims)
    except (InvalidTokenError, ValidationError, TypeError, ValueError) as exc:
        raise invalid_credentials() from exc


def require_editor(principal: Principal = Depends(current_principal)) -> Principal:
    if principal.role not in ("editor", "admin"):
        raise HTTPException(status_code=403, detail="Write permission required")
    return principal


def visible_document(document_id: str, principal: Principal) -> Document:
    doc = documents.get(document_id)
    if doc is None or doc.tenant_id != principal.tenant_id:
        # Avoid revealing whether a different tenant owns the record.
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/documents", response_model=list[Document])
def list_documents(principal: Principal = Depends(current_principal)) -> list[Document]:
    return sorted(
        [doc for doc in documents.values() if doc.tenant_id == principal.tenant_id],
        key=lambda doc: doc.id,
    )


@app.get("/documents/{document_id}", response_model=Document)
def get_document(document_id: str, principal: Principal = Depends(current_principal)) -> Document:
    return visible_document(document_id, principal)


@app.post("/documents", response_model=Document, status_code=201)
def create_document(
    payload: DocumentInput,
    principal: Principal = Depends(require_editor),
) -> Document:
    doc = Document(id=str(uuid4()), tenant_id=principal.tenant_id, **payload.model_dump())
    documents[doc.id] = doc
    return doc


@app.patch("/documents/{document_id}", response_model=Document)
def update_document(
    document_id: str,
    payload: DocumentPatch,
    principal: Principal = Depends(require_editor),
) -> Document:
    current = visible_document(document_id, principal)
    changes = payload.model_dump(exclude_unset=True)
    updated = Document.model_validate({**current.model_dump(), **changes})
    documents[document_id] = updated
    return updated
