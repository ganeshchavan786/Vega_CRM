"""
Phase 2 Data Seeding Script
Creates demo data for Leads, Deals, Tasks, Activities
"""

import requests
import json
from datetime import datetime, timedelta
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api"

stats = {
    "leads_created": 0,
    "deals_created": 0,
    "tasks_created": 0,
    "activities_created": 0,
    "errors": []
}

def login():
    """Login and get token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@crm.com", "password": "Admin@123"}
        )
        if response.status_code == 200:
            return response.json()["data"]["access_token"]
    except:
        pass
    return None

def create_lead(token, company_id, name, email, status="new", priority="medium"):
    """Create a lead"""
    try:
        response = requests.post(
            f"{BASE_URL}/companies/{company_id}/leads",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "lead_name": name,
                "email": email,
                "phone": f"+1-555-{3000 + stats['leads_created']:04d}",
                "status": status,
                "priority": priority,
                "estimated_value": (stats['leads_created'] + 1) * 10000
            }
        )
        if response.status_code == 201:
            stats["leads_created"] += 1
            return response.json()["data"]
    except Exception as e:
        stats["errors"].append(f"Lead error: {str(e)}")
    return None

def create_deal(token, company_id, name, customer_id, stage="prospect", value=50000):
    """Create a deal"""
    try:
        response = requests.post(
            f"{BASE_URL}/companies/{company_id}/deals",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "deal_name": name,
                "deal_value": value,
                "customer_id": customer_id,
                "stage": stage,
                "probability": {"prospect": 10, "qualified": 25, "proposal": 50, "negotiation": 75}[stage],
                "expected_close_date": (datetime.now() + timedelta(days=30)).date().isoformat()
            }
        )
        if response.status_code == 201:
            stats["deals_created"] += 1
            return response.json()["data"]
    except Exception as e:
        stats["errors"].append(f"Deal error: {str(e)}")
    return None

def create_task(token, company_id, title, task_type="general", priority="medium", deal_id=None):
    """Create a task"""
    try:
        task_data = {
            "title": title,
            "task_type": task_type,
            "priority": priority,
            "assigned_to": 1,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        if deal_id:
            task_data["deal_id"] = deal_id
        
        response = requests.post(
            f"{BASE_URL}/companies/{company_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json=task_data
        )
        if response.status_code == 201:
            stats["tasks_created"] += 1
            return response.json()["data"]
    except Exception as e:
        stats["errors"].append(f"Task error: {str(e)}")
    return None

def log_activity(token, company_id, title, activity_type="note", deal_id=None):
    """Log an activity"""
    try:
        activity_data = {
            "activity_type": activity_type,
            "title": title,
            "description": f"Demo activity: {title}",
            "activity_date": datetime.now().isoformat(),
            "outcome": "positive"
        }
        if deal_id:
            activity_data["deal_id"] = deal_id
        
        response = requests.post(
            f"{BASE_URL}/companies/{company_id}/activities",
            headers={"Authorization": f"Bearer {token}"},
            json=activity_data
        )
        if response.status_code == 201:
            stats["activities_created"] += 1
            return response.json()["data"]
    except Exception as e:
        stats["errors"].append(f"Activity error: {str(e)}")
    return None

def main():
    print("=" * 70)
    print("PHASE 2 - DEMO DATA SEEDING")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Login
    print("Step 1: Logging in...")
    token = login()
    if not token:
        print("[ERROR] Login failed")
        return
    print("[SUCCESS] Logged in\n")
    
    company_id = 1
    
    # Create Leads
    print("Step 2: Creating 20 Leads...")
    leads = []
    lead_statuses = ["new", "contacted", "qualified", "converted", "lost"]
    priorities = ["low", "medium", "high"]
    
    for i in range(1, 21):
        status = lead_statuses[i % len(lead_statuses)]
        priority = priorities[i % len(priorities)]
        lead = create_lead(
            token, company_id,
            f"Lead {i:02d} - {status.title()}",
            f"lead{i:02d}@prospects.com",
            status, priority
        )
        if lead:
            leads.append(lead)
            if i % 5 == 0:
                print(f"  [OK] Created {i} leads...")
    print(f"[SUCCESS] Total Leads: {len(leads)}\n")
    
    # Create Deals
    print("Step 3: Creating 15 Deals...")
    deals = []
    stages = ["prospect", "qualified", "proposal", "negotiation"]
    
    for i in range(1, 16):
        stage = stages[i % len(stages)]
        # Get first customer from Phase 1 data
        customer_id = min(i, 75)  # We have 75 customers from Phase 1
        deal = create_deal(
            token, company_id,
            f"Deal {i:02d} - {stage.title()}",
            customer_id,
            stage,
            (i + 1) * 25000
        )
        if deal:
            deals.append(deal)
            if i % 5 == 0:
                print(f"  [OK] Created {i} deals...")
    print(f"[SUCCESS] Total Deals: {len(deals)}\n")
    
    # Create Tasks
    print("Step 4: Creating 25 Tasks...")
    tasks = []
    task_types = ["call", "email", "meeting", "follow_up", "general"]
    
    for i in range(1, 26):
        task_type = task_types[i % len(task_types)]
        priority = priorities[i % len(priorities)]
        deal_id = deals[i % len(deals)]["id"] if deals and i <= len(deals) else None
        
        task = create_task(
            token, company_id,
            f"Task {i:02d} - {task_type.title()}",
            task_type, priority, deal_id
        )
        if task:
            tasks.append(task)
            if i % 5 == 0:
                print(f"  [OK] Created {i} tasks...")
    print(f"[SUCCESS] Total Tasks: {len(tasks)}\n")
    
    # Log Activities
    print("Step 5: Logging 30 Activities...")
    activities = []
    activity_types = ["call", "email", "meeting", "note"]
    
    for i in range(1, 31):
        activity_type = activity_types[i % len(activity_types)]
        deal_id = deals[i % len(deals)]["id"] if deals and i <= len(deals) else None
        
        activity = log_activity(
            token, company_id,
            f"Activity {i:02d} - {activity_type.title()}",
            activity_type, deal_id
        )
        if activity:
            activities.append(activity)
            if i % 10 == 0:
                print(f"  [OK] Logged {i} activities...")
    print(f"[SUCCESS] Total Activities: {len(activities)}\n")
    
    # Final Statistics
    print("=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    print(f"Leads Created:        {stats['leads_created']}")
    print(f"Deals Created:        {stats['deals_created']}")
    print(f"Tasks Created:        {stats['tasks_created']}")
    print(f"Activities Logged:    {stats['activities_created']}")
    print("-" * 70)
    print(f"TOTAL CREATED:        {sum([stats['leads_created'], stats['deals_created'], stats['tasks_created'], stats['activities_created']])}")
    print("=" * 70)
    
    if stats["errors"]:
        print(f"\n[WARNING] Errors: {len(stats['errors'])}")
        for error in stats["errors"][:3]:
            print(f"  - {error}")
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Test Statistics Endpoints
    print("\nTESTING STATISTICS ENDPOINTS:")
    print("-" * 70)
    
    try:
        # Lead Stats
        response = requests.get(
            f"{BASE_URL}/companies/{company_id}/leads-stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            lead_stats = response.json()["data"]
            print(f"\n[LEAD STATS]")
            print(f"  Total Leads: {lead_stats['total_leads']}")
            print(f"  By Status: {lead_stats['by_status']}")
        
        # Deal Stats
        response = requests.get(
            f"{BASE_URL}/companies/{company_id}/deals-stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            deal_stats = response.json()["data"]
            print(f"\n[DEAL STATS]")
            print(f"  Total Deals: {deal_stats['total_deals']}")
            print(f"  Pipeline Value: ${deal_stats['total_pipeline_value']:,.2f}")
            print(f"  By Stage: {deal_stats['by_stage']}")
        
        # Task Stats
        response = requests.get(
            f"{BASE_URL}/companies/{company_id}/tasks-stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            task_stats = response.json()["data"]
            print(f"\n[TASK STATS]")
            print(f"  Total Tasks: {task_stats['total_tasks']}")
            print(f"  By Status: {task_stats['by_status']}")
            print(f"  Overdue: {task_stats['overdue_tasks']}")
        
    except Exception as e:
        print(f"[ERROR] Statistics: {str(e)}")
    
    print("\n" + "=" * 70)
    print("PHASE 2 DEMO DATA - READY!")
    print("=" * 70)
    print("\nNext: Open Swagger UI to test")
    print("URL: http://localhost:8000/docs")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Stopped by user")
    except Exception as e:
        print(f"\n\n[ERROR] {str(e)}")

