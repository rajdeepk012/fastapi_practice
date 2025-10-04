# Session 2 - Path Parameters & Git Branching

**Date:** October 4, 2025
**Phase:** 1.2 - Path Parameters & Git Branching

---

## Commands Used

### Git Branching Commands
- `git checkout -b <branch-name>` - Create and switch to new branch
  - Example: `git checkout -b feature/path-parameters`
- `git branch` - List all local branches (* shows current)
- `git checkout <branch>` - Switch to existing branch
- `git merge <branch>` - Merge specified branch into current branch
- `git branch -d <branch>` - Delete merged branch (safe)
- `git branch -D <branch>` - Force delete branch (even if not merged - dangerous!)
- `git log --oneline --graph` - Show commit history with branch visualization
- `git log --oneline --decorate` - Show commits with branch/tag pointers

### Git Remote Commands
- `git remote -v` - Show configured remote repositories
  - Shows fetch and push URLs
- `git push origin <branch>` - Upload local branch to remote
- `git fetch origin` - Download changes from remote (doesn't merge)
- `git pull origin <branch>` - Download and merge changes (fetch + merge)

### Server Testing
- `curl http://127.0.0.1:8000/users/42` - Test path parameter endpoint
- `curl http://127.0.0.1:8000/users/sa` - Test validation error

---

## Concepts Covered

### Git Concepts

#### 1. Branching Workflow
**Why use branches?**
- Keep `main` stable and working
- Experiment safely without breaking production code
- Easy to discard changes if something goes wrong
- Enable parallel development

**Branch workflow:**
```
1. Create feature branch
2. Make changes and commit
3. Test thoroughly
4. Switch to main
5. Merge feature branch
6. Delete feature branch (cleanup)
```

#### 2. Remote vs Local
**Local Repository:**
- Lives on your computer
- Your personal workspace
- Changes only you can see

**Remote Repository (origin):**
- Lives on GitHub/GitLab/etc.
- Shared storage in the cloud
- Collaboration point for teams

**Common workflow:**
```
Local: make changes → commit
Remote: push → share with team
Remote: teammates push changes
Local: fetch/pull → get updates
```

#### 3. Git Fetch vs Pull
**git fetch:**
- Downloads changes from remote
- Does NOT merge into your branch
- Safe - lets you review first
- Updates local copy of remote branches

**git pull:**
- Downloads AND merges automatically
- Equals: `git fetch` + `git merge`
- Faster but can cause conflicts
- Use when you trust incoming changes

**Best practice:** Use `fetch` to review, then `merge` manually when learning.

#### 4. Fast-Forward Merge
When we merged `feature/path-parameters` into `main`, Git said "Fast-forward":

**What is fast-forward?**
- No divergent changes between branches
- `main` simply moves forward to include new commits
- Linear history (no merge commit needed)
- Cleanest type of merge

```
Before merge:
main:     A -- B
                 \
feature:          C -- D

After fast-forward merge:
main:     A -- B -- C -- D
```

#### 5. HEAD Pointer
- **HEAD** = "You are here" marker in Git
- Points to current commit on current branch
- `HEAD -> main` means you're on main branch at its latest commit

---

### FastAPI Concepts

#### 1. Path Parameters
**What are they?**
- Dynamic variables in URL paths
- Captured and passed to your function
- Enclosed in curly braces: `{variable_name}`

**Example:**
```python
@app.get("/users/{user_id}")  # {user_id} is path parameter
def read_user(user_id: int):
    return {"user_id": user_id}
```

**URL mapping:**
- `/users/42` → `user_id = 42`
- `/users/999` → `user_id = 999`
- `/users/alice` → validation error!

#### 2. Type Hints with Validation
In Python, type hints are usually just documentation:
```python
def add(a: int, b: int):  # Just hints, not enforced
    return a + b

add("hello", "world")  # No error in regular Python!
```

**But FastAPI + Pydantic actually enforce them!**
```python
@app.get("/users/{user_id}")
def read_user(user_id: int):  # Enforced by Pydantic!
    return {"user_id": user_id}

# /users/42 ✓ works
# /users/abc ✗ validation error!
```

#### 3. Pydantic - The Validator
**What is Pydantic?**
- Python library for data validation and parsing
- Used by FastAPI for automatic validation
- Like a smart bouncer checking IDs at a club

**What Pydantic does:**
1. **Validates types** - Ensures data matches expected type
2. **Converts types** - String "42" → integer 42
3. **Returns clear errors** - Detailed JSON explaining what's wrong

**Example validation error:**
```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["path", "user_id"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "sa"
    }
  ]
}
```

**Why this is great:**
- ✅ Clear error messages for API consumers
- ✅ Shows exact location of problem
- ✅ Shows what was received vs expected
- ✅ Client knows how to fix request

#### 4. Automatic Type Conversion
FastAPI + Pydantic automatically convert compatible types:

```python
user_id: int

URL: /users/42
↓
Receives: "42" (string from URL)
↓
Pydantic validates: Can this be an int?
↓
Converts: "42" → 42 (integer)
↓
Your function gets: 42 (int)
```

**Invalid conversions return errors:**
- `/users/3.14` → Error (float, not int)
- `/users/abc` → Error (string, not parseable as int)

---

## Code Written

### Updated main.py
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
```

**New concepts in code:**
- `{user_id}` - Path parameter placeholder
- `user_id: int` - Type hint with validation
- `f"Hello user {user_id}"` - f-string for string interpolation

---

## Quiz Questions & Answers

### Q1: What does `{user_id}` in `@app.get("/users/{user_id}")` do?
**Answer:** It's a path parameter - a dynamic placeholder in the URL that captures whatever value is in that position. For example:
- `/users/42` → `user_id = 42`
- `/users/999` → `user_id = 999`

---

### Q2: What's the difference between type hints in regular Python vs FastAPI?
**Answer:**
- **Regular Python:** Type hints are just documentation, not enforced
- **FastAPI:** Type hints are enforced by Pydantic - they validate and convert data automatically

---

### Q3: What happens when you visit `/users/3.14` with `user_id: int`?
**Answer:** Pydantic validation error! The type hint expects an integer (whole number), but `3.14` is a float (decimal). FastAPI returns a detailed error explaining the type mismatch.

---

### Q4: What is Pydantic and how does FastAPI use it?
**Answer:** Pydantic is a Python library for data validation. FastAPI uses it to:
- Validate that incoming data matches type hints
- Convert compatible types automatically (e.g., string "42" → integer 42)
- Return detailed, helpful error messages when validation fails

---

### Q5: If changes are made on `feature/path-parameters` branch, will they affect `main`?
**Answer:** No! Branches are independent lines of development - like separate houses with copies of the code. Changes on one branch don't affect others until you explicitly merge them.

---

### Q6: What is `origin` in Git?
**Answer:** `origin` is the default name for the remote repository (usually on GitHub/GitLab). It's where you cloned the code from and where you push changes to share with others.

---

### Q7: What's the difference between `git fetch` and `git pull`?
**Answer:**
- **git fetch:** Downloads changes from remote but DOESN'T merge (safe, lets you review first)
- **git pull:** Downloads AND merges automatically (fetch + merge combined)

Best practice when learning: Use fetch to review, then merge manually.

---

### Q8: What does "Fast-forward" mean when merging?
**Answer:** Fast-forward means there are no divergent changes between branches. Git simply moves the `main` branch pointer forward to include the new commits. It creates a linear history without a separate merge commit.

---

### Q9: Why delete a feature branch after merging?
**Answer:** To keep your repository clean and organized. Once changes are merged into `main`, the feature branch is no longer needed. All its commits are preserved in `main`'s history.

---

### Q10: What does the `*` mean in `git branch` output?
**Answer:** The asterisk (*) shows which branch you're currently on (where HEAD points).

---

## Git Workflow This Session

### Commits Made:
1. **Add path parameter endpoint for users** (`8f850ef`)
   - Added `/users/{user_id}` endpoint with integer validation
   - Added session 1 notes
   - Demonstrated Pydantic validation

### Branch Operations:
1. Created `feature/path-parameters` branch from `main`
2. Made changes and committed on feature branch
3. Switched back to `main`
4. Merged `feature/path-parameters` into `main` (fast-forward)
5. Deleted merged feature branch

### Current State:
- On `main` branch
- 3 total commits in history
- Remote (`origin/main`) is 2 commits behind (needs push)

### Best Practices Demonstrated:
1. ✅ Create feature branches for new work
2. ✅ Use descriptive branch names (`feature/path-parameters`)
3. ✅ Commit on feature branch before merging
4. ✅ Switch to `main` before merging
5. ✅ Delete merged feature branches
6. ✅ Use `git branch` to verify current branch
7. ✅ Check `git status` before operations

---

## Key Takeaways

### Git
1. **Branches are cheap** - Create them freely for new features
2. **Fast-forward merges** - Cleanest when no divergent changes
3. **Remote vs Local** - origin is the shared repository, local is your workspace
4. **fetch before pull** - Review changes before merging

### FastAPI
1. **Path parameters** - Dynamic URLs with `{variable}`
2. **Type validation** - FastAPI + Pydantic enforce type hints
3. **Automatic conversion** - Compatible types converted automatically
4. **Clear errors** - Pydantic provides detailed error messages
5. **f-strings** - Modern Python string formatting: `f"Hello {name}"`

---

## Testing Notes

### Successful Tests:
- `curl http://127.0.0.1:8000/users/42` → `{"user_id":42,"message":"Hello user 42"}`
- `curl http://127.0.0.1:8000/users/999` → `{"user_id":999,"message":"Hello user 999"}`

### Validation Error Tests:
- `curl http://127.0.0.1:8000/users/sa` → Pydantic int parsing error
- Expected: `curl http://127.0.0.1:8000/users/3.14` → Would return float parsing error

---

## Next Session Preview

**Phase 1.3: Query Parameters**
- URL parameters with `?key=value` syntax
- Optional vs required parameters
- Default values
- Multiple query parameters
- Combining path and query parameters
- Git: Writing meaningful commit messages

---

**Commands to Review Before Next Session:**
- How query strings work in URLs
- Python default function parameters
- Git commit message best practices
