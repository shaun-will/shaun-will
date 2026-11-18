# FastAPI: JWT authentication, tenant isolation and role-based access

A compact, original engineering demonstration built for a public portfolio. It is **not** source code from an Atelier Williams Studio client project or from HOUSEBOARD.

## What it illustrates

- Verifies signed JWT bearer tokens with explicit algorithm, issuer, audience and expiry checks.
- Takes tenant identity and user role from validated token claims, **not** untrusted request parameters.
- Separates organisations by tenant ID; a cross-tenant resource lookup returns 404.
- Allows viewers to read and editors/admins to create or update records.
- Rejects unauthenticated and unauthorised requests with clear status codes.
- Includes automated tests for isolation, permissions, invalid tokens and normal usage.

## Run locally

Python 3.11+ is required.

```bash
cd showcase/fastapi-rbac
python -m venv .venv
# Activate your virtual environment
python -m pip install -e ".[dev]"
```

Set a local-only signing secret (do not commit real credentials):

```bash
export APP_JWT_SECRET="generate-a-long-random-secret-for-local-testing"
# PowerShell alternative: $env:APP_JWT_SECRET="generate-a-long-random-secret-for-local-testing"
```

Run the tests and API:

```bash
python -m pytest -q
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for API documentation. Tests construct their own short-lived JWTs; no real authentication account is needed. For manual API access, use a signed JWT with issuer `portfolio-demo`, audience `tenant-api`, and `sub`, `tenant_id`, `role`, and `exp` claims.

## API surface

| Route | Viewer | Editor | Admin |
| --- | --- | --- | --- |
| `GET /documents` | Own tenant | Own tenant | Own tenant |
| `GET /documents/{id}` | Own tenant | Own tenant | Own tenant |
| `POST /documents` | Denied | Own tenant | Own tenant |
| `PATCH /documents/{id}` | Denied | Own tenant | Own tenant |

## Security and scope

This is a **policy and API demonstration**, not a production service. Records are stored in memory, seeded with fictional examples and reset when the process restarts. The JWT signing key is provided by an environment variable, and the test secret is for test execution only. Production use would require trusted identity-provider issuance, asymmetric JWT validation or managed key rotation, persistence and migrations, audit logging, throttling, monitoring and deployment hardening. Never reuse a demo secret in production.

### Tech stack

Python · FastAPI · Pydantic · PyJWT · pytest · GitHub Actions
