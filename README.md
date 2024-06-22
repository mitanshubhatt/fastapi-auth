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
