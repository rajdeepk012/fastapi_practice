# Session 10: FastAPI + Database Integration - Complete REST API

**Date:** 2025-11-12
**Focus:** Integrating FastAPI with SQLAlchemy to build a complete database-backed REST API
**Major Milestone:** Complete working application with 16 endpoints!

---

## 🎯 Session Goals

- Understand REST API design principles
- Integrate FastAPI endpoints with database CRUD operations
- Implement complete user and conversation management
- Add proper error handling and validation
- Test all endpoints
- Build production-ready API structure

---

## 📚 REST API Principles

### What is REST?

**REST** = **RE**presentational **S**tate **T**ransfer

A set of architectural constraints for designing web APIs that are:
- Easy to understand and use
- Predictable and consistent
- Scalable and maintainable
- Stateless (each request is independent)

---

### Key REST Principles

**1. Resource-Based URLs**

URLs represent **resources** (nouns), not **actions** (verbs):

```
✅ GOOD (Resource-based):
GET    /users           # Collection of users
GET    /users/1         # Specific user
POST   /users           # Create user
PUT    /users/1         # Update user
DELETE /users/1         # Delete user

❌ BAD (Action-based):
GET    /getUsers
GET    /getUserById?id=1
POST   /createUser
POST   /updateUser
```

**Why:** Makes API intuitive and predictable. Same URL, different HTTP methods = different actions.

---

**2. HTTP Methods Define Actions**

| Method | Action | CRUD | Example | Response Code |
|--------|--------|------|---------|---------------|
| `GET` | Read | Read | `GET /users` | 200 OK |
| `POST` | Create | Create | `POST /users` | 201 Created |
| `PUT` | Full Replace | Update | `PUT /users/1` | 200 OK |
| `PATCH` | Partial Update | Update | `PATCH /users/1` | 200 OK |
| `DELETE` | Delete | Delete | `DELETE /users/1` | 204 No Content |

---

**3. HTTP Status Codes**

Use meaningful status codes to indicate results:

```
2xx = Success
200 OK             - Request succeeded, returning data
201 Created        - New resource created
204 No Content     - Success, no data to return

4xx = Client Error (user's fault)
400 Bad Request    - Invalid input/format
401 Unauthorized   - Not authenticated
403 Forbidden      - Not authorized (authenticated but no permission)
404 Not Found      - Resource doesn't exist
422 Unprocessable  - Validation error (Pydantic uses this)

5xx = Server Error (our fault)
500 Internal Error - Something broke on server
503 Unavailable    - Server overloaded
```

---

**4. Nested Resources**

Show relationships in URLs:

```
GET /users/1/conversations        # Get user 1's conversations
POST /users/1/conversations       # Create conversation for user 1
GET /users/1/conversation-count   # Count user 1's conversations
```

**Pattern:** `/parent/{parent_id}/children`

---

## 🏗️ Complete API Architecture

### The Full Stack

```
┌─────────────────────────────────────────────────┐
│         CLIENT (Browser, Postman, curl)          │
└────────────────┬────────────────────────────────┘
                 │ HTTP/JSON
                 ▼
┌─────────────────────────────────────────────────┐
│         FASTAPI ENDPOINTS (main.py)              │
│  - @app.get("/users")                            │
│  - @app.post("/users")                           │
│  - Depends(get_db) ← dependency injection        │
│  - Error handling (HTTPException)                │
└────────────────┬────────────────────────────────┘
                 │ Python function calls
                 ▼
┌─────────────────────────────────────────────────┐
│            CRUD LAYER (crud.py)                  │
│  - get_users(db, skip, limit)                    │
│  - create_user(db, user)                         │
│  - Business logic queries                        │
└────────────────┬────────────────────────────────┘
                 │ ORM queries
                 ▼
┌─────────────────────────────────────────────────┐
│         SQLALCHEMY ORM (models.py)               │
│  - User model                                    │
│  - Conversation model                            │
│  - Relationships                                 │
└────────────────┬────────────────────────────────┘
                 │ SQL queries
                 ▼
┌─────────────────────────────────────────────────┐
│            MYSQL DATABASE                        │
│  - users table                                   │
│  - conversations table                           │
└─────────────────────────────────────────────────┘
```

---

## 📝 Complete API Endpoints (16 Total)

### Root & Utility

```python
GET  /                          # API information
GET  /health                    # Health check
```

### User Management (Full CRUD)

```python
POST   /users                   # Create user (201)
GET    /users                   # List users (pagination)
GET    /users/{user_id}         # Get specific user
PUT    /users/{user_id}         # Update user
DELETE /users/{user_id}         # Delete user (204)
```

### Conversation Management (Full CRUD)

```python
POST   /conversations           # Create conversation (201)
GET    /conversations           # List conversations
GET    /conversations/{id}      # Get specific conversation
PUT    /conversations/{id}      # Update conversation
DELETE /conversations/{id}      # Delete conversation (204)
```

### Nested Resources

```python
GET    /users/{id}/conversations       # User's conversations
GET    /users/{id}/conversation-count  # Count conversations
```

### Chatbot

```python
POST   /chat                    # Send message (saves to DB!)
```

---

## 💻 Implementation Details

### Endpoint Structure Pattern

Every endpoint follows this pattern:

```python
@app.METHOD("/resource", response_model=schemas.Response, status_code=status.CODE)
def function_name(
    # Path parameters
    resource_id: int,
    # Request body (for POST/PUT)
    resource_data: schemas.ResourceCreate,
    # Query parameters
    skip: int = 0,
    limit: int = 100,
    # Dependency injection
    db: Session = Depends(get_db)
):
    """Docstring explaining what this does"""

    # 1. Validate/check preconditions
    # 2. Call CRUD function
    # 3. Handle errors
    # 4. Return result
```

---

### Example: Create User Endpoint

```python
@app.post("/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user

    - **username**: User's username (required)
    - **email**: User's email address (required, unique)
    """
    # Business logic: Check if email already exists
    existing_user = crud.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    return crud.create_user(db=db, user=user)
```

**Data Flow:**
```
1. Client sends JSON: {"username": "john", "email": "john@example.com"}
2. FastAPI validates with schemas.UserCreate
3. Depends(get_db) injects database session
4. Check if email exists (business logic)
5. If exists: raise HTTPException (400)
6. If not: crud.create_user() saves to database
7. FastAPI validates response with schemas.User
8. Return JSON with 201 Created status
```

---

### Example: Get Users with Pagination

```python
@app.get("/users", response_model=List[schemas.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get list of users with pagination

    - **skip**: Number of users to skip (default: 0)
    - **limit**: Maximum number of users to return (default: 100)
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users
```

**Usage:**
```bash
GET /users              # First 100 users
GET /users?limit=10     # First 10 users
GET /users?skip=10&limit=10  # Users 11-20 (page 2)
```

---

### Example: Enhanced Chatbot Endpoint

```python
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Chatbot endpoint - now saves to database!"""

    # 1. Verify user exists
    user = crud.get_user(db, user_id=request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Get bot's reply
    bot_response = chatbot_reply(request.user_message)

    # 3. Save conversation to database
    conversation_data = schemas.ConversationCreate(
        user_id=request.user_id,
        message=request.user_message,
        bot_reply=bot_response
    )
    saved_conversation = crud.create_conversation(db, conversation_data)

    # 4. Return response with conversation_id
    return ChatResponse(
        bot_reply=bot_response,
        user_message=request.user_message,
        conversation_id=saved_conversation.id,  # ← From database!
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
```

**Before (Session 7):** Conversations saved in memory (lost when server restarts)
**Now (Session 10):** Conversations saved in MySQL (persistent!)

---

## 🔑 Key Concepts

### 1. Dependency Injection

```python
def get_db():
    db = SessionLocal()
    try:
        yield db  # Pause here, give session to endpoint
    finally:
        db.close()  # Always close, even if error

@app.get("/users")
def get_users(db: Session = Depends(get_db)):  # ← Auto-injected!
    return crud.get_users(db)
```

**Benefits:**
- Automatic session management
- No manual open/close
- Easy to test (can inject mock database)
- Cleaner code

---

### 2. Response Models

```python
@app.get("/users", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db)
    # FastAPI automatically:
    # 1. Converts SQLAlchemy models → Pydantic schemas
    # 2. Validates response matches schema
    # 3. Serializes to JSON
```

**from_attributes = True in schemas enables this!**

---

### 3. Error Handling

```python
# Check resource exists
user = crud.get_user(db, user_id)
if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with ID {user_id} not found"
    )

# Check business rules
if existing_user:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already registered"
    )
```

**Pattern:** Check → Raise HTTPException with appropriate code

---

### 4. Status Codes

```python
# 201 for creation
@app.post("/users", status_code=status.HTTP_201_CREATED)

# 204 for deletion (no content returned)
@app.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_user(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Not found")
    return None  # 204 returns no body
```

---

## 🧪 Testing Results

### Test 1: Create User

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com"}'

# Response (201 Created):
{
  "username": "testuser",
  "email": "test@example.com",
  "id": 8,
  "created_at": "2025-11-12T18:58:24"
}
```

✅ User created with auto-generated `id` and `created_at`!

---

### Test 2: Duplicate Email (Error Handling)

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com"}'

# Response (400 Bad Request):
{
  "detail": "Email already registered"
}
```

✅ Business logic validation working!

---

### Test 3: Get All Users

```bash
curl http://localhost:8000/users

# Response (200 OK):
[
  {"username":"ram","email":"ram@god.com","id":1,"created_at":"2025-11-10T10:53:08"},
  {"username":"alice","email":"newemail@example.com","id":2,"created_at":"2025-11-10T11:41:28"},
  ...
  {"username":"testuser","email":"test@example.com","id":8,"created_at":"2025-11-12T18:58:24"}
]
```

✅ Retrieved all 7 users!

---

### Test 4: Chat with Bot (Saves to Database!)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Hello bot!", "user_id": 8}'

# Response (200 OK):
{
  "bot_reply": "Hi there! How can I help you today?",
  "user_message": "Hello bot!",
  "conversation_id": 7,  ← Saved to database!
  "timestamp": "2025-11-12 20:21:31"
}
```

✅ Conversation saved with `conversation_id: 7`!

---

### Test 5: Get User's Conversations

```bash
curl http://localhost:8000/users/8/conversations

# Response (200 OK):
[{
  "message": "Hello bot!",
  "bot_reply": "Hi there! How can I help you today?",
  "id": 7,
  "user_id": 8,
  "created_at": "2025-11-12T20:21:31"
}]
```

✅ Retrieved conversation from database!

---

### Test 6: Update User (Partial Update)

```bash
curl -X PUT http://localhost:8000/users/8 \
  -H "Content-Type: application/json" \
  -d '{"username": "updated_user"}'

# Response (200 OK):
{
  "username": "updated_user",  ← Changed!
  "email": "test@example.com",  ← Stayed same!
  "id": 8,
  "created_at": "2025-11-12T18:58:24"
}
```

✅ Partial update working (`exclude_unset=True` in action)!

---

### Test 7: Get Conversation Count

```bash
curl http://localhost:8000/users/8/conversation-count

# Response (200 OK):
{
  "user_id": 8,
  "conversation_count": 1
}
```

✅ Utility endpoint working!

---

## 📊 Complete Data Flow Example

**User creates account and chats:**

```
Step 1: Create User
POST /users {"username": "john", "email": "john@example.com"}
    ↓
FastAPI validates with schemas.UserCreate
    ↓
Depends(get_db) injects session
    ↓
Check email doesn't exist
    ↓
crud.create_user() → INSERT INTO users
    ↓
Database returns user with id=9
    ↓
FastAPI serializes with schemas.User
    ↓
Client receives: {"id": 9, "username": "john", ...}

Step 2: Send Chat Message
POST /chat {"user_message": "Hello!", "user_id": 9}
    ↓
FastAPI validates with ChatRequest
    ↓
Verify user 9 exists
    ↓
Get bot reply from chatbot_reply()
    ↓
crud.create_conversation() → INSERT INTO conversations
    ↓
Database returns conversation with id=8
    ↓
Client receives: {"bot_reply": "Hi!", "conversation_id": 8, ...}

Step 3: View Conversation History
GET /users/9/conversations
    ↓
Verify user exists
    ↓
crud.get_user_conversations() → SELECT * FROM conversations WHERE user_id = 9
    ↓
Database returns list of conversations
    ↓
FastAPI serializes with List[schemas.Conversation]
    ↓
Client receives: [{"id": 8, "message": "Hello!", ...}]
```

---

## 🎓 Key Takeaways

### What We Accomplished

1. ✅ **Built 16 REST API endpoints** - Complete CRUD for users and conversations
2. ✅ **Integrated FastAPI + SQLAlchemy** - All layers working together
3. ✅ **Proper REST design** - Resource-based URLs, correct HTTP methods and status codes
4. ✅ **Error handling** - 400, 404 with meaningful messages
5. ✅ **Business logic validation** - Email uniqueness, user existence checks
6. ✅ **Dependency injection** - Automatic session management
7. ✅ **Response models** - Type-safe, auto-validated responses
8. ✅ **Pagination** - Handle large datasets
9. ✅ **Nested resources** - `/users/{id}/conversations`
10. ✅ **Enhanced chatbot** - Now saves to database!

### Architecture Benefits

**Separation of Concerns:**
- `main.py` - HTTP layer (endpoints, status codes, error handling)
- `crud.py` - Database layer (queries, business logic)
- `models.py` - ORM layer (table structure)
- `schemas.py` - Validation layer (API contracts)
- `database.py` - Connection layer (session management)

**Each layer can change independently!**

---

## 🚀 Automatic Interactive Documentation

FastAPI automatically generates **Swagger UI** documentation at:

**http://localhost:8000/docs**

**Features:**
- ✅ See all endpoints
- ✅ View request/response schemas
- ✅ Test endpoints in browser
- ✅ Auto-generated from code
- ✅ Always up-to-date

**Alternative documentation (ReDoc):**
**http://localhost:8000/redoc**

---

## 🔄 Git Workflow

**Files Modified:**
- `main.py` (291 additions, 126 deletions)
- `models.py` (1 line cleanup)

**Commit:**
```
Integrate FastAPI with database - Complete REST API

- Completely rewrote main.py with database integration
- Add 16 REST API endpoints with full CRUD operations
- User endpoints: CREATE, READ, UPDATE, DELETE with validation
- Conversation endpoints: Full CRUD with nested resources
- Enhanced chatbot endpoint to save conversations to database
- Implement proper HTTP status codes (200, 201, 204, 400, 404)
- Add error handling and business logic validation
- Use dependency injection for database sessions
- Add pagination support for list endpoints
- Add utility endpoints (health check, conversation count)
- FastAPI auto-generates interactive docs at /docs

Features:
- Email uniqueness validation before user creation
- Partial updates with exclude_unset
- Nested resources (/users/{id}/conversations)
- Response models with automatic serialization
- Complete separation of concerns
```

---

## 📈 Project Progress

```
Phase 1: FastAPI Basics (Sessions 1-7)
✅ Hello World
✅ Path & query parameters
✅ Request/response models
✅ Error handling
✅ Simple chatbot with in-memory storage

Phase 2: Database Basics (Session 8)
✅ MySQL setup
✅ SQL fundamentals
✅ CREATE, SELECT, INSERT, UPDATE, DELETE
✅ JOINs and relationships

Phase 3: ORM Integration (Session 9)
✅ SQLAlchemy setup
✅ Models and schemas
✅ CRUD operations
✅ Dependency injection

Phase 4: Complete Integration (Session 10) ← WE ARE HERE!
✅ 16 REST API endpoints
✅ Full CRUD with database
✅ Error handling and validation
✅ Chatbot saves to database
✅ Production-ready structure

Next: Session 11 - Schema Migrations with Alembic
```

---

## 🎯 What's Next?

**Session 11 will cover:**
- Database migrations with Alembic
- Handling schema changes safely
- Version control for database structure
- Migration best practices
- Rolling back migrations

**You'll learn:**
- How to add/remove columns without losing data
- How to modify existing tables
- How to track database changes in Git
- Production deployment strategies

---

**Session Duration:** ~2 hours
**Endpoints Created:** 16
**Lines Changed:** 291 additions, 126 deletions
**Git Commits:** 1

**Status:** ✅ Session 10 Complete! Full-stack REST API working!
