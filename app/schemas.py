"""
Pydantic schemas for data validation.
"""

from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List


# ---------- Company ----------
class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[int] = 1

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[int] = None

class CompanyOut(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ---------- User ----------
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    company_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        orm_mode = True


# ---------- Application ----------
class ApplicationBase(BaseModel):
    council_waiting_list_number: Optional[str] = None
    name: str
    surname: str
    id_number: str
    dob: date
    residential_address: str
    contact_numbers: str
    employer: Optional[str] = "City of Harare"
    department: Optional[str] = None
    employment_number: Optional[str] = None
    employer_contact: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(ApplicationBase):
    pass

class ApplicationOut(ApplicationBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


# ---------- NextOfKin ----------
class NextOfKinBase(BaseModel):
    name: str
    surname: str
    id_number: str
    dob: date
    relation: str
    profession: Optional[str]
    address: Optional[str]
    cell: Optional[str]

class NextOfKinCreate(NextOfKinBase):
    pass

class NextOfKinUpdate(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    id_number: Optional[str]
    dob: Optional[date]
    relation: Optional[str]
    profession: Optional[str]
    address: Optional[str]
    cell: Optional[str]

class NextOfKinOut(NextOfKinBase):
    id: int
    class Config:
        orm_mode = True


# ---------- Spouse ----------
class SpouseBase(BaseModel):
    name: str
    surname: str
    id_number: str
    dob: date

class SpouseCreate(SpouseBase):
    pass

class SpouseUpdate(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    id_number: Optional[str]
    dob: Optional[date]

class SpouseOut(SpouseBase):
    id: int
    class Config:
        orm_mode = True


# ---------- Beneficiary ----------
class BeneficiaryBase(BaseModel):
    name: str
    dob: date
    id_number: str

class BeneficiaryCreate(BeneficiaryBase):
    pass

class BeneficiaryUpdate(BaseModel):
    name: Optional[str]
    dob: Optional[date]
    id_number: Optional[str]

class BeneficiaryOut(BeneficiaryBase):
    id: int
    class Config:
        orm_mode = True


# ---------- Document ----------
class DocumentBase(BaseModel):
    kind: str
    path: str

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    kind: Optional[str]
    path: Optional[str]

class DocumentOut(DocumentBase):
    id: int
    class Config:
        orm_mode = True


# ---------- Payment ----------
class PaymentBase(BaseModel):
    amount: float
    currency: Optional[str] = "USD"
    description: Optional[str]
    receipt_number: str

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[float]
    currency: Optional[str]
    description: Optional[str]
    receipt_number: Optional[str]

class PaymentOut(PaymentBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# ---------- AuditLog ----------
class AuditLogBase(BaseModel):
    action: str
    target_id: Optional[int]
    meta: Optional[str]

class AuditLogOut(BaseModel):
    id: int
    actor_user_id: int
    action: str
    target_id: Optional[int] = None
    meta: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


# ------------------- Document -------------------
class DocumentBase(BaseModel):
    kind: str  # ID_SCAN, PROOF_OF_RESIDENCE, PAYSLIP, SIGNATURE


class DocumentCreate(DocumentBase):
    pass


class DocumentOut(DocumentBase):
    id: int
    application_id: int
    path: str

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    full_name: Optional[str]
    role: Optional[str]

    class Config:
        orm_mode = True
