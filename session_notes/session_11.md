# Session 11: Database Migrations with Alembic

**Date:** 2025-11-13
**Focus:** Schema migrations, version control for database structure, safe schema evolution
**Major Milestone:** Complete migration system for tracking and managing database changes!

---

## 🎯 Session Goals

- Understand why migrations are needed
- Install and configure Alembic
- Create migrations automatically
- Apply and rollback migrations
- Track schema changes in version control
- Understand columns vs indexes
- Practice safe schema evolution

---

## 🔑 Why Migrations Are Needed

### The Problem

Imagine you have **1,000 users** in production and need to add a `phone_number` column.

**❌ The WRONG Way:**
```sql
-- DON'T DO THIS IN PRODUCTION!
DROP TABLE users;  -- DELETED ALL 1,000 USERS! 😱
CREATE TABLE users (..., phone_number VARCHAR(20));
```

**Result:** All user data GONE! Users can't login, lost conversations, business destroyed!

---

### ✅ The RIGHT Way: Migrations

**Migrations = Git for Your Database Schema**

```
Git tracks code changes          →  Migrations track schema changes

├── Commit A                     ├── Migration 001: Create users table
├── Commit B                     ├── Migration 002: Add email column
├── Commit C                     ├── Migration 003: Add phone column
└── Commit D                     └── Migration 004: Create index
```

---

### What Migrations Give You

1. **Version Control** 📝
   - Track every schema change
   - Know exactly when and why changes were made

2. **Reproducibility** 🔄
   - Anyone can recreate your exact database structure
   - `alembic upgrade head` = get latest schema

3. **Safety** 🛡️
   - Keep existing data
   - Test changes before production

4. **Rollback** ⏮️
   - Something broke? Roll back!
   - `alembic downgrade -1` = undo last migration

5. **Collaboration** 👥
   - Team members stay in sync
   - Merge migration files like code

---

## 📊 Migrations vs Manual Changes

| Aspect | Manual SQL | Migrations |
|--------|-----------|-----------|
| **Tracking** | ❌ No record | ✅ Version controlled |
| **Reproducible** | ❌ Hard to replicate | ✅ Run `upgrade head` |
| **Rollback** | ❌ Manual undo | ✅ `downgrade -1` |
| **Team Sync** | ❌ Everyone does manually | ✅ Automatic |
| **Production** | ❌ Risky | ✅ Tested in dev first |
| **Audit Trail** | ❌ None | ✅ Full history |

---

## 🔧 Installation & Setup

### Step 1: Install Alembic

```bash
pip install alembic
```

**Verify installation:**
```bash
alembic --version
# Output: alembic 1.9.2
```

---

### Step 2: Initialize Alembic

```bash
alembic init alembic
```

**Creates:**
```
fastapi_practice/
├── alembic/                  ← NEW folder!
│   ├── versions/             ← Migration files go here
│   ├── env.py                ← Environment configuration
│   ├── script.py.mako        ← Template for new migrations
│   └── README
└── alembic.ini               ← Main configuration file
```

---

### Step 3: Configure Database Connection

**Edit `alembic.ini` (line 58):**

Before:
```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

After:
```ini
sqlalchemy.url = mysql+pymysql://root:root@localhost:3306/chatbot_db
```

---

### Step 4: Import Models

**Edit `alembic/env.py` (lines 17-21):**

Before:
```python
# target_metadata = mymodel.Base.metadata
target_metadata = None
```

After:
```python
# Import our models so Alembic can detect changes
from models import Base
target_metadata = Base.metadata
```

**Why important:**
- `Base.metadata` contains info about ALL our SQLAlchemy models
- Alembic can now **auto-generate migrations** by comparing models to database
- Without this, we'd have to write migrations manually

---

### Step 5: Verify Configuration

```bash
alembic current
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
```

No errors = configured correctly! ✅

---

## 📝 Migration File Anatomy

```python
"""Migration description

Revision ID: 6590a00d8dcb        ← Unique ID for this migration
Revises: 5e9b3b66f388            ← Previous migration (parent)
Create Date: 2025-11-13          ← When it was created
"""

# Version Info
revision = '6590a00d8dcb'        ← This migration's ID
down_revision = '5e9b3b66f388'   ← Parent migration

def upgrade() -> None:
    """What to do when moving FORWARD"""
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))

def downgrade() -> None:
    """What to do when moving BACKWARD (rollback)"""
    op.drop_column('users', 'phone_number')
```

---

## 🚀 Creating Migrations

### Create First Migration (Baseline)

Our database already has `users` and `conversations` tables. Let's capture current state:

```bash
alembic revision --autogenerate -m "Initial migration - users and conversations tables"
```

**Output:**
```
Generating /home/rajdeep/.../5e9b3b66f388_initial_migration_users_and_.py ...  done
INFO  [alembic.autogenerate.compare] Detected added index 'ix_conversations_id' on '['id']'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_users_id' on '['id']'
```

Alembic detected that our models define indexes that don't exist in the database yet!

---

### Apply Migration

**Two-step process:**

1. **Create migration file** (just Python code):
   ```bash
   alembic revision --autogenerate -m "message"
   ```
   ✅ File created
   ❌ Database NOT changed yet

2. **Execute migration** (actually change database):
   ```bash
   alembic upgrade head
   ```
   ✅ Runs the Python code
   ✅ Changes MySQL
   ✅ Updates version tracking

**Think of it like:**
- ✅ Wrote a recipe (migration file)
- ✅ Cooked the meal (executed migration)

---

### Example: Add Phone Number Column

**Step 1: Update Model**

Edit `models.py`:
```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    phone_number = Column(String(20), nullable=True)  # ← NEW!
    # nullable=True: Existing users won't break

    created_at = Column(DateTime, server_default=func.now())
```

**Step 2: Create Migration**

```bash
alembic revision --autogenerate -m "Add phone_number column to users table"
```

**Output:**
```
Generating .../6590a00d8dcb_add_phone_number_column_to_users_table.py ...  done
INFO  [alembic.autogenerate.compare] Detected added column 'users.phone_number'
```

Alembic automatically detected the new column! ✨

**Step 3: Review Migration**

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'phone_number')
```

**Step 4: Apply Migration**

```bash
alembic upgrade head
```

**Output:**
```
INFO  [alembic.runtime.migration] Running upgrade 5e9b3b66f388 -> 6590a00d8dcb, Add phone_number column to users table
```

**Step 5: Verify in MySQL**

```bash
mysql -u root -proot chatbot_db -e "DESCRIBE users;"
```

**Result:**
```
Field         Type          Null   Key   Default
phone_number  varchar(20)   YES          NULL    ← NEW COLUMN!
```

**Check existing users:**
```sql
SELECT id, username, email, phone_number FROM users LIMIT 5;
```

**Result:**
```
id  username  email                 phone_number
1   ram       ram@god.com           NULL        ✅
2   alice     newemail@example.com  NULL        ✅
4   charlie   charlie@example.com   NULL        ✅
```

All existing users have `phone_number=NULL` - no data lost! ✅

---

## 🔄 Upgrade & Downgrade Workflow

### Migration Chain

```
Migration 1: 5e9b3b66f388 (create indexes)
              ↓ builds on
Migration 2: 6590a00d8dcb (add phone_number)
```

### Upgrade (Move Forward)

```bash
alembic upgrade head
```

**What happens:**
```
Current:  5e9b3b66f388
            ↓ applies migration 2
New:      6590a00d8dcb (head)
```

- Executes `upgrade()` function
- Adds phone_number column
- Updates `alembic_version` table

---

### Downgrade (Rollback)

```bash
alembic downgrade -1
```

**What happens:**
```
Current:  6590a00d8dcb (head)
            ↓ rolls back 1 migration
New:      5e9b3b66f388
```

- Executes `downgrade()` function
- **DELETES phone_number column**
- **DATA IN THAT COLUMN IS LOST!** ⚠️
- Updates `alembic_version` table

---

### Upgrade Again (Restore)

```bash
alembic upgrade head
```

**What happens:**
```
Current:  5e9b3b66f388
            ↓ applies migration 2 again
New:      6590a00d8dcb (head)
```

- Re-creates phone_number column
- Existing users get `phone_number=NULL` again
- Previous phone number data NOT restored (was deleted!)

---

## 🔑 Important Concepts

### 1. Columns vs Indexes

**Columns = Data Storage**
```sql
-- Columns hold actual data
CREATE TABLE users (
    id INT,              ← Column (stores data)
    username VARCHAR(50), ← Column (stores data)
    email VARCHAR(100)   ← Column (stores data)
);
```

**Indexes = Speed Boosters**
```sql
-- Indexes don't store data, they make searches faster!
CREATE INDEX ix_users_id ON users(id);  ← Like a book index!
```

**Analogy:**
- **Column** = Pages in a book (actual content)
- **Index** = Index at the back of a book (helps you find pages faster)

**Performance Example:**

Without Index:
```python
# Database searches EVERY row (slow!)
SELECT * FROM users WHERE id = 1000;
Row 1: id=1? No
Row 2: id=2? No
...
Row 1000: id=1000? YES! ✅ (took 1000 checks!)
```

With Index:
```python
# Database uses index (fast!)
SELECT * FROM users WHERE id = 1000;
Index lookup → Row 1000 directly! ✅ (took 1 check!)
```

---

### 2. nullable=True Importance

**Why nullable=True for new columns?**

**❌ If we used nullable=False:**
```python
phone_number = Column(String(20), nullable=False)  # ❌ BAD!
```

**What would happen:**
```sql
ALTER TABLE users ADD COLUMN phone_number VARCHAR(20) NOT NULL;
                                                        ↑
                                                    ERROR! 💥

MySQL says: "What phone_number should I put for existing users?
              They don't have phone numbers! I can't add NOT NULL!"
```

**Migration would FAIL!** ❌

**✅ Using nullable=True:**
```python
phone_number = Column(String(20), nullable=True)  # ✅ GOOD!
```

**What happens:**
```
Existing users get phone_number=NULL
New users can provide phone numbers
No data lost, no errors!
```

---

### 3. Version Tracking

Alembic creates a special table to track migrations:

```sql
SELECT * FROM alembic_version;
```

**Output:**
```
version_num
6590a00d8dcb  ← Current migration version
```

This table has ONE row that always contains the current migration version.

---

## 📝 Commands Reference

### Essential Commands

```bash
# Create migration (auto-detect changes)
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Show current version
alembic current

# Show migration history
alembic history

# Show migration details
alembic history --verbose
```

### Workflow Example

```bash
# 1. Check current state
alembic current

# 2. Modify models.py
# ... add new column ...

# 3. Create migration
alembic revision --autogenerate -m "Add phone_number column"

# 4. Review migration file
cat alembic/versions/6590a00d8dcb_add_phone_number_column_to_users_table.py

# 5. Apply migration
alembic upgrade head

# 6. Verify in database
mysql -u root -proot chatbot_db -e "DESCRIBE users;"

# 7. If something wrong, rollback
alembic downgrade -1

# 8. If all good, commit to Git
git add alembic/ models.py
git commit -m "Add phone_number column with migration"
```

---

## 🎓 Real-World Migration Strategies

### Strategy 1: Nullable First (What we did)
```python
# Step 1: Add column as nullable
phone_number = Column(String(20), nullable=True)

# Step 2: Gradually collect phone numbers from users
# Step 3: Later, make it NOT NULL (another migration)
```

### Strategy 2: With Default Value
```python
# Add column with default value
phone_number = Column(String(20), nullable=False, server_default="000-000-0000")
# All existing users get "000-000-0000"
```

### Strategy 3: Multi-Step Migration
```
Migration 1: Add column (nullable)
Migration 2: Populate data for existing users
Migration 3: Make column NOT NULL
```

---

## ⚠️ Important Warnings

### 1. Downgrade Deletes Data!

```bash
alembic downgrade -1
```

**This will:**
- ❌ Delete columns
- ❌ Lose all data in those columns
- ❌ Cannot be undone (data is gone!)

**Use carefully in production!**

---

### 2. Auto-generate Isn't Perfect

Alembic can't detect:
- Table renames (sees as drop + create)
- Column renames (sees as drop + add)
- Changes to column types in some cases

**Always review generated migrations!**

---

### 3. Migration Order Matters

Migrations must be applied in order:
```
✅ CORRECT:
001 → 002 → 003

❌ WRONG:
001 → 003 → 002  # Will fail!
```

---

## 🔄 Git Workflow

### Files to Commit

```bash
# Always commit together:
git add models.py                    # Model changes
git add alembic.ini                  # Configuration
git add alembic/env.py               # Environment setup
git add alembic/versions/            # Migration files

git commit -m "Add phone_number column with migration"
```

### What NOT to Commit

```bash
# Don't commit:
.idea/              # IDE files
*.pyc               # Python bytecode
__pycache__/        # Python cache
.env                # Secrets
*.swp               # Vim swap files
```

---

## 📊 Our Session Progress

```
Session 11 Workflow:

1. ✅ Explained why migrations are needed
2. ✅ Installed Alembic (pip install alembic)
3. ✅ Initialized Alembic (alembic init alembic)
4. ✅ Configured database connection (alembic.ini)
5. ✅ Imported models (alembic/env.py)
6. ✅ Created baseline migration (indexes)
7. ✅ Applied baseline migration
8. ✅ Added phone_number column to models.py
9. ✅ Created column migration (auto-detected!)
10. ✅ Applied column migration
11. ✅ Tested downgrade (rollback)
12. ✅ Tested upgrade (restore)
13. ✅ Committed to Git
```

---

## 🎯 Key Takeaways

### What We Accomplished

1. ✅ **Installed Alembic** - Database migration tool
2. ✅ **Configured for MySQL** - Connected to chatbot_db
3. ✅ **Created 2 migrations**:
   - Migration 1: Add indexes
   - Migration 2: Add phone_number column
4. ✅ **Applied migrations** - Changed actual database
5. ✅ **Tested rollback** - Downgrade and upgrade
6. ✅ **Version control** - Tracked in Git
7. ✅ **Understood key concepts**:
   - Columns vs Indexes
   - nullable=True importance
   - Migration chain
   - Upgrade/downgrade workflow

---

### Why This Matters

**Before Alembic:**
- ❌ Manual SQL scripts
- ❌ No version tracking
- ❌ Team not in sync
- ❌ Risky production changes
- ❌ Can't rollback easily

**After Alembic:**
- ✅ Automatic migration generation
- ✅ Version controlled schema
- ✅ Team stays in sync
- ✅ Safe production deployments
- ✅ Easy rollback

---

## 🚀 What's Next?

**Session 12: NoSQL Concepts & MongoDB Setup**

You'll learn:
- SQL vs NoSQL differences
- Document-based databases
- MongoDB concepts (collections, documents)
- When to use MongoDB vs MySQL
- MongoDB installation and configuration

**Upcoming Sessions:**
- Session 13: Motor/PyMongo & Document Mapping
- Session 14: MongoDB CRUD Operations
- Session 15: Hybrid Approach (SQL + NoSQL)
- Session 16: Production Deployment

---

## 📈 Project Structure After Session 11

```
fastapi_practice/
├── main.py                      # FastAPI app (16 endpoints)
├── database.py                  # MySQL connection
├── models.py                    # SQLAlchemy models (+ phone_number!)
├── schemas.py                   # Pydantic schemas
├── crud.py                      # Database operations
├── alembic.ini                  # Alembic configuration ← NEW!
├── alembic/                     # Migration directory ← NEW!
│   ├── versions/
│   │   ├── 5e9b3b66f388_initial_migration_users_and_.py
│   │   └── 6590a00d8dcb_add_phone_number_column_to_users_table.py
│   ├── env.py
│   ├── script.py.mako
│   └── README
└── session_notes/
    ├── session_1.md through session_11.md
    └── phase_3_database_plan.md
```

---

**Session Duration:** ~2 hours
**Migrations Created:** 2
**Lines Added:** 271 insertions, 1 deletion
**Git Commits:** 1

**Status:** ✅ Session 11 Complete! Database migrations working!
