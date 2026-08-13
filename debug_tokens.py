#!/usr/bin/env python
"""Quick debug script to test token creation"""
import sys
sys.path.insert(0, '.')

from app.models.domain import USERS_DB, USERNAME_INDEX, UserInDB, hash_password
from app.services.auth_service import create_tokens

# First, set up test user manually
test_user = UserInDB(
    id="test-admin",
    username="admin",
    email="admin@test.com",
    hashed_password=hash_password("Admin@123"),
    role="admin",
    is_active=True
)
USERS_DB[test_user.id] = test_user
USERNAME_INDEX["admin"] = test_user.id

try:
    print("Creating tokens for admin...")
    tokens = create_tokens(test_user)
    print(f"Success: {tokens}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
