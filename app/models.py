"""
SQLAlchemy models for database tables.
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Enum,Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name =Column(String(200), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="APPLICANT")  # APPLICANT or ADMIN
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    council_waiting_list_number = Column(String(100), nullable=True)
    name = Column(String(100))
    surname = Column(String(100))
    id_number = Column(String(100))
    dob = Column(Date)
    residential_address = Column(Text)
    contact_numbers = Column(String(200))
    employer = Column(String(200), default="City of Harare")
    department=Column (String(200),nullable=True)
    employment_number=Column(String(100),nullable=True)
    employer_contact=Column(String(200),nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="applications")
    next_of_kin = relationship("NextOfKin", back_populates="application", uselist=False)
    spouse = relationship("Spouse", uselist=False, back_populates="application")
    beneficiaries = relationship("Beneficiary", back_populates="application")
    documents = relationship("Document", back_populates="application")
    payments = relationship("Payment", back_populates="application")



class NextOfKin(Base):
    __tablename__ = "next_of_kin"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))

    name = Column(String(100))
    surname = Column(String(100))
    id_number = Column(String(100))
    dob = Column(Date)
    relation = Column(String(50))
    profession = Column(String(100))
    address = Column(Text)
    cell = Column(String(50))

    application = relationship("Application", back_populates="next_of_kin")


class Spouse(Base):
    __tablename__ = "spouses"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))

    name = Column(String(100))
    surname = Column(String(100))
    id_number = Column(String(100))
    dob = Column(Date)

    application = relationship("Application", back_populates="spouse")


class Beneficiary(Base):
    __tablename__ = "beneficiaries"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))

    name = Column(String(100))
    dob = Column(Date)
    id_number = Column(String(100))

    application = relationship("Application", back_populates="beneficiaries")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))

    kind = Column(String(50))  # ID_SCAN, PROOF_OF_RESIDENCE, PAYSLIP, SIGNATURE
    path = Column(String(500))  # file system path or cloud URL

    application = relationship("Application", back_populates="documents")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))

    amount = Column(Float)
    currency = Column(String(10), default="USD")
    description = Column(String(255))
    receipt_number = Column(String(100), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    application = relationship("Application", back_populates="payments")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)

    actor_user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))  # e.g. APPROVE_APPLICATION, REJECT_APPLICATION
    target_id = Column(Integer)   # ID of the application or document affected
    meta = Column(Text)           # JSON or text with details
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 


class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True)
    value = Column(Text)
