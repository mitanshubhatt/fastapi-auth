# FastAPI Authentication and Authorization

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
Docker & Docker compose
FastAPI
SQLAlchemy
Uvicorn (ASGI server)
JWT token handling (python-jose)
Password hashing (passlib)
```

# No need to use cURL commands for all API Endpoints
## Just enter the below command in your system and the APIs should be available on swagger endpoint : ```localhost:8000/docs```

```plaintext
docker-compose up -d
```

## If cURL is required below are the commands for different functionalities

### Register User
```plaintext
curl --location 'localhost:8000/auth/register' \
--header 'Content-Type: application/json' \
--data-raw '{
  "email": "mitanshu@example.com",
  "full_name": "mitanshu",
  "password": "Mitanshu@123"
}'
```
### Login User
```plaintext
curl --location 'localhost:8000/auth/login' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'username=mitanshu@example.com' \
--data-urlencode 'password=Mitanshu@123'
```
### Refresh Access Token
```plaintext
curl --location 'localhost:8000/auth/register' \
--header 'Content-Type: application/json' \
--data-raw '{
  "email": "mitanshu@example.com",
  "full_name": "mitanshu",
  "password": "Mitanshu@123"
}'
```
### Get Current User Details
```plaintext
curl --location 'localhost:8000/auth/users/me' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaXRhbnNodUBleGFtcGxlLmNvbSIsImV4cCI6MTcxOTE0MDQwMH0.3cI3GwZNTpTLDXByj8OgPjvmSf5gIIJk45Aakpli8nA'
```
### Revoke Token
```plaintext
curl --location --request POST 'localhost:8000/auth/revoke-token?refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaXRhbnNodUBleGFtcGxlLmNvbSIsImlhdCI6MTcxOTEzOTUwMCwibm9uY2UiOiI0NDg0MGEwNTg3OTI5N2U0NmUzODM4MzhkMzlmNGVmYiJ9.PsXrv8t_sYFUbQKFN3xcE02LnmTACggbXFiX0GJG79o'
```
