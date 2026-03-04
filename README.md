# COSC310-Project

## Backend Overview

This project uses a small FastAPI backend with JSON-file persistence.

### Architecture — SOLID Principles

The backend is structured around five SOLID principles:

| Principle | Where applied |
|-----------|---------------|
| **S**ingle Responsibility | `PasswordService` only hashes passwords; `SessionService` only manages sessions; `AuthService` only handles registration and login; `ItemService` only handles item CRUD. |
| **O**pen/Closed | `BaseJsonRepository` provides the JSON persistence strategy. New storage backends (e.g. SQLite, PostgreSQL) can be added by extending `BaseJsonRepository` or implementing a repository interface — **no service code changes required**. |
| **L**iskov Substitution | `JsonUserRepository`, `JsonSessionRepository`, and `JsonItemRepository` fully satisfy their corresponding abstract interfaces, so any implementation can be swapped transparently. |
| **I**nterface Segregation | Three narrow interfaces (`IUserRepository`, `ISessionRepository`, `IItemRepository`) are defined in `interfaces/repositories.py`. Services only import the interface they need. |
| **D**ependency Inversion | Services depend on abstract interfaces, not on concrete JSON classes. Concrete bindings live exclusively in `dependencies.py` (the composition root). |

### Backend Layers

```
app/
├── interfaces/          # ISP / DIP — abstract repository contracts
│   └── repositories.py
├── repositories/        # OCP / LSP — concrete JSON implementations
│   ├── base_json_repo.py  ← shared persistence logic (DRY)
│   ├── users_repo.py
│   ├── sessions_repo.py
│   └── items_repo.py
├── services/            # SRP — focused business-logic classes
│   ├── password_service.py   ← password hashing only
│   ├── session_service.py    ← session lifecycle only
│   ├── auth_service.py       ← register / login / role guard
│   └── items_service.py      ← item CRUD only
├── routers/             # HTTP boundary — thin, delegates to services
│   ├── auth.py
│   └── items.py
├── schemas/             # Pydantic request/response models
│   ├── auth.py
│   └── item.py
├── dependencies.py      # Composition root — wires interfaces → implementations
├── main.py
└── data/                # JSON persistence files
    ├── users.json
    ├── sessions.json
    └── items.json
```

Current JSON data files:
- `backend/app/data/items.json`
- `backend/app/data/users.json`
- `backend/app/data/sessions.json`

## Authentication Endpoints

### `POST /auth/register`

Creates an account for one of the supported roles:
- `user`
- `owner`
- `manager`

Example request:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "email": "alice@example.com",
    "password": "secret123",
    "role": "user"
  }'
```

### `POST /auth/login`

Logs in with email and password and returns a bearer token.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "secret123"
  }'
```

Example response:

```json
{
  "token": "your_token_here",
  "token_type": "bearer",
  "expires_at": "2026-03-05T07:23:38Z",
  "user": {
    "id": "user-id",
    "name": "Alice",
    "email": "alice@example.com",
    "role": "user",
    "created_at": "2026-03-04T07:23:01Z"
  }
}
```

### `GET /auth/me`

Returns the current logged-in user profile.

Example request:

```bash
curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Role Behavior

Authentication answers: "Who is making the request?"

Authorization answers: "What is that account allowed to do?"

Current role rules:
- `user` can register, log in, and fetch their current profile
- `owner` can register, log in, fetch their profile, and write item data
- `manager` can register, log in, fetch their profile, and write item data

Item route access:
- `GET /items` is public
- `GET /items/{item_id}` is public
- `POST /items` requires role `owner` or `manager`
- `PUT /items/{item_id}` requires role `owner` or `manager`
- `DELETE /items/{item_id}` requires role `owner` or `manager`

## Quick Role Test

Register an owner:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bob",
    "email": "bob@example.com",
    "password": "abc123",
    "role": "owner"
  }'
```

Log in as that owner:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "password": "abc123"
  }'
```

Create an item with the returned token:

```bash
curl -X POST http://127.0.0.1:8000/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_OWNER_TOKEN_HERE" \
  -d '{
    "title": "Burger",
    "category": "Food",
    "tags": ["fast", "lunch"]
  }'
```

Try the same item creation request with a normal `user` token and it should return `403 Forbidden`.

## Notes

- Passwords are not stored in plaintext
- Passwords are hashed with salted `pbkdf2_hmac`
- Sessions are stored in `sessions.json` with an expiry time
- Protected routes reject missing, invalid, or expired tokens
- Repositories safely handle missing JSON files by returning empty data
