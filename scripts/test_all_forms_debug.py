"""
Comprehensive Test Script - All Forms with Debug
Tests all CRM forms/entities with field-level error tracking
Follows Enterprise CRM Flow: Lead -> Customer -> Contact -> Deal -> Task -> Activity
"""

import requests
import json
import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
API_BASE = "http://localhost:8000/api"
TEST_EMAIL = "admin@crm.com"
TEST_PASSWORD = "Admin@123"

# Colors for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

# Test Statistics
stats = {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "errors": [],
    "created_ids": {
        "leads": [],
        "customers": [],
        "contacts": [],
        "deals": [],
        "tasks": [],
        "activities": []
    }
}

def print_test(test_name: str, status: str, message: str = "", details: str = ""):
    """Print test result with details"""
    icon = "[OK]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
    color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    print(f"{color}{icon} {test_name}: {status}{Colors.END}")
    if message:
        print(f"   {message}")
    if details:
        print(f"   {Colors.CYAN}Details: {details}{Colors.END}")
    print()

def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_subheader(text: str):
    """Print subsection header"""
    print(f"\n{Colors.MAGENTA}{'─'*70}{Colors.END}")
    print(f"{Colors.MAGENTA}{text}{Colors.END}")
    print(f"{Colors.MAGENTA}{'─'*70}{Colors.END}\n")

def debug_error(response: requests.Response, operation: str, entity_type: str = ""):
    """Debug and format error details"""
    try:
        error_data = response.json()
        detail = error_data.get("detail", "Unknown error")
        
        error_msg = f"Status {response.status_code}: {operation}"
        
        # Parse different error formats
        if isinstance(detail, dict):
            error_msg += f"\n   Error Type: {detail.get('error', 'Unknown')}"
            if "duplicate_lead_names" in detail:
                error_msg += f"\n   Duplicate Leads: {detail.get('duplicate_lead_names', [])}"
            if "match_reason" in detail:
                error_msg += f"\n   Match Reason: {detail.get('match_reason', 'N/A')}"
            if "field" in detail:
                error_msg += f"\n   Field: {detail.get('field', 'N/A')}"
            if "msg" in detail:
                error_msg += f"\n   Message: {detail.get('msg', 'N/A')}"
        elif isinstance(detail, list):
            # Pydantic validation errors
            errors = []
            for err in detail:
                if isinstance(err, dict):
                    field = err.get("loc", ["unknown"])[-1]
                    msg = err.get("msg", "Validation error")
                    field_type = err.get("type", "")
                    errors.append(f"   Field '{field}': {msg} ({field_type})")
            error_msg += "\n" + "\n".join(errors) if errors else f"\n   {detail}"
        else:
            error_msg += f"\n   {detail}"
            
        return error_msg
    except:
        return f"Status {response.status_code}: {response.text[:200]}"

# ==================== AUTHENTICATION ====================

def login() -> Optional[str]:
    """Login and get token"""
    print_subheader("[AUTH] Authentication")
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            # Handle nested response: {"success": true, "data": {"access_token": "..."}}
            if "data" in token_data and isinstance(token_data["data"], dict):
                token = token_data["data"].get("access_token") or token_data["data"].get("token")
            else:
                # Handle flat response: {"access_token": "..."}
                token = token_data.get("access_token") or token_data.get("token")
            if token:
                print_test("Login", "PASS", f"Token: {token[:30]}...")
                stats["passed"] += 1
                return token
            else:
                print_test("Login", "FAIL", f"No token in response. Response: {token_data}")
                stats["failed"] += 1
                return None
        else:
            error_msg = debug_error(response, "Login")
            print_test("Login", "FAIL", error_msg)
            print(f"{Colors.YELLOW}Response Status: {response.status_code}{Colors.END}")
            print(f"{Colors.YELLOW}Response Text: {response.text[:500]}{Colors.END}\n")
            stats["failed"] += 1
            return None
    except requests.exceptions.ConnectionError as e:
        print_test("Login", "FAIL", f"Cannot connect to server: {str(e)}")
        print(f"{Colors.YELLOW}Backend URL: {API_BASE}/auth/login{Colors.END}")
        print(f"{Colors.YELLOW}Tip: Make sure backend is running on port 8000{Colors.END}")
        print(f"{Colors.YELLOW}Start backend: python -m uvicorn app.main:app --reload{Colors.END}\n")
        stats["failed"] += 1
        return None
    except Exception as e:
        print_test("Login", "FAIL", f"Exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"{Colors.YELLOW}Traceback:{Colors.END}")
        traceback.print_exc()
        stats["failed"] += 1
        return None

def get_company_id(headers: Dict) -> Optional[int]:
    """Get company ID"""
    try:
        response = requests.get(f"{API_BASE}/companies", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            companies = data.get("data", [])
            if companies:
                company_id = companies[0]["id"]
                print_test("Get Company", "PASS", f"Company ID: {company_id}")
                stats["passed"] += 1
                return company_id
        print_test("Get Company", "FAIL", debug_error(response, "Get Companies"))
        stats["failed"] += 1
        return None
    except Exception as e:
        print_test("Get Company", "FAIL", f"Exception: {str(e)}")
        stats["failed"] += 1
        return None

# ==================== LEAD TESTS ====================

def test_create_lead(headers: Dict, company_id: int, index: int) -> Optional[int]:
    """Test creating a lead with all fields"""
    stats["total_tests"] += 1
    print(f"{Colors.CYAN}[Lead {index}/8] Creating Lead...{Colors.END}")
    
    # Use timestamp + UUID for absolute uniqueness
    import time
    import uuid
    unique_id = str(uuid.uuid4())[:8].replace('-', '')
    unique_suffix = int(time.time() * 1000) % 1000000 + (index * 1000)
    
    # Use completely different company name patterns to avoid similarity matching
    company_prefixes = ["Acme", "TechCorp", "Innovate", "Global", "Prime", "Alpha", "Beta", "Delta"]
    
    lead_data = {
        "lead_name": f"Lead-{unique_id}",
        "first_name": f"John{unique_suffix}",
        "last_name": f"Doe{unique_suffix}",
        "email": f"lead{unique_id}@company{unique_suffix}.com",
        "phone": f"+91-{9876500000 + unique_suffix}",
        "company_name": f"{company_prefixes[index % len(company_prefixes)]} Solutions {unique_suffix} Inc",
        "source": ["Website Form", "Google Ads", "Meta Ads", "Referral"][index % 4],
        "campaign": f"CRM-Q4-2025-{index}",
        "medium": ["CPC", "Email", "Social", "Organic"][index % 4],
        "term": f"crm software {index}",
        "status": ["new", "contacted", "qualified"][index % 3],
        "stage": ["awareness", "consideration", "decision"][index % 3],
        "priority": ["low", "medium", "high"][index % 3],
        "country": "India",
        "industry": ["IT Services", "Healthcare", "Manufacturing", "Retail"][index % 4],
        "estimated_value": float(50000 + (index * 10000)),
        "budget_range": f"₹{(50000 + index * 10000):,}",
        "authority_level": ["decision_maker", "influencer", "user"][index % 3],
        "timeline": f"{3 + index} months",
        "interest_product": "CRM Software",
        "notes": f"Test lead created for comprehensive testing. Index: {index}"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/companies/{company_id}/leads",
            headers=headers,
            json=lead_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            lead = result.get("data", result)
            lead_id = lead.get("id")
            print_test(
                f"Create Lead {index}",
                "PASS",
                f"Lead ID: {lead_id}, Name: {lead_data['lead_name']}, Score: {lead.get('lead_score', 'N/A')}"
            )
            stats["passed"] += 1
            stats["created_ids"]["leads"].append(lead_id)
            return lead_id
        else:
            error_msg = debug_error(response, f"Create Lead {index}", "Lead")
            print_test(f"Create Lead {index}", "FAIL", error_msg)
            stats["failed"] += 1
            stats["errors"].append({
                "operation": f"Create Lead {index}",
                "error": error_msg,
                "data": lead_data
            })
            return None
    except Exception as e:
        print_test(f"Create Lead {index}", "FAIL", f"Exception: {str(e)}")
        stats["failed"] += 1
        stats["errors"].append({
            "operation": f"Create Lead {index}",
            "error": str(e),
            "data": lead_data
        })
        return None

def test_update_lead(headers: Dict, company_id: int, lead_id: int):
    """Test updating a lead"""
    stats["total_tests"] += 1
    print(f"{Colors.CYAN}[Update] Updating Lead ID {lead_id}...{Colors.END}")
    
    update_data = {
        "status": "contacted",
        "priority": "high",
        "notes": "Updated during comprehensive testing",
        "budget_range": "₹8-10 Lakh",
        "timeline": "2 months"
    }
    
    try:
        response = requests.put(
            f"{API_BASE}/companies/{company_id}/leads/{lead_id}",
            headers=headers,
            json=update_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print_test(f"Update Lead {lead_id}", "PASS", f"Updated fields: {', '.join(update_data.keys())}")
            stats["passed"] += 1
        else:
            error_msg = debug_error(response, f"Update Lead {lead_id}", "Lead")
            print_test(f"Update Lead {lead_id}", "FAIL", error_msg)
            stats["failed"] += 1
    except Exception as e:
        print_test(f"Update Lead {lead_id}", "FAIL", f"Exception: {str(e)}")
        stats["failed"] += 1

# ==================== CUSTOMER TESTS ====================

def test_create_customer(headers: Dict, company_id: int, index: int) -> Optional[int]:
    """Test creating a customer (account) with all fields"""
    stats["total_tests"] += 1
    print(f"{Colors.CYAN}[Customer {index}/5] Creating Customer...{Colors.END}")
    
    customer_data = {
        "name": f"Test Customer Company {index}",
        "email": f"customer{index}@company{index}.com",
        "phone": f"+91-98765{54321 + index:05d}",
        "secondary_phone": f"+91-98765{54322 + index:05d}",
        "address": f"{100 + index} Test Street, Test Area",
        "city": ["Mumbai", "Delhi", "Bangalore", "Pune", "Hyderabad"][index % 5],
        "state": ["Maharashtra", "Delhi", "Karnataka", "Maharashtra", "Telangana"][index % 5],
        "country": "India",
        "zip_code": f"{400001 + index}",
        "customer_type": "business" if index % 2 == 0 else "individual",
        "company_name": f"Customer Company {index} Pvt Ltd" if index % 2 == 0 else None,
        "website": f"https://customer{index}.com",
        "industry": ["IT Services", "Healthcare", "Manufacturing", "Retail", "Education"][index % 5],
        "status": ["active", "prospect"][index % 2],
        "source": ["Website", "Referral", "Google Ads"][index % 3],
        "priority": ["low", "medium", "high"][index % 3],
        # Enterprise fields
        "account_type": ["customer", "prospect", "partner"][index % 3],
        "company_size": f"{10 + index * 5}-{50 + index * 5} Employees",
        "annual_revenue": float(1000000 + index * 500000),
        "gstin": f"27ABCDE{1234 + index:04d}F1Z5",
        "health_score": ["green", "yellow", "red"][index % 3],
        "lifecycle_stage": ["MQA", "SQA", "Customer"][index % 3],
        "is_active": True,
        "notes": f"Test customer created for comprehensive testing. Index: {index}"
    }
    
    # Remove None values
    customer_data = {k: v for k, v in customer_data.items() if v is not None}
    
    try:
        response = requests.post(
            f"{API_BASE}/companies/{company_id}/customers",
            headers=headers,
            json=customer_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            customer = result.get("data", result)
            customer_id = customer.get("id")
            print_test(
                f"Create Customer {index}",
                "PASS",
                f"Customer ID: {customer_id}, Name: {customer_data['name']}"
            )
            stats["passed"] += 1
            stats["created_ids"]["customers"].append(customer_id)
            return customer_id
        else:
            error_msg = debug_error(response, f"Create Customer {index}", "Customer")
            print_test(f"Create Customer {index}", "FAIL", error_msg)
            stats["failed"] += 1
            stats["errors"].append({
                "operation": f"Create Customer {index}",
                "error": error_msg,
                "data": customer_data
            })
            return None
    except Exception as e:
        print_test(f"Create Customer {index}", "FAIL", f"Exception: {str(e)}")
        stats["failed"] += 1
        stats["errors"].append({
            "operation": f"Create Customer {index}",
            "error": str(e),
            "data": customer_data
        })
        return None

def test_update_customer(headers: Dict, company_id: int, customer_id: int):
    """Test updating a customer"""
    stats["total_tests"] += 1
    print(f"{Colors.CYAN}[Update] Updating Customer ID {customer_id}...{Colors.END}")
    
    update_data = {
        "status": "active",
        "priority": "high",
        "health_score": "green",
        "notes": "Updated during comprehensive testing"
    }
    
    try:
        response = requests.put(
            f"{API_BASE}/companies/{company_id}/customers/{customer_id}",
            headers=headers,
            json=update_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print_test(f"Update Customer {customer_id}", "PASS", f"Updated fields: {', '.join(update_data.keys())}")
            stats["passed"] += 1
        else:
            error_msg = debug_error(response, f"Update Customer {customer_id}", "Customer")
            print_test(f"Update Customer {customer_id}", "FAIL", error_msg)
            stats["failed"] += 1
    except Exception as e:
        print_test(f"Update Customer {customer_id}", "FAIL", f"Exception: {str(e)}")
        stats["failed"] += 1

# ==================== CONTACT TESTS ====================

def test_create_contact(headers: Dict, company_id: int, customer_id: int, index: int) -> Optional[int]:
    """Test creating a contact with all fields"""
    stats["total_tests"] += 1
    print(f"{Colors.CYAN}[Contact {index}/4] Creating Contact...{Colors.END}")
    
    contact_data = {
        "name": f"Contact Person {index}",
        "job_title": ["CEO", "CTO", "CFO", "Manager"][index % 4],
        "role": ["decision_maker", "influencer", "user", "economic_buyer"][index % 4],
        "email": f"contact{index}@customer{index}.com",
        "phone": f"+91-98765{65432 + index:05d}",
        "preferred_channel": ["email", "whatsapp", "phone", "linkedin"][index % 4],
        "influence_score": ["high", "medium", "low"][index % 3],
        "is_primary_contact": index == 0,  # First contact is primary
        "account_id": customer_id
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/companies/{company_id}/contacts",
            headers=headers,
            json=contact_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            contact = result.get("data", result)
            contact_id = contact.get("id")
            print_test(
                f"Create Contact {index}",
                "PASS",
                f"Contact ID: {contact_id}, Name: {contact_data['name']}, Account ID: {customer_id}"
            )
            stats["passed"] += 1
            stats["created_ids"]["contacts"].append(contact_id)
            return contact_id
        else:
            error_msg = debug_error(response, f"Create Contact {index}", "Contact")
            print_test(f"Create Contact {index}", "FAIL", error_msg)
            stats["failed"] += 1
            stats["errors"].append({
                "operation": f"Create Contact {index}",
                "error": error_msg,
                "data": contact_data
            })
            return None
    except Exception as e:
        print_test(f"Create Contact {index}", "FAIL", f"Exception: {str(e)}")
        stats["failed"] += 1
        stats["errors"].append({
            "operation": f"Create Contact {index}",
            "error": str(e),
            "data": contact_data
        })
        return None

# ==================== DEAL TESTS ====================

def test_create_deal(headers: Dict, company_id: int, customer_id: int, index: int) -> Optional[int]:
    """Test creating a deal with all fields"""
    stats["total_tests"] += 1
    print(f"{Colors.CYAN}[Deal {index}/4] Creating Deal...{Colors.END}")
    
    # Calculate expected close date (30-90 days from now)
    close_date = (date.today() + timedelta(days=30 + index * 15)).isoformat()
    
    deal_data = {
        "deal_name": f"Test Deal {index} - CRM Software",
        "deal_value": float(100000 + index * 50000),
        "currency": "INR",
        "stage": ["prospect", "qualified", "proposal", "negotiation"][index % 4],
        "probability": 20 + index * 15,
        "expected_close_date": close_date,
        "customer_id": customer_id,
        "status": "open",
        "notes": f"Test deal created for comprehensive testing. Index: {index}"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/companies/{company_id}/deals",
            headers=headers,
            json=deal_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            deal = result.get("data", result)
            deal_id = deal.get("id")
            print_test(
                f"Create Deal {index}",
                "PASS",
                f"Deal ID: {deal_id}, Name: {deal_data['deal_name']}, Value: ₹{deal_data['deal_value']:,.0f}"
            )
            stats["passed"] += 1
            stats["created_ids"]["deals"].append(deal_id)
            return deal_id
        else:
            error_msg = debug_error(response, f"Create Deal {index}", "Deal")
            print_test(f"Create Deal {index}", "FAIL", error_msg)
            stats["failed"] += 1
            stats["errors"].append({
                "operation": f"Create Deal {index}",
                "error": error_msg,
                "data": deal_data
            })
            return None
    except Exception as e:
        print_test(f"Create Deal {index}", "FAIL", f"Exception: {str(e)}")
        stats["failed"] += 1
        stats["errors"].append({
            "operation": f"Create Deal {index}",
            "error": str(e),
            "data": deal_data
        })
        return None

def test_update_deal(headers: Dict, company_id: int, deal_id: int):
    """Test updating a deal"""
    stats["total_tests"] += 1
    print(f"{Colors.CYAN}[Update] Updating Deal ID {deal_id}...{Colors.END}")
    
    update_data = {
        "stage": "proposal",
        "probability": 75,
        "notes": "Updated during comprehensive testing"
    }
    
    try:
        response = requests.put(
            f"{API_BASE}/companies/{company_id}/deals/{deal_id}",
            headers=headers,
            json=update_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print_test(f"Update Deal {deal_id}", "PASS", f"Updated fields: {', '.join(update_data.keys())}")
            stats["passed"] += 1
        else:
            error_msg = debug_error(response, f"Update Deal {deal_id}", "Deal")
            print_test(f"Update Deal {deal_id}", "FAIL", error_msg)
            stats["failed"] += 1
    except Exception as e:
        print_test(f"Update Deal {deal_id}", "FAIL", f"Exception: {str(e)}")
        stats["failed"] += 1

# ==================== TASK TESTS ====================

def test_create_task(headers: Dict, company_id: int, customer_id: Optional[int], deal_id: Optional[int], index: int) -> Optional[int]:
    """Test creating a task with all fields"""
    stats["total_tests"] += 1
    print(f"{Colors.CYAN}[Task {index}/2] Creating Task...{Colors.END}")
    
    # Calculate due date (7-14 days from now)
    due_date = (datetime.now() + timedelta(days=7 + index * 7)).isoformat()
    
    task_data = {
        "title": f"Test Task {index} - Follow up",
        "description": f"Test task created for comprehensive testing. Index: {index}",
        "task_type": ["call", "email", "meeting"][index % 3],
        "priority": ["low", "medium", "high", "urgent"][index % 4],
        "status": "pending",
        "due_date": due_date,
        "assigned_to": 1  # Assuming user ID 1 exists
    }
    
    if customer_id:
        task_data["customer_id"] = customer_id
    if deal_id:
        task_data["deal_id"] = deal_id
    
    try:
        response = requests.post(
            f"{API_BASE}/companies/{company_id}/tasks",
            headers=headers,
            json=task_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            task = result.get("data", result)
            task_id = task.get("id")
            print_test(
                f"Create Task {index}",
                "PASS",
                f"Task ID: {task_id}, Title: {task_data['title']}"
            )
            stats["passed"] += 1
            stats["created_ids"]["tasks"].append(task_id)
            return task_id
        else:
            error_msg = debug_error(response, f"Create Task {index}", "Task")
            print_test(f"Create Task {index}", "FAIL", error_msg)
            stats["failed"] += 1
            stats["errors"].append({
                "operation": f"Create Task {index}",
                "error": error_msg,
                "data": task_data
            })
            return None
    except Exception as e:
        print_test(f"Create Task {index}", "FAIL", f"Exception: {str(e)}")
        stats["failed"] += 1
        stats["errors"].append({
            "operation": f"Create Task {index}",
            "error": str(e),
            "data": task_data
        })
        return None

# ==================== ACTIVITY TESTS ====================

def test_create_activity(headers: Dict, company_id: int, customer_id: Optional[int], deal_id: Optional[int], index: int) -> Optional[int]:
    """Test creating an activity with all fields"""
    stats["total_tests"] += 1
    print(f"{Colors.CYAN}[Activity {index}/2] Creating Activity...{Colors.END}")
    
    activity_data = {
        "activity_type": ["call", "email", "meeting", "note"][index % 4],
        "title": f"Test Activity {index} - {['Call', 'Email', 'Meeting', 'Note'][index % 4]}",
        "description": f"Test activity created for comprehensive testing. Index: {index}",
        "duration": 30 + index * 15,  # Minutes
        "outcome": ["positive", "neutral", "follow_up_required"][index % 3],
        "activity_date": datetime.now().isoformat()
    }
    
    if customer_id:
        activity_data["customer_id"] = customer_id
    if deal_id:
        activity_data["deal_id"] = deal_id
    
    try:
        response = requests.post(
            f"{API_BASE}/companies/{company_id}/activities",
            headers=headers,
            json=activity_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            activity = result.get("data", result)
            activity_id = activity.get("id")
            print_test(
                f"Create Activity {index}",
                "PASS",
                f"Activity ID: {activity_id}, Type: {activity_data['activity_type']}"
            )
            stats["passed"] += 1
            stats["created_ids"]["activities"].append(activity_id)
            return activity_id
        else:
            error_msg = debug_error(response, f"Create Activity {index}", "Activity")
            print_test(f"Create Activity {index}", "FAIL", error_msg)
            stats["failed"] += 1
            stats["errors"].append({
                "operation": f"Create Activity {index}",
                "error": error_msg,
                "data": activity_data
            })
            return None
    except Exception as e:
        print_test(f"Create Activity {index}", "FAIL", f"Exception: {str(e)}")
        stats["failed"] += 1
        stats["errors"].append({
            "operation": f"Create Activity {index}",
            "error": str(e),
            "data": activity_data
        })
        return None

# ==================== MAIN TEST FLOW ====================

def main():
    """Main test execution"""
    print_header("COMPREHENSIVE CRM FORMS TEST SUITE")
    print(f"{Colors.CYAN}Testing all forms with field-level error tracking{Colors.END}\n")
    print(f"{Colors.YELLOW}Expected: 25 records (8 Leads, 5 Customers, 4 Contacts, 4 Deals, 2 Tasks, 2 Activities){Colors.END}\n")
    
    # Step 1: Authentication
    token = login()
    if not token:
        print(f"{Colors.RED}Cannot continue without authentication{Colors.END}")
        return 1
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get Company ID
    company_id = get_company_id(headers)
    if not company_id:
        print(f"{Colors.RED}Cannot continue without company ID{Colors.END}")
        return 1
    
    # Step 3: Test Leads (8 records)
    print_header("PHASE 1: LEAD MANAGEMENT")
    lead_ids = []
    for i in range(1, 9):
        lead_id = test_create_lead(headers, company_id, i)
        if lead_id:
            lead_ids.append(lead_id)
    
    # Update first 2 leads
    if len(lead_ids) >= 2:
        test_update_lead(headers, company_id, lead_ids[0])
        test_update_lead(headers, company_id, lead_ids[1])
    
    # Step 4: Test Customers (5 records)
    print_header("PHASE 2: CUSTOMER MANAGEMENT")
    customer_ids = []
    for i in range(1, 6):
        customer_id = test_create_customer(headers, company_id, i)
        if customer_id:
            customer_ids.append(customer_id)
    
    # Update first 2 customers
    if len(customer_ids) >= 2:
        test_update_customer(headers, company_id, customer_ids[0])
        test_update_customer(headers, company_id, customer_ids[1])
    
    # Step 5: Test Contacts (4 records) - Link to customers
    print_header("PHASE 3: CONTACT MANAGEMENT")
    contact_ids = []
    for i in range(1, 5):
        customer_id = customer_ids[i % len(customer_ids)] if customer_ids else None
        if customer_id:
            contact_id = test_create_contact(headers, company_id, customer_id, i)
            if contact_id:
                contact_ids.append(contact_id)
    
    # Step 6: Test Deals (4 records) - Link to customers
    print_header("PHASE 4: DEAL MANAGEMENT")
    deal_ids = []
    for i in range(1, 5):
        customer_id = customer_ids[i % len(customer_ids)] if customer_ids else None
        if customer_id:
            deal_id = test_create_deal(headers, company_id, customer_id, i)
            if deal_id:
                deal_ids.append(deal_id)
    
    # Update first 2 deals
    if len(deal_ids) >= 2:
        test_update_deal(headers, company_id, deal_ids[0])
        test_update_deal(headers, company_id, deal_ids[1])
    
    # Step 7: Test Tasks (2 records) - Link to customers/deals
    print_header("PHASE 5: TASK MANAGEMENT")
    task_ids = []
    for i in range(1, 3):
        customer_id = customer_ids[i % len(customer_ids)] if customer_ids else None
        deal_id = deal_ids[i % len(deal_ids)] if deal_ids else None
        task_id = test_create_task(headers, company_id, customer_id, deal_id, i)
        if task_id:
            task_ids.append(task_id)
    
    # Step 8: Test Activities (2 records) - Link to customers/deals
    print_header("PHASE 6: ACTIVITY MANAGEMENT")
    activity_ids = []
    for i in range(1, 3):
        customer_id = customer_ids[i % len(customer_ids)] if customer_ids else None
        deal_id = deal_ids[i % len(deal_ids)] if deal_ids else None
        activity_id = test_create_activity(headers, company_id, customer_id, deal_id, i)
        if activity_id:
            activity_ids.append(activity_id)
    
    # ==================== SUMMARY ====================
    print_header("TEST SUMMARY")
    
    print(f"{Colors.BOLD}Total Tests: {stats['total_tests']}{Colors.END}")
    print(f"{Colors.GREEN}Passed: {stats['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed: {stats['failed']}{Colors.END}")
    print(f"Success Rate: {(stats['passed'] / stats['total_tests'] * 100):.1f}%\n")
    
    print(f"{Colors.BOLD}Created Records:{Colors.END}")
    print(f"  Leads: {len(stats['created_ids']['leads'])}")
    print(f"  Customers: {len(stats['created_ids']['customers'])}")
    print(f"  Contacts: {len(stats['created_ids']['contacts'])}")
    print(f"  Deals: {len(stats['created_ids']['deals'])}")
    print(f"  Tasks: {len(stats['created_ids']['tasks'])}")
    print(f"  Activities: {len(stats['created_ids']['activities'])}")
    print(f"  {Colors.BOLD}Total: {sum(len(v) for v in stats['created_ids'].values())}{Colors.END}\n")
    
    if stats['errors']:
        print_header("ERRORS DETECTED")
        for i, error in enumerate(stats['errors'], 1):
            print(f"{Colors.RED}{i}. {error['operation']}{Colors.END}")
            print(f"   Error: {error['error']}")
            if 'data' in error:
                print(f"   Data: {json.dumps(error['data'], indent=6, default=str)}")
            print()
    
    # Save results to file
    with open("test_results_debug.json", "w") as f:
        json.dump(stats, f, indent=2, default=str)
    
    print(f"{Colors.CYAN}Detailed results saved to: test_results_debug.json{Colors.END}\n")
    
    return 0 if stats['failed'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

