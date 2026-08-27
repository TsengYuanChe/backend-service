# Backend Service Overview

## Project Purpose

This repository contains a small reusable backend service for personal projects. Its current implementation provides a FastAPI application, a PostgreSQL connection, and user authentication with hashed passwords and JWT access tokens.

The stated longer-term direction is to collect statistics and events such as website visits and email tracking activity, and to expose protected statistics APIs to an `/admin` frontend. The PostgreSQL database is currently intended to be hosted on Google Cloud SQL while the application runs locally. Containerization, deployment to Google Cloud Run, and a possible later move to AWS are future goals; none of their supporting infrastructure is currently present in this repository. The current database configuration uses ordinary PostgreSQL connection parameters and is not tied to a cloud-provider SDK.

## Current Technology Stack

- Python
- FastAPI 0.141.1 and Starlette 1.6.0 for the HTTP application
- Uvicorn 0.52.4 as the ASGI server dependency
- PostgreSQL accessed through SQLAlchemy 2.0.52
- Psycopg 3.3.4 as the PostgreSQL driver (`postgresql+psycopg`)
- Pydantic 2.13.4 for request and response schemas
- PyJWT 2.13.0 for JWT encoding and validation
- `pwdlib` 0.3.1 with its recommended password hasher; the installed dependencies include Argon2 support
- `python-dotenv` 1.2.3 for loading local environment variables

All direct and transitive Python packages are pinned in `requirements.txt`. The repository does not currently contain a Python project metadata file or a separate development dependency definition.

## Current Features

The implemented functionality is:

- A FastAPI application titled `Backend Service`, version `0.1.0`
- A basic root health-style response
- A database connectivity diagnostic that queries the connected database name and PostgreSQL version
- A SQLAlchemy engine and session factory for PostgreSQL
- A SQLAlchemy `User` model mapped to the `users` table
- Password hashing and verification helpers
- Account-name/password login
- JWT access-token generation with an eight-hour expiration
- Bearer-token decoding and active-user lookup for protected routes
- A protected endpoint that returns the current user's public account fields
- An interactive command-line script for creating a user with a hashed password
- FastAPI's default OpenAPI schema and Swagger UI/ReDoc interfaces

There are currently no statistics, website-visit, email-tracking, or admin-data APIs or models.

## Authentication Flow

1. A client sends an `account_name` and `password` to `POST /auth/login`. The request shape is defined by `LoginRequest` in `app/schemas/auth.py`.
2. The handler in `app/routers/auth.py` opens a `SessionLocal` SQLAlchemy session and selects a `User` by `account_name`.
3. The handler rejects a missing or inactive user with HTTP 401, then calls `verify_password()` from `app/core/security.py` to compare the submitted password with the stored hash.
4. On success, `create_access_token()` creates a JWT whose `sub` claim is the user's ID and whose `exp` claim is eight hours after issuance. It signs the token with `JWT_SECRET` and the configured `JWT_ALGORITHM`.
5. The response uses `TokenResponse` and contains the access token plus the token type `bearer`.
6. For a protected request such as `GET /auth/me`, the client sends the token in the `Authorization: Bearer <token>` header.
7. `get_current_user()` in `app/dependencies/auth.py` uses FastAPI's `HTTPBearer`, calls `decode_access_token()`, and reads the user ID from the JWT `sub` claim.
8. The dependency queries the database for that user and rejects invalid or expired tokens, missing users, and inactive users with HTTP 401. It detaches the loaded user from the session before returning it to the route.
9. `GET /auth/me` returns the fields defined by `UserResponse`: `id`, `name`, `account_name`, and `is_active`. The password hash is not part of the response schema.

## Database

`app/database.py` loads environment variables with `python-dotenv` and constructs a SQLAlchemy URL in this form:

```text
postgresql+psycopg://<user>:<password>@<host>:<port>/<database>
```

It creates a module-level SQLAlchemy `engine` and a `SessionLocal` session factory bound to that engine. Authentication routes and dependencies create short-lived sessions with context managers. The `/db-test` endpoint and the user-creation script use the engine directly.

The only table represented by a model in the repository is `users`, defined in `app/models/user.py` with these columns:

- `id`: `BIGINT` primary key
- `name`: required string, maximum length 100
- `account_name`: required, unique string, maximum length 100
- `password_hash`: required string, maximum length 255
- `is_active`: required boolean with a Python-side default of `True`
- `created_at`: required timezone-aware timestamp with a database-side current-time default

The model module defines its own SQLAlchemy declarative `Base`. No schema-creation call, migration framework, or migration files are present, so the repository does not document how the existing table was initially created or is evolved.

The connection is controlled by `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD`. Although the project currently targets a PostgreSQL instance on Google Cloud SQL, the code uses a standard host/port PostgreSQL connection and contains no Cloud SQL-specific connector or provider-specific database code.

## API Endpoints

### Application-defined endpoints

| Method | Path | Purpose | Authentication |
| --- | --- | --- | --- |
| `GET` | `/` | Returns `{"status": "ok"}` as a basic application response. | No |
| `GET` | `/db-test` | Executes `SELECT current_database(), version()` and returns the connected database name and server version. | No |
| `POST` | `/auth/login` | Verifies account credentials and returns a JWT bearer access token. | No |
| `GET` | `/auth/me` | Returns the active user identified by the supplied bearer token. | Yes |

`/db-test` is publicly accessible in the current implementation and exposes database identification/version information.

### FastAPI-provided endpoints

Because the application does not disable FastAPI's defaults, it also provides:

| Method | Path | Purpose | Authentication |
| --- | --- | --- | --- |
| `GET` | `/openapi.json` | OpenAPI schema | No |
| `GET` | `/docs` | Swagger UI | No |
| `GET` | `/docs/oauth2-redirect` | Swagger UI OAuth2 redirect helper | No |
| `GET` | `/redoc` | ReDoc API documentation | No |

## Environment / Configuration

The application references these environment variables. Values are intentionally not included here.

| Variable | Purpose | Default in code |
| --- | --- | --- |
| `DB_HOST` | PostgreSQL server hostname or address | None |
| `DB_PORT` | PostgreSQL server port | None |
| `DB_NAME` | PostgreSQL database name | None |
| `DB_USER` | PostgreSQL login user | None |
| `DB_PASSWORD` | PostgreSQL login password | None |
| `JWT_SECRET` | Secret key used to sign and validate access tokens | None |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |

Both `app/database.py` and `app/core/security.py` call `load_dotenv()` during import. A local `.env` file exists and is excluded by `.gitignore`. The code does not perform explicit startup validation for missing variables or provide a typed settings object.

## Current Development State

### Implemented

- FastAPI application and default API documentation
- Standard PostgreSQL connectivity through SQLAlchemy and Psycopg
- `users` ORM model
- Password hashing and verification
- Login and eight-hour JWT access-token creation
- Bearer-token validation and active-user authentication
- Protected current-user endpoint
- Manual, interactive user-creation script
- Public root and database diagnostic endpoints

### Partially implemented

- Authentication covers login and current-user lookup, but there are no API endpoints for registration, logout, token refresh, password changes, or user administration.
- Database access is configured and a user model exists, but no migration or schema-management mechanism is present in the repository.
- Local environment loading is present, but deployment-specific configuration and startup validation are not.

### Planned or not yet implemented

- Statistics/event storage and retrieval APIs
- Website visit tracking
- Email tracking
- Protected admin statistics/data APIs
- An `/admin` frontend (this backend repository contains no frontend)
- Docker image/configuration
- Google Cloud Run deployment configuration
- AWS migration support or AWS-specific infrastructure
- Automated tests

