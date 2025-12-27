"""
Create Phase 2 Database Tables
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from app.database import engine, Base
from app.models import Lead, Deal, Task, Activity

print("=" * 70)
print("CREATING PHASE 2 DATABASE TABLES")
print("=" * 70)

try:
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("\n[SUCCESS] All Phase 2 tables created:")
    print("   - leads table")
    print("   - deals table")
    print("   - tasks table")
    print("   - activities table")
    print("\n" + "=" * 70)
    print("DATABASE READY FOR PHASE 2!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    print("=" * 70)

