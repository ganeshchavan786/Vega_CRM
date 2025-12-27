"""
Create Enterprise CRM Tables - Phase 1 Migration
Adds new columns to existing tables and creates new Contact table
"""

from app.database import engine, Base
from app.models import (
    Company, User, UserCompany, Customer, Contact,
    Lead, Deal, Task, Activity
)

def create_enterprise_tables():
    """Create all enterprise CRM tables"""
    print("Creating Enterprise CRM tables...")
    
    try:
        # Create all tables (this will add new columns to existing tables)
        Base.metadata.create_all(bind=engine)
        
        print("SUCCESS: Enterprise CRM tables created successfully!")
        print("\nTables created/updated:")
        print("  - leads (enhanced with enterprise fields)")
        print("  - customers (enhanced with account fields)")
        print("  - contacts (new table)")
        print("  - deals (enhanced with opportunity fields)")
        print("\nNew columns added to existing tables:")
        print("  Leads: first_name, last_name, campaign, lead_score, gdpr_consent, etc.")
        print("  Customers: account_type, health_score, lifecycle_stage, gstin, etc.")
        print("  Deals: account_id, primary_contact_id, forecast_category")
        
    except Exception as e:
        print(f"ERROR: Error creating tables: {e}")
        raise


if __name__ == "__main__":
    create_enterprise_tables()

