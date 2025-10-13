# Session 5 - Response Models, Error Handling & Git Merges

**Date:** October 13, 2025
**Phase:** 1.5 - Response Models & HTTP Error Handling

---

## Commands Used

### Git Commands
- `git checkout -b feature/response-models` - Create feature branch
- `git diff --stat main.py` - Show summary of changes
- `git add main.py` - Stage file for commit
- `git commit -m "message"` - Commit changes
- `git show <commit-hash>` - View specific commit changes
- `git show <commit-hash> --stat` - View commit summary with stats
- `git show` - View latest commit (no hash needed)
- `git checkout main` - Switch to main branch
- `git merge feature/response-models` - Merge feature branch
- `git branch -d feature/response-models` - Delete merged branch
- `git log --oneline -5` - Show last 5 commits

### Testing with Status Codes
```bash
# Use -i flag to see HTTP headers (including status code)
curl -i http://127.0.0.1:8000/users/42        # 200 OK
curl -i http://127.0.0.1:8000/users/999       # 404 Not Found
curl -i -X POST http://127.0.0.1:8000/messages \
  -H 'Content-Type: application/json' \
  -d @/tmp/message.json                       # 201 Created
```

---

## Concepts Covered

### HTTP Status Codes

**HTTP status codes** are 3-digit numbers that tell the client what happened with their request.

#### The 5 Categories

| Range | Category | Meaning | When to Use |
|-------|----------|---------|-------------|
| **1xx** | Informational | Request received, processing continues | Rare in APIs |
| **2xx** | Success | Request was successful | Everything worked! |
| **3xx** | Redirection | Further action needed | Resource moved |
| **4xx** | Client Error | Client made a mistake | Bad request format, auth issues |
| **5xx** | Server Error | Server failed | Database down, code bugs |

---

#### Common Status Codes - Detailed

**2xx Success Codes:**

| Code | Name | When to Use | Example |
|------|------|-------------|---------|
| **200** | OK | Standard success | GET request returned data |
| **201** | Created | Resource successfully created | POST created new user |
| **204** | No Content | Success but no response body | DELETE removed item |

**4xx Client Error Codes:**

| Code | Name | When to Use | Example |
|------|------|-------------|---------|
| **400** | Bad Request | Malformed request syntax | Invalid JSON format |
| **401** | Unauthorized | Authentication required | No login token provided |
| **403** | Forbidden | Authenticated but no permission | User can't access admin area |
| **404** | Not Found | Resource doesn't exist | User ID 999 not in database |
| **409** | Conflict | Request conflicts with current state | Email already registered |
| **422** | Unprocessable Entity | Validation failed | FastAPI/Pydantic validation errors |

**5xx Server Error Codes:**

| Code | Name | When to Use | Example |
|------|------|-------------|---------|
| **500** | Internal Server Error | Generic server error | Unhandled exception in code |
| **502** | Bad Gateway | Invalid response from upstream | API gateway error |
| **503** | Service Unavailable | Server temporarily down | Maintenance mode |

---

#### Why Status Codes Matter

**Example: Creating a user**

```python
POST /users
Body: {"name": "Alice", "email": "alice@example.com"}
```

**Different outcomes communicate intent:**
- ✅ **201 Created** - User created successfully, check Location header for new resource
- ❌ **400 Bad Request** - JSON is malformed or missing required fields
- ❌ **409 Conflict** - Email already exists in system
- ❌ **422 Unprocessable Entity** - Email format invalid (failed validation)
- ❌ **500 Internal Server Error** - Database connection failed

**The client knows exactly what happened just by looking at the status code!** No need to parse error messages.

---

### FastAPI Response Models

**Response models** define the structure of what your API returns.

#### What is a Response Model?

```python
class MessageResponse(BaseModel):
    id: int
    status: str
    message_text: str
    from_user: str
    timestamp: int
```

**Think of it as a contract:** "I promise to return data in this exact format"

---

#### Request Model vs Response Model

**Request Model** (what client sends):
```python
class Message(BaseModel):
    text: str           # Client provides this
    user_name: str      # Client provides this
    timestamp: int = 0  # Optional
```

**Response Model** (what API returns):
```python
class MessageResponse(BaseModel):
    id: int                # SERVER generates this
    status: str            # SERVER adds this
    message_text: str      # From request
    from_user: str         # From request
    timestamp: int         # From request or default
```

**Key difference:** Response model includes server-generated fields (id, status) that client doesn't send.

---

#### Using Response Models in Endpoints

**Syntax:**
```python
@app.post("/messages", response_model=MessageResponse)
def create_message(message: Message):
    return MessageResponse(...)
```

**What `response_model=MessageResponse` does:**

1. ✅ **Validates response** - Ensures your function returns correct structure
2. ✅ **Filters fields** - Only returns fields defined in model
3. ✅ **Auto documentation** - Generates API docs automatically
4. ✅ **Type safety** - Catches bugs at development time
5. ✅ **Serialization** - Converts Python objects to JSON

**Example:**
```python
@app.post("/messages", response_model=MessageResponse, status_code=201)
def create_message(message: Message):
    # Even if you return extra fields, only MessageResponse fields are sent
    return MessageResponse(
        id=42,
        status="created",
        message_text=message.text,
        from_user=message.user_name,
        timestamp=message.timestamp
    )
```

---

### HTTPException - Custom Error Handling

**`HTTPException`** allows you to raise custom errors with specific status codes.

#### When to Use HTTPException

**Two types of errors:**

**1. Validation Errors (Automatic - Pydantic):**
```python
# Client sends wrong type
{"text": "hi", "user_name": 123}  # user_name should be string!
# Pydantic automatically returns 422 error
# You don't write any code for this!
```

**2. Business Logic Errors (Manual - HTTPException):**
```python
# Your application logic determines error
if user_id > 100:
    raise HTTPException(
        status_code=404,
        detail="User not found"
    )
```

---

#### HTTPException Syntax

```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,  # HTTP status code
    detail="User with ID 999 not found"      # Error message to client
)
```

**Parameters:**
- `status_code` - HTTP status code (404, 403, 409, etc.)
- `detail` - Error message (string or dict)

---

#### Common HTTPException Patterns

**404 - Not Found:**
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = database.get_user(user_id)  # Check database
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user
```

**403 - Forbidden:**
```python
@app.delete("/posts/{post_id}")
def delete_post(post_id: int, current_user: User):
    post = get_post(post_id)
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this post"
        )
    delete(post)
    return {"status": "deleted"}
```

**409 - Conflict:**
```python
@app.post("/users")
def create_user(user: UserCreate):
    if email_exists(user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    return create_new_user(user)
```

---

#### HTTPException Response Format

**What client receives:**
```json
{
  "detail": "User with ID 999 not found"
}
```

**With HTTP status code in headers:**
```
HTTP/1.1 404 Not Found
Content-Type: application/json

{"detail":"User with ID 999 not found"}
```

---

### Setting Custom Status Codes

**Default status codes:**
- GET, PUT, DELETE → **200 OK**
- POST → **200 OK** (but should be 201!)

**Override with `status_code` parameter:**
```python
@app.post("/messages", status_code=status.HTTP_201_CREATED)
def create_message(message: Message):
    return {...}
```

**Common patterns:**

| HTTP Method | Default | Best Practice |
|-------------|---------|---------------|
| GET | 200 OK | 200 OK ✓ |
| POST (create) | 200 OK | **201 Created** |
| PUT (update) | 200 OK | 200 OK ✓ |
| DELETE | 200 OK | **204 No Content** |

---

## Git Concepts: Git Show & Merge Types

### Git Show Command

**`git show`** displays what changed in a specific commit.

**Difference from `git diff`:**
- `git diff` - Shows **current unstaged** changes (work in progress)
- `git show` - Shows changes from a **specific historical commit**

---

#### Git Show Usage

**Basic syntax:**
```bash
git show <commit-hash>    # Show specific commit
git show                   # Show latest commit (HEAD)
git show HEAD~1           # Show commit before latest
git show HEAD~2           # Show 2 commits before latest
```

**With options:**
```bash
git show <hash> --stat              # Summary with file stats
git show <hash> --name-only         # Just file names
git show <hash> main.py             # Show changes to specific file
git show <hash> --pretty=format:"%h - %s"  # Custom format
```

---

#### Git Show Output Format

```bash
$ git show 308da3b --stat

commit 308da3b75569438ef21bb66a23670f0b631cf86f
Author: Ace-cli <rajdeepkuntal@gmail.com>
Date:   Sun Oct 12 17:03:51 2025 +0530

    Add POST endpoint with Pydantic request body validation

    - Import BaseModel from pydantic for data validation
    - Create Message model with text, user_name, timestamp fields

 main.py | 20 ++++++++++++++++++++
 1 file changed, 20 insertions(+)
```

**Shows:**
1. Commit hash, author, date
2. Full commit message
3. File statistics
4. Complete diff (line-by-line changes)

---

#### When to Use Git Show

**Useful for:**
- ✅ Reviewing what changed in a past commit
- ✅ Understanding why something was changed (commit message context)
- ✅ Debugging: "What changed when this bug appeared?"
- ✅ Learning from history: "How did they implement this feature?"
- ✅ Code review of specific commits

**Example workflow:**
```bash
# Something broke, find when
git log --oneline
# 8703f81 Add response models  ← Suspicious
# 308da3b Add POST endpoint
# a2d20eb Add session 4 notes

# Review the suspicious commit
git show 8703f81

# See what changed in that file
git show 8703f81 main.py
```

---

### Git Merge Types

Git has several ways to combine branches. Each serves different purposes.

---

#### 1. Fast-Forward Merge (What We've Been Using)

**What it is:** Simply moves the branch pointer forward. No merge commit created.

**When it happens:**
- No divergent changes between branches
- Target branch has no new commits since feature branch was created
- Linear history (one straight line)

**Visual:**
```
Before merge:
main:     A -- B -- C
                    \
feature:             D -- E

After fast-forward merge:
main:     A -- B -- C -- D -- E
```

**Command:**
```bash
git checkout main
git merge feature-branch
# Output: "Fast-forward"
```

**Pros:**
- ✅ Clean, linear history
- ✅ No extra merge commits
- ✅ Easy to understand timeline

**Cons:**
- ❌ Loses information about which commits were part of a feature
- ❌ Can't tell when feature was merged vs committed

**Best for:**
- Solo development
- Small features
- When you want simple history

---

#### 2. Three-Way Merge (Merge Commit)

**What it is:** Creates a new "merge commit" that combines changes from both branches.

**When it happens:**
- Both branches have new commits since they diverged
- There are parallel lines of development
- Cannot fast-forward

**Visual:**
```
Before merge:
          C -- D     (main)
         /
    A -- B
         \
          E -- F     (feature)

After three-way merge:
          C -- D ----
         /            \
    A -- B              G (merge commit)
         \            /
          E -- F ----
```

**Command:**
```bash
git checkout main
git merge feature-branch
# Creates merge commit with message: "Merge branch 'feature-branch'"
```

**Prevents fast-forward:**
```bash
git merge --no-ff feature-branch  # Force merge commit even if could fast-forward
```

**Pros:**
- ✅ Preserves complete history
- ✅ Shows when feature was merged
- ✅ Easy to revert entire feature (revert the merge commit)
- ✅ Clear feature boundaries in history

**Cons:**
- ❌ More complex history graph
- ❌ Extra merge commits can clutter log

**Best for:**
- Team collaboration
- Large features
- When you need to track feature integration

---

#### 3. Squash Merge

**What it is:** Combines all commits from feature branch into a single commit on main.

**When it happens:** When you explicitly use `--squash`

**Visual:**
```
Before squash merge:
main:     A -- B -- C
                    \
feature:             D -- E -- F (3 commits)

After squash merge:
main:     A -- B -- C -- G (1 commit with all D+E+F changes)
```

**Command:**
```bash
git checkout main
git merge --squash feature-branch
git commit -m "Add entire feature in one commit"
```

**Pros:**
- ✅ Clean main branch history (one commit per feature)
- ✅ Hides messy work-in-progress commits
- ✅ Easy to revert entire feature
- ✅ Good for pull request workflows

**Cons:**
- ❌ Loses detailed commit history
- ❌ Can't see incremental development
- ❌ Harder to debug which specific change caused issues

**Best for:**
- Features with many small "fix typo" commits
- When you want clean main branch history
- GitHub pull request workflows
- Open source projects

---

#### 4. Rebase (Not Technically a Merge)

**What it is:** Moves feature branch commits to the tip of main, rewriting history.

**When it happens:** When you use `git rebase`

**Visual:**
```
Before rebase:
          C -- D     (main)
         /
    A -- B
         \
          E -- F     (feature)

After rebase:
main:     A -- B -- C -- D
                          \
feature:                   E' -- F' (rewritten commits)

Then fast-forward merge:
main:     A -- B -- C -- D -- E' -- F'
```

**Command:**
```bash
git checkout feature-branch
git rebase main          # Move feature commits onto main
git checkout main
git merge feature-branch # Now can fast-forward
```

**Pros:**
- ✅ Linear history (looks like it was developed sequentially)
- ✅ No merge commits
- ✅ Clean, professional-looking history

**Cons:**
- ❌ Rewrites commit history (changes commit hashes)
- ❌ Dangerous if branch is shared with others
- ❌ Can have complex conflicts

**Best for:**
- Cleaning up feature branches before merging
- Solo development
- When you want perfectly linear history

**⚠️ Golden Rule of Rebase:**
**Never rebase commits that have been pushed to shared branches!**

---

### Comparison of Merge Types

| Feature | Fast-Forward | Three-Way | Squash | Rebase |
|---------|-------------|-----------|--------|--------|
| **Creates merge commit** | No | Yes | Yes | No |
| **Preserves all commits** | Yes | Yes | No | Yes |
| **Linear history** | Yes | No | Yes | Yes |
| **Rewrites history** | No | No | No | Yes |
| **Best for** | Solo, simple | Teams, features | Clean history | Clean history |
| **Can revert easily** | No | Yes | Yes | No |

---

### Choosing a Merge Strategy

**Use Fast-Forward when:**
- Working alone
- Simple, linear development
- Want clean history automatically

**Use Three-Way Merge when:**
- Working in a team
- Want to preserve feature branch context
- Need to easily revert entire features

**Use Squash Merge when:**
- Feature has messy commit history
- Want one commit per feature on main
- Using GitHub pull requests

**Use Rebase when:**
- Want linear history
- Branch is local (not pushed)
- Need to update feature with latest main changes

---

### Our Session Workflow (Fast-Forward)

**What we did:**
```bash
1. git checkout -b feature/response-models  # Create branch
2. # Make changes, commit
3. git checkout main                         # Switch to main
4. git merge feature/response-models        # Fast-forward merge
5. git branch -d feature/response-models    # Clean up
```

**Why fast-forward worked:**
- Main had no new commits while we worked on feature
- Linear development path
- Simple, clean history

---

## Code Written

### Updated main.py - Response Models & Error Handling

```python
# Import the FastAPI class from fastapi library
from fastapi import FastAPI, HTTPException, status
# Import BaseModel from pydantic for data validation
from pydantic import BaseModel

# Create an instance of FastAPI application
app = FastAPI()

# Pydantic model: defines the structure and types for request body
class Message(BaseModel):
    text: str           # Message text (required)
    user_name: str      # Sender's name (required)
    timestamp: int = 0  # Unix timestamp (optional, default 0)

# Response model: defines what the API returns
class MessageResponse(BaseModel):
    id: int                    # Message ID
    status: str                # Status message
    message_text: str          # The message content
    from_user: str             # Sender's name
    timestamp: int             # When message was received

# Route decorator: handles GET requests at root endpoint "/"
@app.get("/")
def read_root():
    # FastAPI auto-converts Python dict to JSON response
    return {"message": "Hello World"}

# Path parameter with error handling
@app.get("/users/{user_id}")
def read_user(user_id: int):
    # Simulate checking if user exists (in real app: check database)
    # For demo: only users 1-100 exist
    if user_id < 1 or user_id > 100:
        # Raise 404 error if user doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    # User exists, return data
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

# POST request with response model and status code
@app.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(message: Message):
    # message parameter automatically validated against Message model
    # In real app: save to database and get real ID
    # For demo: generate fake ID
    fake_id = 42

    # Return response matching MessageResponse model
    return MessageResponse(
        id=fake_id,
        status="created",
        message_text=message.text,
        from_user=message.user_name,
        timestamp=message.timestamp
    )
```

**Changes made:**
1. Added `HTTPException` and `status` imports (line 2)
2. Created `MessageResponse` model (lines 15-21)
3. Updated `/users/{user_id}` with 404 error handling (lines 29-42)
4. Updated POST `/messages` with response model and 201 status (lines 59-74)

---

## Testing Notes

### Test Results Summary

| Test | URL | Expected | Status Code | Result |
|------|-----|----------|-------------|--------|
| Valid user | `/users/42` | Success | **200 OK** | ✅ `{"user_id":42,"message":"Hello user 42"}` |
| Invalid user | `/users/999` | Error | **404 Not Found** | ✅ `{"detail":"User with ID 999 not found"}` |
| Invalid user | `/users/0` | Error | **404 Not Found** | ✅ Custom error message |
| Create message | `POST /messages` | Created | **201 Created** | ✅ Returns MessageResponse with id |

---

### Detailed Test Output

**Test 1: Valid User (200 OK)**
```bash
$ curl -i http://127.0.0.1:8000/users/42

HTTP/1.1 200 OK
content-type: application/json

{"user_id":42,"message":"Hello user 42"}
```

**Test 2: Invalid User (404 Not Found)**
```bash
$ curl -i http://127.0.0.1:8000/users/999

HTTP/1.1 404 Not Found
content-type: application/json

{"detail":"User with ID 999 not found"}
```

**Test 3: Create Message (201 Created)**
```bash
$ curl -i -X POST http://127.0.0.1:8000/messages \
  -H 'Content-Type: application/json' \
  -d '{"text":"Hello","user_name":"Alice"}'

HTTP/1.1 201 Created
content-type: application/json

{
  "id": 42,
  "status": "created",
  "message_text": "Hello",
  "from_user": "Alice",
  "timestamp": 0
}
```

---

## Quiz Questions & Answers

### Q1: What HTTP status code should you return when successfully creating a resource?
**Answer:** **201 Created**, not 200 OK. This follows REST best practices and tells the client a new resource was created.

---

### Q2: What's the difference between Pydantic validation errors and HTTPException?
**Answer:**
- **Pydantic validation (422)** - Automatic type/format validation. You don't write code for this.
- **HTTPException (any status)** - Manual business logic errors. You raise these explicitly for rules like "user doesn't exist" or "permission denied".

---

### Q3: When would you use a 404 vs a 422 status code?
**Answer:**
- **404 Not Found** - Resource doesn't exist (e.g., user ID 999 not in database)
- **422 Unprocessable Entity** - Data validation failed (e.g., email format invalid, missing required field)

---

### Q4: What does `response_model=MessageResponse` do?
**Answer:**
1. Validates your response matches the model
2. Filters fields (only returns what's in model)
3. Auto-generates API documentation
4. Provides type safety
5. Serializes Python objects to JSON

---

### Q5: What's the difference between `git diff` and `git show`?
**Answer:**
- **git diff** - Shows current unstaged changes (work in progress)
- **git show** - Shows changes from a specific historical commit

---

### Q6: What is a fast-forward merge?
**Answer:** A merge where Git simply moves the branch pointer forward without creating a merge commit. Happens when there are no divergent changes between branches, resulting in linear history.

---

### Q7: When should you use `--no-ff` flag with git merge?
**Answer:** When you want to force a merge commit even if fast-forward is possible. Useful for preserving feature branch context and making it easy to revert entire features.

---

### Q8: What's the golden rule of git rebase?
**Answer:** **Never rebase commits that have been pushed to shared branches!** Rebasing rewrites history, which causes problems for collaborators who have pulled those commits.

---

### Q9: What happens when you raise HTTPException in a FastAPI function?
**Answer:**
1. Function execution stops immediately
2. FastAPI catches the exception
3. Returns error response with specified status code
4. Response body contains the detail message
5. Your function code after the exception never runs

---

### Q10: Why use a squash merge?
**Answer:** To combine all commits from a feature branch into a single commit on main. This keeps main branch history clean and hides messy work-in-progress commits. Great for features with many small "fix typo" commits.

---

### Q11: What status code does Pydantic return for validation errors?
**Answer:** **422 Unprocessable Entity** - FastAPI automatically returns this when Pydantic validation fails.

---

### Q12: How do you view changes from 2 commits ago?
**Answer:** `git show HEAD~2` - The `~2` means "2 commits before HEAD"

---

## Git Workflow This Session

### Commits Made:
1. **Add response models and HTTP error handling** (`8703f81`)
   - Added HTTPException and status imports
   - Created MessageResponse model
   - Added 404 error handling to /users endpoint
   - Updated POST with response_model and 201 status

### Branch Operations:
1. Created `feature/response-models` branch
2. Made changes and tested thoroughly
3. Committed on feature branch
4. Switched to main
5. Merged with fast-forward merge
6. Deleted feature branch

### Git Commands Learned:
- `git show <hash>` - View historical commit changes
- `git show --stat` - Commit summary with file statistics
- `git show HEAD~N` - View commit N steps back

### Current State:
- On `main` branch
- 5 endpoints with proper error handling
- Status codes: 200 OK, 201 Created, 404 Not Found, 422 Validation Error
- Clean git history

### Best Practices Demonstrated:
1. ✅ Feature branch workflow
2. ✅ Test before merging
3. ✅ Use `git show` to review historical commits
4. ✅ Proper HTTP status codes
5. ✅ Response models for structured output
6. ✅ HTTPException for business logic errors

---

## Key Takeaways

### FastAPI & HTTP
1. **Status codes matter** - They communicate what happened without parsing errors
2. **201 for POST** - Use 201 Created, not 200, when creating resources
3. **404 for missing** - Return 404 when resource doesn't exist
4. **Response models** - Define and validate what your API returns
5. **HTTPException** - Use for business logic errors (not validation)
6. **Pydantic validation** - Automatic 422 errors for type/format issues

### Git
1. **git show** - View any historical commit's changes
2. **Fast-forward** - Simplest merge, linear history
3. **Three-way merge** - Preserves feature context, creates merge commit
4. **Squash merge** - Clean main history, one commit per feature
5. **Rebase** - Linear history but rewrites commits (use carefully!)
6. **Choose wisely** - Different merge strategies for different needs

---

## Real-World Applications

### Status Code Patterns

**E-commerce API:**
```python
# Create order
POST /orders → 201 Created

# Get order
GET /orders/123 → 200 OK
GET /orders/999 → 404 Not Found

# Update order
PUT /orders/123 → 200 OK
PUT /orders/123 (already shipped) → 409 Conflict

# Cancel order
DELETE /orders/123 → 204 No Content
DELETE /orders/123 (not yours) → 403 Forbidden
```

**User Management:**
```python
# Register user
POST /users → 201 Created
POST /users (email exists) → 409 Conflict
POST /users (invalid email) → 422 Unprocessable Entity

# Get user
GET /users/123 → 200 OK
GET /users/123 (not logged in) → 401 Unauthorized
GET /users/123 (different user) → 403 Forbidden
```

---

### Merge Strategy Scenarios

**Solo Developer:**
```bash
# Use fast-forward for clean history
git checkout main
git merge feature-branch
# Result: Linear history, no merge commits
```

**Team with Large Features:**
```bash
# Use three-way merge to preserve context
git checkout main
git merge --no-ff feature-branch
# Result: Clear feature boundaries, easy to revert
```

**Open Source Project:**
```bash
# Use squash for clean main branch
git checkout main
git merge --squash contributor-branch
git commit -m "Add feature X from contributor"
# Result: One commit per feature, clean history
```

**Updating Feature Branch:**
```bash
# Use rebase to incorporate main changes
git checkout feature-branch
git rebase main
# Result: Feature branch up-to-date with main
```

---

## Common Patterns & Best Practices

### Error Handling Pattern

```python
@app.get("/resource/{id}")
def get_resource(id: int):
    # Check if resource exists
    resource = database.get(id)
    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource {id} not found"
        )

    # Check permissions
    if not user_can_access(resource):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

    return resource
```

### Response Model Pattern

```python
# Input model (what client sends)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# Response model (what API returns)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    # Note: password NOT included in response!

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    # Hash password, save to database
    new_user = save_user(user)
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        created_at=new_user.created_at
    )
```

---

## Next Session Preview

**Phase 2.1: Starting the Chatbot**
- Designing chatbot conversation flow
- State management (tracking conversation)
- Multiple endpoints for chat operations
- Testing conversation logic
- Git: Handling merge conflicts

---

**Commands to Review Before Next Session:**
- Think about how to structure a conversation
- What state needs to be tracked in a chatbot?
- Review sessions 1-5 notes for comprehensive understanding
