# Session 3 - Query Parameters & Optional Values

**Date:** October 12, 2025
**Phase:** 1.3 - Query Parameters

---

## Commands Used

### Git Commands
- `git checkout -b feature/query-parameters` - Create and switch to feature branch
- `git branch` - List branches and show current branch (*)
- `git status` - Check modified/untracked files
- `git add main.py` - Stage specific file for commit
- `git commit -m "message"` - Commit staged changes
- `git checkout main` - Switch back to main branch
- `git merge feature/query-parameters` - Merge feature into main (fast-forward)
- `git branch -d feature/query-parameters` - Delete merged branch
- `git log --oneline -6` - Show last 6 commits in compact format

### Testing Commands
- `curl "http://127.0.0.1:8000/search?q=laptop"` - Test required query parameter
- `curl "http://127.0.0.1:8000/search"` - Test missing required parameter (error)
- `curl "http://127.0.0.1:8000/search?q=ram&sam=10"` - Test with extra parameter
- `curl "http://127.0.0.1:8000/items"` - Test optional parameters (defaults used)
- `curl "http://127.0.0.1:8000/items?skip=5"` - Test partial parameters
- `curl "http://127.0.0.1:8000/items?skip=10&limit=50"` - Test all parameters provided

---

## Concepts Covered

### FastAPI Concepts

#### 1. Query Parameters vs Path Parameters

**URL Structure:**
```
http://127.0.0.1:8000/users/42?skip=5&limit=10
                      ^^^^^^^^ ^^^^^^^^^^^^^^^^
                      path     query string
```

**Comparison:**

| Feature | Path Parameter | Query Parameter |
|---------|---------------|-----------------|
| **Location** | In URL path: `/users/42` | After `?`: `?skip=5&limit=10` |
| **Syntax in code** | `{variable}` in route | Function parameter only |
| **Required** | Yes (by default) | Depends on default value |
| **Position matters** | Yes | No |
| **Multiple values** | Define multiple: `/{id}/{name}` | Separate with `&`: `?a=1&b=2` |

**Examples you see daily:**
- Google: `google.com/search?q=fastapi&lang=en`
- YouTube: `youtube.com/watch?v=VIDEO_ID`
- Amazon: `amazon.com/products?category=books&sort=price`

#### 2. How FastAPI Determines Parameter Type

**The Golden Rule:**

```python
@app.get("/users/{user_id}")           # user_id in path
def read_user(user_id: int, limit: int = 10):
    ...
```

**FastAPI's decision process:**
1. **Is parameter in path `{}`?** → Path parameter
2. **Only in function?** → Query parameter

**Visual:**
```python
# Path parameter - MUST be in route AND function
@app.get("/users/{user_id}")     # ← Declared here
def read_user(user_id: int):     # ← AND here
    ...

# Query parameter - ONLY in function
@app.get("/items")               # ← NOT in route
def read_items(skip: int = 0):   # ← ONLY here
    ...
```

#### 3. Required vs Optional Query Parameters

**Required (no default value):**
```python
@app.get("/search")
def search_items(q: str):  # No default = REQUIRED
    return {"query": q}

# Must provide: /search?q=something
# Error without it: "Field required"
```

**Optional (has default value):**
```python
@app.get("/items")
def read_items(skip: int = 0, limit: int = 10):  # Defaults = OPTIONAL
    return {"skip": skip, "limit": limit}

# Can omit: /items → uses defaults
# Can provide some: /items?skip=5 → skip=5, limit=10
# Can provide all: /items?skip=5&limit=20 → both custom
```

#### 4. Default Values Behavior

```python
def read_items(skip: int = 0, limit: int = 10):
    ...
```

**How it works:**
- `/items` → `skip=0, limit=10` (both defaults)
- `/items?skip=5` → `skip=5, limit=10` (one provided, one default)
- `/items?limit=20` → `skip=0, limit=20` (one default, one provided)
- `/items?skip=5&limit=20` → `skip=5, limit=20` (both provided)

**Order doesn't matter:**
- `/items?skip=5&limit=20` ✓ same as
- `/items?limit=20&skip=5` ✓

#### 5. Extra Parameters are Ignored

```python
@app.get("/search")
def search_items(q: str):  # Only defines 'q'
    return {"query": q}

# /search?q=laptop&extra=ignored
# FastAPI uses: q=laptop
# FastAPI ignores: extra=ignored
```

#### 6. Pydantic Validation for Query Parameters

Just like path parameters, query parameters get validated:

```python
def read_items(skip: int = 0):
    ...

# /items?skip=abc → Error: "Input should be a valid integer"
# /items?skip=5 → ✓ Validated and converted to int
```

**Error format:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "q"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

---

### Git Concepts

#### Branch Workflow (Reinforcement)

**Best Practice Workflow:**
```
1. Create feature branch: git checkout -b feature/name
2. Make changes and test
3. Commit on feature branch: git add . && git commit -m "msg"
4. Switch to main: git checkout main
5. Merge feature: git merge feature/name
6. Delete feature branch: git branch -d feature/name
```

**Why this workflow?**
- ✅ Keeps `main` stable
- ✅ Easy to experiment
- ✅ Can discard failed experiments
- ✅ Clean history

#### Fast-Forward Merge (Reinforcement)

When merging, if no divergent changes exist:
- Git moves `main` pointer forward
- No separate merge commit needed
- Linear, clean history

---

## Code Written

### Updated main.py - Query Parameters

```python
# Import the FastAPI class from fastapi library
from fastapi import FastAPI

# Create an instance of FastAPI application
app = FastAPI()

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
    # /items → skip=0, limit=10
    # /items?skip=5 → skip=5, limit=10
    # /items?skip=5&limit=20 → skip=5, limit=20
    return {"skip": skip, "limit": limit}
```

**New endpoints:**
1. `/search` - Required query parameter
2. `/items` - Optional query parameters with defaults

---

## Quiz Questions & Answers

### Q1: What's the difference between path parameters and query parameters in the URL?
**Answer:**
- **Path parameters** are embedded IN the URL path: `/users/42`
- **Query parameters** are appended AFTER the path with `?`: `/search?q=laptop`

Both are part of the URL, just in different sections.

---

### Q2: How does FastAPI know if a parameter is a path parameter or query parameter?
**Answer:**
1. If the parameter appears in the route path with `{}` → Path parameter
2. If the parameter only appears in the function → Query parameter

Example:
```python
@app.get("/users/{user_id}")  # user_id is path parameter
def read_user(user_id: int, limit: int = 10):  # limit is query parameter
    ...
```

---

### Q3: What makes a query parameter required vs optional?
**Answer:**
- **Required**: No default value → `q: str`
- **Optional**: Has default value → `skip: int = 0`

Required parameters must be provided or FastAPI returns "Field required" error.

---

### Q4: What happens if you visit `/items` without any query parameters?
**Answer:** The default values are used. With `def read_items(skip: int = 0, limit: int = 10)`, visiting `/items` returns `{"skip":0,"limit":10}`.

---

### Q5: Does the order of query parameters matter?
**Answer:** No! `/items?skip=5&limit=10` is the same as `/items?limit=10&skip=5`. Query parameters are key-value pairs, so order doesn't matter.

---

### Q6: What happens if you provide extra query parameters not defined in the function?
**Answer:** FastAPI ignores them. Example:
```python
def search_items(q: str):
    ...
# /search?q=laptop&extra=ignored
# FastAPI uses q, ignores extra
```

---

### Q7: Can you have both path and query parameters in the same endpoint?
**Answer:** Yes! Absolutely!
```python
@app.get("/users/{user_id}")
def read_user(user_id: int, limit: int = 10):
    # user_id from path: /users/42
    # limit from query: ?limit=20
    ...
```

---

### Q8: What error do you get if a required query parameter is missing?
**Answer:** Pydantic validation error with:
```json
{
  "detail": [{
    "type": "missing",
    "loc": ["query", "q"],
    "msg": "Field required"
  }]
}
```

---

### Q9: If you have `/items?skip=5`, what happens to the `limit` parameter?
**Answer:** The `limit` parameter uses its default value (10). So you get `{"skip":5,"limit":10}`. Each parameter independently uses its default if not provided.

---

### Q10: Can query parameters have type validation like path parameters?
**Answer:** Yes! Pydantic validates query parameters too. Example:
```python
def read_items(skip: int = 0):
    ...
# /items?skip=abc → Error: "Input should be a valid integer"
# /items?skip=5 → ✓ Validated and converted
```

---

## Testing Notes

### Successful Tests

**Required parameter:**
- ✓ `curl "/search?q=laptop"` → `{"query":"laptop","message":"Searching for: laptop"}`
- ✗ `curl "/search"` → Error: "Field required"

**Extra parameters ignored:**
- ✓ `curl "/search?q=ram&sam=10"` → `{"query":"ram","message":"Searching for: ram"}`
  - Used: `q=ram`
  - Ignored: `sam=10`

**Optional parameters with defaults:**
- ✓ `curl "/items"` → `{"skip":0,"limit":10}` (both defaults)
- ✓ `curl "/items?skip=5"` → `{"skip":5,"limit":10}` (one provided)
- ✓ `curl "/items?skip=10&limit=50"` → `{"skip":10,"limit":50}` (both provided)

---

## Git Workflow This Session

### Commits Made:
1. **Add query parameter endpoints** (`5ff37d2`)
   - Added `/search` with required query parameter
   - Added `/items` with optional parameters and defaults
   - Demonstrated difference between required and optional

### Branch Operations:
1. Created `feature/query-parameters` branch
2. Made changes and committed on feature branch
3. Switched back to `main`
4. Merged feature branch (fast-forward)
5. Deleted merged feature branch

### Current State:
- On `main` branch
- 6 total commits in history
- Clean, linear history with fast-forward merges

### Best Practices Demonstrated:
1. ✅ Feature branch workflow
2. ✅ Descriptive branch names
3. ✅ Meaningful commit messages
4. ✅ Fast-forward merges (clean history)
5. ✅ Delete merged branches

---

## Key Takeaways

### FastAPI
1. **Query parameters** come after `?` in URL: `/search?q=laptop`
2. **Default values** make parameters optional: `skip: int = 0`
3. **No default** makes parameters required: `q: str`
4. **FastAPI determines type** by whether parameter is in path `{}`
5. **Order doesn't matter** for query parameters
6. **Extra parameters ignored** - only defined ones extracted
7. **Pydantic validates** query parameters just like path parameters

### Git
1. **Feature branch workflow** keeps main stable
2. **Fast-forward merges** create clean history
3. **Delete merged branches** keeps repo organized
4. **Meaningful commits** document what and why

---

## Real-World Use Cases

### Query Parameters in the Wild:

**Pagination:**
```python
@app.get("/products")
def get_products(skip: int = 0, limit: int = 20):
    # /products?skip=20&limit=20  → Page 2
    ...
```

**Search & Filtering:**
```python
@app.get("/search")
def search(q: str, category: str = "all", sort: str = "relevance"):
    # /search?q=laptop&category=electronics&sort=price
    ...
```

**Combining Path & Query:**
```python
@app.get("/users/{user_id}/posts")
def get_user_posts(user_id: int, limit: int = 10):
    # /users/42/posts?limit=5
    ...
```

---

## Next Session Preview

**Phase 1.4: Request Body & POST Requests**
- POST vs GET requests
- Request body with Pydantic models
- Creating resources (not just reading)
- Data validation with complex objects
- Git: Reviewing diffs before committing

---

**Commands to Review Before Next Session:**
- HTTP methods (GET, POST, PUT, DELETE)
- What is a request body?
- Python classes and data models
- `git diff` command
