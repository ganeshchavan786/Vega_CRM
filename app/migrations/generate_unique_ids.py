"""
Migration Script: Generate unique IDs for existing records
v2.1.0 Feature - Add unique_id to all modules

Run this script to populate unique_id for existing records
"""

import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, get_db
from app.models.customer import Customer
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.deal import Deal
from app.models.task import Task
from app.models.activity import Activity
from app.models.report import Report
from app.utils.unique_id import (
    generate_account_id, generate_contact_id, generate_lead_id,
    generate_opportunity_id, generate_task_id, generate_activity_id, generate_report_id
)


def migrate_unique_ids():
    """Generate unique IDs for all existing records"""
    
    print("Starting unique ID migration for existing records...")
    
    db = next(get_db())
    
    try:
        # Get all companies
        companies = db.execute(text("SELECT id FROM companies ORDER BY id")).fetchall()
        
        total_updated = 0
        
        for company in companies:
            company_id = company[0]
            print(f"\nProcessing Company {company_id}...")
            
            # Migrate Customers (Accounts)
            customers = db.query(Customer).filter(
                Customer.company_id == company_id,
                Customer.unique_id.is_(None)
            ).order_by(Customer.created_at).all()
            
            for customer in customers:
                customer.unique_id = generate_account_id(company_id, customer.created_at, db)
                total_updated += 1
                print(f"  Customer {customer.id}: {customer.unique_id}")
            
            # Migrate Contacts
            contacts = db.query(Contact).filter(
                Contact.company_id == company_id,
                Contact.unique_id.is_(None)
            ).order_by(Contact.created_at).all()
            
            for contact in contacts:
                contact.unique_id = generate_contact_id(company_id, contact.created_at, db)
                total_updated += 1
                print(f"  Contact {contact.id}: {contact.unique_id}")
            
            # Migrate Leads
            leads = db.query(Lead).filter(
                Lead.company_id == company_id,
                Lead.unique_id.is_(None)
            ).order_by(Lead.created_at).all()
            
            for lead in leads:
                lead.unique_id = generate_lead_id(company_id, lead.created_at, db)
                total_updated += 1
                print(f"  Lead {lead.id}: {lead.unique_id}")
            
            # Migrate Deals (Opportunities)
            deals = db.query(Deal).filter(
                Deal.company_id == company_id,
                Deal.unique_id.is_(None)
            ).order_by(Deal.created_at).all()
            
            for deal in deals:
                deal.unique_id = generate_opportunity_id(company_id, deal.created_at, db)
                total_updated += 1
                print(f"  Deal {deal.id}: {deal.unique_id}")
            
            # Migrate Tasks
            tasks = db.query(Task).filter(
                Task.company_id == company_id,
                Task.unique_id.is_(None)
            ).order_by(Task.created_at).all()
            
            for task in tasks:
                task.unique_id = generate_task_id(company_id, task.created_at, db)
                total_updated += 1
                print(f"  Task {task.id}: {task.unique_id}")
            
            # Migrate Activities
            activities = db.query(Activity).filter(
                Activity.company_id == company_id,
                Activity.unique_id.is_(None)
            ).order_by(Activity.created_at).all()
            
            for activity in activities:
                activity.unique_id = generate_activity_id(company_id, activity.created_at, db)
                total_updated += 1
                print(f"  Activity {activity.id}: {activity.unique_id}")
            
            # Migrate Reports
            reports = db.query(Report).filter(
                Report.company_id == company_id,
                Report.unique_id.is_(None)
            ).order_by(Report.created_at).all()
            
            for report in reports:
                report.unique_id = generate_report_id(company_id, report.created_at, db)
                total_updated += 1
                print(f"  Report {report.id}: {report.unique_id}")
            
            # Commit changes for this company
            db.commit()
            print(f"  Company {company_id} completed")
        
        print(f"\nMigration completed!")
        print(f"Total records updated: {total_updated}")
        
        # Show summary
        print("\nSummary by module:")
        modules = [
            ('customers', Customer),
            ('contacts', Contact),
            ('leads', Lead),
            ('deals', Deal),
            ('tasks', Task),
            ('activities', Activity),
            ('reports', Report)
        ]
        
        for module_name, model in modules:
            count = db.query(model).filter(model.unique_id.isnot(None)).count()
            print(f"  {module_name}: {count} records with unique_id")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def verify_unique_ids():
    """Verify that all records have unique IDs"""
    
    print("\nVerifying unique IDs...")
    
    db = next(get_db())
    
    try:
        modules = [
            ('customers', Customer),
            ('contacts', Contact),
            ('leads', Lead),
            ('deals', Deal),
            ('tasks', Task),
            ('activities', Activity),
            ('reports', Report)
        ]
        
        all_good = True
        
        for module_name, model in modules:
            total = db.query(model).count()
            with_unique_id = db.query(model).filter(model.unique_id.isnot(None)).count()
            without_unique_id = total - with_unique_id
            
            if without_unique_id > 0:
                print(f"  WARNING: {module_name}: {without_unique_id} records without unique_id")
                all_good = False
            else:
                print(f"  OK: {module_name}: All {with_unique_id} records have unique_id")
        
        if all_good:
            print("\nAll records have unique IDs!")
        else:
            print("\nSome records are missing unique IDs")
            
    except Exception as e:
        print(f"Error during verification: {str(e)}")
    finally:
        db.close()


def rollback_unique_ids():
    """Rollback unique IDs (set to NULL)"""
    
    print("Rolling back unique IDs...")
    
    db = next(get_db())
    
    try:
        modules = [Customer, Contact, Lead, Deal, Task, Activity, Report]
        
        for model in modules:
            db.query(model).filter(model.unique_id.isnot(None)).update(
                {model.unique_id: None}, synchronize_session=False
            )
        
        db.commit()
        print("Unique IDs rolled back (set to NULL)")
        
    except Exception as e:
        print(f"Error during rollback: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unique ID Migration Script")
    parser.add_argument("action", choices=["migrate", "verify", "rollback"], 
                       help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "migrate":
        migrate_unique_ids()
        verify_unique_ids()
    elif args.action == "verify":
        verify_unique_ids()
    elif args.action == "rollback":
        rollback_unique_ids()
        verify_unique_ids()
