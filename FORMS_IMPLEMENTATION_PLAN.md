# Forms Implementation Plan

**Status:** In Progress  
**Date:** December 22, 2025

## Forms to Create

1. ✅ **Customer Form** - COMPLETE
2. ✅ **Lead Form** - COMPLETE  
3. 🔄 **Deal Form** - IN PROGRESS
4. ⏳ **Task Form** - PENDING
5. ⏳ **Activity Form** - PENDING

## Implementation Pattern

All forms follow the same pattern:
- Use `formModal` and `formContent` from index.html
- Global variables: `window.currentEditing{Entity}Id`
- Functions: `show{Entity}Form()`, `edit{Entity}()`, `open{Entity}Modal()`, `handle{Entity}Submit()`, `delete{Entity}()`
- Form structure: form-modal-header, form-advanced, form-section-advanced, form-actions-sticky
- Error handling: customerFormError div, try-catch blocks, 401 handling

## Deal Form Fields

### Required:
- deal_name
- deal_value
- customer_id

### Optional:
- currency (default: USD/INR)
- stage (prospect, qualified, proposal, negotiation, closed_won, closed_lost)
- probability (0-100)
- expected_close_date
- status (open, won, lost)
- loss_reason
- notes
- lead_id
- assigned_to

## Task Form Fields

### Required:
- title
- assigned_to

### Optional:
- description
- task_type (call, email, meeting, general, follow_up)
- priority (low, medium, high, urgent)
- status (pending, in_progress, completed, cancelled)
- due_date
- customer_id
- lead_id
- deal_id

## Activity Form Fields

### Required:
- activity_type (call, email, meeting, note, status_change)
- title
- activity_date

### Optional:
- description
- duration (minutes)
- outcome (positive, negative, neutral, follow_up_required)
- customer_id
- lead_id
- deal_id
- task_id

