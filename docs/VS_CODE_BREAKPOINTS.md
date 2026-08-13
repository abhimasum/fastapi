"""
DEBUGGING WITH BREAKPOINTS IN VS CODE
Like Visual Studio, but for FastAPI!
=====================================

This is EXACTLY like debugging ASP.NET Web API in Visual Studio.
Same breakpoints, same step through code, same variable inspection.
"""

# QUICK START COMPARISON
# ======================
# 
# ASP.NET Visual Studio:
# ├── Set breakpoint (click line number → red dot)
# ├── Press F5 to start debugging
# ├── Make HTTP request
# ├── Code pauses at breakpoint
# ├── Step through code (F10 = Step Over, F11 = Step Into)
# ├── Hover over variables to see values
# └── Press F5 to continue
#
# FastAPI VS Code:
# ├── Set breakpoint (click line number → red dot) ← SAME!
# ├── Press F5 to start debugging ← SAME!
# ├── Make HTTP request via Swagger UI
# ├── Code pauses at breakpoint ← SAME!
# ├── Step through code (F10 = Step Over, F11 = Step Into) ← SAME!
# ├── Hover over variables to see values ← SAME!
# └── Press F5 to continue ← SAME!


# STEP-BY-STEP DEBUGGING GUIDE
# =============================

# Step 1: Open the file you want to debug
# File: app/services/auth_service.py

def login(username: str, password: str) -> TokenResponse:
    """This is where we'll add a breakpoint"""
    user = USERS_DB.get(username)  # ← CLICK HERE to add breakpoint
    # A red dot appears on the line number
    # That's your breakpoint!


# Step 2: Set Breakpoints
# =======================
# Click on the line number (left margin) where you want to pause
# You'll see a red dot appear
#
# Example breakpoints to set:
# 
# app/services/auth_service.py
#   Line 15: user = USERS_DB.get(username)  ← Check if user exists
#   Line 16: if not user: ← Check condition
#   
# app/core/security.py
#   Line 30: verify_password(password, user.hashed_password)  ← Check password
#   Line 35: create_access_token(...)  ← Check token creation


# Step 3: Start Debugging
# =======================
# Press F5 (or Debug → Start Debugging from menu)
# Terminal shows:
# 
#   Starting debugger...
#   Uvicorn running on http://127.0.0.1:8000
#   Type c to continue, q to quit, etc.


# Step 4: Make a Request
# ======================
# Open Swagger UI: http://localhost:8000/docs
# Click on POST /auth/login
# Enter credentials:
#   username: admin
#   password: Admin@123
# Click "Try it out"
#
# → Code pauses at first breakpoint!


# Step 5: VS Code Debug Panel Appears
# ====================================
# Top of VS Code shows:
# 
# [Continue] [Step Over] [Step Into] [Step Out] [Restart] [Stop]
#    F5         F10         F11       Shift+F11
#
# Left panel shows:
# ├── Variables (local variables visible)
# ├── Watch (add custom expressions)
# ├── Call Stack (see function call history)
# └── Breakpoints (see all your breakpoints)


# Step 6: Inspect Variables
# ==========================
# Hover over any variable to see its value in a popup!
# 
# Example:
# 
# def login(username: str, password: str) -> TokenResponse:
#     user = USERS_DB.get(username)  ← Hover over 'user'
#                                       Shows: user = UserInDB(id='user_1', username='admin', ...)
#     
#     if not user:
#         hover over 'username' ← Shows: username = 'admin'


# Step 7: Step Through Code
# ==========================
# 
# F10 = Step Over (go to next line, don't enter functions)
# F11 = Step Into (enter the function being called)
# Shift+F11 = Step Out (exit current function)
# F5 = Continue (resume execution)
#
# Example flow:
#
# Current line: user = USERS_DB.get(username)
# 
# Press F10 → Goes to next line (skips USERS_DB.get)
# OR
# Press F11 → Enters USERS_DB.get function if you want to see inside


# EXAMPLE DEBUGGING SESSION
# ==========================

# 1. Stop at: app/services/auth_service.py line 15
#    def login(username: str, password: str):
#        user = USERS_DB.get(username)  ← BREAKPOINT
#
#    Variables panel shows:
#    └── username: "admin"
#    └── password: "Admin@123"

# 2. Press F10 (Step Over)
#    Now at: if not user:
#
#    Variables panel shows:
#    └── user: UserInDB(id='user_1', username='admin', role='admin')

# 3. Press F10 again
#    Now at: if not user.verify_password(password):  (false, so skipped)

# 4. Press F10 again
#    Now at: access_token = create_access_token(...)
#
#    Hover over user to see: UserInDB {...}

# 5. Press F11 (Step Into)
#    Enters create_access_token function
#    You're now in app/core/security.py
#
#    Can see JWT encoding happening!

# 6. Press F5 (Continue)
#    Resumes execution
#    Code finishes, returns token to client


# WATCH EXPRESSIONS
# =================
# 
# You can add custom expressions to watch:
#
# In Debug panel:
# 1. Click WATCH section
# 2. Click + icon
# 3. Type: user.username
# 4. Watches that expression as you step through code


# CONDITIONAL BREAKPOINTS
# =======================
# 
# Right-click on breakpoint (red dot)
# Select "Edit Breakpoint"
# Enter condition: username == "admin"
# 
# Code only pauses at that breakpoint if condition is true!
#
# Useful for:
# - Debug only specific users
# - Debug only when certain values
# - Skip breakpoints in loops except 10th iteration


# DEBUG CONSOLE
# =============
# 
# Bottom of VS Code shows Debug Console
# You can TYPE Python code while paused!
#
# Example:
# > user
# UserInDB(id='user_1', username='admin', role='admin')
# 
# > len(USERS_DB)
# 3
#
# > user.hashed_password
# '$2b$12$abcd...xyz'


# COMMON DEBUGGING SCENARIOS
# ===========================

# Scenario 1: Find why login is failing
# ======================================
# Breakpoints at:
# 1. app/api/v1/endpoints/auth.py - login() entry
# 2. app/services/auth_service.py - login() entry
# 3. app/core/security.py - verify_password()
#
# Step through each, inspect user/password at each point


# Scenario 2: Debug plant creation
# ================================
# Breakpoints at:
# 1. app/api/v1/endpoints/plants.py - create_plant()
# 2. app/services/plant_service.py - create_plant()
#
# Check current_user, request data, database state


# Scenario 3: Debug role-based access
# ====================================
# Set breakpoint in:
# app/core/dependencies.py - require_admin()
#
# Step through and see if current_user.role == 'admin'


# KEYBOARD SHORTCUTS
# ==================
# F5              → Start/Continue debugging
# Shift+F5        → Stop debugging
# F10             → Step Over (next line)
# F11             → Step Into (enter function)
# Shift+F11       → Step Out (exit function)
# Ctrl+K Ctrl+I   → Open hover tooltip
# Ctrl+Shift+D    → Open Debug view


# COMPARISON WITH ASP.NET
# =======================
#
# Visual Studio (ASP.NET):
# ├── Set breakpoints ✓
# ├── F5 to debug ✓
# ├── Step Over/Into ✓
# ├── Inspect variables ✓
# ├── Watch expressions ✓
# ├── Call stack ✓
# ├── Conditional breakpoints ✓
# └── Debug console ✓
#
# VS Code (FastAPI):
# ├── Set breakpoints ✓ (SAME!)
# ├── F5 to debug ✓ (SAME!)
# ├── Step Over/Into ✓ (SAME!)
# ├── Inspect variables ✓ (SAME!)
# ├── Watch expressions ✓ (SAME!)
# ├── Call stack ✓ (SAME!)
# ├── Conditional breakpoints ✓ (SAME!)
# └── Debug console ✓ (SAME!)
#
# It's essentially identical! The workflow is the same.
"""

# YOUR FIRST BREAKPOINT DEBUGGING SESSION
# =========================================

# 1. Open app/services/auth_service.py
# 2. Click on line 15 (left margin) → red dot appears
# 3. Press F5 (or Debug menu → Start Debugging)
# 4. Wait for: "Uvicorn running on http://127.0.0.1:8000"
# 5. Open http://localhost:8000/docs
# 6. Try login with admin/Admin@123
# 7. VS Code pauses at your breakpoint!
# 8. Hover over variables to see values
# 9. Press F10 to go to next line
# 10. Press F5 to continue
# 11. Login completes!

# That's it! You're debugging FastAPI like you would ASP.NET!
