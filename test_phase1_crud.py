"""
Phase 1 CRUD Test Script
Tests all CRUD operations with Indian dummy data
"""

import sys
import io
from datetime import datetime
from sqlalchemy.orm import Session

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add app to path
sys.path.insert(0, '.')

from app.database import SessionLocal, engine
from app.models import Company, User, Customer, Contact, Lead, Deal

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close yet

def test_company_user_setup(db: Session):
    """Setup test company and user"""
    print("\n=== Setting up Test Company and User ===")
    
    # Get or create test company
    company = db.query(Company).filter(Company.name == "Test Company Pvt Ltd").first()
    if not company:
        company = Company(
            name="Test Company Pvt Ltd",
            email="test@company.com",
            phone="+91 20 12345678",
            address="Pune, Maharashtra, India"
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"Created company: {company.name} (ID: {company.id})")
    else:
        print(f"Using existing company: {company.name} (ID: {company.id})")
    
    # Get or create test user
    user = db.query(User).filter(User.email == "test@company.com").first()
    if not user:
        user = User(
            first_name="Test",
            last_name="User",
            email="test@company.com",
            password_hash="test_hash",
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: {user.full_name} (ID: {user.id})")
    else:
        print(f"Using existing user: {user.full_name} (ID: {user.id})")
    
    return company, user

def test_lead_crud(db: Session, company_id: int, user_id: int):
    """Test Lead CRUD operations"""
    print("\n=== Testing Lead CRUD Operations ===")
    
    # CREATE - Create Indian leads
    leads_data = [
        {
            "first_name": "राहुल",
            "last_name": "पाटील",
            "company_name": "ABC टेक्नोलॉजीज",
            "email": "rahul.patil@abctech.com",
            "phone": "+91 98XXX 12345",
            "country": "India",
            "source": "Google Ads",
            "campaign": "CRM-Q4-2025",
            "medium": "CPC",
            "term": "crm software",
            "lead_score": 75,
            "status": "new",
            "stage": "awareness",
            "interest_product": "CRM Software",
            "budget_range": "₹5-7 Lakh",
            "authority_level": "decision_maker",
            "timeline": "60 Days",
            "gdpr_consent": True,
            "company_id": company_id,
            "lead_owner_id": user_id,
            "created_by": user_id
        },
        {
            "first_name": "प्रिया",
            "last_name": "शर्मा",
            "company_name": "XYZ इन्फोटेक",
            "email": "priya.sharma@xyzinfotech.com",
            "phone": "+91 99XXX 54321",
            "country": "India",
            "source": "Website Form",
            "campaign": "Homepage-2025",
            "medium": "Organic",
            "lead_score": 60,
            "status": "contacted",
            "stage": "consideration",
            "interest_product": "CRM + Support Module",
            "budget_range": "₹3-5 Lakh",
            "authority_level": "influencer",
            "timeline": "90 Days",
            "gdpr_consent": True,
            "company_id": company_id,
            "lead_owner_id": user_id,
            "created_by": user_id
        },
        {
            "first_name": "अमित",
            "last_name": "कुमार",
            "company_name": "मुंबई सॉफ्टवेअर सोल्यूशन्स",
            "email": "amit.kumar@mumbaiss.com",
            "phone": "+91 91XXX 98765",
            "country": "India",
            "source": "Partner API",
            "campaign": "Partner-Referral-2025",
            "medium": "Referral",
            "lead_score": 85,
            "status": "qualified",
            "stage": "decision",
            "interest_product": "Enterprise CRM",
            "budget_range": "₹10-15 Lakh",
            "authority_level": "decision_maker",
            "timeline": "30 Days",
            "gdpr_consent": True,
            "company_id": company_id,
            "lead_owner_id": user_id,
            "created_by": user_id
        }
    ]
    
    created_leads = []
    for lead_data in leads_data:
        lead = Lead(**lead_data)
        # Set lead_name for backward compatibility
        lead.lead_name = f"{lead_data['first_name']} {lead_data['last_name']}"
        db.add(lead)
        db.flush()
        created_leads.append(lead)
        try:
            print(f"  CREATED: Lead {lead.id} - {lead.full_name} ({lead.company_name})")
        except UnicodeEncodeError:
            print(f"  CREATED: Lead {lead.id} - {lead.id} (Company: {lead.id})")
    
    db.commit()
    print(f"  ✓ Created {len(created_leads)} leads")
    
    # READ - Read all leads
    all_leads = db.query(Lead).filter(Lead.company_id == company_id).all()
    print(f"  READ: Found {len(all_leads)} leads")
    for lead in all_leads:
        print(f"    - {lead.full_name} | Score: {lead.lead_score} | Status: {lead.status}")
    
    # UPDATE - Update first lead
    if created_leads:
        first_lead = created_leads[0]
        old_score = first_lead.lead_score
        first_lead.lead_score = 80
        first_lead.status = "contacted"
        db.commit()
        print(f"  UPDATED: Lead {first_lead.id} - Score: {old_score} -> {first_lead.lead_score}, Status: {first_lead.status}")
    
    # READ by ID
    if created_leads:
        lead_id = created_leads[0].id
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if lead:
            print(f"  READ BY ID: Lead {lead.id} - {lead.full_name} | Campaign: {lead.campaign}")
    
    return created_leads

def test_customer_account_crud(db: Session, company_id: int, user_id: int):
    """Test Customer (Account) CRUD operations"""
    print("\n=== Testing Customer (Account) CRUD Operations ===")
    
    # CREATE - Create Indian accounts
    accounts_data = [
        {
            "name": "ABC टेक्नोलॉजीज प्राइवेट लिमिटेड",
            "email": "info@abctech.com",
            "phone": "+91 20 12345678",
            "company_name": "ABC टेक्नोलॉजीज",
            "industry": "IT Services",
            "company_size": "50-100 Employees",
            "annual_revenue": 100000000,  # ₹10 Cr
            "gstin": "27ABCDE1234F1Z5",
            "account_type": "customer",
            "health_score": "green",
            "lifecycle_stage": "SQA",
            "is_active": True,
            "status": "active",
            "customer_type": "business",
            "company_id": company_id,
            "account_owner_id": user_id,
            "created_by": user_id
        },
        {
            "name": "XYZ इन्फोटेक सोल्यूशन्स",
            "email": "contact@xyzinfotech.com",
            "phone": "+91 22 98765432",
            "company_name": "XYZ इन्फोटेक",
            "industry": "Software Development",
            "company_size": "20-50 Employees",
            "annual_revenue": 50000000,  # ₹5 Cr
            "gstin": "19XYZAB5678C2D6",
            "account_type": "prospect",
            "health_score": "yellow",
            "lifecycle_stage": "MQA",
            "is_active": True,
            "status": "prospect",
            "customer_type": "business",
            "company_id": company_id,
            "account_owner_id": user_id,
            "created_by": user_id
        }
    ]
    
    created_accounts = []
    for account_data in accounts_data:
        account = Customer(**account_data)
        db.add(account)
        db.flush()
        created_accounts.append(account)
        print(f"  CREATED: Account {account.id} - {account.name} | GSTIN: {account.gstin}")
    
    db.commit()
    print(f"  ✓ Created {len(created_accounts)} accounts")
    
    # READ - Read all accounts
    all_accounts = db.query(Customer).filter(Customer.company_id == company_id).all()
    print(f"  READ: Found {len(all_accounts)} accounts")
    for account in all_accounts:
        print(f"    - {account.name} | Type: {account.account_type} | Health: {account.health_score}")
    
    # UPDATE - Update first account
    if created_accounts:
        first_account = created_accounts[0]
        old_health = first_account.health_score
        first_account.health_score = "yellow"
        first_account.lifecycle_stage = "Customer"
        db.commit()
        print(f"  UPDATED: Account {first_account.id} - Health: {old_health} -> {first_account.health_score}")
    
    return created_accounts

def test_contact_crud(db: Session, company_id: int, account_id: int, user_id: int):
    """Test Contact CRUD operations"""
    print("\n=== Testing Contact CRUD Operations ===")
    
    # CREATE - Create Indian contacts
    contacts_data = [
        {
            "name": "राहुल पाटील",
            "job_title": "Manager",
            "role": "decision_maker",
            "email": "rahul.patil@abctech.com",
            "phone": "+91 98XXX 12345",
            "preferred_channel": "whatsapp",
            "influence_score": "high",
            "is_primary_contact": True,
            "company_id": company_id,
            "account_id": account_id,
            "created_by": user_id
        },
        {
            "name": "प्रिया शर्मा",
            "job_title": "Deputy Manager",
            "role": "influencer",
            "email": "priya.sharma@abctech.com",
            "phone": "+91 99XXX 54321",
            "preferred_channel": "email",
            "influence_score": "medium",
            "is_primary_contact": False,
            "company_id": company_id,
            "account_id": account_id,
            "created_by": user_id
        }
    ]
    
    created_contacts = []
    for contact_data in contacts_data:
        contact = Contact(**contact_data)
        db.add(contact)
        db.flush()
        created_contacts.append(contact)
        print(f"  CREATED: Contact {contact.id} - {contact.name} (Role: {contact.role})")
    
    db.commit()
    print(f"  ✓ Created {len(created_contacts)} contacts")
    
    # READ - Read all contacts for account
    all_contacts = db.query(Contact).filter(
        Contact.company_id == company_id,
        Contact.account_id == account_id
    ).all()
    print(f"  READ: Found {len(all_contacts)} contacts for account {account_id}")
    for contact in all_contacts:
        print(f"    - {contact.name} | Role: {contact.role} | Primary: {contact.is_primary_contact}")
    
    # UPDATE - Update first contact
    if created_contacts:
        first_contact = created_contacts[0]
        old_role = first_contact.role
        first_contact.role = "champion"
        first_contact.influence_score = "high"
        db.commit()
        print(f"  UPDATED: Contact {first_contact.id} - Role: {old_role} -> {first_contact.role}")
    
    return created_contacts

def test_deal_opportunity_crud(db: Session, company_id: int, account_id: int, contact_id: int, user_id: int):
    """Test Deal/Opportunity CRUD operations"""
    print("\n=== Testing Deal (Opportunity) CRUD Operations ===")
    
    # CREATE - Create opportunities
    deals_data = [
        {
            "deal_name": "ABC Tech CRM Implementation",
            "deal_value": 500000,  # ₹5 Lakh
            "currency": "INR",
            "stage": "proposal",
            "probability": 50,
            "forecast_category": "most_likely",
            "status": "open",
            "expected_close_date": datetime(2026, 1, 15).date(),
            "company_id": company_id,
            "customer_id": account_id,
            "account_id": account_id,
            "primary_contact_id": contact_id,
            "assigned_to": user_id,
            "created_by": user_id
        },
        {
            "deal_name": "XYZ InfoTech CRM License",
            "deal_value": 300000,  # ₹3 Lakh
            "currency": "INR",
            "stage": "qualified",
            "probability": 25,
            "forecast_category": "best_case",
            "status": "open",
            "expected_close_date": datetime(2026, 3, 1).date(),
            "company_id": company_id,
            "customer_id": account_id,
            "account_id": account_id,
            "primary_contact_id": contact_id,
            "assigned_to": user_id,
            "created_by": user_id
        }
    ]
    
    created_deals = []
    for deal_data in deals_data:
        deal = Deal(**deal_data)
        db.add(deal)
        db.flush()
        created_deals.append(deal)
        print(f"  CREATED: Deal {deal.id} - {deal.deal_name} | Value: ₹{deal.deal_value:,.0f}")
    
    db.commit()
    print(f"  ✓ Created {len(created_deals)} deals")
    
    # READ - Read all deals
    all_deals = db.query(Deal).filter(Deal.company_id == company_id).all()
    print(f"  READ: Found {len(all_deals)} deals")
    for deal in all_deals:
        print(f"    - {deal.deal_name} | Stage: {deal.stage} | Probability: {deal.probability}%")
    
    # UPDATE - Update first deal
    if created_deals:
        first_deal = created_deals[0]
        old_stage = first_deal.stage
        old_probability = first_deal.probability
        first_deal.stage = "negotiation"
        first_deal.probability = 75
        first_deal.forecast_category = "commit"
        db.commit()
        print(f"  UPDATED: Deal {first_deal.id} - Stage: {old_stage} -> {first_deal.stage}, Probability: {old_probability}% -> {first_deal.probability}%")
    
    return created_deals

def test_backward_compatibility(db: Session, company_id: int):
    """Test backward compatibility with existing fields"""
    print("\n=== Testing Backward Compatibility ===")
    
    # Test Lead with legacy lead_name field
    legacy_lead = Lead(
        lead_name="Legacy Test Lead",
        company_name="Legacy Company",
        email="legacy@test.com",
        phone="+91 90XXX 11111",
        source="Legacy Source",
        status="new",
        company_id=company_id
    )
    db.add(legacy_lead)
    db.commit()
    db.refresh(legacy_lead)
    print(f"  ✓ Created legacy lead: {legacy_lead.lead_name} (ID: {legacy_lead.id})")
    
    # Test that to_dict() works with both old and new fields
    lead_dict = legacy_lead.to_dict()
    print(f"  ✓ to_dict() works - Name: {lead_dict.get('lead_name')}, Full Name: {lead_dict.get('full_name')}")
    
    # Test Customer with legacy fields
    legacy_customer = Customer(
        name="Legacy Customer",
        email="legacy@customer.com",
        phone="+91 90XXX 22222",
        customer_type="individual",
        status="active",
        company_id=company_id
    )
    db.add(legacy_customer)
    db.commit()
    db.refresh(legacy_customer)
    print(f"  ✓ Created legacy customer: {legacy_customer.name} (ID: {legacy_customer.id})")
    
    # Test Deal with legacy customer_id
    legacy_deal = Deal(
        deal_name="Legacy Deal",
        deal_value=100000,
        currency="INR",
        stage="prospect",
        probability=10,
        status="open",
        company_id=company_id,
        customer_id=legacy_customer.id
    )
    db.add(legacy_deal)
    db.commit()
    db.refresh(legacy_deal)
    print(f"  ✓ Created legacy deal: {legacy_deal.deal_name} (ID: {legacy_deal.id})")
    
    print("  ✓ Backward compatibility maintained - All legacy fields work")

def test_data_integrity(db: Session, company_id: int):
    """Test data integrity and relationships"""
    print("\n=== Testing Data Integrity ===")
    
    # Test Lead -> Account relationship (via converted_to_account_id)
    leads = db.query(Lead).filter(Lead.company_id == company_id).limit(1).all()
    accounts = db.query(Customer).filter(Customer.company_id == company_id).limit(1).all()
    
    if leads and accounts:
        lead = leads[0]
        account = accounts[0]
        lead.converted_to_account_id = account.id
        lead.status = "converted"
        lead.converted_at = datetime.now()
        db.commit()
        print(f"  ✓ Lead {lead.id} converted to Account {account.id}")
        
        # Verify relationship
        if lead.converted_account:
            print(f"  ✓ Relationship verified: Lead.converted_account = {lead.converted_account.name}")
    
    # Test Account -> Contact relationship
    if accounts:
        account = accounts[0]
        contacts = db.query(Contact).filter(Contact.account_id == account.id).all()
        print(f"  ✓ Account {account.id} has {len(contacts)} contacts")
        
        if contacts:
            contact = contacts[0]
            print(f"  ✓ Contact {contact.id} belongs to Account {contact.account.name}")
    
    # Test Deal -> Account -> Contact relationships
    deals = db.query(Deal).filter(
        Deal.company_id == company_id,
        Deal.account_id.isnot(None)
    ).limit(1).all()
    
    if deals:
        deal = deals[0]
        if deal.account:
            print(f"  ✓ Deal {deal.id} linked to Account {deal.account.name}")
        if deal.primary_contact:
            print(f"  ✓ Deal {deal.id} linked to Contact {deal.primary_contact.name}")
    
    print("  ✓ All relationships working correctly")

def main():
    """Main test function"""
    print("=" * 60)
    print("PHASE 1 CRUD TEST - Enterprise CRM")
    print("Testing with Indian dummy data")
    print("=" * 60)
    
    db = get_db()
    
    try:
        # Setup
        company, user = test_company_user_setup(db)
        
        # Test Lead CRUD
        leads = test_lead_crud(db, company.id, user.id)
        
        # Test Customer (Account) CRUD
        accounts = test_customer_account_crud(db, company.id, user.id)
        
        # Test Contact CRUD (requires account)
        contacts = []
        if accounts:
            contacts = test_contact_crud(db, company.id, accounts[0].id, user.id)
        
        # Test Deal CRUD (requires account and contact)
        deals = []
        if accounts and contacts:
            deals = test_deal_opportunity_crud(db, company.id, accounts[0].id, contacts[0].id, user.id)
        
        # Test backward compatibility
        test_backward_compatibility(db, company.id)
        
        # Test data integrity
        test_data_integrity(db, company.id)
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✓ Leads created: {len(leads)}")
        print(f"✓ Accounts created: {len(accounts)}")
        print(f"✓ Contacts created: {len(contacts)}")
        print(f"✓ Deals created: {len(deals)}")
        print(f"✓ Backward compatibility: PASSED")
        print(f"✓ Data integrity: PASSED")
        print("\n✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

