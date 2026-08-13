#!/usr/bin/env python
"""Quick debug script to test auth flow"""
import sys
sys.path.insert(0, '.')

from app.services.auth_service import authenticate_user
from app.core.exceptions import CredentialsError

try:
    print("Attempting to authenticate admin with wrong password...")
    user = authenticate_user("admin", "WrongPass@123")
    print(f"Success: {user}")
except CredentialsError as e:
    print(f"CredentialsError (expected): {e}")
except Exception as e:
    print(f"Unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
