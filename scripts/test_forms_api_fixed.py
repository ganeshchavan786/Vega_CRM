"""
Forms API Test Script
Tests all form-related API endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000/api"
TEST_EMAIL = "admin@crm.com"
TEST_PASSWORD = "Admin123!"

# Colors for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(test_name, status, message=""):
    """Print test result"""
    icon = "[OK]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
    color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    msg = f" - {message}" if message else ""
    print(f"{color}{icon} {test_name}: {status}{msg}{Colors.END}")

def print_header(text):
    """Print header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

# Test Results
results = {"passed": 0, "failed": 0, "errors": []}

def main():
    print_header("FORMS API TEST SUITE")
    
    # Step 1: Login
    print(f"{Colors.BLUE}Step 1: Authentication...{Colors.END}")
    try:
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=5
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token") or token_data.get("token")
            user_id = token_data.get("user_id")
            
            if token:
                print_test("Login", "PASS", f"Token received: {token[:20]}...")
                results["passed"] += 1
            else:
                print_test("Login", "FAIL", "No token in response")
                results["failed"] += 1
                print(f"{Colors.RED}[FAIL] Cannot continue without authentication{Colors.END}")
                return 1
        else:
            print_test("Login", "FAIL", f"Status: {login_response.status_code}")
            results["failed"] += 1
            print(f"{Colors.RED}[FAIL] Cannot continue without authentication{Colors.END}")
            return 1
            
    except requests.exceptions.ConnectionError:
        print_test("Login", "FAIL", "Cannot connect to server. Is backend running?")
        results["failed"] += 1
        print(f"\n{Colors.YELLOW}Tip: Start backend server: python -m uvicorn app.main:app --reload{Colors.END}\n")
        return 1
    except Exception as e:
        print_test("Login", "FAIL", str(e))
        results["failed"] += 1
        return 1
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get Companies
    print(f"\n{Colors.BLUE}Step 2: Get Companies...{Colors.END}")
    company_id = None
    try:
        companies_response = requests.get(f"{API_BASE}/companies", headers=headers, timeout=5)
        if companies_response.status_code == 200:
            companies_data = companies_response.json()
            companies = companies_data.get("data", [])
            
            if companies:
                company_id = companies[0]["id"]
                print_test("Get Companies", "PASS", f"Found {len(companies)} companies. Using ID: {company_id}")
                results["passed"] += 1
            else:
                print_test("Get Companies", "FAIL", "No companies found")
                results["failed"] += 1
                print(f"{Colors.YELLOW}Tip: Create a company first{Colors.END}")
                return 1
        else:
            print_test("Get Companies", "FAIL", f"Status: {companies_response.status_code}")
            results["failed"] += 1
            return 1
    except Exception as e:
        print_test("Get Companies", "FAIL", str(e))
        results["failed"] += 1
        return 1
    
    if not company_id:
        print(f"{Colors.RED}[FAIL] No company ID available{Colors.END}")
        return 1
    
    # Step 3: Test API Endpoints
    print(f"\n{Colors.BLUE}Step 3: Testing API Endpoints...{Colors.END}")
    
    endpoints = [
        {
            "name": "Customers API",
            "method": "GET",
            "url": f"{API_BASE}/companies/{company_id}/customers",
            "params": {"page": 1, "per_page": 5}
        },
        {
            "name": "Leads API",
            "method": "GET",
            "url": f"{API_BASE}/companies/{company_id}/leads",
            "params": {"page": 1, "per_page": 5}
        },
        {
            "name": "Deals API",
            "method": "GET",
            "url": f"{API_BASE}/companies/{company_id}/deals",
            "params": {"page": 1, "per_page": 5}
        },
        {
            "name": "Tasks API",
            "method": "GET",
            "url": f"{API_BASE}/companies/{company_id}/tasks",
            "params": {"page": 1, "per_page": 5}
        },
        {
            "name": "Activities API",
            "method": "GET",
            "url": f"{API_BASE}/companies/{company_id}/activities",
            "params": {"page": 1, "per_page": 5}
        }
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                endpoint["url"],
                headers=headers,
                params=endpoint["params"],
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get("data", []))
                print_test(endpoint["name"], "PASS", f"Status: 200, Records: {count}")
                results["passed"] += 1
            elif response.status_code == 401:
                print_test(endpoint["name"], "FAIL", "401 Unauthorized - Token expired")
                results["failed"] += 1
            else:
                print_test(endpoint["name"], "FAIL", f"Status: {response.status_code}")
                results["failed"] += 1
                
        except Exception as e:
            print_test(endpoint["name"], "FAIL", str(e))
            results["failed"] += 1
    
    # Step 4: Test Form Data Validation (Customer CRUD)
    print(f"\n{Colors.BLUE}Step 4: Testing Form Data Validation (Customer CRUD)...{Colors.END}")
    
    test_customer_id = None
    
    # Test Customer Create
    try:
        customer_data = {
            "name": "Test Customer API",
            "customer_type": "individual",
            "status": "active"
        }
        
        create_response = requests.post(
            f"{API_BASE}/companies/{company_id}/customers",
            headers=headers,
            json=customer_data,
            timeout=5
        )
        
        if create_response.status_code in [200, 201]:
            customer_result = create_response.json()
            test_customer_id = customer_result.get("data", {}).get("id") or customer_result.get("id")
            print_test("Customer Create", "PASS", f"Customer ID: {test_customer_id}")
            results["passed"] += 1
        else:
            error_detail = create_response.json().get("detail", "Unknown error")
            print_test("Customer Create", "FAIL", f"Status: {create_response.status_code}, {error_detail}")
            results["failed"] += 1
            
    except Exception as e:
        print_test("Customer Create", "FAIL", str(e))
        results["failed"] += 1
    
    # Test Customer Update
    if test_customer_id:
        try:
            update_data = {"name": "Updated Test Customer"}
            update_response = requests.put(
                f"{API_BASE}/companies/{company_id}/customers/{test_customer_id}",
                headers=headers,
                json=update_data,
                timeout=5
            )
            
            if update_response.status_code == 200:
                print_test("Customer Update", "PASS")
                results["passed"] += 1
            else:
                print_test("Customer Update", "FAIL", f"Status: {update_response.status_code}")
                results["failed"] += 1
        except Exception as e:
            print_test("Customer Update", "FAIL", str(e))
            results["failed"] += 1
    
    # Test Customer Delete
    if test_customer_id:
        try:
            delete_response = requests.delete(
                f"{API_BASE}/companies/{company_id}/customers/{test_customer_id}",
                headers=headers,
                timeout=5
            )
            
            if delete_response.status_code == 200:
                print_test("Customer Delete", "PASS")
                results["passed"] += 1
            else:
                print_test("Customer Delete", "FAIL", f"Status: {delete_response.status_code}")
                results["failed"] += 1
        except Exception as e:
            print_test("Customer Delete", "FAIL", str(e))
            results["failed"] += 1
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = results["passed"] + results["failed"]
    pass_rate = (results["passed"] / total * 100) if total > 0 else 0
    
    print(f"{Colors.GREEN}[OK] Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}[FAIL] Failed: {results['failed']}{Colors.END}")
    print(f"{Colors.BLUE}Pass Rate: {pass_rate:.1f}%{Colors.END}")
    
    if results["failed"] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}SUCCESS: All tests passed! Forms are ready to use.{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}WARNING: Some tests failed. Check errors above.{Colors.END}\n")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}WARNING: Test interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR] Unexpected error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

