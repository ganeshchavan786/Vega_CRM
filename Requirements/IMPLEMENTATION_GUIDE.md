# Enterprise CRM Data Flow - Implementation Guide

**Version:** 1.0  
**Date:** December 22, 2025  
**Based on:** ENTERPRISE_CRM_DATA_FLOW.md

---

## Table of Contents

1. [Implementation Overview](#implementation-overview)
2. [Phase 1: Database Schema & Models](#phase-1-database-schema--models)
3. [Phase 2: Lead Management System](#phase-2-lead-management-system)
4. [Phase 3: Data Governance Layer](#phase-3-data-governance-layer)
5. [Phase 4: Lead Nurturing Engine](#phase-4-lead-nurturing-engine)
6. [Phase 5: Qualification Framework](#phase-5-qualification-framework)
7. [Phase 6: Account-First Conversion](#phase-6-account-first-conversion)
8. [Phase 7: Opportunities & Revenue](#phase-7-opportunities--revenue)
9. [Phase 8: Activities Timeline](#phase-8-activities-timeline)
10. [Phase 9: Security & Permissions](#phase-9-security--permissions)
11. [Phase 10: Testing & Deployment](#phase-10-testing--deployment)

---

## Implementation Overview

### Implementation Strategy

**Approach:** Incremental implementation starting from core entities and building up to advanced features.

**Timeline:** 10 phases, approximately 4-6 weeks for complete implementation.

### Prerequisites

- ✅ FastAPI backend setup
- ✅ SQLite database configured
- ✅ Authentication system in place
- ✅ Basic models (User, Company) implemented

---

## Phase 1: Database Schema & Models

### Step 1.1: Create Lead Model

**File:** `app/models/lead.py` (Already exists, enhance it)

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from app.database import Base
import enum

class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONVERTED = "converted"
    RECYCLED = "recycled"
    DISQUALIFIED = "disqualified"

class LeadStage(str, enum.Enum):
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    DECISION = "decision"
    CONVERTED = "converted"

class AuthorityLevel(str, enum.Enum):
    DECISION_MAKER = "decision_maker"
    INFLUENCER = "influencer"
    USER = "user"
    GATEKEEPER = "gatekeeper"

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Basic Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company_name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False, index=True)
    country = Column(String(100), default="India")
    
    # Source Attribution (Mandatory)
    lead_source = Column(String(100), nullable=False)  # Google Ads, Website, etc.
    campaign = Column(String(200), nullable=False)  # Campaign name
    medium = Column(String(50))  # CPC, Email, Social
    term = Column(String(200))  # Search term
    
    # Lead Management
    lead_owner_id = Column(Integer, ForeignKey("users.id"))  # Assigned SDR
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    stage = Column(Enum(LeadStage), default=LeadStage.AWARENESS)
    lead_score = Column(Integer, default=0)  # 0-100
    
    # Qualification Fields
    interest_product = Column(String(200))
    budget_range = Column(String(100))
    authority_level = Column(Enum(AuthorityLevel))
    timeline = Column(String(100))  # 3-6 Months
    
    # Privacy & Compliance
    gdpr_consent = Column(Boolean, default=False)
    dnd_status = Column(Boolean, default=False)
    opt_in_date = Column(DateTime)
    
    # System Flags
    is_duplicate = Column(Boolean, default=False)
    spam_score = Column(Integer, default=0)  # 0-100
    validation_status = Column(String(50), default="pending")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    converted_at = Column(DateTime)
```

### Step 1.2: Enhance Account Model

**File:** `app/models/customer.py` (Rename to account.py or enhance existing)

Add these fields:
- `account_type` (Customer, Prospect, Partner)
- `industry`
- `company_size`
- `annual_revenue`
- `gstin`
- `health_score` (Green, Yellow, Red, Black)
- `lifecycle_stage` (MQA, SQA, Customer, Churned)
- `is_active` (Boolean, default=True)

### Step 1.3: Enhance Contact Model

**File:** `app/models/customer.py` (Add Contact model or separate file)

```python
class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    name = Column(String(200), nullable=False)
    job_title = Column(String(100))
    role = Column(String(50))  # Decision Maker, Influencer, etc.
    email = Column(String(255))
    phone = Column(String(20))
    
    preferred_channel = Column(String(50))  # Email, WhatsApp, Phone
    influence_score = Column(String(20))  # High, Medium, Low
    is_primary_contact = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Step 1.4: Enhance Deal/Opportunity Model

**File:** `app/models/deal.py` (Already exists, enhance it)

Add:
- `forecast_category` (Best Case, Commit, Most Likely, Worst Case)
- `source`
- Link to `account_id` and `primary_contact_id`

### Step 1.5: Create Migration Script

**File:** `create_enterprise_tables.py`

```python
from app.database import engine, Base
from app.models.lead import Lead
from app.models.customer import Account, Contact
# ... other models

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Enterprise CRM tables created successfully!")

if __name__ == "__main__":
    create_tables()
```

**Run:** `python create_enterprise_tables.py`

---

## Phase 2: Lead Management System

### Step 2.1: Create Lead Schemas

**File:** `app/schemas/lead.py` (Enhance existing)

```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from app.models.lead import LeadStatus, LeadStage, AuthorityLevel

class LeadCreate(BaseModel):
    first_name: str
    last_name: str
    company_name: str
    email: EmailStr
    phone: str
    country: str = "India"
    
    # Mandatory Attribution
    lead_source: str
    campaign: str
    medium: Optional[str] = None
    term: Optional[str] = None
    
    # Optional Fields
    interest_product: Optional[str] = None
    budget_range: Optional[str] = None
    authority_level: Optional[AuthorityLevel] = None
    timeline: Optional[str] = None
    gdpr_consent: bool = False
    
    @validator('lead_source', 'campaign')
    def validate_attribution(cls, v):
        if not v or not v.strip():
            raise ValueError('Lead source and campaign are mandatory')
        return v.strip()

class LeadResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    company_name: str
    email: str
    phone: str
    lead_source: str
    campaign: str
    status: LeadStatus
    stage: LeadStage
    lead_score: int
    # ... other fields
    
    class Config:
        from_attributes = True
```

### Step 2.2: Create Lead Controller

**File:** `app/controllers/lead_controller.py` (Enhance existing)

Add methods:
- `create_lead()` - Create new lead with validation
- `get_leads()` - List leads with filters
- `get_lead_by_id()` - Get single lead
- `update_lead()` - Update lead
- `qualify_lead()` - Mark as qualified/unqualified
- `convert_lead()` - Convert to account (Phase 6)

### Step 2.3: Create Lead Routes

**File:** `app/routes/lead.py` (Enhance existing)

Add endpoints:
- `POST /api/companies/{company_id}/leads` - Create lead
- `GET /api/companies/{company_id}/leads` - List leads
- `GET /api/companies/{company_id}/leads/{lead_id}` - Get lead
- `PUT /api/companies/{company_id}/leads/{lead_id}` - Update lead
- `POST /api/companies/{company_id}/leads/{lead_id}/qualify` - Qualify lead
- `POST /api/companies/{company_id}/leads/{lead_id}/convert` - Convert lead

---

## Phase 3: Data Governance Layer

### Step 3.1: Duplicate Detection Service

**File:** `app/services/duplicate_service.py`

```python
from sqlalchemy.orm import Session
from app.models.lead import Lead
from fuzzywuzzy import fuzz

class DuplicateService:
    @staticmethod
    def check_duplicate(db: Session, company_id: int, email: str, phone: str, company_name: str):
        # Exact match on email or phone
        exact_match = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.status != "converted",
            (Lead.email == email) | (Lead.phone == phone)
        ).first()
        
        if exact_match:
            return {"is_duplicate": True, "match_type": "exact", "lead_id": exact_match.id}
        
        # Fuzzy match on company name + email/phone
        fuzzy_match = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.status != "converted"
        ).all()
        
        for lead in fuzzy_match:
            company_similarity = fuzz.ratio(lead.company_name.lower(), company_name.lower())
            if company_similarity > 80 and (lead.email == email or lead.phone == phone):
                return {"is_duplicate": True, "match_type": "fuzzy", "lead_id": lead.id}
        
        return {"is_duplicate": False}
```

### Step 3.2: Lead Scoring Service

**File:** `app/services/lead_scoring_service.py`

```python
class LeadScoringService:
    BASE_SCORE = 0
    
    @staticmethod
    def calculate_base_score(lead_data: dict) -> int:
        score = 0
        
        # Source-based scoring
        source_scores = {
            "website_form": 10,
            "google_ads": 15,
            "partner_api": 20,
            "referral": 25
        }
        score += source_scores.get(lead_data.get("lead_source", "").lower(), 5)
        
        # Authority level scoring
        authority_scores = {
            "decision_maker": 20,
            "influencer": 15,
            "user": 5
        }
        score += authority_scores.get(lead_data.get("authority_level", "").lower(), 0)
        
        # Budget scoring
        if lead_data.get("budget_range"):
            score += 15
        
        # Timeline scoring
        if lead_data.get("timeline"):
            if "30" in lead_data["timeline"] or "60" in lead_data["timeline"]:
                score += 20
            elif "90" in lead_data["timeline"]:
                score += 10
        
        return min(score, 100)  # Cap at 100
    
    @staticmethod
    def increment_score(current_score: int, activity_type: str) -> int:
        increments = {
            "email_open": 5,
            "email_click": 10,
            "form_submit": 15,
            "call_made": 20,
            "meeting_scheduled": 30
        }
        increment = increments.get(activity_type, 0)
        return min(current_score + increment, 100)
```

### Step 3.3: Assignment Rules Service

**File:** `app/services/assignment_service.py`

```python
class AssignmentService:
    @staticmethod
    def assign_lead_round_robin(db: Session, company_id: int, sdr_users: list):
        # Get last assigned user
        last_assigned = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.lead_owner_id.isnot(None)
        ).order_by(Lead.created_at.desc()).first()
        
        if not last_assigned or not sdr_users:
            return sdr_users[0].id if sdr_users else None
        
        # Find next user in round-robin
        current_index = next((i for i, u in enumerate(sdr_users) if u.id == last_assigned.lead_owner_id), 0)
        next_index = (current_index + 1) % len(sdr_users)
        return sdr_users[next_index].id
    
    @staticmethod
    def assign_lead_territory(db: Session, company_id: int, lead_data: dict, users: list):
        # Territory-based assignment logic
        # Based on country, industry, etc.
        country = lead_data.get("country", "")
        industry = lead_data.get("industry", "")
        
        # Match user territory with lead attributes
        for user in users:
            if hasattr(user, "territory"):
                if country in user.territory.get("countries", []):
                    return user.id
        
        # Default to round-robin if no territory match
        return AssignmentService.assign_lead_round_robin(db, company_id, users)
```

### Step 3.4: Integrate in Lead Creation

**Update:** `app/controllers/lead_controller.py`

```python
async def create_lead(db: Session, company_id: int, lead_data: LeadCreate, current_user: User):
    # 1. Duplicate Check
    duplicate_check = DuplicateService.check_duplicate(
        db, company_id, lead_data.email, lead_data.phone, lead_data.company_name
    )
    
    if duplicate_check["is_duplicate"]:
        raise ValueError(f"Duplicate lead found: Lead ID {duplicate_check['lead_id']}")
    
    # 2. Calculate Initial Score
    initial_score = LeadScoringService.calculate_base_score(lead_data.dict())
    
    # 3. Assign Lead Owner
    sdr_users = db.query(User).filter(User.company_id == company_id, User.role == "sdr").all()
    lead_owner_id = AssignmentService.assign_lead_round_robin(db, company_id, sdr_users)
    
    # 4. Create Lead
    lead = Lead(
        company_id=company_id,
        first_name=lead_data.first_name,
        last_name=lead_data.last_name,
        company_name=lead_data.company_name,
        email=lead_data.email,
        phone=lead_data.phone,
        lead_source=lead_data.lead_source,
        campaign=lead_data.campaign,
        lead_score=initial_score,
        lead_owner_id=lead_owner_id or current_user.id,
        gdpr_consent=lead_data.gdpr_consent,
        # ... other fields
    )
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    return lead
```

---

## Phase 4: Lead Nurturing Engine

### Step 4.1: Email Sequence Model

**File:** `app/models/nurturing.py`

```python
class EmailSequence(Base):
    __tablename__ = "email_sequences"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(String(200))
    trigger_event = Column(String(50))  # lead_created, score_threshold
    is_active = Column(Boolean, default=True)

class EmailSequenceStep(Base):
    __tablename__ = "email_sequence_steps"
    
    id = Column(Integer, primary_key=True)
    sequence_id = Column(Integer, ForeignKey("email_sequences.id"))
    step_number = Column(Integer)
    subject = Column(String(500))
    body = Column(Text)
    delay_days = Column(Integer)  # Days after previous email
    is_active = Column(Boolean, default=True)

class LeadEmailActivity(Base):
    __tablename__ = "lead_email_activities"
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    sequence_id = Column(Integer, ForeignKey("email_sequences.id"))
    step_id = Column(Integer, ForeignKey("email_sequence_steps.id"))
    sent_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
```

### Step 4.2: Nurturing Service

**File:** `app/services/nurturing_service.py`

```python
class NurturingService:
    @staticmethod
    def trigger_email_sequence(db: Session, lead_id: int):
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return
        
        # Get active sequence for this trigger
        sequence = db.query(EmailSequence).filter(
            EmailSequence.company_id == lead.company_id,
            EmailSequence.trigger_event == "lead_created",
            EmailSequence.is_active == True
        ).first()
        
        if sequence:
            # Schedule first email
            first_step = db.query(EmailSequenceStep).filter(
                EmailSequenceStep.sequence_id == sequence.id,
                EmailSequenceStep.step_number == 1,
                EmailSequenceStep.is_active == True
            ).first()
            
            if first_step:
                # Send email (integrate with email service)
                send_email(lead.email, first_step.subject, first_step.body)
                
                # Log activity
                activity = LeadEmailActivity(
                    lead_id=lead_id,
                    sequence_id=sequence.id,
                    step_id=first_step.id,
                    sent_at=datetime.utcnow()
                )
                db.add(activity)
                db.commit()
                
                # Increment lead score
                lead.lead_score = LeadScoringService.increment_score(lead.lead_score, "email_sent")
                db.commit()
    
    @staticmethod
    def check_conversion_eligibility(lead: Lead) -> bool:
        # Check if lead can be converted
        return lead.lead_score > 70 and lead.status == LeadStatus.CONTACTED
```

### Step 4.3: Background Tasks for Nurturing

**File:** `app/services/background_tasks.py`

Use Celery or FastAPI BackgroundTasks:

```python
from fastapi import BackgroundTasks

async def process_nurturing_tasks(background_tasks: BackgroundTasks, db: Session):
    # Get leads that need nurturing
    leads = db.query(Lead).filter(
        Lead.status.in_([LeadStatus.NEW, LeadStatus.CONTACTED]),
        Lead.lead_score < 70
    ).all()
    
    for lead in leads:
        background_tasks.add_task(NurturingService.trigger_email_sequence, db, lead.id)
```

---

## Phase 5: Qualification Framework

### Step 5.1: Qualification Schema

**File:** `app/schemas/qualification.py`

```python
class BANTQualification(BaseModel):
    budget: Optional[str] = None
    authority: Optional[str] = None
    need: Optional[str] = None
    timeline: Optional[str] = None

class MEDDICCQualification(BaseModel):
    metrics: Optional[str] = None
    economic_buyer: Optional[str] = None
    decision_criteria: Optional[str] = None
    decision_process: Optional[str] = None
    identify_pain: Optional[str] = None
    champion: Optional[str] = None
    competition: Optional[str] = None

class QualificationRequest(BaseModel):
    lead_id: int
    bant: BANTQualification
    meddicc: Optional[MEDDICCQualification] = None
    risk_score: Optional[str] = "low"  # low, medium, high

class QualificationResponse(BaseModel):
    is_qualified: bool
    qualification_score: int  # 0-100
    missing_criteria: list[str]
    recommendation: str  # "qualified", "nurture_more", "disqualify"
```

### Step 5.2: Qualification Service

**File:** `app/services/qualification_service.py`

```python
class QualificationService:
    @staticmethod
    def qualify_lead(bant: BANTQualification, meddicc: Optional[MEDDICCQualification] = None):
        score = 0
        missing = []
        
        # BANT Scoring
        if bant.budget:
            score += 25
        else:
            missing.append("Budget")
        
        if bant.authority:
            score += 25
        else:
            missing.append("Authority")
        
        if bant.need:
            score += 25
        else:
            missing.append("Need")
        
        if bant.timeline:
            score += 25
        else:
            missing.append("Timeline")
        
        # MEDDICC Bonus
        if meddicc:
            meddicc_fields = [
                meddicc.metrics, meddicc.economic_buyer, meddicc.decision_criteria,
                meddicc.decision_process, meddicc.identify_pain, meddicc.champion, meddicc.competition
            ]
            filled_fields = sum(1 for field in meddicc_fields if field)
            score += min(filled_fields * 5, 20)  # Max 20 bonus points
        
        # Determine qualification
        is_qualified = score >= 75
        recommendation = "qualified" if is_qualified else ("nurture_more" if score >= 50 else "disqualify")
        
        return {
            "is_qualified": is_qualified,
            "qualification_score": score,
            "missing_criteria": missing,
            "recommendation": recommendation
        }
```

### Step 5.3: Qualification Endpoint

**File:** `app/routes/lead.py`

```python
@router.post("/{company_id}/leads/{lead_id}/qualify")
async def qualify_lead(
    company_id: int,
    lead_id: int,
    qualification: QualificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.company_id == company_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    result = QualificationService.qualify_lead(qualification.bant, qualification.meddicc)
    
    # Update lead status
    if result["is_qualified"]:
        lead.status = LeadStatus.QUALIFIED
    elif result["recommendation"] == "disqualify":
        lead.status = LeadStatus.UNQUALIFIED
    
    db.commit()
    
    return {
        "success": True,
        "qualification_result": result,
        "lead_status": lead.status
    }
```

---

## Phase 6: Account-First Conversion

### Step 6.1: Conversion Service

**File:** `app/services/conversion_service.py`

```python
class ConversionService:
    @staticmethod
    def convert_lead_to_account(
        db: Session,
        lead: Lead,
        opportunity_amount: Optional[float] = None,
        close_date: Optional[datetime] = None
    ):
        # Step 1: Create Account
        account = Account(
            company_id=lead.company_id,
            name=lead.company_name,
            account_type="prospect",
            account_owner_id=lead.lead_owner_id,
            lifecycle_stage="SQA",
            health_score="green",
            is_active=True
        )
        db.add(account)
        db.flush()
        
        # Step 2: Create Contact
        contact = Contact(
            company_id=lead.company_id,
            account_id=account.id,
            name=f"{lead.first_name} {lead.last_name}",
            email=lead.email,
            phone=lead.phone,
            role="decision_maker",
            is_primary_contact=True
        )
        db.add(contact)
        db.flush()
        
        # Step 3: Create Opportunity (if amount provided)
        opportunity = None
        if opportunity_amount:
            opportunity = Opportunity(
                company_id=lead.company_id,
                account_id=account.id,
                primary_contact_id=contact.id,
                deal_value=opportunity_amount,
                pipeline_stage="prospect",
                probability=10,
                close_date=close_date or (datetime.utcnow() + timedelta(days=90)),
                owner_id=lead.lead_owner_id
            )
            db.add(opportunity)
            db.flush()
        
        # Step 4: Log Initial Activity
        activity = Activity(
            company_id=lead.company_id,
            related_to_type="account",
            related_to_id=account.id,
            activity_type="note",
            subject="Lead Converted",
            notes=f"Lead {lead.id} converted to Account {account.id}",
            owner_id=lead.lead_owner_id
        )
        db.add(activity)
        
        # Step 5: Update Lead Status
        lead.status = LeadStatus.CONVERTED
        lead.converted_at = datetime.utcnow()
        lead.converted_to_account_id = account.id
        
        db.commit()
        
        return {
            "account_id": account.id,
            "contact_id": contact.id,
            "opportunity_id": opportunity.id if opportunity else None
        }
```

### Step 6.2: Conversion Endpoint

**File:** `app/routes/lead.py`

```python
@router.post("/{company_id}/leads/{lead_id}/convert")
async def convert_lead(
    company_id: int,
    lead_id: int,
    conversion_data: LeadConversionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.company_id == company_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check if lead is qualified
    if lead.status != LeadStatus.QUALIFIED:
        raise HTTPException(status_code=400, detail="Lead must be qualified before conversion")
    
    # Check conversion eligibility
    if not NurturingService.check_conversion_eligibility(lead):
        raise HTTPException(status_code=400, detail="Lead score must be >70 and status must be 'contacted'")
    
    result = ConversionService.convert_lead_to_account(
        db, lead, conversion_data.opportunity_amount, conversion_data.close_date
    )
    
    return {
        "success": True,
        "message": "Lead converted successfully",
        "conversion_result": result
    }
```

---

## Phase 7: Opportunities & Revenue

### Step 7.1: Enhance Opportunity Model

Update `app/models/deal.py` (or rename to opportunity.py):

- Add `account_id` (link to Account)
- Add `primary_contact_id` (link to Contact)
- Add `forecast_category` field
- Add probability mapping based on stage

### Step 7.2: Opportunity Pipeline Management

**File:** `app/services/pipeline_service.py`

```python
class PipelineService:
    STAGE_PROBABILITIES = {
        "prospect": 10,
        "qualified": 25,
        "proposal_sent": 50,
        "negotiation": 75,
        "closed_won": 100,
        "closed_lost": 0
    }
    
    @staticmethod
    def update_opportunity_stage(db: Session, opportunity_id: int, new_stage: str):
        opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opportunity:
            return
        
        opportunity.pipeline_stage = new_stage
        opportunity.probability = PipelineService.STAGE_PROBABILITIES.get(new_stage, 0)
        db.commit()
```

---

## Phase 8: Activities Timeline

### Step 8.1: Enhance Activity Model

Update `app/models/activity.py`:

- Add `related_to_type` (account, contact, opportunity, lead)
- Add `related_to_id`
- Add `activity_type` (call, email, meeting, note, whatsapp)
- Add `outcome` (positive, negative, neutral, follow_up_required)

### Step 8.2: Activity Timeline Service

**File:** `app/services/activity_service.py`

```python
class ActivityService:
    @staticmethod
    def get_timeline(db: Session, company_id: int, related_to_type: str, related_to_id: int, limit: int = 50):
        activities = db.query(Activity).filter(
            Activity.company_id == company_id,
            Activity.related_to_type == related_to_type,
            Activity.related_to_id == related_to_id
        ).order_by(Activity.created_at.desc()).limit(limit).all()
        
        return activities
```

---

## Phase 9: Security & Permissions

### Step 9.1: Row-Level Security

**File:** `app/utils/permissions.py`

```python
class RowLevelSecurity:
    @staticmethod
    def filter_by_owner(query, model, current_user: User):
        # Owner sees own records
        # Manager sees team records
        if current_user.role == "admin":
            return query
        
        if current_user.role == "manager":
            # Get team members
            team_members = db.query(User).filter(User.manager_id == current_user.id).all()
            team_ids = [u.id for u in team_members] + [current_user.id]
            return query.filter(model.owner_id.in_(team_ids))
        
        return query.filter(model.owner_id == current_user.id)
```

### Step 9.2: Audit Logging

**File:** `app/models/audit_log.py`

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    entity_type = Column(String(50))  # lead, account, contact, opportunity
    entity_id = Column(Integer)
    action = Column(String(50))  # create, update, delete
    field_name = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## Phase 10: Testing & Deployment

### Step 10.1: Unit Tests

**File:** `tests/test_lead_management.py`

```python
def test_create_lead_with_duplicate():
    # Test duplicate detection
    pass

def test_lead_scoring():
    # Test scoring calculation
    pass

def test_lead_qualification():
    # Test BANT/MEDDICC qualification
    pass

def test_lead_conversion():
    # Test account-first conversion
    pass
```

### Step 10.2: Integration Tests

Test complete flow:
1. Lead creation
2. Nurturing
3. Qualification
4. Conversion
5. Opportunity creation

### Step 10.3: Deployment Checklist

- [ ] Database migrations run
- [ ] Environment variables set
- [ ] Email service configured
- [ ] Background tasks configured
- [ ] Security permissions tested
- [ ] Audit logging enabled
- [ ] Performance tested
- [ ] Documentation updated

---

## Implementation Order

**Week 1:**
- Phase 1: Database Schema
- Phase 2: Lead Management (Basic CRUD)

**Week 2:**
- Phase 3: Data Governance
- Phase 4: Lead Nurturing (Basic)

**Week 3:**
- Phase 5: Qualification
- Phase 6: Conversion

**Week 4:**
- Phase 7: Opportunities
- Phase 8: Activities

**Week 5:**
- Phase 9: Security
- Phase 10: Testing

---

## Next Steps

1. ✅ Review this implementation guide
2. ✅ Set up development environment
3. ✅ Start with Phase 1 (Database Schema)
4. ✅ Implement incrementally
5. ✅ Test each phase before moving to next

---

**Ready to start implementation!** 🚀

