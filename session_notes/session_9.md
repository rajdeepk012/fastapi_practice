# Session 9: SQLAlchemy ORM & Model Mapping

**Date:** 2025-11-11
**Focus:** SQLAlchemy ORM, Pydantic schemas, CRUD operations, and database integration
**Database:** chatbot_db (MySQL)

---

## 🎯 Session Goals

- Understand Object-Relational Mapping (ORM)
- Install and configure SQLAlchemy with MySQL
- Create database models and schemas
- Implement CRUD operations
- Test ORM integration
- Learn data transformation concepts
- Understand SOLID principles

---

## 📚 Core Concepts Covered

### 1. What is ORM?

**ORM = Object-Relational Mapping**

A technique that lets you interact with databases using Python objects instead of writing SQL queries.

**Without ORM (Raw SQL):**
```python
import mysql.connector

conn = mysql.connector.connect(host="localhost", user="root", password="root", database="chatbot_db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE id = %s", (1,))
result = cursor.fetchone()
print(result[1])  # What is index 1? 🤔
```

**With ORM (SQLAlchemy):**
```python
from sqlalchemy.orm import Session

user = session.query(User).filter(User.id == 1).first()
print(user.username)  # Clear and readable! ✅
```

**Benefits:**
- ✅ Write Python code, not SQL strings
- ✅ Type checking and IDE autocomplete
- ✅ Automatic connection management
- ✅ Access data by attribute names
- ✅ Database-agnostic (easy to switch databases)
- ✅ Prevents SQL injection automatically

---

### 2. SQLAlchemy Architecture

```
┌─────────────────────────────────────────────┐
│         FastAPI Application                  │
│  (Endpoints, Business Logic)                 │
└──────────────┬──────────────────────────────┘
               │ Python Objects
               ▼
┌─────────────────────────────────────────────┐
│         SQLAlchemy ORM Layer                 │
│  - Session (manages transactions)            │
│  - Models (User, Conversation classes)       │
│  - Relationships (one-to-many)               │
└──────────────┬──────────────────────────────┘
               │ SQL Queries
               ▼
┌─────────────────────────────────────────────┐
│              MySQL Database                  │
│  (chatbot_db)                                │
└─────────────────────────────────────────────┘
```

---

### 3. Three Key Components

| Component | File | Purpose | Example |
|-----------|------|---------|---------|
| **Database Config** | `database.py` | Connection, engine, sessions | `SessionLocal()`, `get_db()` |
| **SQLAlchemy Models** | `models.py` | Database structure (ORM) | `class User(Base)` |
| **Pydantic Schemas** | `schemas.py` | API validation | `class UserCreate(BaseModel)` |
| **CRUD Operations** | `crud.py` | Database queries | `get_user()`, `create_user()` |

---

### 4. SQLAlchemy Models vs Pydantic Schemas

**Critical distinction!**

| Aspect | SQLAlchemy Model (`models.py`) | Pydantic Schema (`schemas.py`) |
|--------|--------------------------------|-------------------------------|
| **Purpose** | Database ORM | API validation/serialization |
| **Inherits from** | `Base` (declarative_base) | `BaseModel` |
| **Used for** | Database operations | API requests/responses |
| **Has** | Columns, relationships, constraints | Fields, validators, configs |
| **Mapping** | Python ↔ SQL | JSON ↔ Python |
| **Example** | `Column(String(50))` | `username: str` |
| **Knows about** | Database structure | JSON structure |

**Data Flow:**
```
Client (JSON) → Pydantic (validation) → Business Logic → SQLAlchemy (ORM) → MySQL (database)
      ↓                                                                              ↓
   Request                                                                        Storage
      ↑                                                                              ↑
Client (JSON) ← Pydantic (serialization) ← Business Logic ← SQLAlchemy (ORM) ← MySQL (database)
```

---

## 💻 Files Created

### 1. database.py - Database Connection Setup

**Purpose:** Configure database connection, create engine, sessions, and dependency injection

**Key components:**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/chatbot_db"
# Format: dialect+driver://username:password@host:port/database

# Engine: Manages connections
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# SessionLocal: Factory for creating sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: Foundation for all models
Base = declarative_base()

# Dependency for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db  # Pause here, give session to endpoint
    finally:
        db.close()  # Always close, even if error
```

**Explanation:**
- **Engine:** Connection pool to database
- **SessionLocal:** Creates individual database sessions
- **Base:** All models inherit from this
- **get_db():** Dependency injection for FastAPI (provides and closes sessions automatically)

**Database URL breakdown:**
```
mysql+pymysql://root:root@localhost:3306/chatbot_db
│      │        │    │    │         │    └─ Database name
│      │        │    │    │         └────── Port (MySQL default: 3306)
│      │        │    │    └──────────────── Host
│      │        │    └───────────────────── Password
│      │        └────────────────────────── Username
│      └─────────────────────────────────── Driver
└────────────────────────────────────────── Database type
```

---

### 2. models.py - SQLAlchemy ORM Models

**Purpose:** Define database table structures as Python classes

**User Model:**
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship (NOT a database column!)
    conversations = relationship("Conversation", back_populates="user")
```

**Conversation Model:**
```python
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    bot_reply = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship
    user = relationship("User", back_populates="conversations")
```

**Key concepts:**
- **`__tablename__`**: Which MySQL table this class maps to
- **`Column()`**: Defines database columns with types and constraints
- **`relationship()`**: Creates Python-level connection between models (NOT a database column!)
- **`ForeignKey()`**: Creates foreign key constraint in database

**Column types mapping:**
| SQLAlchemy | MySQL | Python |
|------------|-------|--------|
| `Integer` | `INT` | `int` |
| `String(50)` | `VARCHAR(50)` | `str` |
| `Text` | `TEXT` | `str` |
| `DateTime` | `DATETIME` | `datetime` |

---

### 3. schemas.py - Pydantic Models

**Purpose:** Validate API requests and serialize responses

**Schema hierarchy:**

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Base schema (DRY principle)
class UserBase(BaseModel):
    username: str
    email: EmailStr

# Create schema (request validation)
class UserCreate(UserBase):
    pass  # Inherits username, email

# Update schema (partial updates)
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

# Response schema (API response)
class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models

# Nested schema (with relationships)
class UserWithConversations(User):
    conversations: List['Conversation'] = []
```

**Why different schemas?**

| Schema | Purpose | Required Fields | Use Case |
|--------|---------|-----------------|----------|
| `UserCreate` | Create request | username, email | `POST /users` |
| `UserUpdate` | Update request | All optional | `PUT/PATCH /users/{id}` |
| `User` | Response | All + id, created_at | `GET /users/{id}` |
| `UserWithConversations` | Detailed response | User + conversations | `GET /users/{id}/with-conversations` |

**Why `from_attributes = True`?**

Allows Pydantic to read from SQLAlchemy model attributes:

```python
# SQLAlchemy object from database
db_user = db.query(models.User).first()

# Convert to Pydantic (only works with from_attributes = True!)
pydantic_user = schemas.User.model_validate(db_user)

# FastAPI does this automatically when you have response_model!
```

---

### 4. crud.py - CRUD Operations

**Purpose:** Reusable database query functions

**Structure:**
- Separation of concerns (endpoints don't write SQL)
- Reusable across multiple endpoints
- Easy to test
- Centralized database logic

**Example operations:**

**Create:**
```python
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        username=user.username,
        email=user.email
    )
    db.add(db_user)  # Stage changes
    db.commit()  # Save to database
    db.refresh(db_user)  # Get generated id and created_at
    return db_user
```

**Read:**
```python
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()
```

**Update:**
```python
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    # Only update fields that were provided
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user
```

**Delete:**
```python
def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True
```

---

## 🔑 Key Concepts Explained

### 1. Database Session

**What is a session?**

A session is a "workspace" for database operations. Think of it as a shopping cart:
- You add items (objects) to the cart
- You can modify items
- You checkout (commit) to save everything
- You can abandon the cart (rollback) if needed

```python
db = SessionLocal()  # Open shopping cart
user = db.query(User).first()  # Get item from warehouse
user.username = "new_name"  # Modify item in cart
db.commit()  # Checkout (save to database)
db.close()  # Close cart
```

**Session lifecycle:**
1. Create: `db = SessionLocal()`
2. Use: `db.query()`, `db.add()`, `db.delete()`
3. Save: `db.commit()`
4. Close: `db.close()`

**Why `autocommit=False`?**
- Gives you control over when changes are saved
- Allows transactions (all-or-nothing)
- Can rollback if something goes wrong
- Prevents partial/inconsistent updates

---

### 2. Dependency Injection with `yield`

**What is dependency injection?**

Automatically providing resources that a function needs.

**Without dependency injection:**
```python
@app.get("/users")
def get_users():
    db = SessionLocal()  # Manual session creation
    try:
        users = db.query(User).all()
        return users
    finally:
        db.close()  # Manual cleanup
    # Repeat this boilerplate in EVERY endpoint! ❌
```

**With dependency injection:**
```python
from fastapi import Depends

@app.get("/users")
def get_users(db: Session = Depends(get_db)):  # ← Automatic!
    users = db.query(User).all()
    return users
    # Session automatically closed! ✅
```

**How `yield` works:**

```python
def get_db():
    db = SessionLocal()    # 1. Create session
    yield db               # 2. PAUSE, give to endpoint
                          # 3. Endpoint uses db...
                          # 4. Endpoint finishes, RESUME here
    db.close()            # 5. Close session
```

**Execution flow:**
```
FastAPI: "I see Depends(get_db)"
    ↓
FastAPI: Calls get_db() →
    ↓
get_db: Creates session
    ↓
get_db: yield db  ← PAUSES HERE
    ↓
FastAPI: Takes db, calls endpoint(db)
    ↓
Endpoint: Uses db to query
    ↓
Endpoint: Returns result
    ↓
FastAPI: Endpoint done, resume get_db()
    ↓
get_db: db.close()  ← Always runs!
```

---

### 3. Relationships in ORM

**One-to-Many relationship:**

```
User (ONE)              Conversation (MANY)
┌────┬──────────┐      ┌────┬─────────┬─────────┐
│ 1  │ ram      │─────▶│ 2  │    1    │ Hello   │
│    │          │  ┌──▶│ 3  │    1    │ Hi      │
└────┴──────────┘  │   └────┴─────────┴─────────┘
                   │        ▲
                   └── user_id (Foreign Key)
```

**In code:**
```python
# User model
class User(Base):
    conversations = relationship("Conversation", back_populates="user")

# Conversation model
class Conversation(Base):
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="conversations")

# Usage
user = db.query(User).first()
for conv in user.conversations:  # ← No JOIN written!
    print(conv.message)
# SQLAlchemy automatically queries conversations WHERE user_id = user.id
```

**Lazy loading vs Eager loading:**

**Lazy loading (default):**
```python
user = db.query(User).first()
# SQL: SELECT * FROM users LIMIT 1

for conv in user.conversations:  # ← SQL query runs HERE!
    # SQL: SELECT * FROM conversations WHERE user_id = 1
    print(conv.message)
```

**Eager loading (more efficient):**
```python
from sqlalchemy.orm import joinedload

user = db.query(User)\
    .options(joinedload(User.conversations))\
    .first()
# SQL: SELECT users.*, conversations.* FROM users LEFT JOIN conversations ...
# Everything loaded in ONE query!

for conv in user.conversations:  # ← No additional SQL!
    print(conv.message)
```

---

### 4. Pagination

**Purpose:** Load data in chunks instead of all at once

**Implementation:**
```python
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

# Get first 10 users (page 1)
page1 = get_users(db, skip=0, limit=10)   # Users 1-10

# Get next 10 users (page 2)
page2 = get_users(db, skip=10, limit=10)  # Users 11-20

# Formula: skip = (page_number - 1) * page_size
```

**SQL generated:**
```sql
-- Page 1
SELECT * FROM users LIMIT 10 OFFSET 0;

-- Page 2
SELECT * FROM users LIMIT 10 OFFSET 10;

-- Page 3
SELECT * FROM users LIMIT 10 OFFSET 20;
```

---

### 5. Partial Updates with `exclude_unset`

**Purpose:** Update only fields that were provided

```python
# Client sends: {"username": "new_name"}
# (email NOT provided)

user_update = UserUpdate(username="new_name")

# WITHOUT exclude_unset=True
user_update.model_dump()
# Result: {"username": "new_name", "email": None}
# Would set email to None! ❌

# WITH exclude_unset=True
user_update.model_dump(exclude_unset=True)
# Result: {"username": "new_name"}
# Only updates username! ✅
```

**In CRUD function:**
```python
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)

    # Get only fields that were set
    update_data = user_update.model_dump(exclude_unset=True)

    # Update dynamically
    for field, value in update_data.items():
        setattr(db_user, field, value)  # user.username = "new_name"

    db.commit()
    return db_user
```

---

### 6. SQL Injection Protection

**SQLAlchemy automatically uses parameterized queries:**

```python
# Safe! ✅
user_id = "1 OR 1=1"  # Malicious input
db.query(User).filter(User.id == user_id).first()

# Generated SQL:
# SELECT * FROM users WHERE id = ?
# Parameters: {'id_1': '1 OR 1=1'}
# Treats entire string as a VALUE, not SQL code!
```

**Why it's safe:**
1. SQL structure is defined first: `WHERE id = ?`
2. User input fills placeholder as DATA
3. Database knows: "This is a value, not code"
4. SQL injection commands are treated as harmless strings

**Dangerous (raw SQL):**
```python
# NEVER DO THIS! ❌
query = f"SELECT * FROM users WHERE id = {user_input}"
# user_input = "1; DROP TABLE users; --"
# Your table gets deleted! 💀
```

---

## 🧠 Data Transformation Concepts

### Mapping, Serialization, Encoding, Encryption

**Mapping (General concept):**
Converting data from one format to another

**Serialization:**
Converting objects → bytes/text for storage/transmission

```python
# Serialization
python_dict = {"name": "ram", "age": 25}
json_string = json.dumps(python_dict)  # → '{"name": "ram", "age": 25}'

# Deserialization
restored_dict = json.loads(json_string)  # → {"name": "ram", "age": 25}
```

**Encoding:**
Converting text → bytes using a character set

```python
# Encoding
text = "Hello 🚀"
bytes_utf8 = text.encode('utf-8')  # → b'Hello \xf0\x9f\x9a\x80'

# Decoding
restored_text = bytes_utf8.decode('utf-8')  # → "Hello 🚀"
```

**Encryption:**
Converting readable → unreadable (for security)

```python
# Encryption
plaintext = "My password"
ciphertext = cipher.encrypt(plaintext)  # → Unreadable gibberish

# Decryption (with key)
restored = cipher.decrypt(ciphertext)  # → "My password"
```

**Comparison:**

| Type | Purpose | Changes Meaning? | Reversible? | Security? |
|------|---------|------------------|-------------|-----------|
| **Mapping** | Format conversion | ❌ No | ✅ Yes | ❌ No |
| **Serialization** | Storage/transmission | ❌ No | ✅ Yes | ❌ No |
| **Encoding** | Text ↔ Bytes | ❌ No | ✅ Yes | ❌ No |
| **Encryption** | Security/privacy | ❌ No | ✅ Yes (with key) | ✅ YES |

---

## 🏗️ SOLID Principles

### Single Responsibility Principle
**"A class should have one, and only one, reason to change."**

✅ Our structure:
- `database.py` → Only database connection
- `models.py` → Only database structure
- `schemas.py` → Only API validation
- `crud.py` → Only database operations
- `main.py` → Only API endpoints

### Open/Closed Principle
**"Open for extension, closed for modification."**

Can add new endpoints/models without changing existing code.

### Liskov Substitution Principle
**"Objects should be replaceable with subtypes."**

Could swap MySQL for PostgreSQL without breaking code.

### Interface Segregation Principle
**"Many specific interfaces better than one general."**

Separate schemas for Create, Update, Response instead of one giant schema.

### Dependency Inversion Principle
**"Depend on abstractions, not implementations."**

`Depends(get_db)` injects Session abstraction, not specific database implementation.

---

## 🧪 Tests Created

### test_db.py - ORM Connection Test

Tests:
1. Query all users
2. Get specific user by ID
3. Get conversations
4. Use relationships (user.conversations)
5. Reverse relationships (conversation.user)

**Key observation:** Lazy loading - conversations query only runs when accessed!

### test_crud.py - CRUD Operations Test

Tests:
1. Get all users
2. Get user by ID
3. Get user by email
4. Count user's conversations
5. Get user's conversations
6. Get user with conversations (JOIN)
7. Create new conversation
8. Update conversation
9. Delete conversation
10. Pagination

**All tests passed!** ✅

---

## 📊 Project Structure (After Session 9)

```
fastapi_practice/
├── main.py                 # FastAPI endpoints (from previous sessions)
├── database.py             # ✨ NEW: Database connection setup
├── models.py               # ✨ NEW: SQLAlchemy models
├── schemas.py              # ✨ NEW: Pydantic schemas
├── crud.py                 # ✨ NEW: CRUD operations
├── schema.sql              # Database schema (Session 8)
├── test_db.py              # ✨ NEW: ORM connection test
├── test_crud.py            # ✨ NEW: CRUD operations test
└── session_notes/
    ├── session_1.md through session_8.md
    └── session_9.md        # This file
```

---

## 💡 Key Takeaways

### What We Learned

1. **ORM Concepts:**
   - Object-Relational Mapping bridges Python and SQL
   - Write Python code instead of SQL strings
   - Automatic connection management

2. **SQLAlchemy Architecture:**
   - Engine → Connection pool
   - SessionLocal → Session factory
   - Base → Model foundation
   - Models → Table definitions
   - Relationships → One-to-many connections

3. **Pydantic vs SQLAlchemy:**
   - SQLAlchemy → Database ORM
   - Pydantic → API validation
   - Different purposes, work together

4. **CRUD Operations:**
   - Separation of concerns
   - Reusable database functions
   - Centralized query logic

5. **Advanced Concepts:**
   - Dependency injection with `yield`
   - Lazy vs eager loading
   - Pagination with skip/limit
   - Partial updates with `exclude_unset`
   - SQL injection protection
   - Transaction management (commit/rollback)

### Best Practices

1. ✅ Use dependency injection for database sessions
2. ✅ Separate SQLAlchemy models from Pydantic schemas
3. ✅ Put CRUD operations in separate file
4. ✅ Use `autocommit=False` for transaction control
5. ✅ Always close sessions (use `try/finally` or `yield`)
6. ✅ Use relationships for connected data
7. ✅ Use eager loading when you know you'll need related data
8. ✅ Implement pagination for large datasets
9. ✅ Use parameterized queries (SQLAlchemy does this automatically)
10. ✅ Validate with Pydantic, store with SQLAlchemy

---

## 🔄 Git Workflow

**Files committed:**
- database.py
- models.py
- schemas.py
- crud.py
- test_db.py
- test_crud.py

**Commit message:**
```
Add SQLAlchemy ORM integration with MySQL

- Create database.py: Connection setup, engine, SessionLocal, dependency injection
- Create models.py: User and Conversation SQLAlchemy models with relationships
- Create schemas.py: Pydantic schemas for API validation and serialization
- Create crud.py: Complete CRUD operations for users and conversations
- Add test_db.py: Test ORM connection and relationships
- Add test_crud.py: Test all CRUD operations

Features:
- One-to-many relationship (User has many Conversations)
- Foreign key constraints
- Eager loading with joinedload()
- Pagination support (skip/limit)
- Partial updates with exclude_unset
- Parameterized queries for SQL injection protection
```

**Lines of code:** 778 lines added

---

## 🚀 What's Next?

**Session 10 will cover:**
- Integrating CRUD operations with FastAPI endpoints
- Creating REST API endpoints using our CRUD functions
- Response models and error handling
- Testing endpoints with FastAPI's TestClient
- Real-world business logic implementation

**We'll build endpoints like:**
```python
POST   /users              # Create user
GET    /users              # List users (with pagination)
GET    /users/{id}         # Get specific user
PUT    /users/{id}         # Update user
DELETE /users/{id}         # Delete user

POST   /conversations      # Create conversation
GET    /conversations      # List conversations
GET    /users/{id}/conversations  # Get user's conversations
```

---

## 📝 Commands Used

### Installation
```bash
pip3 install sqlalchemy pymysql
```

### Testing
```bash
python3 test_db.py
python3 test_crud.py
```

### Git
```bash
git status
git add database.py models.py schemas.py crud.py test_db.py test_crud.py
git commit -m "Add SQLAlchemy ORM integration with MySQL..."
git log -1 --stat
```

---

## 🎓 Quiz Questions & Answers

### Q1: What is ORM?
**A:** Object-Relational Mapping - a technique to interact with databases using Python objects instead of SQL queries.

### Q2: What's the difference between SQLAlchemy models and Pydantic schemas?
**A:**
- SQLAlchemy models → Database ORM (Python ↔ SQL)
- Pydantic schemas → API validation (JSON ↔ Python)

### Q3: What does `yield` do in `get_db()`?
**A:** Pauses the function, gives the session to the endpoint, resumes after endpoint finishes to close the session.

### Q4: Why use `autocommit=False`?
**A:** Gives manual control over transactions - can commit or rollback. Prevents partial/inconsistent updates.

### Q5: What is lazy loading?
**A:** Related data is only queried when you access it, not when you query the parent object.

### Q6: What does `exclude_unset=True` do?
**A:** Only includes fields that were actually set by the user, excludes fields with default values.

### Q7: How does pagination work?
**A:** Use `skip` (offset) and `limit` to load data in chunks. Formula: skip = (page - 1) * limit

### Q8: Why are parameterized queries safe?
**A:** SQL structure is defined first, user input is treated as DATA (not code), prevents SQL injection.

### Q9: What's the difference between `get_user_conversations()` and `get_user_with_conversations()`?
**A:**
- `get_user_conversations()` → Returns LIST of Conversation objects
- `get_user_with_conversations()` → Returns ONE User object with conversations loaded (eager loading)

### Q10: What does `db.refresh()` do?
**A:** Fetches database-generated values (like id, created_at) back to the Python object after commit.

---

**Session Duration:** ~4 hours
**Concepts Covered:** 15+ major topics
**Code Written:** 778 lines
**Git Commits:** 1

**Status:** ✅ Session 9 Complete! Ready for FastAPI endpoint integration in Session 10!
