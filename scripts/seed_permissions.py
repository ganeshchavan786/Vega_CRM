"""
Seed Default Permissions Script
Run this to populate the permissions table with default permissions
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.permission import Permission, RolePermission

# Default permissions to seed
DEFAULT_PERMISSIONS = [
    # Customer permissions
    {"resource": "customer", "action": "create", "description": "Create new customers"},
    {"resource": "customer", "action": "read", "description": "View customer details"},
    {"resource": "customer", "action": "update", "description": "Update customer information"},
    {"resource": "customer", "action": "delete", "description": "Delete customers"},
    
    # Lead permissions
    {"resource": "lead", "action": "create", "description": "Create new leads"},
    {"resource": "lead", "action": "read", "description": "View lead details"},
    {"resource": "lead", "action": "update", "description": "Update lead information"},
    {"resource": "lead", "action": "delete", "description": "Delete leads"},
    {"resource": "lead", "action": "convert", "description": "Convert leads to customers"},
    
    # Deal permissions
    {"resource": "deal", "action": "create", "description": "Create new deals"},
    {"resource": "deal", "action": "read", "description": "View deal details"},
    {"resource": "deal", "action": "update", "description": "Update deal information"},
    {"resource": "deal", "action": "delete", "description": "Delete deals"},
    
    # Task permissions
    {"resource": "task", "action": "create", "description": "Create new tasks"},
    {"resource": "task", "action": "read", "description": "View task details"},
    {"resource": "task", "action": "update", "description": "Update task information"},
    {"resource": "task", "action": "delete", "description": "Delete tasks"},
    
    # Activity permissions
    {"resource": "activity", "action": "create", "description": "Create new activities"},
    {"resource": "activity", "action": "read", "description": "View activity details"},
    {"resource": "activity", "action": "update", "description": "Update activity information"},
    {"resource": "activity", "action": "delete", "description": "Delete activities"},
    
    # User permissions
    {"resource": "user", "action": "create", "description": "Create new users"},
    {"resource": "user", "action": "read", "description": "View user details"},
    {"resource": "user", "action": "update", "description": "Update user information"},
    {"resource": "user", "action": "delete", "description": "Delete users"},
    
    # Company permissions
    {"resource": "company", "action": "create", "description": "Create new companies"},
    {"resource": "company", "action": "read", "description": "View company details"},
    {"resource": "company", "action": "update", "description": "Update company information"},
    {"resource": "company", "action": "delete", "description": "Delete companies"},
    
    # Contact permissions
    {"resource": "contact", "action": "create", "description": "Create new contacts"},
    {"resource": "contact", "action": "read", "description": "View contact details"},
    {"resource": "contact", "action": "update", "description": "Update contact information"},
    {"resource": "contact", "action": "delete", "description": "Delete contacts"},
    
    # Report permissions
    {"resource": "report", "action": "create", "description": "Create new reports"},
    {"resource": "report", "action": "read", "description": "View reports"},
    {"resource": "report", "action": "update", "description": "Update reports"},
    {"resource": "report", "action": "delete", "description": "Delete reports"},
    {"resource": "report", "action": "run", "description": "Execute reports"},
    
    # Permission management
    {"resource": "permission", "action": "read", "description": "View permissions"},
    {"resource": "permission", "action": "update", "description": "Update permissions"},
    
    # Audit trail
    {"resource": "audit", "action": "read", "description": "View audit trails"},
    
    # System logs
    {"resource": "logs", "action": "read", "description": "View system logs"},
    {"resource": "logs", "action": "delete", "description": "Cleanup old logs"},
    
    # Admin settings
    {"resource": "settings", "action": "read", "description": "View system settings"},
    {"resource": "settings", "action": "update", "description": "Update system settings"},
]

# Default role permissions (which roles get which permissions by default)
DEFAULT_ROLE_PERMISSIONS = {
    "admin": ["*"],  # Admin gets all permissions
    "manager": [
        "customer:*", "lead:*", "deal:*", "task:*", "activity:*", 
        "contact:*", "report:read", "report:run", "user:read"
    ],
    "sales_rep": [
        "customer:create", "customer:read", "customer:update",
        "lead:create", "lead:read", "lead:update", "lead:convert",
        "deal:create", "deal:read", "deal:update",
        "task:create", "task:read", "task:update",
        "activity:create", "activity:read", "activity:update",
        "contact:create", "contact:read", "contact:update",
        "report:read", "report:run"
    ],
    "user": [
        "customer:read", "lead:read", "deal:read", 
        "task:read", "task:create", "task:update",
        "activity:read", "activity:create",
        "contact:read", "report:read"
    ]
}


def seed_permissions():
    """Seed default permissions into database"""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if permissions already exist
        existing_count = db.query(Permission).count()
        if existing_count > 0:
            print(f"Permissions table already has {existing_count} entries.")
            user_input = input("Do you want to add missing permissions? (y/n): ")
            if user_input.lower() != 'y':
                print("Skipping permission seeding.")
                return
        
        # Seed permissions
        added_count = 0
        for perm_data in DEFAULT_PERMISSIONS:
            # Check if permission already exists
            existing = db.query(Permission).filter(
                Permission.resource == perm_data["resource"],
                Permission.action == perm_data["action"]
            ).first()
            
            if not existing:
                permission = Permission(
                    resource=perm_data["resource"],
                    action=perm_data["action"],
                    description=perm_data["description"]
                )
                db.add(permission)
                added_count += 1
                print(f"  Added: {perm_data['resource']}:{perm_data['action']}")
        
        db.commit()
        print(f"\n[OK] Added {added_count} new permissions")
        
        # Get total count
        total = db.query(Permission).count()
        print(f"Total permissions in database: {total}")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding permissions: {e}")
        raise
    finally:
        db.close()


def list_permissions():
    """List all permissions in database"""
    db = SessionLocal()
    try:
        permissions = db.query(Permission).all()
        print(f"\nPermissions in database ({len(permissions)} total):\n")
        for p in permissions:
            print(f"  [{p.id}] {p.resource}:{p.action} - {p.description}")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Permission Seeding Script")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_permissions()
    else:
        seed_permissions()
        print("\n" + "=" * 50)
        list_permissions()
