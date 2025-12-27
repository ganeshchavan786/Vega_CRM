"""
Phase 1 Migration Script - Add new columns to existing tables
SQLite ALTER TABLE migration for Phase 1 enterprise fields
"""

import sqlite3
from pathlib import Path

def get_db_path():
    """Get database path from config"""
    from app.config import settings
    # SQLite URL format: sqlite:///./data/crm.db
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_path = Path(db_path).resolve()
    else:
        db_path = Path(db_path)
        if not db_path.is_absolute():
            db_path = Path.cwd() / db_path
    return str(db_path)

def add_column_if_not_exists(cursor, table_name, column_name, column_definition):
    """Add column to table if it doesn't exist"""
    # Check if column exists
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    
    if column_name not in columns:
        try:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
            print(f"  [OK] Added column {table_name}.{column_name}")
            return True
        except sqlite3.OperationalError as e:
            print(f"  [ERROR] Error adding {table_name}.{column_name}: {e}")
            return False
    else:
        print(f"  [SKIP] Column {table_name}.{column_name} already exists")
        return False

def migrate_leads_table(cursor):
    """Add new columns to leads table"""
    print("\n=== Migrating leads table ===")
    
    columns_to_add = [
        ("converted_to_account_id", "INTEGER"),
        ("first_name", "VARCHAR(100)"),
        ("last_name", "VARCHAR(100)"),
        ("country", "VARCHAR(100) DEFAULT 'India'"),
        ("campaign", "VARCHAR(200)"),
        ("medium", "VARCHAR(50)"),
        ("term", "VARCHAR(200)"),
        ("lead_owner_id", "INTEGER"),
        ("stage", "VARCHAR(50) DEFAULT 'awareness'"),
        ("lead_score", "INTEGER DEFAULT 0"),
        ("interest_product", "VARCHAR(200)"),
        ("budget_range", "VARCHAR(100)"),
        ("authority_level", "VARCHAR(50)"),
        ("timeline", "VARCHAR(100)"),
        ("gdpr_consent", "BOOLEAN DEFAULT 0"),
        ("dnd_status", "BOOLEAN DEFAULT 0"),
        ("opt_in_date", "DATETIME"),
        ("is_duplicate", "BOOLEAN DEFAULT 0"),
        ("spam_score", "INTEGER DEFAULT 0"),
        ("validation_status", "VARCHAR(50) DEFAULT 'pending'"),
        ("converted_at", "DATETIME"),
    ]
    
    added_count = 0
    for column_name, column_def in columns_to_add:
        if add_column_if_not_exists(cursor, "leads", column_name, column_def):
            added_count += 1
    
    # Add foreign key constraints (SQLite doesn't support ADD CONSTRAINT, so we'll note them)
    print(f"  Note: Foreign keys will be handled by application layer")
    
    return added_count

def migrate_customers_table(cursor):
    """Add new columns to customers table"""
    print("\n=== Migrating customers table ===")
    
    columns_to_add = [
        ("account_type", "VARCHAR(50)"),
        ("company_size", "VARCHAR(100)"),
        ("annual_revenue", "NUMERIC(15, 2)"),
        ("gstin", "VARCHAR(15)"),
        ("health_score", "VARCHAR(20)"),
        ("lifecycle_stage", "VARCHAR(50)"),
        ("is_active", "BOOLEAN DEFAULT 1"),
        ("account_owner_id", "INTEGER"),
    ]
    
    added_count = 0
    for column_name, column_def in columns_to_add:
        if add_column_if_not_exists(cursor, "customers", column_name, column_def):
            added_count += 1
    
    return added_count

def migrate_deals_table(cursor):
    """Add new columns to deals table"""
    print("\n=== Migrating deals table ===")
    
    columns_to_add = [
        ("account_id", "INTEGER"),
        ("primary_contact_id", "INTEGER"),
        ("forecast_category", "VARCHAR(50)"),
    ]
    
    added_count = 0
    for column_name, column_def in columns_to_add:
        if add_column_if_not_exists(cursor, "deals", column_name, column_def):
            added_count += 1
    
    return added_count

def create_contacts_table(cursor):
    """Create contacts table if it doesn't exist"""
    print("\n=== Creating contacts table ===")
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='contacts'
    """)
    
    if cursor.fetchone():
        print("  - contacts table already exists")
        return False
    else:
        cursor.execute("""
            CREATE TABLE contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                account_id INTEGER NOT NULL,
                name VARCHAR(200) NOT NULL,
                job_title VARCHAR(100),
                role VARCHAR(50),
                email VARCHAR(255),
                phone VARCHAR(20),
                preferred_channel VARCHAR(50),
                influence_score VARCHAR(20),
                is_primary_contact BOOLEAN NOT NULL DEFAULT 0,
                created_by INTEGER,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (account_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX ix_contacts_company_id ON contacts(company_id)")
        cursor.execute("CREATE INDEX ix_contacts_account_id ON contacts(account_id)")
        cursor.execute("CREATE INDEX ix_contacts_email ON contacts(email)")
        cursor.execute("CREATE INDEX ix_contacts_created_by ON contacts(created_by)")
        
        print("  [OK] Created contacts table with indexes")
        return True

def main():
    """Run migration"""
    print("=" * 60)
    print("PHASE 1 DATABASE MIGRATION")
    print("Adding enterprise columns to existing tables")
    print("=" * 60)
    
    db_path = get_db_path()
    print(f"\nDatabase: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        total_added = 0
        
        # Migrate leads table
        added = migrate_leads_table(cursor)
        total_added += added
        
        # Migrate customers table
        added = migrate_customers_table(cursor)
        total_added += added
        
        # Migrate deals table
        added = migrate_deals_table(cursor)
        total_added += added
        
        # Create contacts table
        created = create_contacts_table(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print(f"✓ Columns added: {total_added}")
        print(f"✓ Contacts table created: {created}")
        print("\nSUCCESS: Migration completed!")
        print("=" * 60)
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()

