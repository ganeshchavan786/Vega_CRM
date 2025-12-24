"""
Pydantic Schemas Package
"""

from app.schemas.auth import *
from app.schemas.company import *
from app.schemas.user import *
from app.schemas.customer import *
from app.schemas.contact import *
from app.schemas.lead import *
from app.schemas.deal import *
from app.schemas.task import *
from app.schemas.activity import *
from app.schemas.response import *

__all__ = [
    # Auth
    "UserRegister",
    "UserLogin",
    "Token",
    "TokenData",
    "ChangePassword",
    
    # Company
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    
    # Customer
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    
    # Contact
    "ContactCreate",
    "ContactUpdate",
    "ContactResponse",
    
    # Lead
    "LeadCreate",
    "LeadUpdate",
    "LeadResponse",
    
    # Deal
    "DealCreate",
    "DealUpdate",
    "DealResponse",
    
    # Task
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    
    # Activity
    "ActivityCreate",
    "ActivityUpdate",
    "ActivityResponse",
    
    # Response
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
]

