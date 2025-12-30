# UI Development TODO List

**Version:** 1.0  
**Date:** December 29, 2025  
**Backend Status:** 90% Complete (54/60 items)  
**UI Status:** 67% Complete (8/12 items)

---

## 📊 UI Development Overview

| Phase | Backend | UI Status | Priority |
|-------|---------|-----------|----------|
| Phase 1: Foundation | ✅ 100% | ✅ Done | High |
| Phase 2: Nurturing | ✅ 100% | ✅ Done | High |
| Phase 3: Qualification | ✅ 100% | ✅ Done | High |
| Phase 4: Conversion | ✅ 100% | ✅ Done | Medium |
| Phase 5: Account & Contact | ✅ 100% | ⏳ Partial | Medium |
| Phase 6: Opportunity | ✅ 100% | ✅ Done | Medium |
| Phase 7: Activities | ✅ 100% | ✅ Done | Low |
| Security & Admin | ✅ 100% | ✅ Done | Low |

---

## 🎯 Phase 1: Foundation - UI TODO

### ✅ Already Done:
- [x] Login Page (`frontend/pages/login.html`)
- [x] Dashboard (`frontend/pages/dashboard.html`)
- [x] Leads List Page (`frontend/pages/leads.html`)
- [x] Lead Form (Create/Edit)
- [x] Company Selection Page (`frontend/pages/company-selection.html`)

### ⏳ Pending UI:

#### 1. Data Quality Dashboard
**API Ready:** `GET /data-quality/metrics`, `GET /data-quality/freshness`, `GET /data-quality/duplicates`

**UI Components Needed:**
- [ ] Data Quality Overview Card
  - Overall quality score (A/B/C/D grade)
  - Quality percentage meter
- [ ] Completeness Metrics Section
  - Leads completeness (email, phone, name, source)
  - Customers completeness
  - Contacts completeness
- [ ] Data Freshness Section
  - Fresh vs Stale records chart
  - Freshness percentage by entity
- [ ] Duplicate Detection Section
  - Duplicate emails list
  - Duplicate phones list
  - Merge duplicates action button

**Location:** `frontend/pages/admin.html` (new tab) or `frontend/pages/data-quality.html`

---

#### 2. Data Governance Dashboard
**API Ready:** `GET /data-governance/policies`, `GET /data-governance/compliance`, `GET /data-governance/retention`

**UI Components Needed:**
- [ ] Compliance Score Card
  - Overall compliance percentage
  - Compliance grade (A/B/C/D)
- [ ] Policy List Section
  - Required fields policy
  - Source attribution policy
  - Duplicate prevention policy
- [ ] Retention Report Section
  - Records exceeding retention
  - Stale records count
  - Archive recommendations

**Location:** `frontend/pages/admin.html` (new tab)

---

#### 3. Lead Scoring Display Enhancement
**API Ready:** Lead score already in model

**UI Components Needed:**
- [ ] Lead Score Badge on Lead Cards
  - Color-coded (Green: 70+, Yellow: 40-69, Red: <40)
  - Score number display
- [ ] Lead Score Breakdown Modal
  - Source score (20 pts)
  - BANT score (30 pts)
  - Engagement score (30 pts)
  - Completeness score (10 pts)
  - Authority score (10 pts)
- [ ] Batch Recalculate Scores Button (Admin)

**Location:** `frontend/pages/leads.html`, `frontend/js/pages/leads.js`

---

## 🎯 Phase 2: Nurturing - UI TODO

### ⏳ All Pending:

#### 1. Email Sequence Management UI
**API Ready:** `GET /email-sequences/analytics`, `POST /email-sequences/{id}/start/{lead_id}`, `POST /email-sequences/track-event`

**UI Components Needed:**
- [ ] Email Sequences List Page
  - Sequence name, status, trigger condition
  - Active/Inactive toggle
  - Edit/Delete actions
- [ ] Create/Edit Sequence Form
  - Sequence name
  - Trigger condition (on_creation, score_threshold)
  - Score threshold input
  - Email templates editor
- [ ] Sequence Analytics Dashboard
  - Total sent, opens, clicks, replies
  - Open rate, click rate, reply rate
  - Sequence performance chart
- [ ] Lead Enrollment Modal
  - Select sequence
  - Start sequence for lead

**Location:** `frontend/pages/email-sequences.html` (new page)

---

#### 2. Task Automation UI
**API Ready:** `POST /tasks/auto-create-followup`, `GET /tasks/overdue`, `POST /tasks/escalate-overdue`, `GET /tasks/automation-stats`

**UI Components Needed:**
- [ ] Task Automation Dashboard
  - Total tasks, pending, overdue, completed today
  - Tasks by priority chart
  - Overdue rate percentage
- [ ] Overdue Tasks Alert Section
  - List of overdue tasks
  - Days overdue indicator
  - Escalate button
- [ ] Auto-Create Task Button
  - Select lead
  - Days delay input
  - Priority selection
- [ ] Bulk Escalation Button (Admin)

**Location:** `frontend/pages/tasks.html` (enhance existing)

---

#### 3. WhatsApp Integration UI
**API Ready:** `POST /whatsapp/send`, `POST /whatsapp/send-template`, `GET /whatsapp/analytics`

**UI Components Needed:**
- [ ] WhatsApp Chat Panel (on Lead/Contact detail)
  - Send message input
  - Template selection dropdown
  - Message history
- [ ] WhatsApp Templates List
  - welcome, follow_up, reminder templates
  - Preview template
- [ ] WhatsApp Analytics Card
  - Total messages sent/received
  - Response rate
- [ ] Schedule Follow-ups Modal
  - Days delay
  - Number of messages

**Location:** `frontend/pages/leads.html` (side panel), `frontend/pages/whatsapp.html` (new)

---

#### 4. Score Increment UI
**API Ready:** `POST /leads/{id}/increment-score`, `POST /leads/batch-recalculate-scores`

**UI Components Needed:**
- [ ] Manual Score Increment Modal
  - Increment amount (+/-)
  - Reason input
- [ ] Score History Timeline
  - Score changes over time
  - Reason for each change
- [ ] Batch Recalculate Button (Admin)

**Location:** `frontend/pages/leads.html` (lead detail modal)

---

## 🎯 Phase 3: Qualification - UI TODO

### ⏳ All Pending:

#### 1. BANT Qualification UI
**API Ready:** `GET /leads/{id}/qualification-score`, `POST /leads/{id}/qualify`, `GET /leads/{id}/qualification-checklist`

**UI Components Needed:**
- [ ] BANT Score Card on Lead Detail
  - Total score (0-100)
  - Score breakdown (Budget, Authority, Need, Timeline)
  - Qualification status badge
- [ ] Qualification Checklist Panel
  - Budget ✓/✗
  - Authority ✓/✗
  - Need ✓/✗
  - Timeline ✓/✗
  - Contact Info ✓/✗
  - Completion percentage
- [ ] Qualify Lead Button
  - One-click qualification
  - Status update confirmation
- [ ] Qualification Analytics Dashboard
  - Qualification rate
  - Leads by status chart
  - BANT completion rates

**Location:** `frontend/pages/leads.html` (lead detail), `frontend/pages/qualification.html` (new)

---

#### 2. Risk Scoring UI
**API Ready:** `GET /leads/{id}/risk-score`, `GET /risk/high-risk-leads`, `GET /risk/analytics`

**UI Components Needed:**
- [ ] Risk Score Badge on Lead Cards
  - Color-coded (Green: Low, Yellow: Medium, Orange: High, Red: Critical)
  - Risk level text
- [ ] Risk Assessment Panel
  - Total risk score
  - Risk breakdown (BANT, Engagement, Data Quality, Time)
  - Risk factors list
  - Recommendations list
- [ ] High Risk Leads Alert Section
  - List of high/critical risk leads
  - Risk score and factors
  - Action buttons (Follow-up, Disqualify)
- [ ] Risk Analytics Dashboard
  - Risk distribution pie chart
  - Average risk score
  - High risk count

**Location:** `frontend/pages/leads.html`, `frontend/pages/risk-dashboard.html` (new)

---

#### 3. Conversion Triggers UI
**API Ready:** `GET /leads/{id}/conversion-eligibility`, `GET /conversion/ready-leads`, `POST /leads/{id}/auto-convert`

**UI Components Needed:**
- [ ] Conversion Eligibility Panel
  - Eligibility status (Yes/No)
  - Criteria checklist
  - Blocking issues list
- [ ] Conversion-Ready Leads Section
  - List of leads ready for conversion
  - Score and criteria met
  - Convert button
- [ ] Auto-Convert Button
  - One-click conversion
  - Confirmation modal
- [ ] Conversion Analytics Dashboard
  - Conversion rate
  - Converted in period
  - Average converted score

**Location:** `frontend/pages/leads.html`, `frontend/pages/conversion.html` (new)

---

## 🎯 Phase 4: Conversion - UI TODO

### ⏳ Pending:

#### 1. Lead Conversion Wizard
**API Ready:** `POST /leads/{id}/convert`, `GET /leads/{id}/conversion-preview`, `GET /leads/{id}/validate-conversion`

**UI Components Needed:**
- [ ] Conversion Wizard Modal (Multi-step)
  - Step 1: Validation Check
  - Step 2: Account Preview
  - Step 3: Contact Preview
  - Step 4: Opportunity Preview
  - Step 5: Confirm & Convert
- [ ] Conversion Preview Cards
  - Account details preview
  - Contact details preview
  - Opportunity details preview
- [ ] Batch Conversion UI
  - Select multiple leads
  - Batch convert button
  - Progress indicator

**Location:** `frontend/pages/leads.html` (modal)

---

#### 2. Conversion Analytics UI
**API Ready:** `GET /leads/conversion-analytics`

**UI Components Needed:**
- [ ] Conversion Analytics Dashboard
  - Total converted
  - Conversion rate
  - Average time to convert
  - Conversion by source chart

**Location:** `frontend/pages/analytics.html` or `frontend/pages/leads.html`

---

## 🎯 Phase 5: Account & Contact - UI TODO

### ✅ Already Done:
- [x] Accounts List Page (`frontend/pages/accounts.html`)
- [x] Contacts List Page (`frontend/pages/contacts.html`)
- [x] Account Detail View
- [x] Contact Detail View

### ⏳ Pending:

#### 1. Lifecycle Stage UI
**API Ready:** `POST /customers/{id}/recalculate-lifecycle-stage`, `GET /customers/lifecycle-analytics`

**UI Components Needed:**
- [ ] Lifecycle Stage Badge on Account Cards
  - MQA, SQA, Customer, Churned
  - Color-coded badges
- [ ] Lifecycle Stage Dropdown (Edit)
  - Manual stage change
  - Auto-recalculate button
- [ ] Lifecycle Analytics Dashboard
  - Accounts by stage chart
  - Stage transitions count
  - Conversion/Churn rate

**Location:** `frontend/pages/accounts.html`

---

#### 2. Contact Role Management UI
**API Ready:** `PUT /contacts/{id}/role`, `PUT /contacts/{id}/set-primary`, `GET /contacts/role-analytics`

**UI Components Needed:**
- [ ] Contact Role Badge
  - decision_maker, influencer, user, gatekeeper, champion, economic_buyer
  - Color-coded badges
- [ ] Role Dropdown (Edit)
  - Change role
- [ ] Set Primary Contact Button
  - Mark as primary
- [ ] Contact Role Analytics
  - Contacts by role chart
  - Influence score by role

**Location:** `frontend/pages/contacts.html`

---

#### 3. Health Score UI
**API Ready:** Already exists

**UI Components Needed:**
- [ ] Health Score Badge on Account Cards
  - Green, Yellow, Red, Black
  - Score indicator
- [ ] Health Score Breakdown Modal
  - Factors contributing to score
  - Recommendations

**Location:** `frontend/pages/accounts.html`

---

## 🎯 Phase 6: Opportunity - UI TODO

### ✅ Already Done:
- [x] Deals List Page (`frontend/pages/deals.html`)
- [x] Deal Form (Create/Edit)
- [x] Deal Statistics

### ⏳ Pending:

#### 1. Pipeline Kanban Board
**API Ready:** `GET /deals/pipeline-view`, `PUT /deals/{id}/move-stage`

**UI Components Needed:**
- [ ] Kanban Board View
  - Columns: Prospect, Qualified, Proposal, Negotiation, Closed Won, Closed Lost
  - Deal cards in each column
  - Drag-and-drop between columns
- [ ] Deal Card
  - Deal name, value, probability
  - Account name
  - Expected close date
- [ ] Pipeline Summary
  - Total deals per stage
  - Total value per stage
  - Win rate

**Location:** `frontend/pages/pipeline.html` (new) or `frontend/pages/deals.html` (tab)

---

#### 2. Sales Forecast UI
**API Ready:** `GET /deals/forecast`, `GET /deals/trend-analysis`

**UI Components Needed:**
- [ ] Forecast Dashboard
  - Weighted pipeline value
  - Forecast by category (best_case, commit, most_likely)
  - Monthly projections chart
- [ ] Trend Analysis Section
  - Monthly revenue trends chart
  - Win/loss trends
  - Growth rates
- [ ] Forecast Confidence Indicator
  - High/Medium/Low confidence

**Location:** `frontend/pages/forecast.html` (new) or `frontend/pages/deals.html` (tab)

---

#### 3. Pipeline Analytics UI
**API Ready:** `GET /deals/pipeline-analytics`

**UI Components Needed:**
- [ ] Pipeline Analytics Dashboard
  - Deals by stage chart
  - Values by stage chart
  - Win rate, average deal value
  - Pipeline health indicators

**Location:** `frontend/pages/deals.html` or `frontend/pages/analytics.html`

---

## 🎯 Phase 7: Activities - UI TODO

### ✅ Already Done:
- [x] Activity Timeline (`frontend/pages/activities.html`)
- [x] Activity Logging
- [x] Activity Types

---

## 🎯 Security & Admin - UI TODO

### ✅ Already Done:
- [x] Admin Settings Page (`frontend/pages/admin.html`)
- [x] User Management
- [x] Audit Trail
- [x] System Logs
- [x] Email Settings
- [x] Permission Management

---

## 📋 UI Development Priority Order

### 🔴 High Priority (Do First):
1. **Lead Scoring Display** - Show scores on lead cards
2. **BANT Qualification UI** - Qualification checklist and score
3. **Risk Scoring UI** - Risk badges and high-risk alerts
4. **Conversion Triggers UI** - Conversion eligibility and ready leads

### 🟡 Medium Priority:
5. **Pipeline Kanban Board** - Drag-and-drop deal management
6. **Email Sequence Management** - Create and manage sequences
7. **WhatsApp Integration** - Send messages from UI
8. **Task Automation Dashboard** - Overdue tasks and escalation

### 🟢 Low Priority:
9. **Data Quality Dashboard** - Quality metrics and duplicates
10. **Sales Forecast UI** - Forecast and trends
11. **Lifecycle Stage UI** - Account lifecycle management
12. **Contact Role Management** - Role badges and analytics

---

## 🛠️ Technical Notes

### Frontend Stack:
- **HTML/CSS/JavaScript** (Vanilla)
- **Bootstrap 5** for styling
- **Chart.js** for charts
- **Lucide Icons** for icons

### API Base URL:
```
/api/companies/{company_id}/
```

### Authentication:
- JWT token in cookie
- Include credentials in fetch requests

### Common Components to Create:
1. **Score Badge Component** - Reusable score display
2. **Risk Badge Component** - Reusable risk level display
3. **Kanban Board Component** - Drag-and-drop board
4. **Analytics Chart Component** - Reusable chart wrapper
5. **Checklist Component** - Reusable checklist display

---

## 📊 Estimated Effort

| Category | Items | Estimated Days |
|----------|-------|----------------|
| High Priority | 4 | 5-7 days |
| Medium Priority | 4 | 6-8 days |
| Low Priority | 4 | 4-5 days |
| **Total** | **12** | **15-20 days** |

---

**Last Updated:** December 29, 2025
