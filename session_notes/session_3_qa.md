# Session 3 - Q&A Deep Dive

**Date:** October 12, 2025
**Topics:** Git Time Travel, Route Behavior, GitHub Actions, Server Ports

---

## Question 1: Git Time Travel - Going Back to Previous Commits

### How to Go Back to a Previous Commit

**Command:** `git checkout <commit-hash>`

**Example:**
```bash
# View commit history
git log --oneline

# Output:
# 51e6b24 Add session 3 notes: Query parameters and optional values
# 5ff37d2 Add query parameter endpoints
# 26d020a Add FastAPI Hello World endpoint
# a386415 Initial commit

# Travel back to Hello World commit
git checkout 26d020a
```

### What Happens When You Go Back?

**You enter "Detached HEAD" state:**
- HEAD normally points to a branch (like `main`)
- Now HEAD points directly to a specific commit
- You're in "read-only tourist mode" - viewing history
- Your files change to match that point in time

**Visual:**
```
Normal state:    HEAD → main → 51e6b24 (latest)
Detached HEAD:   HEAD → 26d020a (older commit)
```

**Example:** When we went back to `26d020a`, our `main.py` only had the Hello World endpoint. All the path parameters and query parameters disappeared (because they didn't exist yet at that point in history)!

### Coming Back to Present

**Command:** `git checkout main` or `git switch main`

```bash
git checkout main  # Returns to latest commit on main branch
```

**Result:** All your files return to their current state. All endpoints are back!

---

### What If You Make Changes in the Past?

#### Scenario 1: Make Changes WITHOUT Committing
```bash
git checkout 26d020a      # Go to past
# Edit main.py
git checkout main         # Return to present
```
**Result:** Changes are **lost** when you return to `main`. No conflicts, safe to do.

---

#### Scenario 2: Make Changes AND Commit in Detached HEAD
```bash
git checkout 26d020a      # Go to past
# Edit main.py
git add main.py
git commit -m "Fix"       # Creates orphan commit
git checkout main         # Return to present
```
**Result:** Git warns you! The commit becomes an "orphan" (not on any branch). It will eventually be garbage collected unless you save it to a branch.

---

#### Scenario 3: Want to Keep Changes from the Past
```bash
git checkout 26d020a              # Go to past
# Make changes
git checkout -b fix-from-past     # Create NEW branch from this point
git add .
git commit -m "Fix from past"
git checkout main                 # Return to main
git merge fix-from-past           # Merge the fix
```

**This might cause conflicts if:**
- Same lines were changed in both the past commit AND current main
- Git can't automatically merge them
- You'll need to manually resolve conflicts

---

### When Do Conflicts Happen?

**Conflicts occur when:**
1. You modify the same lines of code in two different commits
2. Git can't decide which version to keep
3. You must manually choose which changes to keep

**Example of conflict:**
```
Past commit changes line 10: return {"message": "Old version"}
Current main has line 10:     return {"message": "New version"}
→ Conflict! Git doesn't know which to keep
```

---

### Summary: Git Time Travel

| Action | Command | Result |
|--------|---------|--------|
| Go to past commit | `git checkout <hash>` | Detached HEAD, files change to past state |
| Return to present | `git checkout main` | Back to latest commit |
| Save changes from past | `git checkout -b <new-branch>` | Create branch to preserve changes |
| View history | `git log --oneline` | See all commits with hashes |

**Key Concept:** Detached HEAD is safe for viewing history. If you want to make lasting changes, create a branch!

---

## Question 2: Can We Have Multiple Functions on Same Route?

### Short Answer: NO (with same HTTP method)

You **cannot** have two functions on the **same route** with the **same HTTP method**.

### What Happens If You Try?

```python
@app.get("/")
def first():
    return {"msg": "first"}

@app.get("/")  # DUPLICATE! Same route + same method
def second():
    return {"msg": "second"}
```

**Result:** The **LAST** one wins! The `second()` function overwrites `first()`. FastAPI silently overwrites without error.

**When you visit `/`:** Only `second()` will be called. `first()` is ignored.

---

### What You CAN Do: Same Route, Different HTTP Methods ✓

```python
@app.get("/users")         # GET /users
def read_users():
    return {"users": ["Alice", "Bob"]}

@app.post("/users")        # POST /users
def create_user():
    return {"created": True}

@app.put("/users")         # PUT /users
def update_users():
    return {"updated": True}

@app.delete("/users")      # DELETE /users
def delete_users():
    return {"deleted": True}
```

**These are DIFFERENT routes** because they use different HTTP methods!

- `GET /users` → `read_users()`
- `POST /users` → `create_user()`
- `PUT /users` → `update_users()`
- `DELETE /users` → `delete_users()`

All work on the same path `/users` but handle different types of requests!

---

### HTTP Methods Overview

| Method | Purpose | Has Body? | Example |
|--------|---------|-----------|---------|
| GET | Read/retrieve data | No | Get list of users |
| POST | Create new resource | Yes | Create new user |
| PUT | Update entire resource | Yes | Replace user data |
| PATCH | Update part of resource | Yes | Update user email |
| DELETE | Remove resource | No | Delete user |

---

### Best Practice

**Each route + method combination should be unique!**

✓ Good:
```python
@app.get("/users")      # GET /users
@app.post("/users")     # POST /users
@app.get("/products")   # GET /products
```

✗ Bad (second overwrites first):
```python
@app.get("/users")      # This gets overwritten
@app.get("/users")      # Only this one works
```

---

## Question 3: What is GitHub Actions?

### Definition

**GitHub Actions** = Automation platform built into GitHub

**Think of it as:** A robot that runs tasks automatically when specific events happen on your GitHub repository.

**Key Points:**
- Runs on GitHub's servers (not your computer)
- Triggered by events: push, pull request, schedule, manual trigger, etc.
- Free for public repositories (limited free minutes for private repos)
- Uses YAML files to define workflows

---

### How It Works

1. **You define a workflow** (YAML file in `.github/workflows/`)
2. **An event occurs** (you push code, create PR, etc.)
3. **GitHub detects the event**
4. **GitHub spins up a fresh virtual machine** (Ubuntu, Windows, or macOS)
5. **Runs your workflow steps** (install dependencies, run tests, deploy, etc.)
6. **Reports results** (success/failure, logs, artifacts)

---

### Common Use Cases

#### 1. Continuous Integration (CI)
**Automatically test code on every push:**
```yaml
# When you push code:
✓ Install dependencies
✓ Run automated tests
✓ Check code style/formatting
✓ Build the project
✓ Report if anything fails
```

**Benefit:** Catch bugs before merging to main!

---

#### 2. Continuous Deployment (CD)
**Automatically deploy when code is merged:**
```yaml
# When you merge to main branch:
✓ Build production version
✓ Run final tests
✓ Deploy to production server
✓ Update documentation website
✓ Create release notes
```

**Benefit:** Fast, consistent deployments!

---

#### 3. Automation & Maintenance
**Schedule regular tasks:**
```yaml
# Daily/weekly/monthly tasks:
✓ Security vulnerability scans
✓ Dependency updates (Dependabot)
✓ Generate reports
✓ Clean up old data
✓ Send notifications
```

**Benefit:** Set it and forget it!

---

### Example GitHub Action Workflow

**File:** `.github/workflows/test.yml`

```yaml
name: Run Tests

# Trigger: Run on every push to any branch
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest  # Use Ubuntu server

    steps:
      # Step 1: Get the code
      - name: Checkout code
        uses: actions/checkout@v2

      # Step 2: Set up Python
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      # Step 3: Install dependencies
      - name: Install dependencies
        run: |
          pip install fastapi uvicorn pytest

      # Step 4: Run tests
      - name: Run tests
        run: pytest

      # Step 5: Report results
      - name: Test Report
        if: always()
        run: echo "Tests completed!"
```

**What happens:**
1. You push code to GitHub
2. GitHub detects the push event
3. GitHub creates a fresh Ubuntu virtual machine
4. Checks out your code
5. Installs Python 3.10
6. Installs FastAPI, uvicorn, pytest
7. Runs your tests
8. Reports success or failure (visible on GitHub)

---

### For Your FastAPI Project

**You could create actions to:**

```yaml
# .github/workflows/fastapi-test.yml
✓ Run FastAPI app on every push
✓ Test all endpoints automatically
✓ Check code formatting (black, flake8)
✓ Deploy to a server when merging to main
✓ Generate API documentation
```

**Benefits:**
- Catch bugs early (before they reach production)
- Consistent testing environment
- Automatic deployment
- Team confidence in code quality

---

### GitHub Actions vs Local Development

| Aspect | Local (Your Computer) | GitHub Actions |
|--------|----------------------|----------------|
| **Where** | Your machine | GitHub's servers |
| **When** | When you manually run | Automatically on events |
| **Environment** | Your setup | Fresh VM every time |
| **Cost** | Free (your electricity) | Free for public repos |
| **Visibility** | Only you | Entire team sees results |

---

### Getting Started

**To use GitHub Actions:**
1. Create `.github/workflows/` directory in your repo
2. Add a YAML file (e.g., `test.yml`)
3. Define triggers and steps
4. Push to GitHub
5. View results in the "Actions" tab on GitHub

**Example starter workflow:**
```bash
mkdir -p .github/workflows
# Create test.yml with the example above
git add .github/workflows/test.yml
git commit -m "Add GitHub Actions workflow"
git push
# Check the Actions tab on GitHub!
```

---

## Question 4: Different Ports for Running the Server

### Default Port

**FastAPI/Uvicorn default:** Port **8000**

**URLs we've been using:**
- `http://127.0.0.1:8000/`
- `http://localhost:8000/`

---

### Changing the Port

**Syntax:** `uvicorn main:app --port <PORT_NUMBER>`

**Examples:**
```bash
# Port 8000 (default)
uvicorn main:app --port 8000

# Port 8001
uvicorn main:app --port 8001

# Port 3000 (common for Node.js)
uvicorn main:app --port 3000

# Port 5000 (common for Flask)
uvicorn main:app --port 5000

# Port 9999 (any valid port)
uvicorn main:app --port 9999
```

**Then access with:**
```bash
curl http://127.0.0.1:9999/
```

---

### Port Number Ranges

**Valid port range:** 1 - 65535

#### Ports 1-1023 (System/Privileged Ports)
- Require administrator/root access
- Reserved for system services
- **Examples:**
  - Port 80: HTTP (web traffic)
  - Port 443: HTTPS (secure web)
  - Port 22: SSH
  - Port 21: FTP
  - Port 25: SMTP (email)

**For development:** ❌ Avoid these unless you need them and have admin rights

---

#### Ports 1024-49151 (Registered/User Ports)
- No special permissions needed
- Can be used by any user application
- **Common application ports:**
  - 3000: Node.js, React development
  - 4200: Angular development
  - 5000: Flask default
  - 8000: FastAPI, Django default
  - 8080: Alternative HTTP, Jenkins
  - 8888: Jupyter Notebooks
  - 9000: PHP-FPM

**For development:** ✅ Use these! Safe and no admin required

---

#### Ports 49152-65535 (Dynamic/Private Ports)
- Temporary/ephemeral ports
- Often used by system for outgoing connections
- Can also use for your apps

**For development:** ✅ Also safe to use

---

### Common Port Conflicts

**Problem:** "Address already in use"

**Cause:** Another process is using that port

**Example:**
```bash
# Server 1 running on port 8000
uvicorn main:app --port 8000

# Try to start server 2 on same port
uvicorn main:app --port 8000
# Error: OSError: [Errno 98] Address already in use
```

---

### Solutions to Port Conflicts

#### Solution 1: Use a Different Port
```bash
uvicorn main:app --port 8001  # Use 8001 instead
```

#### Solution 2: Find What's Using the Port
```bash
lsof -i :8000  # Shows processes on port 8000
```

**Output example:**
```
COMMAND   PID    USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
uvicorn 14411 rajdeep  3u  IPv4 103972      0t0  TCP localhost:8000 (LISTEN)
```

#### Solution 3: Kill the Process
```bash
# Find the PID from lsof output (e.g., 14411)
kill 14411

# Or kill all uvicorn processes
pkill uvicorn
```

---

### Multiple Servers on Different Ports

**You CAN run multiple servers simultaneously on different ports:**

```bash
# Terminal 1: Main app on 8000
uvicorn main:app --port 8000

# Terminal 2: Test app on 8001
uvicorn test:app --port 8001

# Terminal 3: Another app on 9000
uvicorn other:app --port 9000
```

**Access each:**
- `http://127.0.0.1:8000/` → Main app
- `http://127.0.0.1:8001/` → Test app
- `http://127.0.0.1:9000/` → Other app

---

### Port Recommendations for Development

**For FastAPI development:**
- **Primary app:** 8000 (default)
- **Second app:** 8001, 8002, etc.
- **Testing:** 8080, 9000, 9999

**Avoid:**
- Ports 1-1023 (need admin)
- Ports already used by common services (3306 MySQL, 5432 PostgreSQL, 6379 Redis)

---

### Additional Port Options

**Binding to specific IP:**
```bash
# Only localhost (default - secure)
uvicorn main:app --host 127.0.0.1 --port 8000

# All network interfaces (accessible from other devices)
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Warning:** Using `0.0.0.0` makes your server accessible from other computers on your network. Only use in trusted environments!

---

### Summary: Server Ports

| Port Range | Access Required | Recommended Use |
|------------|----------------|-----------------|
| 1-1023 | Admin/Root | System services only |
| 1024-49151 | User | ✅ Perfect for development |
| 49152-65535 | User | ✅ Also good for development |

**Default ports to remember:**
- FastAPI/Django: 8000
- Flask: 5000
- Node.js/React: 3000
- HTTP: 80
- HTTPS: 443

**Change port command:**
```bash
uvicorn main:app --port <PORT_NUMBER>
```

---

## Quick Reference Summary

### Git Time Travel
```bash
git log --oneline              # View commits
git checkout <commit-hash>     # Go to past (detached HEAD)
git checkout main              # Return to present
git checkout -b <branch>       # Create branch from current point
```

### Route Behavior
- ❌ Same path + same method = second overwrites first
- ✅ Same path + different methods = different routes work fine

### GitHub Actions
- Automation on GitHub servers
- Triggered by events (push, PR, schedule)
- Define workflows in `.github/workflows/*.yml`
- Use cases: Testing, deployment, automation

### Server Ports
```bash
uvicorn main:app --port 8000   # Default
uvicorn main:app --port 8001   # Custom port
lsof -i :8000                  # Check what's using port
pkill uvicorn                  # Kill uvicorn processes
```

---

**These are advanced topics that will serve you well as you continue learning FastAPI and Git!**
