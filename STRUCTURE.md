# Repository Structure

```text
backend-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── security.py
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py
│   └── schemas/
│       ├── __init__.py
│       ├── auth.py
│       └── user.py
├── scripts/
│   ├── __init__.py
│   └── create_user.py
├── .env                 # local, ignored; values not documented
├── .gitignore
├── README.md
└── requirements.txt
```

Generated directories, Git internals, virtual environments, caches, and IDE metadata are omitted.

## Application Entry Point

### `app/main.py`

This is the FastAPI application entry point. It:

- Instantiates `app` with the title `Backend Service` and version `0.1.0`.
- Imports and includes the authentication router from `app.routers.auth`.
- Defines `root()`, the handler for `GET /`.
- Defines `db_test()`, the handler for `GET /db-test`; this uses the shared SQLAlchemy engine and a textual SQL query to return the current database name and PostgreSQL version.

It depends on FastAPI, SQLAlchemy's `text()`, `app.database.engine`, and the authentication router. An ASGI server such as Uvicorn depends on this module to obtain the `app` object.

### Package initializers

`app/__init__.py` and the `__init__.py` files under `core`, `dependencies`, `models`, `routers`, and `schemas` are currently empty. They mark/importably organize the Python packages but do not re-export objects or perform initialization.

## Database Layer

### `app/database.py`

This module owns database connection setup. At import time it:

- Loads variables from a local dotenv file when available.
- Reads `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD`.
- Constructs a `postgresql+psycopg` SQLAlchemy URL.
- Creates the shared `engine`.
- Creates `SessionLocal`, a session factory bound to that engine.

It depends on `os`, `python-dotenv`, and SQLAlchemy. The application entry point and user-creation script depend directly on `engine`; the authentication router and current-user dependency depend on `SessionLocal`.

There is no session-yielding FastAPI dependency, repository layer, migration setup, connection-pool customization, or declarative base in this module.

## Models

### `app/models/user.py`

This module defines:

- `Base`, the project's current SQLAlchemy `DeclarativeBase` subclass.
- `User`, the ORM mapping for the `users` table.

`User` contains the `id`, `name`, `account_name`, `password_hash`, `is_active`, and `created_at` columns. The authentication router queries it during login, the authentication dependency queries it when resolving a bearer token, and the user-creation script uses it to construct an insert.

The model depends only on SQLAlchemy and Python's `datetime` type. No relationships or additional models are present. `Base` is not currently imported elsewhere for metadata creation or migrations.

## Schemas

### `app/schemas/auth.py`

Defines the Pydantic boundary types for login:

- `LoginRequest`: accepts `account_name` and `password` strings.
- `TokenResponse`: returns `access_token` and a `token_type` that defaults to `bearer`.

The authentication router depends on both schemas.

### `app/schemas/user.py`

Defines `UserResponse`, containing `id`, `name`, `account_name`, and `is_active`. The protected current-user route uses it as its response model, preventing `password_hash` and `created_at` from appearing in that response.

Both schema modules depend only on Pydantic. They do not currently define field constraints or custom validation.

## Routers

### `app/routers/auth.py`

Defines an `APIRouter` with the `/auth` prefix and `Authentication` OpenAPI tag. It contains:

- `login()`: handles `POST /auth/login`, directly opens a database session, selects a user by account name, checks active status and password, and returns a new JWT.
- `get_me()`: handles `GET /auth/me`, depends on `get_current_user()`, and returns the resolved user through `UserResponse`.

This module depends on:

- FastAPI routing, dependency injection, and HTTP errors
- SQLAlchemy queries
- `app.database.SessionLocal`
- `app.models.user.User`
- Password verification and token creation from `app.core.security`
- Login/token and user response schemas
- The current-user dependency from `app.dependencies.auth`

`app.main` depends on and mounts this router.

## Dependencies

### `app/dependencies/auth.py`

This module implements reusable request authentication:

- `bearer_scheme` is FastAPI's `HTTPBearer` security scheme.
- `get_current_user()` extracts bearer credentials, decodes the JWT, queries the user by ID, verifies that the user exists and is active, detaches the ORM object from the session, and returns it.

Token decoding failures and invalid user states are converted to HTTP 401 responses with a common message. The module depends on PyJWT exception types, FastAPI, SQLAlchemy, `app.core.security`, `app.database`, and the `User` model. The `/auth/me` route currently depends on it; it is reusable by future protected routes.

There is no general database-session dependency in the current code. Sessions are opened directly where needed.

## Security / Authentication

### `app/core/security.py`

This module centralizes password and JWT primitives:

- Initializes `PasswordHash.recommended()`.
- Loads `JWT_SECRET` and `JWT_ALGORITHM`; the algorithm defaults to `HS256`.
- `hash_password()` hashes a plaintext password for storage.
- `verify_password()` verifies a plaintext password against a stored hash.
- `create_access_token()` creates a signed JWT with a string user ID in `sub` and an expiration eight hours in the future.
- `decode_access_token()` validates and decodes a JWT, then converts `sub` to an integer user ID.

It depends on `pwdlib`, PyJWT, `python-dotenv`, standard datetime utilities, and environment access. The login router uses verification and token creation, the authentication dependency uses decoding, and the user-creation script uses hashing.

The module provides primitives rather than HTTP behavior; HTTP 401 handling lives in the router/dependency modules. No refresh tokens, token revocation, role/permission checks, or configurable token lifetime are implemented.

## Scripts

### `scripts/create_user.py`

An interactive command-line utility that:

1. Prompts for a display name and account name.
2. Reads a password without echoing it via `getpass`.
3. Hashes the password with `app.core.security.hash_password()`.
4. Inserts an active user through `app.database.engine` and the `User` table mapping.

It depends directly on the database engine, user model, security helper, and SQLAlchemy Core `insert()`. It does not create the `users` table, validate input, or catch uniqueness/database errors.

`scripts/__init__.py` is empty and makes the directory a Python package.

## Root Configuration and Documentation

### `requirements.txt`

Pins the runtime stack and its transitive dependencies, including FastAPI, Uvicorn, SQLAlchemy, Psycopg, Pydantic, PyJWT, `pwdlib`, Argon2 bindings, and `python-dotenv`. There is no separate test/development dependency file.

### `.gitignore`

A broad Python-oriented ignore file covering bytecode, build products, virtual environments, dotenv files, test/tool caches, and common editor/tool artifacts. In particular, `.env` and `.venv` are ignored.

### `.env`

A local ignored configuration file is present. The application-referenced variable names are `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `JWT_SECRET`, and `JWT_ALGORITHM`. Credential values are intentionally not reproduced in this documentation.

### `README.md`

Currently contains only the project name and a one-line description: a backend service for personal analytics and tracking.

## Dependency Direction

The login path currently follows this direction:

```text
POST /auth/login
        |
        v
app.routers.auth
   |         |
   v         v
SessionLocal   app.core.security
   |         (verify password, create JWT)
   v
User model
   |
   v
PostgreSQL
```

The protected current-user path is:

```text
GET /auth/me
      |
      v
app.routers.auth
      |
      v
app.dependencies.auth.get_current_user
      |                     |
      v                     v
app.core.security       SessionLocal
(decode JWT)                |
                            v
                        User model
                            |
                            v
                        PostgreSQL
```

At module level, the composition is:

```text
app.main
  +-- app.routers.auth
  |     +-- app.dependencies.auth
  |     +-- app.core.security
  |     +-- app.database
  |     +-- app.models.user
  |     +-- app.schemas.auth / user
  +-- app.database
```

There is no separate service or repository layer: route/dependency functions issue SQLAlchemy queries directly.

## Architecture Observations

- The project already separates routing, schemas, ORM models, security primitives, and reusable authentication dependencies into small modules.
- Database setup is reusable and provider-neutral at the code level because it uses a standard PostgreSQL SQLAlchemy URL, though environment loading and connection construction happen at module import time.
- Login currently combines HTTP handling, database lookup, account-state checks, and credential verification in one route function. This is proportionate to the current size but may become a point of growth if authentication features expand.
- Database access is coupled directly to the authentication router and dependency through the global `SessionLocal`; there is not yet a service/repository abstraction or a shared FastAPI session dependency.
- `get_current_user()` is a reusable boundary for protecting future admin endpoints.
- The declarative `Base` lives in the user model module. If more models and migrations are added, model metadata organization will become more significant.
- The repository currently has no event/statistics domain modules. Adding tracking models and endpoints will introduce new choices around validation, ingestion, querying, and separation from authentication concerns.
- `/db-test` is unauthenticated and returns database/version information; that current behavior may matter when discussing a production deployment.
- No automated tests, migration tooling, container configuration, or cloud deployment files are present, so those concerns are not yet represented in the architecture.

