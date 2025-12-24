"""
Data Seeding Script for CRM SAAS
Creates test data: 100 Create, 100 Update, 25 Delete
"""

import requests
import json
from datetime import datetime
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api"

# Statistics
stats = {
    "companies_created": 0,
    "users_created": 0,
    "customers_created": 0,
    "total_created": 0,
    "total_updated": 0,
    "total_deleted": 0,
    "errors": []
}

def register_user(email, password, first_name, last_name):
    """Register a new user"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name
            }
        )
        if response.status_code == 201:
            stats["users_created"] += 1
            stats["total_created"] += 1
            return response.json()["data"]
        else:
            stats["errors"].append(f"User registration failed: {email}")
            return None
    except Exception as e:
        stats["errors"].append(f"Error registering user {email}: {str(e)}")
        return None

def login_user(email, password):
    """Login and get JWT token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            return response.json()["data"]["access_token"]
        return None
    except:
        return None

def create_company(token, name, email):
    """Create a company"""
    try:
        response = requests.post(
            f"{BASE_URL}/companies",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": name,
                "email": email,
                "phone": f"+1-555-{1000 + stats['companies_created']:04d}",
                "city": "New York",
                "country": "USA"
            }
        )
        if response.status_code == 201:
            stats["companies_created"] += 1
            stats["total_created"] += 1
            return response.json()["data"]
        else:
            stats["errors"].append(f"Company creation failed: {name}")
            return None
    except Exception as e:
        stats["errors"].append(f"Error creating company {name}: {str(e)}")
        return None

def create_customer(token, company_id, name, email, customer_type="individual"):
    """Create a customer"""
    try:
        response = requests.post(
            f"{BASE_URL}/companies/{company_id}/customers",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": name,
                "email": email,
                "phone": f"+1-555-{2000 + stats['customers_created']:04d}",
                "customer_type": customer_type,
                "status": "active",
                "priority": "medium"
            }
        )
        if response.status_code == 201:
            stats["customers_created"] += 1
            stats["total_created"] += 1
            return response.json()["data"]
        else:
            stats["errors"].append(f"Customer creation failed: {name}")
            return None
    except Exception as e:
        stats["errors"].append(f"Error creating customer {name}: {str(e)}")
        return None

def update_customer(token, company_id, customer_id, updates):
    """Update a customer"""
    try:
        response = requests.put(
            f"{BASE_URL}/companies/{company_id}/customers/{customer_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=updates
        )
        if response.status_code == 200:
            stats["total_updated"] += 1
            return True
        else:
            stats["errors"].append(f"Customer update failed: ID {customer_id}")
            return False
    except Exception as e:
        stats["errors"].append(f"Error updating customer {customer_id}: {str(e)}")
        return False

def delete_customer(token, company_id, customer_id):
    """Delete a customer"""
    try:
        response = requests.delete(
            f"{BASE_URL}/companies/{company_id}/customers/{customer_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            stats["total_deleted"] += 1
            return True
        else:
            stats["errors"].append(f"Customer deletion failed: ID {customer_id}")
            return False
    except Exception as e:
        stats["errors"].append(f"Error deleting customer {customer_id}: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("CRM SAAS - DATA SEEDING SCRIPT")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Try to login with existing user first
    print("STEP 1: Attempting login with existing user...")
    token = login_user("admin@crm.com", "Admin@123")
    
    if not token:
        # If existing user doesn't work, create new one
        print("Creating new seeder user...")
        from random import randint
        email = f"seeder{randint(1000,9999)}@crm.com"
        admin = register_user(email, "Seed@123", "Data", "Seeder")
        if not admin:
            print("❌ Failed to create admin user")
            return
        print(f"✅ Admin user created: {admin['email']}")
        
        # Step 2: Login
        print("\nSTEP 2: Logging in...")
        token = login_user(email, "Seed@123")
    else:
        print("✅ Using existing admin@crm.com user")
    if not token:
        print("❌ Login failed")
        return
    print("✅ Login successful")
    
    # Step 3: Create companies (10 companies)
    print("\nSTEP 3: Creating Companies...")
    companies = []
    for i in range(1, 11):
        company = create_company(
            token,
            f"Company {i:02d}",
            f"company{i:02d}@business.com"
        )
        if company:
            companies.append(company)
            print(f"  ✅ Created: {company['name']}")
    print(f"✅ Total Companies Created: {len(companies)}")
    
    if not companies:
        print("❌ No companies created")
        return
    
    # Use first company for customers
    company = companies[0]
    company_id = company["id"]
    
    # Step 4: Create 100 customers
    print(f"\nSTEP 4: Creating 100 Customers in {company['name']}...")
    customers = []
    for i in range(1, 101):
        customer_type = "business" if i % 3 == 0 else "individual"
        customer = create_customer(
            token,
            company_id,
            f"Customer {i:03d}",
            f"customer{i:03d}@email.com",
            customer_type
        )
        if customer:
            customers.append(customer)
            if i % 10 == 0:
                print(f"  ✅ Created {i} customers...")
    print(f"✅ Total Customers Created: {len(customers)}")
    
    # Step 5: Update 100 records
    print(f"\nSTEP 5: Updating 100 Customer Records...")
    update_count = min(100, len(customers))
    priorities = ["low", "medium", "high"]
    statuses = ["active", "inactive", "prospect"]
    
    for i in range(update_count):
        customer = customers[i]
        updates = {
            "priority": priorities[i % 3],
            "status": statuses[i % 3],
            "notes": f"Updated record {i+1} - Test data"
        }
        if update_customer(token, company_id, customer["id"], updates):
            if (i + 1) % 10 == 0:
                print(f"  ✅ Updated {i + 1} records...")
    print(f"✅ Total Records Updated: {stats['total_updated']}")
    
    # Step 6: Delete 25 records
    print(f"\nSTEP 6: Deleting 25 Customer Records...")
    delete_count = min(25, len(customers))
    
    for i in range(delete_count):
        customer = customers[-(i+1)]  # Delete from end
        if delete_customer(token, company_id, customer["id"]):
            if (i + 1) % 5 == 0:
                print(f"  ✅ Deleted {i + 1} records...")
    print(f"✅ Total Records Deleted: {stats['total_deleted']}")
    
    # Final Statistics
    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    print(f"Companies Created:    {stats['companies_created']}")
    print(f"Users Created:        {stats['users_created']}")
    print(f"Customers Created:    {stats['customers_created']}")
    print("-" * 70)
    print(f"TOTAL CREATED:        {stats['total_created']}")
    print(f"TOTAL UPDATED:        {stats['total_updated']}")
    print(f"TOTAL DELETED:        {stats['total_deleted']}")
    print("-" * 70)
    print(f"CRUD OPERATIONS:      {stats['total_created'] + stats['total_updated'] + stats['total_deleted']}")
    print("=" * 70)
    
    if stats["errors"]:
        print(f"\n⚠️  Errors encountered: {len(stats['errors'])}")
        for error in stats["errors"][:5]:  # Show first 5 errors
            print(f"   - {error}")
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Database Summary
    print("\n" + "=" * 70)
    print("DATABASE SUMMARY")
    print("=" * 70)
    remaining_customers = stats['customers_created'] - stats['total_deleted']
    print(f"Total Companies:      {stats['companies_created']}")
    print(f"Total Users:          {stats['users_created'] + 1}")  # +1 for initial admin
    print(f"Active Customers:     {remaining_customers}")
    print(f"Deleted Customers:    {stats['total_deleted']}")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Script interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")

