
# [Fynix AI Code Assistant](https://marketplace.visualstudio.com/items?itemName=Fynix.fynix) - FastAPI Authentication and Authorization System

This project, powered by **Fynix AI Code Assistant**, implements an advanced authentication and authorization system using **FastAPI**, **SQLAlchemy**, and modern tokenization techniques such as **JWT** and **PASETO**. It supports multiple authentication providers (Google, GitHub, and Microsoft), token management, and a robust RBAC system for organization and team-level access.

---

## Project Structure

```plaintext
.
├── Dockerfile
├── RBAC
│   ├── __init__.py
│   ├── models.py
│   ├── router.py
│   └── schemas.py
├── README.md
├── app
│   ├── __init__.py
│   └── server.py
├── auth
│   ├── __init__.py
│   ├── dependencies.py
│   ├── models.py
│   ├── router.py
│   ├── schemas.py
│   ├── providers.py
│   └── utils.py
├── config
│   ├── __init__.py
│   └── settings.py
├── db
│   ├── __init__.py
│   └── connection.py
├── docker-compose.yaml
├── main.py
├── requirements.txt
├── tests
│   ├── __init__.py
│   ├── auth
│   │   └── test_register.py
│   └── confest.py
└── utils
    └── custom_logger.py
```

---

## Features

- **Multi-provider Authentication**:
  - Google OAuth
  - GitHub OAuth
  - Microsoft Azure Auth
- **Token Management**:
  - JWT Access and Refresh Tokens
  - PASETO Tokens with Private-Public Key Encryption
- **RBAC (Role-Based Access Control)**:
  - Organization-level access
  - Team-level access
- **User Management**:
  - User registration and login
  - Secure password hashing (using `passlib`)
  - Token revocation for enhanced security
- **Swagger Documentation**: Easily test APIs via an interactive UI at `localhost:8000/docs`

---

## Prerequisites

- Python 3.7+
- Docker & Docker Compose
- FastAPI
- SQLAlchemy
- Uvicorn (ASGI server)
- OAuth libraries (`authlib`)
- JWT token handling (`python-jose`)
- PASETO token handling (`pyseto`)

---

## Quick Start

### Run the Application

To launch the application with all dependencies, run:

```plaintext
docker-compose up -d
```

Once up, the API documentation will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### Key Endpoints

| Functionality               | Endpoint                         | Method   |
|-----------------------------|----------------------------------|----------|
| **User Registration**       | `/auth/register`                | `POST`   |
| **User Login (JWT)**        | `/auth/login`                   | `POST`   |
| **Login with Google**       | `/auth/google`                  | `GET`    |
| **Login with GitHub**       | `/auth/github/login`            | `GET`    |
| **Login with Microsoft**    | `/auth/microsoft`               | `GET`    |
| **Token Refresh**           | `/auth/refresh-token`           | `POST`   |
| **Get Current User**        | `/auth/users/me`                | `GET`    |
| **Revoke Token**            | `/auth/revoke-token`            | `POST`   |

---

## Example cURL Commands

### Register a New User
```plaintext
curl --location 'localhost:8000/auth/register' \
--header 'Content-Type: application/json' \
--data-raw '{
  "email": "user@example.com",
  "full_name": "User Name",
  "password": "SecurePass123"
}'
```

### Login User with JWT
```plaintext
curl --location 'localhost:8000/auth/login' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'username=user@example.com' \
--data-urlencode 'password=SecurePass123'
```

### Login with Google
```plaintext
curl --location 'localhost:8000/auth/google-login' \
--header 'Content-Type: application/json'
```

### Get Current User Details
```plaintext
curl --location 'localhost:8000/auth/users/me' \
--header 'Authorization: Bearer <ACCESS_TOKEN>'
```

---

## Highlights

### Enhanced Authentication Mechanisms
- **JWT**: Lightweight and stateless access tokens.
- **PASETO**: More secure alternative to JWT with public-private key encryption.

### OAuth Integration
- Seamless login via **Google**, **GitHub**, and **Microsoft** for faster and secure authentication.

### RBAC Support
- Manage roles and permissions at **organization** and **team** levels.

---

## Made with [Fynix AI Code Assistant](https://marketplace.visualstudio.com/items?itemName=Fynix.fynix)

This project is built using **Fynix AI Code Assistant**, which simplifies and accelerates development with:
- AI-powered code suggestions.
- Automated code reviews and improvements.
- Intelligent debugging and testing.

Experience the power of **Fynix AI** to build smarter, more secure, and scalable applications. 🚀
