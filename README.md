# FastAPI Authentication and Authorization Project

This project implements a basic authentication and authorization system using FastAPI, SQLAlchemy, and JWT. It supports user registration, login, and token management (access and refresh tokens).

## Project Structure

```plaintext
.
├── app
│   ├── __init__.py        # Initializes the app as a package
│   ├── server.py          # Setup routes, middleware, and other server configurations
├── auth
│   ├── __init__.py
│   ├── models.py          # Database models, including User and RefreshToken
│   ├── schemas.py         # Pydantic schemas for request and response models, including user and token schemas
│   ├── routers.py         # API routers for handling authentication-related endpoints
│   ├── utils.py           # Utility functions for auth like password hashing and token generation
│   └── dependencies.py    # Dependency injection for routes, including current user retrieval
├── db
│   ├── __init__.py
│   └── connection.py      # Database connection setup using SQLAlchemy
├── config
│   ├── __init__.py
│   └── settings.py        # Configuration settings using pydantic-settings
└── main.py                # Main application setup

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
