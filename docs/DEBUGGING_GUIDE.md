"""
DEBUGGING API CALLS - Complete Guide
=====================================

There are 5 ways to debug your FastAPI application.
Choose based on your debugging needs.
"""

# FLOW OF AN API CALL:
# ====================
# 
# 1. Client sends HTTP request
#    POST /api/v1/auth/login
#    { "username": "admin", "password": "Admin@123" }
#    
# 2. FastAPI Router matches the path
#    → Looks for POST /auth/login
#    → Found in app/api/v1/endpoints/auth.py
#    
# 3. Request validation (Pydantic)
#    → Validates body matches LoginRequest schema
#    → If invalid → 422 Unprocessable Entity
#    
# 4. Dependency Injection
#    → current_user dependency runs (but login doesn't need auth)
#    
# 5. Endpoint Handler executes
#    → auth.login(body.username, body.password)
#    
# 6. Service Layer (business logic)
#    → auth_service.login() called
#    → Finds user in USERS_DB
#    → Verifies password
#    → Creates JWT token
#    
# 7. Response serialization
#    → TokenResponse converted to JSON
#    → Status code 200
#    
# 8. Client receives response
#    { "access_token": "eyJ...", "token_type": "bearer" }


# METHOD 1: Simple Print Debugging
# =================================

# File: app/api/v1/endpoints/auth.py
from app.services import auth_service

@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    print(f"\n{'='*60}")
    print(f"🔐 LOGIN REQUEST")
    print(f"{'='*60}")
    print(f"Username: {body.username}")
    print(f"Password: {'*' * len(body.password)}")  # Don't print password!
    
    # Call service
    result = auth_service.login(body.username, body.password)
    
    print(f"\n✅ Login successful!")
    print(f"Access token: {result.access_token[:20]}...")
    print(f"{'='*60}\n")
    
    return result

# In terminal:
# ============================================================
# 🔐 LOGIN REQUEST
# ============================================================
# Username: admin
# Password: *********
#
# ✅ Login successful!
# Access token: eyJhbGciOiJIUzI1NiIsI...
# ============================================================


# METHOD 2: Logging (Better than print)
# ======================================

import logging

logger = logging.getLogger(__name__)  # Best practice

@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    logger.info(f"Login attempt for user: {body.username}")
    
    try:
        result = auth_service.login(body.username, body.password)
        logger.info(f"Login successful for user: {body.username}")
        return result
    except Exception as e:
        logger.error(f"Login failed for {body.username}: {str(e)}")
        raise

# Run with:
# .venv\Scripts\Activate.ps1
# uvicorn app.main:app --log-level debug

# Output shows:
# INFO:app.api.v1.endpoints.auth:Login attempt for user: admin
# INFO:app.api.v1.endpoints.auth:Login successful for user: admin


# METHOD 3: Python Debugger (pdb) - Interactive
# ===============================================

@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    breakpoint()  # ← Execution pauses here
    # Now terminal becomes interactive!
    # You can inspect variables, step through code
    
    result = auth_service.login(body.username, body.password)
    return result

# Run normally:
# .venv\Scripts\Activate.ps1
# uvicorn app.main:app --reload

# Make request via Swagger UI
# Terminal shows:
# > 
# Type: l (list), p body, p result, n (next), s (step), c (continue), q (quit)
#
# > p body
# LoginRequest(username='admin', password='Admin@123')
# 
# > n  # Next line
# > c  # Continue


# METHOD 4: VS Code Debugger - Visual & Powerful
# ===============================================

# Create .vscode/launch.json:
import json
config = {
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI Debug",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["app.main:app", "--reload", "--port", "8000"],
            "jinja": True,
            "console": "integratedTerminal"
        }
    ]
}

# Then:
# 1. Click on line number (left margin) to add red breakpoint dot
# 2. Press F5 to start debugging
# 3. Make request via Swagger UI
# 4. Code stops at breakpoint
# 5. Hover over variables to see values
# 6. Use Debug panel (Variables, Watch, etc.)


# METHOD 5: Test-Driven Debugging (Best for understanding)
# =========================================================

# File: tests/integration/test_auth_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_flow():
    """Complete login flow with detailed inspection"""
    
    print("\n" + "="*60)
    print("TEST: Login Flow")
    print("="*60)
    
    # Step 1: Make request
    print("\n1️⃣  Making login request...")
    response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "Admin@123"
    })
    print(f"   Status: {response.status_code}")
    
    # Step 2: Check response
    print("\n2️⃣  Response received:")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    # Step 3: Verify data
    print("\n3️⃣  Verifying response format:")
    assert response.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    print("   ✅ All checks passed!")
    
    # Step 4: Use token
    print("\n4️⃣  Using token for authenticated request:")
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = client.get("/api/v1/auth/me", headers=headers)
    print(f"   GET /auth/me status: {profile_response.status_code}")
    print(f"   Profile: {profile_response.json()}")
    print("="*60)

# Run with:
# pytest tests/integration/test_auth_endpoints.py::test_login_flow -v -s

# Output shows EVERYTHING with print statements!


# FLOW TRACING WITH LOGGING AT EACH LAYER
# =========================================

# app/core/security.py
import logging
logger = logging.getLogger("security")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.debug(f"Verifying password... (hashed: {hashed_password[:20]}...)")
    result = pwd_context.verify(plain_password, hashed_password)
    logger.debug(f"Password verification result: {result}")
    return result

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    logger.debug(f"Creating access token for user: {data.get('sub')}")
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    logger.debug(f"Token created: {encoded_jwt[:30]}...")
    return encoded_jwt

# app/services/auth_service.py
logger = logging.getLogger("auth_service")

def login(username: str, password: str) -> TokenResponse:
    logger.info(f"Login attempt for: {username}")
    
    user = USERS_DB.get(username)
    if not user:
        logger.warning(f"User not found: {username}")
        raise CredentialsError("Invalid credentials")
    
    logger.debug(f"User found: {user.username}, verifying password")
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Invalid password for user: {username}")
        raise CredentialsError("Invalid credentials")
    
    logger.debug(f"Password verified for: {username}")
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    logger.info(f"Login successful for: {username}")
    return TokenResponse(access_token=access_token, token_type="bearer")

# Run with:
# export PYTHONLOGGING=debug  (or set in .env)
# uvicorn app.main:app --log-level debug

# Terminal output shows COMPLETE TRACE:
# INFO:auth_service:Login attempt for: admin
# DEBUG:auth_service:User found: admin, verifying password
# DEBUG:security:Verifying password... (hashed: $2b$12$abcd...)
# DEBUG:security:Password verification result: True
# DEBUG:security:Creating access token for user: user_1
# DEBUG:security:Token created: eyJhbGciOiJIUzI1NiIsI...
# INFO:auth_service:Login successful for: admin


# SUMMARY: Which Method to Use?
# ==============================
# 
# 1. Quick print debugging?
#    → Method 1 (Print)
#
# 2. Production-grade logging?
#    → Method 2 (Logging)
#
# 3. Interactive variable inspection?
#    → Method 3 (pdb breakpoint)
#
# 4. Visual debugging with UI?
#    → Method 4 (VS Code Debugger) ⭐ RECOMMENDED
#
# 5. Understand complete flow?
#    → Method 5 (Test-Driven) ⭐ BEST FOR LEARNING
#
# Best Practice:
# Use Method 2 (logging) in code
# Use Method 4 (VS Code) when debugging specific issues
# Use Method 5 (tests) when learning the codebase
