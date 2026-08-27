# Backend Service

A containerized backend service for personal analytics and tracking, built with FastAPI and PostgreSQL.

The project provides a centralized backend for collecting and querying data used across my personal projects. It currently implements JWT-based authentication and serves as the foundation for future website analytics, email tracking, and admin dashboard APIs.

## Live API

Swagger / OpenAPI documentation:

https://api.adamtseng.com/docs

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT Authentication
- Docker
- Google Cloud SQL
- Google Artifact Registry
- Google Cloud Run
- GitHub Actions

## Current Features

- User authentication with account name and password
- Argon2 password hashing
- JWT access token generation and validation
- Protected API endpoints using Bearer authentication
- PostgreSQL persistence with SQLAlchemy
- Cloud SQL integration
- Dockerized FastAPI application
- Automated deployment to Cloud Run with GitHub Actions
- Custom API domain with HTTPS

## API

### Authentication

| Method | Endpoint | Authentication | Description |
| --- | --- | --- | --- |
| POST | `/auth/login` | No | Authenticate a user and return a JWT access token |
| GET | `/auth/me` | Bearer Token | Return the currently authenticated user |

Interactive API documentation is available through Swagger UI at `/docs`.

## Authentication Flow

```text
Client
  │
  │ account_name + password
  ▼
POST /auth/login
  │
  ▼
PostgreSQL / Cloud SQL
  │
  │ User lookup
  ▼
Argon2 Password Verification
  │
  ▼
JWT Access Token
  │
  │ Authorization: Bearer <token>
  ▼
Protected API
  │
  ▼
GET /auth/me
```

Passwords are never stored in plaintext. Password hashes are generated using Argon2, and protected endpoints validate signed JWT access tokens.

## Architecture

```text
                        GitHub
                          │
                          │ push / merge to main
                          ▼
                    GitHub Actions
                          │
                          │ Build Docker image
                          ▼
                 Google Artifact Registry
                          │
                          │ Deploy
                          ▼
Client ───────────► Google Cloud Run
                          │
                          │ FastAPI
                          ▼
                     SQLAlchemy
                          │
                          ▼
                   Google Cloud SQL
                     PostgreSQL
```

The application uses standard PostgreSQL and SQLAlchemy interfaces to keep the application layer largely independent of the underlying cloud provider.

## Deployment

The application is packaged as a Docker image and deployed to Google Cloud Run.

Deployment is automated through GitHub Actions:

```text
Push / Merge to main
        │
        ▼
GitHub Actions
        │
        ▼
Build linux/amd64 Docker Image
        │
        ▼
Push to Artifact Registry
        │
        ▼
Deploy new Cloud Run revision
```

Application configuration and credentials are supplied through environment variables and are not included in the Docker image or repository.

## Project Structure

```text
backend-service/
├── app/
│   ├── core/           # Security and authentication utilities
│   ├── dependencies/   # FastAPI dependencies
│   ├── models/         # SQLAlchemy models
│   ├── routers/        # API routes
│   ├── schemas/        # Pydantic schemas
│   ├── database.py
│   └── main.py
├── scripts/
│   └── create_user.py
├── .github/
│   └── workflows/
│       └── deploy.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

More detailed documentation:

- `OVERVIEW.md` — Current application behavior and implementation
- `STRUCTURE.md` — Repository structure and module responsibilities

## Roadmap

Planned extensions include:

- Website visit tracking
- Email tracking
- Analytics and aggregation APIs
- Admin dashboard APIs
- Additional statistics/event sources
- Automated testing and CI checks
- Further deployment and infrastructure improvements

The long-term goal is to use this service as a reusable analytics backend for multiple personal projects.

## Status

The first deployment milestone is complete:

- FastAPI application
- PostgreSQL / Cloud SQL
- JWT authentication
- Docker deployment
- Cloud Run
- Custom API domain
- Automated CD pipeline

The next milestone is integration with an `/admin` dashboard and the first analytics APIs.