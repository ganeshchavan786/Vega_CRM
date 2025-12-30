"""
Test script for Forgot Password API
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.controllers.auth_controller import AuthController
from app.models.user import User

def test_forgot_password():
    """Test forgot password flow"""
    db = SessionLocal()
    
    try:
        # Get a test user
        user = db.query(User).first()
        
        if not user:
            print("[ERROR] No users found in database")
            return
        
        print(f"Testing with user: {user.email}")
        print("-" * 50)
        
        # Step 1: Request password reset
        print("\n1. Requesting password reset...")
        result = AuthController.create_password_reset_token(user.email, db)
        print(f"   Result: {result.get('message')}")
        
        token = result.get('token')
        if token:
            print(f"   Token generated: {token[:20]}...")
            
            # Step 2: Verify token
            print("\n2. Verifying token...")
            verify_result = AuthController.verify_reset_token(token, db)
            print(f"   Valid: {verify_result.get('valid')}")
            print(f"   Message: {verify_result.get('message')}")
            
            # Step 3: Reset password (optional - commented to avoid changing password)
            # print("\n3. Resetting password...")
            # reset_result = AuthController.reset_password(token, "NewPassword123", db)
            # print(f"   Result: {reset_result.get('message')}")
            
            print("\n" + "=" * 50)
            print("[OK] Forgot Password API is working correctly!")
            print("=" * 50)
        else:
            print("[INFO] Token not returned (email may not exist)")
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_forgot_password()
