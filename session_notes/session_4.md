# Session 4 - POST Requests & Pydantic Models

**Date:** October 12, 2025
**Phase:** 1.4 - Request Body & POST Requests

---

## Commands Used

### Git Commands
- `git checkout -b feature/post-requests` - Create feature branch
- `git diff main.py` - Show changes in specific file
- `git diff --stat` - Show summary statistics of changes
- `git add main.py` - Stage file for commit
- `git commit -m "message"` - Commit with descriptive message
- `git checkout main` - Switch to main branch
- `git merge feature/post-requests` - Merge feature (fast-forward)
- `git branch -d feature/post-requests` - Delete merged branch
- `git log --oneline -5` - Show last 5 commits

### Testing POST Requests
```bash
# Create JSON file (avoid shell escaping issues)
cat > /tmp/message.json << 'EOF'
{
  "text": "Hello from FastAPI!",
  "user_name": "Alice"
}
EOF

# Send POST request with JSON body
curl -X POST http://127.0.0.1:8000/messages \
  -H 'Content-Type: application/json' \
  -d @/tmp/message.json
```

**Key parts:**
- `-X POST` - Use POST method
- `-H 'Content-Type: application/json'` - Specify JSON content
- `-d @/tmp/message.json` - Send data from file

---

## Concepts Covered

### HTTP Methods: GET vs POST

| Feature | GET | POST |
|---------|-----|------|
| **Purpose** | Retrieve/Read data | Create/Send data |
| **Has request body?** | ❌ No (only URL params) | ✅ Yes (can send complex data) |
| **Data visible in URL** | ✅ All data in URL | ❌ Data hidden in body |
| **Cacheable** | ✅ Yes | ❌ Usually not |
| **Idempotent** | ✅ Yes (same result each time) | ❌ Not necessarily |
| **Examples** | View page, search, list items | Submit form, upload file, create user |

**Real-world examples:**
- **GET**: Viewing YouTube videos, searching Google, reading tweets, fetching user profile
- **POST**: Submitting contact form, uploading profile picture, creating account, posting tweet

---

### Request Body vs URL Parameters

**GET Request (data in URL):**
```
GET /search?q=laptop&limit=10&sort=price
```
- All data visible in URL
- Limited size (~2000 characters)
- Simple key-value pairs
- Good for: filtering, pagination, search

**POST Request (data in body):**
```
POST /messages
Content-Type: application/json

{
  "text": "Hello from FastAPI!",
  "user_name": "Alice",
  "timestamp": 1234567890,
  "metadata": {
    "source": "web",
    "device": "mobile"
  }
}
```
- Data in request body (not URL)
- Can send large amounts of data
- Supports complex nested structures
- Good for: creating resources, complex data

---

### Pydantic Models - Data Classes

**What is Pydantic?**
- Python library for data validation and parsing #Parsing = breaking down raw input and converting it into a usable, structured form.
- Uses type hints and models  to validate data automatically
- FastAPI uses it for request/response validation

**BaseModel:**
- Base class from Pydantic
- All data models inherit from it
- Provides automatic validation

**Defining a model:**
```python
from pydantic import BaseModel

class Message(BaseModel):
    text: str           # Required field (no default)
    user_name: str      # Required field
    timestamp: int = 0  # Optional field (has default)
```

**What Pydantic provides:**
1. ✅ **Structure definition** - What fields exist and their types
2. ✅ **Automatic validation** - Checks types match
3. ✅ **Type conversion** - Converts compatible types
4. ✅ **Default values** - Uses defaults for optional fields
5. ✅ **Clear error messages** - Tells you exactly what's wrong
6. ✅ **Documentation** - Auto-generates API docs

---

### Required vs Optional Fields in Pydantic

**Required fields (no default value):**
```python
class Message(BaseModel):
    text: str          # Must be provided
    user_name: str     # Must be provided
```

**Request must include:**
```json
{
  "text": "Hello",
  "user_name": "Alice"
}
```

**Missing field → Error:**
```json
{
  "text": "Hello"
  // Missing user_name!
}
// Error: "Field required"
```

---

**Optional fields (has default value):**
```python
class Message(BaseModel):
    text: str
    user_name: str
    timestamp: int = 0      # Optional (defaults to 0)
    priority: str = "low"   # Optional (defaults to "low")
```

**Can omit optional fields:**
```json
{
  "text": "Hello",
  "user_name": "Alice"
  // timestamp defaults to 0
  // priority defaults to "low"
}
```

**Or provide them:**
```json
{
  "text": "Hello",
  "user_name": "Alice",
  "timestamp": 1234567890,
  "priority": "high"
}
```

---

### How FastAPI Uses Pydantic Models

**Decision rule:**
- **Pydantic model parameter** → Request body
- **Simple type parameter** → Query/path parameter

**Example:**
```python
# Request body (Pydantic model)
@app.post("/messages")
def create_message(message: Message):  # From request body
    return {"received": message.text}

# Query parameter (simple type)
@app.get("/search")
def search(q: str):  # From URL query string
    return {"query": q}

# Path parameter (in route)
@app.get("/users/{user_id}")
def get_user(user_id: int):  # From URL path
    return {"user_id": user_id}
```

---

### Pydantic Validation Flow

**What happens when a request comes in:**

```
1. Client sends POST request
   ↓
2. FastAPI reads JSON from request body
   ↓
3. Pydantic validates against model
   ├─ Check all required fields present?
   ├─ Check types match?
   ├─ Try type conversions if needed
   └─ Apply default values for optional fields
   ↓
4a. Valid → Create model instance → Call function
4b. Invalid → Return 422 error with details
```

**Key insight:** Validation happens BEFORE your function runs. Invalid data never reaches your code!

---

### Validation Error Examples

**Missing required field:**
```json
// Request
{
  "text": "Hello"
  // Missing: user_name
}

// Response (422 error)
{
  "detail": [{
    "type": "missing",
    "loc": ["body", "user_name"],
    "msg": "Field required",
    "input": {"text": "Hello"}
  }]
}
```

**Wrong type:**
```json
// Request
{
  "text": "Hello",
  "user_name": "Alice",
  "timestamp": "not_a_number"  // Should be int!
}

// Response (422 error)
{
  "detail": [{
    "type": "int_parsing",
    "loc": ["body", "timestamp"],
    "msg": "Input should be a valid integer, unable to parse string as an integer",
    "input": "not_a_number"
  }]
}
```

**Error response fields:**
- `type` - Error category (missing, int_parsing, etc.)
- `loc` - Location of error ([body, field_name])
- `msg` - Human-readable message
- `input` - What was actually received

---

### Accessing Model Fields

**Once validated, access fields with dot notation:**

```python
@app.post("/messages")
def create_message(message: Message):
    # Access fields
    text = message.text              # "Hello from FastAPI!"
    name = message.user_name         # "Alice"
    time = message.timestamp         # 0 or provided value

    # Use in logic
    return {
        "status": "received",
        "message_text": message.text,
        "from": message.user_name,
        "timestamp": message.timestamp
    }
```

---

## Git Concepts: Understanding Diffs

### What is `git diff`?

Shows **what changed** in your files before committing.

**Benefits:**
- ✅ Catch mistakes before committing
- ✅ Understand what you're committing
- ✅ Write better commit messages
- ✅ Review your work

---

### Reading Git Diff Output

**Basic structure:**
```diff
diff --git a/main.py b/main.py
index e4b25d8..162c82c 100644
--- a/main.py          # Old version
+++ b/main.py          # New version
@@ -1,9 +1,17 @@        # Chunk header
 # Import the FastAPI class from fastapi library
 from fastapi import FastAPI
+# Import BaseModel from pydantic for data validation
+from pydantic import BaseModel
```

**Symbols:**
- `---` - Old file (before changes)
- `+++` - New file (after changes)
- `-` (minus) - Line removed (shown in red)
- `+` (plus) - Line added (shown in green)
- No symbol - Unchanged line (context)

---

### Understanding Chunk Headers

**Format:** `@@ -<old_start>,<old_count> +<new_start>,<new_count> @@`

**Example:** `@@ -1,9 +1,17 @@`
- `-1,9` - OLD file: line 1, showing 9 lines
- `+1,17` - NEW file: line 1, showing 17 lines
- **Result:** 17 - 9 = 8 lines added

**Another example:** `@@ -30,3 +38,15 @@`
- `-30,3` - OLD file: line 30, showing 3 lines
- `+38,15` - NEW file: line 38, showing 15 lines (shifted by 8)
- **Result:** 15 - 3 = 12 lines added

---

### Git Diff Commands

**Show all changes:**
```bash
git diff              # All unstaged changes
git diff main.py      # Changes in specific file
```

**Show summary statistics:**
```bash
git diff --stat

# Output:
# main.py | 20 ++++++++++++++++++++
# 1 file changed, 20 insertions(+)
```
- Much easier to read!
- Shows files changed, insertions (+), deletions (-)

**Show staged changes:**
```bash
git diff --staged     # Changes that are staged for commit
```

**Compare branches:**
```bash
git diff main         # Compare current branch with main
```

---

## Code Written

### Updated main.py - POST Endpoint

```python
# Import the FastAPI class from fastapi library
from fastapi import FastAPI
# Import BaseModel from pydantic for data validation
from pydantic import BaseModel

# Create an instance of FastAPI application
app = FastAPI()

# Pydantic model: defines the structure and types for request body
class Message(BaseModel):
    text: str           # Message text (required)
    user_name: str      # Sender's name (required)
    timestamp: int = 0  # Unix timestamp (optional, default 0)

# Route decorator: handles GET requests at root endpoint "/"
@app.get("/")
def read_root():
    # FastAPI auto-converts Python dict to JSON response
    return {"message": "Hello World"}

# Path parameter: {user_id} is a dynamic variable in the URL
@app.get("/users/{user_id}")
def read_user(user_id: int):
    # user_id is extracted from URL and validated as integer
    return {"user_id": user_id, "message": f"Hello user {user_id}"}

# Query parameters: variables passed after ? in URL
@app.get("/search")
def search_items(q: str):
    # q is extracted from URL query string: /search?q=laptop
    return {"query": q, "message": f"Searching for: {q}"}

# Optional query parameter with default value
@app.get("/items")
def read_items(skip: int = 0, limit: int = 10):
    # skip and limit are optional - have default values
    return {"skip": skip, "limit": limit}

# POST request with request body using Pydantic model
@app.post("/messages")
def create_message(message: Message):
    # message parameter automatically validated against Message model
    # FastAPI extracts JSON from request body and validates it
    return {
        "status": "received",
        "message_text": message.text,
        "from": message.user_name,
        "timestamp": message.timestamp
    }
```

**Changes made:**
1. Added `from pydantic import BaseModel` import
2. Created `Message` Pydantic model
3. Added `@app.post("/messages")` endpoint

---

## Testing Notes

### Successful Tests

**Test 1: Valid data (no timestamp)**
```bash
# Request
{
  "text": "Hello from FastAPI!",
  "user_name": "Alice"
}

# Response
{
  "status": "received",
  "message_text": "Hello from FastAPI!",
  "from": "Alice",
  "timestamp": 0  # Default value used!
}
```

**Test 2: Valid data (with timestamp)**
```bash
# Request
{
  "text": "Second message",
  "user_name": "Bob",
  "timestamp": 1234567890
}

# Response
{
  "status": "received",
  "message_text": "Second message",
  "from": "Bob",
  "timestamp": 1234567890  # Provided value used!
}
```

---

### Validation Error Tests

**Test 3: Missing required field**
```bash
# Request
{
  "text": "Missing user_name!"
  // user_name not provided
}

# Response (422 Error)
{
  "detail": [{
    "type": "missing",
    "loc": ["body", "user_name"],
    "msg": "Field required",
    "input": {"text": "Missing user_name!"}
  }]
}
```

**Test 4: Wrong type**
```bash
# Request
{
  "text": "Test message",
  "user_name": "Charlie",
  "timestamp": "not_a_number"
}

# Response (422 Error)
{
  "detail": [{
    "type": "int_parsing",
    "loc": ["body", "timestamp"],
    "msg": "Input should be a valid integer, unable to parse string as an integer",
    "input": "not_a_number"
  }]
}
```

---

## Quiz Questions & Answers

### Q1: What's the main difference between GET and POST requests?
**Answer:**
- **GET** - Retrieve/read data, no request body, data in URL
- **POST** - Create/send data, has request body, data hidden from URL
- GET is for reading, POST is for creating/sending

---

### Q2: What is a Pydantic model and why do we use it?
**Answer:** A Pydantic model is a class that inherits from `BaseModel` and defines:
- The structure of data (what fields exist)
- Type of each field (str, int, etc.)
- Which fields are required vs optional
- Default values

We use it for automatic validation, type conversion, and clear error messages.

---

### Q3: How does FastAPI know a parameter should come from the request body?
**Answer:** If the parameter type is a **Pydantic model** (inherits from BaseModel), FastAPI automatically treats it as request body data. Simple types (str, int) are treated as query or path parameters.

---

### Q4: What makes a field required vs optional in a Pydantic model?
**Answer:**
- **Required** - No default value: `text: str`
- **Optional** - Has default value: `timestamp: int = 0`

---

### Q5: When does Pydantic validation happen?
**Answer:** **Before** your function runs! FastAPI validates the request against the Pydantic model first. If validation fails, your function never executes and a 422 error is returned.

---

### Q6: What information does a Pydantic validation error provide?
**Answer:**
- `type` - Error category (missing, int_parsing, etc.)
- `loc` - Exact location of error ([body, field_name])
- `msg` - Human-readable error message
- `input` - What was actually received

---

### Q7: What does `@@ -1,9 +1,17 @@` mean in git diff?
**Answer:**
- `-1,9` - OLD file: starting at line 1, showing 9 lines
- `+1,17` - NEW file: starting at line 1, showing 17 lines
- This chunk added 17 - 9 = 8 lines

---

### Q8: What's the easiest way to see a summary of git changes?
**Answer:** `git diff --stat` - Shows a simple summary with file names and number of insertions/deletions

---

### Q9: Can you send complex nested data in a POST request body?
**Answer:** Yes! JSON supports nested objects and arrays. You can define nested Pydantic models:
```python
class Address(BaseModel):
    city: str
    country: str

class User(BaseModel):
    name: str
    address: Address  # Nested model!
```

---

### Q10: Why review git diff before committing?
**Answer:** To:
- Catch mistakes and unintended changes
- Remove debug code or test data
- Understand what you're committing
- Write better, more accurate commit messages

---

## Git Workflow This Session

### Commits Made:
1. **Add POST endpoint with Pydantic request body validation** (`308da3b`)
   - Added BaseModel import from pydantic
   - Created Message model (text, user_name, timestamp)
   - Added POST /messages endpoint
   - Demonstrated validation for required/optional fields

### Branch Operations:
1. Created `feature/post-requests` branch
2. Made changes and tested thoroughly
3. Reviewed changes with `git diff`
4. Committed on feature branch
5. Switched to main
6. Merged (fast-forward)
7. Deleted feature branch

### Current State:
- On `main` branch
- 5 working endpoints (4 GET, 1 POST)
- Clean git history
- All changes tested and validated

### Best Practices Demonstrated:
1. ✅ Feature branch workflow
2. ✅ Review changes with `git diff` before committing
3. ✅ Use `git diff --stat` for quick overview
4. ✅ Write descriptive commit messages
5. ✅ Test thoroughly before merging
6. ✅ Clean up by deleting merged branches

---

## Key Takeaways

### FastAPI & Pydantic
1. **POST for creating** - Use POST when sending data to create resources
2. **Pydantic models** - Define structure and types for validation
3. **Required = no default** - Fields without defaults must be provided
4. **Optional = has default** - Fields with defaults can be omitted
5. **Validation first** - Pydantic validates before function runs
6. **Clear errors** - Pydantic tells you exactly what's wrong
7. **Request body** - Pydantic models come from request body, not URL

### Git
1. **Review before commit** - Use `git diff` to see what changed
2. **--stat for overview** - Quick summary of changes
3. **Chunk headers** - `@@ -old +new @@` shows line changes
4. **Catch mistakes** - Diff helps spot unintended changes
5. **Better commits** - Understanding changes → better commit messages

---

## Real-World Applications

### POST Requests in Practice

**Creating user account:**
```python
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    age: int = 18  # Optional, defaults to 18

@app.post("/users")
def create_user(user: UserCreate):
    # Validate, hash password, save to database
    return {"id": 123, "username": user.username}
```

**Submitting contact form:**
```python
class ContactForm(BaseModel):
    name: str
    email: str
    subject: str
    message: str
    phone: str = ""  # Optional

@app.post("/contact")
def submit_contact(form: ContactForm):
    # Send email, save to database
    return {"status": "sent"}
```

**Uploading data:**
```python
class DataUpload(BaseModel):
    filename: str
    content: str
    tags: list[str] = []  # Optional list

@app.post("/upload")
def upload_data(data: DataUpload):
    # Process and store data
    return {"uploaded": data.filename}
```

---

## Next Session Preview

**Phase 1.5: Response Models & Error Handling**
- Response models (controlling what you send back)
- HTTP status codes (200, 201, 404, 422, 500)
- Custom error handling
- Proper REST API responses
- Git: Viewing specific commit changes

---

**Commands to Review Before Next Session:**
- HTTP status codes (what do 200, 201, 404, 422 mean?)
- REST API best practices
- `git show <commit>` command
