"""
CRUD API Test Script
Tests all major entity CRUD operations
Routes are: /api/companies/{company_id}/{entity}
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"
COMPANY_ID = 1

# First login to get token
def login():
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@crm.com",
        "password": "Admin@123"
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("data", {}).get("access_token")
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def test_crud(entity_name, endpoint, token, company_id=1, create_data=None, update_data=None):
    """Test CRUD operations for an entity"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n{'='*50}")
    print(f"Testing: {entity_name}")
    print(f"{'='*50}")
    
    results = {
        "entity": entity_name,
        "list": None,
        "create": None,
        "read": None,
        "update": None,
        "delete": None
    }
    
    # Routes are: /api/companies/{company_id}/{entity}
    base_entity_url = f"{BASE_URL}/companies/{company_id}/{endpoint}"
    
    # 1. LIST
    try:
        response = requests.get(base_entity_url, headers=headers)
        results["list"] = {"status": response.status_code, "ok": response.status_code == 200}
        print(f"  LIST: {response.status_code} - {'OK' if response.status_code == 200 else 'FAIL'}")
        if response.status_code != 200:
            print(f"    Error: {response.text[:200]}")
    except Exception as e:
        results["list"] = {"status": "error", "error": str(e)}
        print(f"  LIST: ERROR - {e}")
    
    # 2. CREATE (if data provided)
    created_id = None
    if create_data:
        try:
            response = requests.post(base_entity_url, headers=headers, json=create_data)
            results["create"] = {"status": response.status_code, "ok": response.status_code in [200, 201]}
            print(f"  CREATE: {response.status_code} - {'OK' if response.status_code in [200, 201] else 'FAIL'}")
            if response.status_code in [200, 201]:
                data = response.json()
                created_id = data.get("id") or data.get("data", {}).get("id")
                print(f"    Created ID: {created_id}")
            else:
                print(f"    Error: {response.text[:300]}")
        except Exception as e:
            results["create"] = {"status": "error", "error": str(e)}
            print(f"  CREATE: ERROR - {e}")
    
    # 3. READ (if we have an ID)
    if created_id:
        try:
            url = f"{base_entity_url}/{created_id}"
            response = requests.get(url, headers=headers)
            results["read"] = {"status": response.status_code, "ok": response.status_code == 200}
            print(f"  READ: {response.status_code} - {'OK' if response.status_code == 200 else 'FAIL'}")
            if response.status_code != 200:
                print(f"    Error: {response.text[:200]}")
        except Exception as e:
            results["read"] = {"status": "error", "error": str(e)}
            print(f"  READ: ERROR - {e}")
    
    # 4. UPDATE (if we have an ID and update data)
    if created_id and update_data:
        try:
            url = f"{base_entity_url}/{created_id}"
            response = requests.put(url, headers=headers, json=update_data)
            results["update"] = {"status": response.status_code, "ok": response.status_code == 200}
            print(f"  UPDATE: {response.status_code} - {'OK' if response.status_code == 200 else 'FAIL'}")
            if response.status_code != 200:
                print(f"    Error: {response.text[:200]}")
        except Exception as e:
            results["update"] = {"status": "error", "error": str(e)}
            print(f"  UPDATE: ERROR - {e}")
    
    # 5. DELETE (if we have an ID)
    if created_id:
        try:
            url = f"{base_entity_url}/{created_id}"
            response = requests.delete(url, headers=headers)
            results["delete"] = {"status": response.status_code, "ok": response.status_code in [200, 204]}
            print(f"  DELETE: {response.status_code} - {'OK' if response.status_code in [200, 204] else 'FAIL'}")
            if response.status_code not in [200, 204]:
                print(f"    Error: {response.text[:200]}")
        except Exception as e:
            results["delete"] = {"status": "error", "error": str(e)}
            print(f"  DELETE: ERROR - {e}")
    
    return results


def main():
    print("="*60)
    print("CRUD API TEST SCRIPT")
    print("="*60)
    
    # Login
    print("\n1. Logging in...")
    token = login()
    if not token:
        print("Failed to login. Exiting.")
        return
    print(f"   Token obtained: {token[:20]}...")
    
    all_results = []
    
    # Test Customers (Accounts)
    all_results.append(test_crud(
        "Customers (Accounts)",
        "customers",
        token,
        create_data={
            "name": "Test Customer API",
            "email": "testcustomer@api.com",
            "phone": "1234567890",
            "customer_type": "individual",
            "status": "active"
        },
        update_data={
            "name": "Test Customer API Updated"
        }
    ))
    
    # Test Contacts - requires name and account_id
    all_results.append(test_crud(
        "Contacts",
        "contacts",
        token,
        create_data={
            "name": "Test Contact API",
            "first_name": "Test",
            "last_name": "Contact",
            "email": "testcontact@api.com",
            "phone": "9876543210",
            "account_id": 1  # Link to existing customer/account
        },
        update_data={
            "name": "Test Contact Updated"
        }
    ))
    
    # Test Leads - requires lead_name
    all_results.append(test_crud(
        "Leads",
        "leads",
        token,
        create_data={
            "lead_name": "Test Lead API",
            "first_name": "Test",
            "last_name": "Lead",
            "email": "testlead@api.com",
            "phone": "5555555555",
            "source": "website",
            "status": "new"
        },
        update_data={
            "status": "contacted"
        }
    ))
    
    # Test Deals (Opportunities) - stage must match pattern, needs customer_id
    all_results.append(test_crud(
        "Deals (Opportunities)",
        "deals",
        token,
        create_data={
            "deal_name": "Test Deal API",
            "deal_value": 10000,
            "stage": "prospect",
            "status": "open",
            "customer_id": 1  # Link to existing customer
        },
        update_data={
            "deal_name": "Test Deal API Updated",
            "stage": "qualified"
        }
    ))
    
    # Test Tasks - requires assigned_to
    all_results.append(test_crud(
        "Tasks",
        "tasks",
        token,
        create_data={
            "title": "Test Task API",
            "description": "Test task description",
            "status": "pending",
            "priority": "medium",
            "assigned_to": 1  # Assign to user ID 1
        },
        update_data={
            "title": "Test Task API Updated",
            "status": "in_progress"
        }
    ))
    
    # Test Activities - requires title and activity_date
    all_results.append(test_crud(
        "Activities",
        "activities",
        token,
        create_data={
            "activity_type": "call",
            "title": "Test Activity API",
            "subject": "Test Activity Subject",
            "description": "Test activity description",
            "activity_date": "2025-12-29T10:00:00"
        },
        update_data={
            "title": "Test Activity API Updated"
        }
    ))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for result in all_results:
        entity = result["entity"]
        list_ok = result["list"]["ok"] if result["list"] else "N/A"
        create_ok = result["create"]["ok"] if result["create"] else "N/A"
        read_ok = result["read"]["ok"] if result["read"] else "N/A"
        update_ok = result["update"]["ok"] if result["update"] else "N/A"
        delete_ok = result["delete"]["ok"] if result["delete"] else "N/A"
        
        status_icons = {True: "OK", False: "FAIL", "N/A": "-"}
        
        print(f"{entity:25} | LIST:{status_icons.get(list_ok, '?')} CREATE:{status_icons.get(create_ok, '?')} READ:{status_icons.get(read_ok, '?')} UPDATE:{status_icons.get(update_ok, '?')} DELETE:{status_icons.get(delete_ok, '?')}")


if __name__ == "__main__":
    main()
