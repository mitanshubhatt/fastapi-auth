# FastAPI Authentication and Authorization Project

This project implements a basic authentication and authorization system using FastAPI, SQLAlchemy, and JWT. It supports user registration, login, and token management (access and refresh tokens).

## Project Structure

```plaintext
.
├── auth
│   ├── __init__.py
│   ├── models.py       # Database models
│   ├── schemas.py      # Pydantic schemas for request and response models
│   ├── routers.py      # API routers
│   ├── utils.py        # Utility functions for auth like token generation
│   └── dependencies.py # Dependency injection for routes
├── db
│   ├── __init__.py
│   └── connection.py   # Database connection setup
└── main.py             # FastAPI application creation and configuration

```

# Features
```plaintext
User registration
User login
JWT access and refresh token generation
Endpoint security with token verification
Access and Refresh token generation
Revoke the refresh token
Swagger documentation
```

# Prerequisites
```plaintext
Python 3.7+
FastAPI
SQLAlchemy
Uvicorn (ASGI server)
JWT token handling (python-jose)
Password hashing (passlib)
```

# API Endpoints
## Register a new user
```plaintext
POST /auth/register
```
## Log in and receive access and refresh tokens
```plaintext
POST /auth/login
```
## Refresh access token
```plaintext
POST /auth/refresh-token
```
## Get current user details
```plaintext
GET /auth/users/me
```
