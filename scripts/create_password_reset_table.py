"""
Script to create password_reset_tokens table in SQLite database
Run this script to manually create the table if needed
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models.password_reset import PasswordResetToken

def create_table():
    """Create password_reset_tokens table"""
    print("Creating password_reset_tokens table...")
    
    # Create only the PasswordResetToken table
    PasswordResetToken.__table__.create(bind=engine, checkfirst=True)
    
    print("[OK] Table created successfully!")
    
    # Verify table exists
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if 'password_reset_tokens' in tables:
        print("[OK] Verified: password_reset_tokens table exists")
        
        # Show table columns
        columns = inspector.get_columns('password_reset_tokens')
        print("\nTable columns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    else:
        print("[ERROR] Table was not created")

if __name__ == "__main__":
    create_table()
