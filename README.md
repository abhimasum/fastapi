# FastAPI Industrial Agent Service

A production-ready FastAPI application demonstrating:
- ✅ JWT-based authentication & authorization
- ✅ Role-Based Access Control (RBAC)
- ✅ Full input validation with Pydantic v2
- ✅ Structured error handling (never leaks internals)
- ✅ Rate limiting middleware
- ✅ Swagger UI + ReDoc auto-documentation
- ✅ Unit + integration tests with pytest
- ✅ 90%+ test coverage
- ✅ GCP-ready (Cloud Run compatible)

---

## Project Structure

```
fastapi_app/
├── app/
│   ├── main.py                     # App entry point, middleware, routers
│   ├── core/
│   │   ├── config.py               # Settings (env vars via pydantic-settings)
│   │   ├── security.py             # JWT creation/validation, password hashing
│   │   ├── dependencies.py         # FastAPI dependency injectors
│   │   └── exceptions.py           # Custom exceptions + handlers
│   ├── models/
│   │   └── domain.py               # In-memory "DB" models (swap with SQLAlchemy)
│   ├── schemas/
│   │   ├── auth.py                 # Auth request/response schemas
│   │   ├── plant.py                # Plant resource schemas
│   │   └── common.py              # Shared response envelopes
│   ├── services/
│   │   ├── auth_service.py         # Business logic: login, token refresh
│   │   └── plant_service.py        # Business logic: CRUD for Plant resources
│   ├── api/
│   │   └── v1/
│   │       ├── router.py           # Aggregates all v1 routes
│   │       └── endpoints/
│   │           ├── auth.py         # /auth/login, /auth/refresh, /auth/me
│   │           └── plants.py       # /plants CRUD
│   └── middleware/
│       ├── logging.py              # Structured request/response logging
│       └── rate_limit.py           # In-memory sliding-window rate limiter
├── tests/
│   ├── conftest.py                 # Shared fixtures (test client, test DB)
│   ├── unit/
│   │   ├── test_security.py        # JWT, password hashing
│   │   ├── test_plant_service.py   # Service layer logic
│   │   └── test_schemas.py         # Pydantic validation edge cases
│   └── integration/
│       ├── test_auth_endpoints.py  # Auth flow end-to-end
│       └── test_plant_endpoints.py # Plant CRUD end-to-end
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 📖 Manual Setup Guide - Complete Learning Path

Choose your package manager below and follow step-by-step!

### ⭐ Option 1: Setup with `uv` (Recommended - Faster)

**What is `uv`?**
- Modern, fast Python package manager (written in Rust)
- Automatically creates virtual environment
- Creates `uv.lock` for reproducible builds
- Perfect for learning

**Prerequisites:**
- Python 3.12+ installed
- `uv` installed (see Step 0 below)

#### Step 0️⃣: Install `uv` (one-time)
```bash
# Windows (PowerShell) - Run as Administrator
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:
```bash
uv --version
# Should show: uv 0.x.x
```

#### Step 1️⃣: Navigate to project folder
```bash
cd "c:\Abhishek\OtherAndResearch\Learning Practical\FastApi\fastapi_app"
```

#### Step 2️⃣: Sync dependencies (auto-creates .venv)
```bash
uv sync
```

**What happens:**
- ✅ Creates `.venv` folder
- ✅ Downloads all packages from `pyproject.toml`
- ✅ Creates `uv.lock` (exact versions recorded)
- ✅ Takes ~30-60 seconds first time
- ✅ Subsequent runs are instant

**Output:**
```
Resolved 42 packages
Prepared 42 packages
Installed 42 packages in 1.23s
```

#### Step 3️⃣: Copy environment file
```bash
Copy-Item .env.example .env
```

**What's in `.env`?**
- Database settings
- JWT secret key
- API configuration
- Environment mode (development/production)

#### Step 4️⃣: Activate virtual environment
```bash
.venv\Scripts\Activate.ps1
```

**How to verify activation:**
```bash
# Prompt should now show:
(.venv) PS C:\Abhishek\OtherAndResearch\Learning Practical\FastApi\fastapi_app>
#       ^^^^^^
#       This shows venv is active!
```

#### Step 5️⃣: Run development server
```bash
uvicorn app.main:app --reload --port 8000
```

**What `--reload` does:**
- Watches for file changes
- Auto-restarts server when code changes
- Great for development!

**Expected output:**
```
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### Step 6️⃣: Test the API
Open browser: **http://localhost:8000/docs**

**What you see:**
- Interactive Swagger UI documentation
- All endpoints listed
- "Try it out" button to test endpoints
- Login endpoint available

#### Step 7️⃣: Try login endpoint
1. Click on `POST /api/v1/auth/login`
2. Click "Try it out"
3. Enter in request body:
```json
{
  "username": "admin",
  "password": "Admin@123"
}
```
4. Click "Execute"

**Response (success):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Step 8️⃣: Run tests (in new terminal)
```bash
# New terminal (keep server running)
.venv\Scripts\Activate.ps1
pytest --cov=app --cov-report=term-missing -v
```

**What tests do:**
- ✅ Unit tests (functions individually)
- ✅ Integration tests (complete flows)
- ✅ Coverage report (% of code tested)

#### Step 9️⃣: Add new dependencies (when needed)
```bash
# Add production dependency
uv add requests
uv add sqlalchemy

# Add development dependency
uv add --dev black
uv add --dev pytest-watch

# Remove dependency
uv remove requests
```

#### 🔟: Stop the server
```bash
# Press Ctrl+C in terminal
# Ctrl+C + wait 2 seconds
```

**Useful `uv` commands reference:**
```bash
uv sync                  # Install dependencies
uv sync --upgrade        # Update all packages
uv add <package>         # Add dependency
uv add --dev <package>   # Add dev dependency
uv remove <package>      # Remove dependency
uv pip list              # List all packages
uv lock                   # Regenerate lock file
```

---

### 📦 Option 2: Setup with `pip` (Traditional)

**What is `pip`?**
- Default Python package manager
- Comes built-in with Python
- Slower than `uv` but widely used
- More manual setup required

**Prerequisites:**
- Python 3.12+ installed
- `pip` comes automatically with Python

#### Step 1️⃣: Check Python version
```bash
python --version
# Should show: Python 3.12.x or higher

# If shows "command not found" or version < 3.12:
# Download from: https://www.python.org/downloads/
# Install with "Add Python to PATH" checked
# Restart terminal after install
```

#### Step 2️⃣: Navigate to project
```bash
cd ".\fastapi_app"
```

#### Step 3️⃣: Create virtual environment
```bash
python -m venv .venv
```

**What happens:**
- ✅ Creates `.venv` folder with isolated Python
- ✅ Takes ~10-20 seconds
- ✅ Prevents conflicts with other projects

**Why virtual environment?**
- Each project has its own packages
- Prevents version conflicts
- Clean, reproducible setup

#### Step 4️⃣: Activate virtual environment
```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```

**Verify activation:**
```bash
# Prompt should change to:
(.venv) PS C:\...>
#       ^^^^^^
#       Venv is active!
```

#### Step 5️⃣: Upgrade `pip` (important!)
```bash
python -m pip install --upgrade pip
```

**Why upgrade?**
- Newer `pip` is faster
- Fixes security issues
- Better error messages

#### Step 6️⃣: Install dependencies
```bash
# Install production requirements
pip install -r requirements.txt

# Install development requirements
pip install -r requirements-dev.txt
```

**What happens:**
- ✅ Downloads packages from PyPI (Python Package Index)
- ✅ Installs exact versions from `requirements.txt`
- ✅ Takes ~2-5 minutes (first time)
- ✅ Shows progress with package names

**Expected output:**
```
Collecting fastapi==0.115.5
  Downloading fastapi-0.115.5-py3-none-any.whl
Installing collected packages: fastapi, pydantic, uvicorn, ...
Successfully installed fastapi-0.115.5 uvicorn-0.32.1 ... (41 packages)
```

#### Step 7️⃣: Copy environment file
```bash
Copy-Item .env.example .env
```

#### Step 8️⃣: Run development server
```bash
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started server process [xxxxx]
INFO:     Application startup complete.
```

#### Step 9️⃣: Test the API
Open: **http://localhost:8000/docs**

**Login test:**
1. POST `/api/v1/auth/login`
2. Username: `admin`
3. Password: `Admin@123`
4. Click "Execute"

#### 🔟: Run tests
```bash
# In new terminal
.venv\Scripts\Activate.ps1
pytest --cov=app --cov-report=term-missing -v
```

**Useful `pip` commands reference:**
```bash
pip install <package>              # Add package
pip uninstall <package>            # Remove package
pip list                           # List packages
pip install --upgrade <package>    # Update package
pip freeze > requirements.txt      # Save packages to file
pip install -r requirements.txt    # Install from file
```

---

## Comparison: `uv` vs `pip`

| Feature | `uv` | `pip` |
|---------|------|-------|
| **Speed** | ⚡⚡⚡ Very fast | ⚡ Slower |
| **Setup Time** | 5 minutes | 10-15 minutes |
| **Venv Creation** | ✅ Automatic | ❌ Manual |
| **Lock File** | ✅ `uv.lock` | ❌ Requires `pip freeze` |
| **Installation** | `uv sync` | `pip install -r` |
| **Add Package** | `uv add pkg` | `pip install pkg` |
| **Learning Curve** | Modern, simple | Traditional, familiar |
| **Industry Use** | Growing rapidly | Everywhere |

**Recommendation for Learning: Start with `uv` ⭐**

---

## Quick Start

### Using `uv` (Recommended - faster & simpler)

```bash
# 1. Clone and enter project
cd fastapi_app

# 2. Sync dependencies (creates .venv and uv.lock)
uv sync

# 3. Set environment variables
cp .env.example .env

# 4. Activate the virtual environment
.venv\Scripts\Activate.ps1    # Windows PowerShell
source .venv/bin/activate     # macOS/Linux

# 5. Run the server
uvicorn app.main:app --reload --port 8000

# 6. Open Swagger UI
open http://localhost:8000/docs

# 7. Run tests with coverage
uv run pytest --cov=app --cov-report=term-missing -v

# 8. Add a new dependency
uv add requests
uv add --dev black  # dev dependency
```

### Using `pip` (Traditional approach)

```bash
# 1. Clone and enter project
cd fastapi_app

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate.ps1    # Windows PowerShell
source .venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env and set SECRET_KEY to a long random string

# 5. Run the server
uvicorn app.main:app --reload --port 8000

# 6. Open Swagger UI
open http://localhost:8000/docs

# 7. Run tests with coverage
pytest --cov=app --cov-report=term-missing -v
```

### Using `uv run` (Direct execution)

```bash
# Run server without activation
uv run uvicorn app.main:app --reload --port 8000

# Run tests
uv run pytest --cov=app --cov-report=term-missing -v
```

---

## Environment Setup (Important)

**VS Code users:** Enable environment file injection for proper `.env` loading:
1. Press `Ctrl + ,` to open Settings
2. Search for `python.terminal.useEnvFile`
3. Check the box to enable it

Or add to `.vscode/settings.json`:
```json
{
    "python.terminal.useEnvFile": true
}
```

---

## API Overview

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| POST | `/api/v1/auth/login` | No | Any | Get JWT token |
| POST | `/api/v1/auth/refresh` | Token | Any | Refresh access token |
| GET | `/api/v1/auth/me` | Token | Any | Current user info |
| GET | `/api/v1/plants` | Token | viewer+ | List all plants |
| POST | `/api/v1/plants` | Token | operator+ | Create plant |
| GET | `/api/v1/plants/{id}` | Token | viewer+ | Get plant by ID |
| PUT | `/api/v1/plants/{id}` | Token | operator+ | Update plant |
| DELETE | `/api/v1/plants/{id}` | Token | admin | Delete plant |
| GET | `/health` | No | Any | Health check |

### Test Users (seeded in-memory)

| Username | Password | Role |
|----------|----------|------|
| admin | Admin@123 | admin |
| operator | Operator@123 | operator |
| viewer | Viewer@123 | viewer |

---

## 🧪 Running Tests

This project includes comprehensive unit and integration tests with pytest.

### Test Structure

```
tests/
├── conftest.py                          # Shared fixtures
├── unit/
│   ├── test_security.py                 # Password hashing & JWT tokens
│   ├── test_schemas.py                  # Pydantic validation
│   └── test_plant_service.py            # Business logic
└── integration/
    ├── test_auth_endpoints.py           # Auth flows end-to-end
    └── test_plant_endpoints.py          # Plant CRUD end-to-end
```

### Quick Test Commands

```bash
# Activate virtual environment first
.venv\Scripts\Activate.ps1        # Windows PowerShell
source .venv/bin/activate         # macOS/Linux

# Run ALL tests with coverage report
pytest --cov=app --cov-report=term-missing -v

# Run tests quietly (summary only)
pytest --tb=no -q

# Run only unit tests
pytest tests/unit -v

# Run only integration tests
pytest tests/integration -v

# Run a specific test file
pytest tests/unit/test_security.py -v

# Run a specific test class
pytest tests/integration/test_auth_endpoints.py::TestLoginEndpoint -v

# Run a specific test function
pytest tests/integration/test_auth_endpoints.py::TestLoginEndpoint::test_login_valid_admin -v

# Watch mode - re-run on file changes (requires pytest-watch)
ptw -- --tb=short
```

### Detailed Test Commands

#### 1️⃣ Run all tests with coverage
```bash
.venv\Scripts\Activate.ps1
pytest --cov=app --cov-report=term-missing -v
```

**What you'll see:**
- ✅ Test results (PASSED/FAILED)
- ✅ Coverage percentage per module
- ✅ Which lines are untested
- ✅ Summary statistics

**Expected output:**
```
tests/unit/test_security.py::TestPasswordHashing::test_hash_produces_bcrypt_format PASSED
tests/unit/test_schemas.py::TestLoginRequestSchema::test_valid_login PASSED
tests/integration/test_auth_endpoints.py::TestLoginEndpoint::test_login_valid_admin PASSED
...
======================== 128 passed in 102.89s ========================
```

#### 2️⃣ Run only unit tests
```bash
pytest tests/unit -v
```

**Unit tests cover:**
- Password hashing (bcrypt)
- JWT token creation & validation
- Pydantic schema validation
- Service layer business logic

**Why unit tests?**
- Fast (run in milliseconds)
- Test individual functions
- No HTTP requests
- Perfect for TDD

#### 3️⃣ Run only integration tests
```bash
pytest tests/integration -v
```

**Integration tests cover:**
- Complete HTTP request/response cycles
- End-to-end authentication flows
- Authorization checks (roles/permissions)
- Error handling (404, 401, 403, 409, etc.)
- Validation error responses

**Why integration tests?**
- Test real API behavior
- Catch middleware issues
- Verify error responses
- Ensure auth actually works

#### 4️⃣ Run specific test
```bash
# Test successful login
pytest tests/integration/test_auth_endpoints.py::TestLoginEndpoint::test_login_valid_admin -v

# Test wrong password returns 401
pytest tests/integration/test_auth_endpoints.py::TestLoginEndpoint::test_login_wrong_password -v

# Test plant creation
pytest tests/integration/test_plant_endpoints.py::TestCreatePlant::test_operator_can_create -v
```

#### 5️⃣ Run with detailed output
```bash
# Show print statements and full output
pytest tests/unit/test_security.py -v --capture=no

# Show variable values on failure
pytest -vv

# Show short summary only
pytest --tb=no -q

# Stop on first failure
pytest -x

# Run last failed test
pytest --lf
```

### Coverage Report Explained

```
tests/unit/test_security.py::TestPasswordHashing::test_hash_produces_bcrypt_format PASSED
Name                    Stmts   Miss  Cover   Missing
─────────────────────────────────────────────────────
app/core/security.py       45      2    96%    105-106
app/core/exceptions.py     65      3    95%    142, 200-202
app/services/auth.py       30      1    97%    54
─────────────────────────────────────────────────────
TOTAL                     140      6    96%
```

**What it means:**
- `Stmts` = Total lines of code
- `Miss` = Uncovered lines
- `Cover` = Percentage covered (aim for >90%)
- `Missing` = Specific line numbers not tested

### Test Data (Fixtures)

Tests use seeded in-memory database with:
- 3 test users (admin, operator, viewer)
- Fresh DB per test (isolation)
- No external dependencies

**Test Users:**
```
Username: admin    | Password: Admin@123    | Role: admin
Username: operator | Password: Operator@123 | Role: operator
Username: viewer   | Password: Viewer@123   | Role: viewer
```

### Using uv to Run Tests

```bash
# Without activating venv
uv run pytest --cov=app -v

# Watch mode with uv
uv run ptw -- --tb=short

# Run specific test
uv run pytest tests/integration/test_auth_endpoints.py::TestLoginEndpoint -v
```

### Common Test Scenarios

**Test Authentication:**
```bash
pytest tests/integration/test_auth_endpoints.py -v
# Tests: login, token refresh, user info, invalid tokens
```

**Test Authorization:**
```bash
pytest tests/integration/test_plant_endpoints.py::TestCreatePlant -v
# Tests: who can create plants, who cannot
```

**Test Validation:**
```bash
pytest tests/unit/test_schemas.py -v
# Tests: invalid input, edge cases, boundary values
```

**Test Business Logic:**
```bash
pytest tests/unit/test_plant_service.py -v
# Tests: duplicate names, pagination, filtering
```

### Debugging Failed Tests

If a test fails:

1. **Run with verbose output:**
   ```bash
   pytest -vv tests/path/to/test.py::TestClass::test_function
   ```

2. **Add breakpoint in test:**
   ```python
   def test_something():
       # ... test code ...
       breakpoint()  # Drops into debugger here
       # ... more test code ...
   ```

3. **Run with debugger:**
   ```bash
   pytest -vv -s --pdb tests/path/to/test.py
   ```

4. **Print debugging:**
   ```bash
   pytest -s tests/path/to/test.py  # Shows print() statements
   ```

---

## Dependency Management

### Adding Dependencies with `uv`

```bash
# Activate venv first
.venv\Scripts\Activate.ps1

# Add production dependency
uv add fastapi-cors
uv add sqlalchemy@latest

# Add dev dependency
uv add --dev black ruff mypy

# Remove dependency
uv remove requests

# Update all dependencies
uv sync --upgrade

# View installed packages
uv pip list
```

### Generating Lockfile

```bash
# Generate/update uv.lock for reproducible installs
uv lock

# Install from lockfile (CI/CD)
uv sync
```

---

## Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# Access the application
# App: http://localhost:8080
# Docs: http://localhost:8080/docs
```

**Note:** Docker automatically uses `uv.lock` for reproducible builds. The `Dockerfile` has been optimized for faster builds with `uv`.

---

## Cloud Run Deployment

```bash
# Build and push
docker build -t asia-south1-docker.pkg.dev/PROJECT/REPO/plant-api:latest .
docker push asia-south1-docker.pkg.dev/PROJECT/REPO/plant-api:latest

# Deploy
gcloud run deploy plant-api \
  --image asia-south1-docker.pkg.dev/PROJECT/REPO/plant-api:latest \
  --region asia-south1 \
  --set-env-vars SECRET_KEY=your-secret,ENVIRONMENT=production \
  --min-instances 1
```

---

## Troubleshooting

### Bcrypt/Passlib Compatibility Warning
**Note:** You may see a warning `AttributeError: module 'bcrypt' has no attribute '__about__'` on startup. This is a known issue between passlib 1.7.4 and newer bcrypt versions. It's non-fatal — the app works correctly. This warning is suppressed at runtime.

### Module Import Error: `ModuleNotFoundError: No module named 'app'`
**Solution:** Ensure the package is installed in editable mode:
```bash
uv pip install -e .
# OR
pip install -e .
```

### `.env` file not being loaded
**Solution (VS Code):** Enable environment file injection in settings:
```json
{
    "python.terminal.useEnvFile": true
}
```

### Virtual environment issues
**Clear and recreate:**
```bash
rm -r .venv uv.lock  # PowerShell: Remove-Item .venv, uv.lock -Recurse -Force
uv sync
```

### Uvicorn can't start
**Check logs and try activating venv explicitly:**
```bash
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # macOS/Linux
uvicorn app.main:app --reload --port 8000
```

---

## 📚 Detailed File Guide - Learn the Architecture

### Core Application Files

#### `app/main.py` - Application Factory & Entry Point
```python
# This is where everything starts
app = create_app()  # FastAPI instance created here
```
**What it does:**
- Creates the FastAPI application instance
- Registers exception handlers (handle errors gracefully)
- Adds middleware (CORS, logging, rate limiting)
- Includes routers (mount API endpoints)
- Defines health check endpoint

**Key Learning:** This follows the **Factory Pattern** — keeps app initialization separate from execution.

---

### Configuration & Settings

#### `app/core/config.py` - Environment Configuration
```python
# All settings are type-safe and validated
class Settings(BaseSettings):
    secret_key: str  # Loads from .env
    environment: str  # development, staging, production
    debug: bool
    # ...all config in one place
```
**What it does:**
- Loads environment variables from `.env` file
- Validates all settings at startup (fail fast!)
- Provides default values
- Used across the app via `get_settings()`

**Why it's separate:** Keeps secrets out of code, follows **12-factor app** methodology.

---

### Security Layer

#### `app/core/security.py` - Authentication & Authorization
```python
def hash_password(password: str) -> str:
    # Securely hashes passwords with bcrypt
    
def create_access_token(data: dict, expires_delta: timedelta) -> str:
    # Creates JWT tokens
```
**What it does:**
- Password hashing (bcrypt with salt)
- JWT token generation & validation
- Token expiration handling

**Security Best Practices:**
- Never stores plaintext passwords
- JWTs are signed but not encrypted (don't store sensitive data in them)
- Uses HS256 algorithm (secret key must be 32+ characters)

---

#### `app/core/dependencies.py` - FastAPI Dependency Injection
```python
async def get_current_user(token: str = Depends(HTTPBearer())) -> UserInDB:
    # Validates token and returns user
    # Automatically called by FastAPI for protected endpoints
```
**What it does:**
- Dependency injectors for FastAPI
- Validates JWT tokens
- Checks user roles (viewer, operator, admin)
- Returns current user or raises 401/403 errors

**Why separate:** Reusable auth logic across multiple endpoints.

---

#### `app/core/exceptions.py` - Error Handling
```python
class AppError(Exception):
    """Base for all app errors"""
    status_code = 500
    error_code = "INTERNAL_ERROR"
    
# All errors mapped to HTTP status codes:
# - NotFoundError → 404
# - CredentialsError → 401
# - ForbiddenError → 403
# - ConflictError → 409
```
**What it does:**
- Custom exception hierarchy
- Automatic error response formatting
- Never leaks stack traces or DB details to clients

**Learning Point:** Good error handling is critical for security and debugging!

---

### Data Models & Schemas

#### `app/models/domain.py` - Database Models (In-Memory)
```python
class UserInDB(BaseModel):
    id: str
    username: str
    hashed_password: str
    role: str

class PlantInDB(BaseModel):
    id: str
    name: str
    status: str
    owner_id: str
    created_at: datetime
    # ...fields

# Seeded test data
USERS_DB = {...}  # In-memory "database"
PLANTS_DB = {...}
```
**What it does:**
- Defines data structure for users and plants
- Uses in-memory dictionaries (for learning; replace with SQLAlchemy for production)
- Seeds test data (admin, operator, viewer users)

**Next Step:** Replace `USERS_DB` and `PLANTS_DB` dicts with SQLAlchemy + PostgreSQL

---

#### `app/schemas/` - Pydantic Models (Request/Response Validation)
```python
# auth.py
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    
# plant.py
class PlantCreate(BaseModel):
    name: str
    location: str
    capacity_kw: float
    
class PlantResponse(BaseModel):
    id: str
    name: str
    owner_id: str
```
**What it does:**
- Validates incoming requests (auto-generates 422 errors)
- Serializes outgoing responses (auto-converts to JSON)
- Generates OpenAPI/Swagger documentation automatically

**Why separate from models:** Clear separation of concerns:
- `domain.py` = what's in the DB
- `schemas/*.py` = what clients send/receive

---

### Business Logic

#### `app/services/auth_service.py` - Authentication Logic
```python
def login(username: str, password: str) -> TokenResponse:
    # Find user, verify password, create token
    
def refresh_token(refresh_token: str) -> TokenResponse:
    # Validate old token, issue new one
```
**What it does:**
- Encapsulates login/token logic
- Separates business rules from HTTP layer
- Can be tested independently

**Design Pattern:** **Service Layer** — keeps endpoints thin, logic reusable.

---

#### `app/services/plant_service.py` - Plant CRUD Logic
```python
def list_plants(params: PlantQueryParams) -> PaginatedResponse[PlantResponse]:
    # Filter, paginate, return results
    
def create_plant(data: PlantCreate, current_user: UserInDB) -> PlantResponse:
    # Validate uniqueness, create, store
    
def update_plant(plant_id: str, data: PlantUpdate, user: UserInDB):
    # Check ownership, apply updates, save
```
**What it does:**
- CRUD operations for plants
- Business rule validation (unique names, ownership checks)
- No HTTP details here — pure business logic

---

### API Endpoints

#### `app/api/v1/endpoints/auth.py` - Authentication Endpoints
```python
@router.post("/auth/login")
async def login(body: LoginRequest) -> TokenResponse:
    # HTTP layer — converts request to service call
    # Returns response

@router.post("/auth/refresh")
async def refresh(body: RefreshRequest) -> TokenResponse:
    # Refresh token endpoint
```
**What it does:**
- HTTP request/response handling
- Calls service layer for business logic
- Returns formatted responses

---

#### `app/api/v1/endpoints/plants.py` - Plant Endpoints
```python
@router.get("", response_model=PaginatedResponse[PlantResponse])
async def list_plants(
    current_user: UserInDB = Depends(require_viewer),
    page: int = Query(1)
) -> PaginatedResponse[PlantResponse]:
    # Dependency injection handles auth
    # Service layer handles logic
    return plant_service.list_plants(params)
```
**What it does:**
- CRUD endpoints
- Dependency injection for auth
- Response validation

---

### Middleware

#### `app/middleware/logging.py` - Request/Response Logging
```python
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Log: request_id, method, path, status, duration
        # Useful for debugging and monitoring
```
**What it does:**
- Logs all HTTP requests with timing
- Attaches request IDs for correlation
- Cloud-Run compatible JSON logging

---

#### `app/middleware/rate_limit.py` - Rate Limiting
```python
class RateLimitMiddleware:
    def _check_rate_limit(self, request):
        # Track requests per IP
        # Raise 429 if exceeded
```
**What it does:**
- Per-IP request rate limiting
- Sliding window algorithm
- In-memory store (upgrade to Redis for multi-instance)

---

### `__init__.py` Files - Why They're Empty

**What they do:**
- Mark directories as Python packages
- Allow imports like `from app.services import plant_service`
- Can be empty (Python 3.3+) — they're just markers

**Python needs them because:**
```python
# With __init__.py:
from app.services import plant_service  # ✅ Works

# Without __init__.py:
from app.services import plant_service  # ❌ ModuleNotFoundError
```

**When to add code to `__init__.py`:**
```python
# app/__init__.py
from app.core.config import get_settings  # Re-export commonly used items
from app.models import UserInDB

# Now users can do:
from app import get_settings, UserInDB  # Cleaner imports
```

**For this project:** We keep them empty because each module is accessed directly. This is fine and common!

---

## 🐛 Debugging Complete API Flow

### Option 1: Print Debugging in VS Code

#### Step 1: Add Debug Logs
```python
# In app/api/v1/endpoints/plants.py
@router.get("", response_model=PaginatedResponse[PlantResponse])
async def list_plants(
    current_user: UserInDB = Depends(require_viewer),
    page: int = Query(1)
):
    print(f"DEBUG: User {current_user.username} requesting plants, page {page}")
    result = plant_service.list_plants(params)
    print(f"DEBUG: Returning {len(result.items)} plants")
    return result
```

#### Step 2: Check Terminal Output
Server logs appear in your terminal when requests come in.

---

### Option 2: Python Debugger (pdb) - **RECOMMENDED**

#### Step 1: Add Breakpoint
```python
# In any file
def list_plants(params):
    breakpoint()  # Execution pauses here
    all_plants = list(PLANTS_DB.values())
    # Interactive inspection
```

#### Step 2: Run Server in Debug Mode
```bash
# Start server normally
uvicorn app.main:app --reload --port 8000

# Then make API request via Swagger UI
# Server will pause at breakpoint, terminal becomes interactive
```

#### Step 3: Inspect Variables
```
> l  # List code
> p all_plants  # Print variable
> n  # Next line
> s  # Step into function
> c  # Continue
> q  # Quit
```

---

### Option 3: VS Code Debugger - **BEST**

#### Step 1: Add `.vscode/launch.json`
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI Debug",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["app.main:app", "--reload", "--port", "8000"],
            "jinja": true,
            "console": "integratedTerminal"
        }
    ]
}
```

#### Step 2: Set Breakpoints
- Click left of line number in VS Code to add red dot
- Shows variable values on hover

#### Step 3: Start Debugging
- Press `F5` or Run → Start Debugging
- Make request via Swagger UI
- Code pauses at breakpoint with full VS Code debug panel

---

### Option 4: Complete Request Flow Tracing

**Flow diagram:**
```
1. Client (Swagger UI)
   ↓ HTTP POST /api/v1/auth/login
   
2. FastAPI Router
   ↓ Matches route, validates request body (LoginRequest)
   
3. Endpoint Handler (endpoints/auth.py)
   → auth_service.login(username, password)
   ↓
   
4. Service Layer (services/auth_service.py)
   → USERS_DB.get(username)
   → security.verify_password()
   → security.create_access_token()
   ↓
   
5. Response
   ← TokenResponse (JSON)
   ← HTTP 200 OK
```

**Add logging at each step:**
```python
# app/core/security.py
import logging
logger = logging.getLogger(__name__)

def create_access_token(data: dict):
    logger.debug(f"Creating token for: {data}")
    token = jwt.encode(...)
    logger.debug(f"Token created: {token[:20]}...")
    return token
```

**View logs:**
```bash
# Terminal shows all debug logs during request
DEBUG:app.core.security:Creating token for: {'sub': 'admin'}
DEBUG:app.core.security:Token created: eyJhbGciOiJIUzI1Ni...
INFO:app.access:http_request method=POST path=/api/v1/auth/login status_code=200 duration_ms=15.5
```

---

### Option 5: Test-Driven Debugging

**Best for understanding flows:**
```python
# tests/integration/test_auth_endpoints.py
def test_login_flow():
    # Setup
    client = TestClient(app)
    
    # Act
    response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "Admin@123"
    })
    
    # Assert & Inspect
    assert response.status_code == 200
    data = response.json()
    print(f"Response: {data}")
    assert "access_token" in data
    print("✅ Login flow works!")
```

**Run with output:**
```bash
pytest tests/integration/test_auth_endpoints.py -v -s
```

The `-s` flag shows all `print()` statements!

---

## Learning Checklist

- [ ] Understand Factory Pattern in `main.py`
- [ ] Read through `config.py` and modify `.env` values
- [ ] Trace JWT creation in `security.py`
- [ ] Run `pytest` and read test flows
- [ ] Add a breakpoint and debug a request
- [ ] Modify a service function and see it reflected in API
- [ ] Check logs in terminal while making requests
- [ ] Try the Swagger UI with different roles (admin/operator/viewer)
- [ ] Create new plant, then try to delete it as non-admin (should fail!)

---

## Next Steps for Production

1. **Replace in-memory DB with SQLAlchemy + PostgreSQL**
2. **Add proper logging to file**
3. **Deploy to Cloud Run**
4. **Add more tests for edge cases**
5. **Implement caching with Redis**
6. **Add database migrations with Alembic**
