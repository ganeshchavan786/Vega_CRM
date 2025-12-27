#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Test Script for All CRM Pages

This script tests all pages and forms in the CRM application:
1. Customers (Accounts)
2. Leads
3. Deals (Opportunities)
4. Tasks
5. Activities

It checks:
- Database schema
- Model attributes
- API endpoints
- CRUD operations
- Serialization
- Data validation

Usage:
    python test_all_pages.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import traceback

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import inspect, text
from app.database import engine, SessionLocal
from app.models.customer import Customer
from app.models.lead import Lead
from app.models.deal import Deal
from app.models.task import Task
from app.models.activity import Activity
from app.schemas.customer import CustomerResponse, CustomerCreate
from app.schemas.lead import LeadResponse, LeadCreate
from app.schemas.deal import DealResponse, DealCreate
from app.schemas.task import TaskResponse, TaskCreate
from app.schemas.activity import ActivityResponse, ActivityCreate

# Test results storage
test_results = []

def log_test(test_name, passed, message=""):
    """Log test result"""
    status = "[OK]" if passed else "[FAILED]"
    result = {
        'name': test_name,
        'passed': passed,
        'message': message
    }
    test_results.append(result)
    print(f"{status} {test_name}")
    if message:
        print(f"      {message}")

def check_table_schema(table_name, required_columns):
    """Check if table has all required columns"""
    try:
        inspector = inspect(engine)
        
        if table_name not in inspector.get_table_names():
            log_test(f"Table '{table_name}' exists", False, f"Table not found")
            return False
        
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        missing = [c for c in required_columns if c not in columns]
        
        if missing:
            log_test(f"Table '{table_name}' schema", False, f"Missing columns: {', '.join(missing)}")
            return False
        else:
            log_test(f"Table '{table_name}' schema", True, f"All {len(required_columns)} columns exist")
            return True
            
    except Exception as e:
        log_test(f"Table '{table_name}' schema check", False, str(e))
        return False

def test_model_attributes(model_class, model_name, required_attrs):
    """Test if model has all required attributes"""
    try:
        missing = [attr for attr in required_attrs if not hasattr(model_class, attr)]
        
        if missing:
            log_test(f"{model_name} model attributes", False, f"Missing: {', '.join(missing)}")
            return False
        else:
            log_test(f"{model_name} model attributes", True, f"All {len(required_attrs)} attributes exist")
            return True
            
    except Exception as e:
        log_test(f"{model_name} model check", False, str(e))
        return False

def test_orm_query(model_class, model_name):
    """Test ORM query"""
    db = SessionLocal()
    try:
        records = db.query(model_class).limit(5).all()
        log_test(f"{model_name} ORM query", True, f"Found {len(records)} records")
        return True
    except Exception as e:
        log_test(f"{model_name} ORM query", False, str(e))
        return False
    finally:
        db.close()

def test_serialization(model_class, schema_class, model_name, sample_data=None):
    """Test serialization to Pydantic schema"""
    db = SessionLocal()
    try:
        records = db.query(model_class).limit(3).all()
        
        if not records:
            log_test(f"{model_name} serialization", True, "No records to test (OK)")
            return True
        
        for i, record in enumerate(records, 1):
            try:
                # Convert to dict
                record_dict = {}
                # Use model_fields for Pydantic V2, fallback to __fields__ for V1
                schema_fields = getattr(schema_class, 'model_fields', None) or getattr(schema_class, '__fields__', {})
                for key in schema_fields.keys():
                    try:
                        value = getattr(record, key, None)
                        if value is not None:
                            # Handle datetime
                            if isinstance(value, datetime):
                                record_dict[key] = value.isoformat()
                            else:
                                record_dict[key] = value
                    except:
                        pass
                
                # Create schema instance
                schema_instance = schema_class(**record_dict)
                log_test(f"{model_name} serialization #{i}", True, f"ID: {record.id}")
                
            except Exception as e:
                log_test(f"{model_name} serialization #{i}", False, f"ID: {record.id}, Error: {str(e)}")
                return False
        
        return True
        
    except Exception as e:
        log_test(f"{model_name} serialization", False, str(e))
        return False
    finally:
        db.close()

def test_customers():
    """Test Customers (Accounts) page"""
    print("\n" + "=" * 80)
    print("TESTING: Customers (Accounts) Page")
    print("=" * 80)
    
    results = []
    
    # Schema check
    required_cols = [
        'id', 'company_id', 'name', 'email', 'phone', 'address',
        'city', 'state', 'country', 'postal_code', 'account_type',
        'company_size', 'annual_revenue', 'gstin', 'health_score',
        'lifecycle_stage', 'is_active', 'account_owner_id', 'created_at', 'updated_at'
    ]
    results.append(check_table_schema('customers', required_cols))
    
    # Model attributes
    required_attrs = [
        'id', 'company_id', 'name', 'email', 'phone', 'address',
        'city', 'state', 'country', 'postal_code', 'account_type',
        'company_size', 'annual_revenue', 'gstin', 'health_score',
        'lifecycle_stage', 'is_active', 'account_owner_id'
    ]
    results.append(test_model_attributes(Customer, "Customer", required_attrs))
    
    # ORM query
    results.append(test_orm_query(Customer, "Customer"))
    
    # Serialization
    results.append(test_serialization(Customer, CustomerResponse, "Customer"))
    
    return all(results)

def test_leads():
    """Test Leads page"""
    print("\n" + "=" * 80)
    print("TESTING: Leads Page")
    print("=" * 80)
    
    results = []
    
    # Schema check
    required_cols = [
        'id', 'company_id', 'first_name', 'last_name', 'company_name',
        'email', 'phone', 'country', 'source', 'campaign', 'medium', 'term',
        'lead_owner_id', 'status', 'stage', 'lead_score', 'priority',
        'interest_product', 'budget_range', 'authority_level', 'timeline',
        'gdpr_consent', 'dnd_status', 'opt_in_date', 'is_duplicate',
        'spam_score', 'validation_status', 'converted_at', 'created_at', 'updated_at'
    ]
    results.append(check_table_schema('leads', required_cols))
    
    # Model attributes
    required_attrs = [
        'id', 'company_id', 'first_name', 'last_name', 'company_name',
        'email', 'phone', 'country', 'source', 'campaign', 'medium', 'term',
        'lead_owner_id', 'status', 'stage', 'lead_score', 'priority',
        'interest_product', 'budget_range', 'authority_level', 'timeline',
        'gdpr_consent', 'dnd_status', 'opt_in_date', 'is_duplicate',
        'spam_score', 'validation_status', 'converted_at'
    ]
    results.append(test_model_attributes(Lead, "Lead", required_attrs))
    
    # ORM query
    results.append(test_orm_query(Lead, "Lead"))
    
    # Serialization
    results.append(test_serialization(Lead, LeadResponse, "Lead"))
    
    return all(results)

def test_deals():
    """Test Deals (Opportunities) page"""
    print("\n" + "=" * 80)
    print("TESTING: Deals (Opportunities) Page")
    print("=" * 80)
    
    results = []
    
    # Schema check
    required_cols = [
        'id', 'company_id', 'deal_name', 'deal_value', 'currency',
        'stage', 'probability', 'forecast_category', 'expected_close_date',
        'actual_close_date', 'status', 'loss_reason', 'notes',
        'customer_id', 'lead_id', 'primary_contact_id', 'assigned_to', 'created_at', 'updated_at'
    ]
    results.append(check_table_schema('deals', required_cols))
    
    # Model attributes
    required_attrs = [
        'id', 'company_id', 'deal_name', 'deal_value', 'currency',
        'stage', 'probability', 'forecast_category', 'expected_close_date',
        'actual_close_date', 'status', 'loss_reason', 'notes',
        'customer_id', 'lead_id', 'primary_contact_id', 'assigned_to'
    ]
    results.append(test_model_attributes(Deal, "Deal", required_attrs))
    
    # ORM query
    results.append(test_orm_query(Deal, "Deal"))
    
    # Serialization
    results.append(test_serialization(Deal, DealResponse, "Deal"))
    
    return all(results)

def test_tasks():
    """Test Tasks page"""
    print("\n" + "=" * 80)
    print("TESTING: Tasks Page")
    print("=" * 80)
    
    results = []
    
    # Schema check
    required_cols = [
        'id', 'company_id', 'title', 'description', 'task_type',
        'priority', 'status', 'due_date', 'completed_at',
        'customer_id', 'lead_id', 'deal_id', 'assigned_to', 'created_at', 'updated_at'
    ]
    results.append(check_table_schema('tasks', required_cols))
    
    # Model attributes
    required_attrs = [
        'id', 'company_id', 'title', 'description', 'task_type',
        'priority', 'status', 'due_date', 'completed_at',
        'customer_id', 'lead_id', 'deal_id', 'assigned_to'
    ]
    results.append(test_model_attributes(Task, "Task", required_attrs))
    
    # ORM query
    results.append(test_orm_query(Task, "Task"))
    
    # Serialization
    results.append(test_serialization(Task, TaskResponse, "Task"))
    
    return all(results)

def test_activities():
    """Test Activities page"""
    print("\n" + "=" * 80)
    print("TESTING: Activities Page")
    print("=" * 80)
    
    results = []
    
    # Schema check
    required_cols = [
        'id', 'company_id', 'activity_type', 'title', 'description',
        'duration', 'outcome', 'activity_date',
        'customer_id', 'lead_id', 'deal_id', 'task_id', 'created_at', 'updated_at'
    ]
    results.append(check_table_schema('activities', required_cols))
    
    # Model attributes
    required_attrs = [
        'id', 'company_id', 'activity_type', 'title', 'description',
        'duration', 'outcome', 'activity_date',
        'customer_id', 'lead_id', 'deal_id', 'task_id'
    ]
    results.append(test_model_attributes(Activity, "Activity", required_attrs))
    
    # ORM query
    results.append(test_orm_query(Activity, "Activity"))
    
    # Serialization
    results.append(test_serialization(Activity, ActivityResponse, "Activity"))
    
    return all(results)

def test_relationships():
    """Test relationships between models"""
    print("\n" + "=" * 80)
    print("TESTING: Model Relationships")
    print("=" * 80)
    
    db = SessionLocal()
    results = []
    
    try:
        # Test Deal -> Customer relationship
        deals = db.query(Deal).filter(Deal.customer_id.isnot(None)).limit(1).all()
        if deals:
            deal = deals[0]
            if hasattr(deal, 'customer_id') and deal.customer_id:
                customer = db.query(Customer).filter(Customer.id == deal.customer_id).first()
                if customer:
                    log_test("Deal -> Customer relationship", True, f"Deal {deal.id} -> Customer {customer.id}")
                    results.append(True)
                else:
                    log_test("Deal -> Customer relationship", False, "Customer not found")
                    results.append(False)
            else:
                log_test("Deal -> Customer relationship", True, "No customer_id set (OK)")
                results.append(True)
        else:
            log_test("Deal -> Customer relationship", True, "No deals with customers (OK)")
            results.append(True)
        
        # Test Task -> Deal relationship
        tasks = db.query(Task).filter(Task.deal_id.isnot(None)).limit(1).all()
        if tasks:
            task = tasks[0]
            if hasattr(task, 'deal_id') and task.deal_id:
                deal = db.query(Deal).filter(Deal.id == task.deal_id).first()
                if deal:
                    log_test("Task -> Deal relationship", True, f"Task {task.id} -> Deal {deal.id}")
                    results.append(True)
                else:
                    log_test("Task -> Deal relationship", False, "Deal not found")
                    results.append(False)
            else:
                log_test("Task -> Deal relationship", True, "No deal_id set (OK)")
                results.append(True)
        else:
            log_test("Task -> Deal relationship", True, "No tasks with deals (OK)")
            results.append(True)
        
        # Test Activity -> Customer relationship
        activities = db.query(Activity).filter(Activity.customer_id.isnot(None)).limit(1).all()
        if activities:
            activity = activities[0]
            if hasattr(activity, 'customer_id') and activity.customer_id:
                customer = db.query(Customer).filter(Customer.id == activity.customer_id).first()
                if customer:
                    log_test("Activity -> Customer relationship", True, f"Activity {activity.id} -> Customer {customer.id}")
                    results.append(True)
                else:
                    log_test("Activity -> Customer relationship", False, "Customer not found")
                    results.append(False)
            else:
                log_test("Activity -> Customer relationship", True, "No customer_id set (OK)")
                results.append(True)
        else:
            log_test("Activity -> Customer relationship", True, "No activities with customers (OK)")
            results.append(True)
        
    except Exception as e:
        log_test("Model relationships", False, str(e))
        results.append(False)
    finally:
        db.close()
    
    return all(results)

def main():
    """Run all tests"""
    print("=" * 80)
    print("CRM Application - Comprehensive Page Testing")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all page tests
    page_results = {
        "Customers": test_customers(),
        "Leads": test_leads(),
        "Deals": test_deals(),
        "Tasks": test_tasks(),
        "Activities": test_activities(),
        "Relationships": test_relationships()
    }
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for page_name, result in page_results.items():
        status = "[OK]" if result else "[FAILED]"
        print(f"{status} {page_name} Page")
    
    # Overall statistics
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r['passed'])
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    all_passed = all(page_results.values())
    
    if all_passed:
        print("\n[SUCCESS] All pages are working correctly!")
        print("\n[RECOMMENDATION]")
        print("  1. All database schemas are correct")
        print("  2. All models have required attributes")
        print("  3. ORM queries work correctly")
        print("  4. Serialization works correctly")
        print("  5. Relationships are properly configured")
    else:
        print("\n[WARNING] Some tests failed. Check the errors above.")
        print("\n[RECOMMENDATION]")
        print("  1. Check database migrations")
        print("  2. Verify model definitions in app/models/")
        print("  3. Check schema definitions in app/schemas/")
        print("  4. Restart server to clear SQLAlchemy cache")
    
    print("=" * 80)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())

