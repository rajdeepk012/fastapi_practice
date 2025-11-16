# Session 13: Motor/PyMongo & Document Mapping

**Date:** 2025-11-16
**Focus:** Async MongoDB driver (Motor), Pydantic models for MongoDB, CRUD operations
**Major Milestone:** Successfully connected Python to MongoDB with async operations!

---

## 🎯 Session Goals

- Understand async operations and why Motor is needed
- Install Motor (async MongoDB driver)
- Create MongoDB connection configuration
- Map Pydantic models to MongoDB documents
- Implement async CRUD operations
- Test all functionality

---

## 🔄 Why Motor? Understanding Async Operations

### The Problem: Blocking Operations

FastAPI is **async** (uses `async def`), but regular database drivers are synchronous (blocking).

**Without async (PyMongo - blocking):**
```
Server Timeline:

Request 1 comes in → Query database (WAITS 2s) → Can't handle Request 2!
                                            ↑
                                    Server is FROZEN!
```

**With async (Motor - non-blocking):**
```
Server Timeline:

Request 1 → Start query → (while waiting) → Handle Request 2! ✅
                ↓
            Result comes back → Return to Request 1
```

**Key insight:** Server can handle multiple requests while waiting for database!

---

### PyMongo vs Motor Comparison

| Feature | PyMongo | Motor |
|---------|---------|-------|
| **Type** | Synchronous (blocking) | Asynchronous (non-blocking) |
| **Works with** | Flask, Django | FastAPI, Tornado |
| **Syntax** | `db.users.find()` | `await db.users.find().to_list()` |
| **Performance** | One request at a time | Multiple requests concurrently |
| **When to use** | Simple scripts, sync apps | FastAPI, high-performance apps |

---

### Real-World Impact

**Scenario:** 100 users request `/users` simultaneously

**With PyMongo (blocking):**
```
100 users × 0.5 seconds each = 50 seconds total
Last user waits: 50 seconds! 😱
Server handles: 2 requests/second
```

**With Motor (async):**
```
All 100 users served in: ~0.5 seconds! 🎉
Server handles: 200+ requests/second
```

---

## 🎓 Quiz 1: Understanding Async

### Question 1: Why PyMongo Won't Work with FastAPI

**Your Answer:**
> "PyMongo is sequential it wait until output from previous call comes rather than handling different request, increase i/o operations time while fastapi by nature is prompt fast, it supports concurrent task rather than waiting for previous command output, PyMongo is compatible with old frameworks like flask and Django"

**✅ PERFECT!** You identified:
- Sequential/blocking nature
- I/O wait time impact
- FastAPI's concurrent capabilities
- Framework compatibility

---

### Question 2: What Does await Do?

**Your Answer:**
> "await don't wait for db.users.find() call output to come and hold everything else rather than it handles other thing and comes back to call when the output comes"

**✅ EXCELLENT!** Key points:
- Pauses the function, not the server
- Server can handle other requests
- Returns when result is ready

**Clarification:** `await` **does** wait for that specific function, but allows the **server** to handle other requests while waiting.

---

### Question 3: 10 Simultaneous Requests

**Your Answer:**
> "Pymongo handle one request at a time end to end and other request waits but in Motor it runs and handle multiple request call and service each as it is computed"

**✅ PERFECT!** You understood event-driven processing!

**PyMongo (Sequential):**
```
Request 1: |----Query (1s)----|----Response----|
Request 2:                      |----Query (1s)----|----Response----|
Total: 10 seconds for 10 requests
```

**Motor (Concurrent):**
```
Request 1-10: |----All queries run together (1s)----| All responses
Total: ~1 second for 10 requests! ⚡
```

---

## 📦 Installation

```bash
pip install motor
```

**Installed:**
- motor 3.7.1
- pymongo 4.15.4 (dependency)

---

## 📝 File Structure Created

```
fastapi_practice/
├── mongodb.py          # MongoDB connection configuration
├── mongo_models.py     # Pydantic models for MongoDB
├── mongo_crud.py       # Async CRUD operations
└── test_mongodb.py     # Test suite
```

---

## 🔧 MongoDB Configuration (mongodb.py)

### Connection Setup

```python
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://localhost:27017"

# Create async MongoDB client
client = AsyncIOMotorClient(
    MONGODB_URL,
    maxPoolSize=10,      # Max connections in pool
    minPoolSize=1        # Always keep 1 ready
)

# Get database reference
database = client.chatbot_db
```

---

### Connection Pool Concept

**What's a connection pool?**

Like keeping restaurant doors open:
- **Without pool:** Every customer opens kitchen door (slow!)
- **With pool:** Keep 10 doors open, customers use available ones (fast!)

**Why?**
- Creating connections is expensive (time + resources)
- Pool keeps connections ready to use
- Reuse instead of creating new ones
- "Redundant but net positive" (your words!) ✅

---

### Comparison: MySQL vs MongoDB Setup

**MySQL (database.py):**
```python
# Synchronous
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()  # New session per request
    try:
        yield db
    finally:
        db.close()
```

**MongoDB (mongodb.py):**
```python
# Asynchronous
client = AsyncIOMotorClient(MONGODB_URL)
database = client.chatbot_db  # Single client, reused

def get_database():
    return database  # Just return reference!
```

**Key differences:**
- MySQL: New session per request
- MongoDB: Single client, pool manages connections
- MySQL: Must close session
- MongoDB: No cleanup needed per request

---

## 🎓 Quiz 2: Understanding MongoDB Setup

### Question 1: client vs database

**Your Answer:**
> "client represents the actual connection we made to mongodb server and database represent the database which is in use which is client.chatbot_db where client is mongodb"

**✅ PERFECT!**

```
client = AsyncIOMotorClient(...)  → Connects to MongoDB Server
database = client.chatbot_db      → Points to specific database
```

---

### Question 2: Why Connection Pool?

**Your Answer:**
> "because it is resource and time intensive to create new connections for each new request rather we make more than one connection as time when we make our first connection which can be used when needed without creating new, it is redundant but net positive"

**✅ BRILLIANT!** Especially "redundant but net positive"! 🌟

**Performance:**
```
Without pool: 100ms (create) + 10ms (query) = 110ms per request
With pool:    10ms (query) = 10ms per request (11x faster!)
```

---

### Question 3: SessionLocal vs Motor

**Your Answer:**
> "SessionLocal() is synchronous and handle only one request at a time"

**✅ CORRECT!** Plus additional insight:
- MySQL: New session per request
- MongoDB: Shared client, pool manages connections

---

## 📊 Pydantic Models for MongoDB (mongo_models.py)

### Why No SQLAlchemy?

**Your Answer:**
> "because mongodb and python dictionary have similar structure they don't need translation and mongodb has javascript like structure they are both programming language structure and have similarities but in sql we have table like structure so we have to translate because the query structure is very different in application layer and sql db"

**💯 BRILLIANT!** You identified the fundamental difference!

**MongoDB (No Translation):**
```python
# Python dictionary
{"username": "alice", "email": "alice@example.com"}
        ↓ Direct mapping!
# MongoDB document
{"username": "alice", "email": "alice@example.com"}
```

**MySQL (Needs Translation):**
```python
# Python dictionary
{"username": "alice", "email": "alice@example.com"}
        ↓ SQLAlchemy translates ↓
# SQL table
┌──────────┬─────────────────────┐
│ username │ email               │
├──────────┼─────────────────────┤
│ alice    │ alice@example.com   │
└──────────┴─────────────────────┘
```

**Key insight:** MongoDB = dictionaries, SQL = tables (different structures!)

---

### PyObjectId - Custom Type

**Your Answer:**
> "well pydantic don't have any ObjectId type so we defined PyObjectId class so it can understand ObjectId and don't throw the error"

**✅ PERFECT!**

**The Problem:**
```python
# MongoDB returns:
{"_id": ObjectId("507f...")}

# Pydantic doesn't know what ObjectId is! ❌
```

**The Solution:**
```python
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        # Teach Pydantic about ObjectId
        # Pydantic v2 compatible! ✅
```

**Bug encountered:** Pydantic v1 → v2 compatibility issue
**Fix:** Updated to Pydantic v2 `__get_pydantic_core_schema__()` method

---

### Model Hierarchy

**Your Answer:**
> "different structure for different scenario for user request validation, mongo insert, response, loose coupling"

**💯 EXCELLENT!** You mentioned **loose coupling** - advanced concept! 🌟

```
UserBase          ← Common fields
    ↓
UserCreate        ← Client provides (POST)
UserUpdate        ← Client updates (PUT) - optional fields
UserInDB          ← Database document (_id, created_at)
    ↓
User              ← API response (safe fields)
```

**Benefits of loose coupling:**
- Security: Password never in API responses
- Validation: Client can't set `_id` or `created_at`
- Flexibility: Internal fields stay private
- Maintainability: Change one without breaking others

---

## 💻 CRUD Operations (mongo_crud.py)

### Key Differences from MySQL

**MySQL (Synchronous):**
```python
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()
```

**MongoDB (Asynchronous):**
```python
async def get_user(db, user_id: str):
    return await db.users.find_one({"_id": ObjectId(user_id)})
```

---

### find() vs to_list()

**Your Answer:**
> "well db.users.find() is a pointer which points to certain or several memory unit depending on the data, but does not contains the data or if not in python readable format, that's why we use .to_list() to get the data or convert into readable format for python"

**💯 EXCELLENT!** Perfect use of "pointer"!

```python
# Step 1: find() creates cursor (pointer)
cursor = db.users.find()  # ☞ Points to data, not loaded yet

# Step 2: to_list() fetches data
users = await cursor.to_list(length=100)  # ✅ Actual Python dictionaries
```

**Why this design?**
- Efficient for large datasets
- Don't load 1 million documents into memory
- Load in chunks (pagination)

---

### await Behavior

**Your Answer:**
> "awaits wait for function to return output without blocking the server (refusing more request), so it can handle multiple requests concurrently"

**✅ PERFECT!** Key insight: Server doesn't refuse requests!

```python
async def get_users():
    users = await db.users.find().to_list(100)
    #       ↑ Function pauses here, but server is FREE
    return users
```

---

### ObjectId Conversion

**Your Answer:**
> "because it is not stored as string internally so we have to convert it to ObjectID type"

**✅ CORRECT!**

```python
# In Python/API (string)
user_id = "507f1f77bcf86cd799439011"

# In MongoDB (ObjectId - special BSON type)
{"_id": ObjectId("507f1f77bcf86cd799439011")}

# Must convert for queries
await db.users.find_one({"_id": ObjectId(user_id)})
```

**Why ObjectId is better:**
- Globally unique (even across servers!)
- Includes timestamp (creation time)
- More efficient storage (12 bytes vs 24)
- Sortable by creation time

---

## 🧪 Testing Results

All tests passed! ✅

```
✅ TEST 1:  MongoDB Connection
✅ TEST 2:  Create User (ObjectId auto-generated)
✅ TEST 3:  Get User by ID
✅ TEST 4:  Get User by Email
✅ TEST 5:  Get All Users (5 found)
✅ TEST 6:  Update User (partial update)
✅ TEST 7:  Create Conversation
✅ TEST 8:  Get User Conversations (2 found)
✅ TEST 9:  Count User Conversations
✅ TEST 10: Delete User
```

---

## 📊 Complete Comparison Tables

### MySQL vs MongoDB: Setup

| Aspect | MySQL | MongoDB |
|--------|-------|---------|
| **Driver** | PyMySQL (sync) | Motor (async) |
| **ORM needed** | ✅ Yes (SQLAlchemy) | ❌ No (dictionaries) |
| **Files** | models.py + schemas.py | mongo_models.py |
| **Session** | New per request | Single client reused |
| **Cleanup** | Must close session | No cleanup needed |

---

### MySQL vs MongoDB: Queries

| Operation | MySQL (SQLAlchemy) | MongoDB (Motor) |
|-----------|-------------------|-----------------|
| **Create** | `db.add(user); db.commit()` | `await db.users.insert_one({...})` |
| **Read** | `db.query(User).filter(...).first()` | `await db.users.find_one({...})` |
| **Read All** | `db.query(User).all()` | `await db.users.find().to_list()` |
| **Update** | `user.field = value; db.commit()` | `await db.users.update_one({}, {"$set": {...}})` |
| **Delete** | `db.delete(user); db.commit()` | `await db.users.delete_one({...})` |

---

### MySQL vs MongoDB: IDs

| Aspect | MySQL | MongoDB |
|--------|-------|---------|
| **Type** | Integer (auto-increment) | ObjectId (generated) |
| **Format** | `1, 2, 3, ...` | `"507f1f77bcf86cd799439011"` |
| **Size** | 4-8 bytes | 12 bytes |
| **Metadata** | None | Includes timestamp! |
| **Global Unique** | Per table | Globally unique! |

---

## 🔑 Key Concepts Mastered

### 1. Async/Await Operations
- `async def` for async functions
- `await` pauses function, not server
- Server handles multiple requests concurrently
- Motor enables non-blocking database calls

### 2. Connection Pooling
- Pre-created connections ready to use
- Reuse instead of creating new ones
- "Redundant but net positive" trade-off
- Max/min pool size configuration

### 3. MongoDB Cursors
- `find()` returns pointer (cursor)
- `to_list()` fetches actual data
- Efficient for large datasets
- Supports pagination

### 4. ObjectId Handling
- MongoDB's unique identifier
- Must convert string → ObjectId for queries
- Includes timestamp metadata
- Globally unique across servers

### 5. Pydantic Models
- No ORM needed (dictionaries = documents)
- Custom PyObjectId type for validation
- Model hierarchy for loose coupling
- Pydantic v2 compatibility

### 6. Dictionary-Based Queries
- MongoDB queries use Python dictionaries
- No SQL translation needed
- `{"field": value}` filter syntax
- `{"$set": {...}}` update operator

---

## 🎯 Your Understanding Summary

**Exceptional concepts you demonstrated:**

| Concept | Your Insight | Status |
|---------|--------------|--------|
| **Async benefits** | "Concurrent tasks, not waiting" | 💯 |
| **Connection pool** | "Redundant but net positive" | 🌟 |
| **Cursor concept** | "Pointer to memory" | 💯 |
| **await behavior** | "Without blocking server" | 💯 |
| **No ORM needed** | "Dictionary = document structure" | 💯 |
| **Loose coupling** | Mentioned advanced concept! | 🌟 |

**Score: 100/100 with bonus points for advanced insights!** 🚀

---

## 📁 Files Created

```
mongodb.py (60 lines)
- Motor client configuration
- Connection pool setup
- Connect/disconnect functions

mongo_models.py (180 lines)
- PyObjectId custom type (Pydantic v2)
- User models (Base, Create, Update, InDB)
- Conversation models
- ChatRequest/Response models

mongo_crud.py (280 lines)
- Async user CRUD operations
- Async conversation CRUD operations
- ObjectId conversion handling
- Cursor to list conversions

test_mongodb.py (210 lines)
- Comprehensive test suite
- 10 test scenarios
- All tests passed! ✅
```

---

## 🎯 What We Accomplished

1. ✅ **Understood async operations** - Why Motor vs PyMongo
2. ✅ **Installed Motor** - Async MongoDB driver
3. ✅ **Configured MongoDB connection** - Connection pooling
4. ✅ **Created Pydantic models** - No ORM needed!
5. ✅ **Implemented CRUD operations** - All async
6. ✅ **Fixed Pydantic v2 bug** - PyObjectId compatibility
7. ✅ **Tested everything** - 10/10 tests passed!
8. ✅ **Committed to Git** - Clean implementation

---

## 🚀 What's Next?

**Session 14: MongoDB CRUD Operations with FastAPI**

You'll learn:
- Integrate MongoDB with FastAPI endpoints
- Create REST API for MongoDB
- Async dependency injection
- Error handling with ObjectId
- Compare MySQL vs MongoDB endpoints side-by-side

**Preview:**
```python
@app.post("/mongo/users")
async def create_mongo_user(user: mongo_models.UserCreate, db=Depends(get_database)):
    return await mongo_crud.create_user(db, user)
```

---

**Session Duration:** ~2.5 hours
**Lines of Code:** ~730 lines
**Tests:** 10/10 passed ✅
**Git Commits:** 1

**Status:** ✅ Session 13 Complete! Motor/PyMongo integration working!
