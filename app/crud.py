from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models ,schemas
import httpx
import shutil
import os
from fastapi import UploadFile
from .config import UPLOAD_DIR
import json
from typing import Optional

# if not os.path.exists(UPLOAD_DIR):
#     os.makedirs(UPLOAD_DIR)

pwd_context=  CryptContext(schemes=["bcrypt"], deprecated="auto")

BLOB_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN")
BLOB_API_URL = "https://blob.vercel-storage.com/upload"


# ------------------ COMPANIES ------------------
def create_company(db: Session, company: schemas.CompanyCreate):
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_company_by_id(db: Session, company_id: int):
    return db.query(models.Company).filter(models.Company.id == company_id).first()

def get_company_by_name(db: Session, name: str):
    return db.query(models.Company).filter(models.Company.name == name).first()

def get_companies(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True):
    query = db.query(models.Company)
    if active_only:
        query = query.filter(models.Company.is_active == 1)
    return query.offset(skip).limit(limit).all()

def update_company(db: Session, company_id: int, company_update: schemas.CompanyUpdate):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if company:
        for key, value in company_update.dict(exclude_unset=True).items():
            setattr(company, key, value)
        db.commit()
        db.refresh(company)
    return company

def delete_company(db: Session, company_id: int):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if company:
        db.delete(company)
        db.commit()
        return True
    return False


# ------------------ AUDIT LOGS ------------------
def log_action(
    db: Session,
    *,
    actor_user_id: int,
    action: str,
    target_id: Optional[int] = None,
    meta: Optional[dict] = None,
):
    entry = models.AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        target_id=target_id,
        meta=json.dumps(meta or {}),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def list_audit_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AuditLog).order_by(models.AuditLog.id.desc()).offset(skip).limit(limit).all()

def list_audit_logs_for_application(db: Session, application_id: int):
    return (
        db.query(models.AuditLog)
        .filter(models.AuditLog.target_id == application_id)
        .order_by(models.AuditLog.id.desc())
        .all()
    )


#----------------USERS-----------
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()



def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password_hash=hashed_password,
        company_id=user.company_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def delete_user(db: Session, user_id: int):
    """
    Delete a user and all their related data (cascading delete).
    This will automatically delete:
    - All user's applications
    - All related next of kin records
    - All related spouse records
    - All related beneficiary records
    - All related document records
    - All related payment records
    - Sets audit log actor_user_id to NULL for this user
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False


def get_users(db: Session, skip: int = 0, limit: int = 100, company_id: int = None):
    """Get all users with optional company filtering"""
    query = db.query(models.User)
    if company_id:
        query = query.filter(models.User.company_id == company_id)
    return query.offset(skip).limit(limit).all()


# ------------------ APPLICATIONS ------------------
def create_application(db: Session, app_data: schemas.ApplicationCreate, user_id: int):
    db_app = models.Application(
        user_id=user_id,
        council_waiting_list_number=app_data.council_waiting_list_number,
        name=app_data.name,
        surname=app_data.surname,
        id_number=app_data.id_number,
        dob=app_data.dob,
        residential_address=app_data.residential_address,
        contact_numbers=app_data.contact_numbers,
        employer=app_data.employer,
        department=app_data.department,
        employment_number=app_data.employment_number,
        employer_contact=app_data.employer_contact,
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    # log
    log_action(
        db,
        actor_user_id=user_id,
        action="APPLICATION_CREATED",
        target_id=db_app.id,
        meta={"name": db_app.name, "surname": db_app.surname},
    )
    return db_app


def get_applications_by_user(db: Session, user_id: int):
    apps = db.query(models.Application).filter(models.Application.user_id == user_id).all()
    return apps


def get_application_by_id(db: Session, application_id: int):
    return db.query(models.Application).filter(models.Application.id == application_id).first()


def list_all_applications(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Application).offset(skip).limit(limit).all()


def update_application_status(db: Session, application_id: int, status: str, actor_user_id: int = None):
    app = db.query(models.Application).filter(models.Application.id == application_id).first()
    if app:
        app.status = status
        db.commit()
        db.refresh(app)
        if actor_user_id is not None:
            log_action(
                db,
                actor_user_id=actor_user_id,
                action="APPLICATION_STATUS_CHANGED",
                target_id=application_id,
                meta={"new_status": status},
            )
    return app


# ------------------ NEXT OF KIN ------------------
def add_next_of_kin(db: Session, kin: schemas.NextOfKinCreate, application_id: int, actor_user_id: int = None):
    db_kin = models.NextOfKin(application_id=application_id, **kin.dict())
    db.add(db_kin)
    db.commit()
    db.refresh(db_kin)
    if actor_user_id is not None:
        log_action(
            db,
            actor_user_id=actor_user_id,
            action="NEXT_OF_KIN_ADDED",
            target_id=application_id,
            meta={"kin_id": db_kin.id},
        )
    return db_kin


# ------------------ SPOUSE ------------------
def add_spouse(db: Session, spouse: schemas.SpouseCreate, application_id: int, actor_user_id: int = None):
    db_spouse = models.Spouse(application_id=application_id, **spouse.dict())
    db.add(db_spouse)
    db.commit()
    db.refresh(db_spouse)
    if actor_user_id is not None:
        log_action(
            db,
            actor_user_id=actor_user_id,
            action="SPOUSE_ADDED",
            target_id=application_id,
            meta={"spouse_id": db_spouse.id},
        )
    return db_spouse


# ------------------ BENEFICIARIES ------------------
def add_beneficiary(db: Session, beneficiary: schemas.BeneficiaryCreate, application_id: int, actor_user_id: int = None):
    db_ben = models.Beneficiary(application_id=application_id, **beneficiary.dict())
    db.add(db_ben)
    db.commit()
    db.refresh(db_ben)
    if actor_user_id is not None:
        log_action(
            db,
            actor_user_id=actor_user_id,
            action="BENEFICIARY_ADDED",
            target_id=application_id,
            meta={"beneficiary_id": db_ben.id},
        )
    return db_ben


# ------------------ PAYMENTS ------------------
def add_payment(db: Session, payment: schemas.PaymentCreate, application_id: int, actor_user_id: int = None):
    db_payment = models.Payment(application_id=application_id, **payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    if actor_user_id is not None:
        log_action(
            db,
            actor_user_id=actor_user_id,
            action="PAYMENT_RECORDED",
            target_id=application_id,
            meta={"payment_id": db_payment.id, "amount": db_payment.amount, "currency": db_payment.currency},
        )
    return db_payment




# ------------------ DOCUMENTS ------------------
# def add_document(db: Session, application_id: int, file: UploadFile, kind: str):
#     """
#     Save file to disk and insert metadata into DB
#     """
#     # ensure folder exists
#     app_folder = os.path.join(UPLOAD_DIR, f"application_{application_id}")
#     os.makedirs(app_folder, exist_ok=True)

#     file_path = os.path.join(app_folder, file.filename)

#     # save file to disk
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # save metadata in DB
#     db_doc = models.Document(
#         application_id=application_id,
#         kind=kind,
#         path=file_path,
#     )
#     db.add(db_doc)
#     db.commit()
#     db.refresh(db_doc)
#     if actor_user_id is not None:
#         log_action(
#             db,
#             actor_user_id=actor_user_id,
#             action="DOCUMENT_UPLOADED",
#             target_id=application_id,
#             meta={"document_id": db_doc.id, "kind": kind, "path": file_path},
#         )
#     return db_doc

async def add_document(
    db: Session,
    application_id: int,
    file: UploadFile,
    kind: str,
    actor_user_id: int | None = None,
):
    """
    Upload file to Vercel Blob and insert metadata into DB
    """
    if not BLOB_TOKEN:
        raise RuntimeError("Missing BLOB_READ_WRITE_TOKEN environment variable")

    # read file content
    file_bytes = await file.read()

    # upload to vercel blob
    async with httpx.AsyncClient() as client:
        files = {"file": (file.filename, file_bytes, file.content_type)}
        headers = {"Authorization": f"Bearer {BLOB_TOKEN}"}
        resp = await client.post(BLOB_API_URL, files=files, headers=headers)

    if resp.status_code != 200:
        raise RuntimeError(f"Vercel Blob upload failed: {resp.text}")

    blob_data = resp.json()
    blob_url = blob_data["url"]  # permanent public URL

    # save metadata in DB
    db_doc = models.Document(
        application_id=application_id,
        kind=kind,
        path=blob_url,  # now stores blob URL instead of local path
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    # optional: log action
    if actor_user_id is not None:
        log_action(
            db,
            actor_user_id=actor_user_id,
            action="DOCUMENT_UPLOADED",
            target_id=application_id,
            meta={"document_id": db_doc.id, "kind": kind, "url": blob_url},
        )

    return db_doc


def get_documents_by_application(db: Session, application_id: int):
    return db.query(models.Document).filter(models.Document.application_id == application_id).all()