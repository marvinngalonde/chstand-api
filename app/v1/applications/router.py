"""
Application routes.
"""

from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from ... import crud, schemas
from ...deps import get_db
from ...auth.security import get_current_user, get_current_admin
from fastapi import File,UploadFile


router = APIRouter(prefix="/applications", tags=["applications"])

# ------------------- Applicant Endpoints -------------------
@router.post("/", response_model=schemas.ApplicationOut)
def create_application(
    app_data: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new housing application (Applicant only).
    """
    return crud.create_application(db, app_data, user_id=current_user.id)


# Add NextOfKin
@router.post("/{application_id}/next-of-kin", response_model=schemas.NextOfKinOut)
def add_next_of_kin(
    application_id: int,
    kin: schemas.NextOfKinCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    app = crud.get_application_by_id(db, application_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.add_next_of_kin(db, kin, application_id,actor_user_id=current_user.id)


# Add Spouse
@router.post("/{application_id}/spouse", response_model=schemas.SpouseOut)
def add_spouse(
    application_id: int,
    spouse: schemas.SpouseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    app = crud.get_application_by_id(db, application_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.add_spouse(db, spouse, application_id,actor_user_id=current_user.id)


# Add Beneficiary
@router.post("/{application_id}/beneficiaries", response_model=schemas.BeneficiaryOut)
def add_beneficiary(
    application_id: int,
    beneficiary: schemas.BeneficiaryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    app = crud.get_application_by_id(db, application_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.add_beneficiary(db, beneficiary, application_id,actor_user_id=current_user.id)


# Add Payment
@router.post("/{application_id}/payments", response_model=schemas.PaymentOut)
def add_payment(
    application_id: int,
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    app = crud.get_application_by_id(db, application_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.add_payment(db, payment, application_id,actor_user_id=current_user.id)


@router.get("/my", response_model=List[schemas.ApplicationOut])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get all applications submitted by the logged-in user.
    """
    return crud.get_applications_by_user(db, user_id=current_user.id)


@router.get("/{application_id}", response_model=schemas.ApplicationOut)
def get_application_detail(
    application_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get details of one application (only if owned by user).
    """
    app = crud.get_application_by_id(db, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to view this application")
    return app


# ------------------- Admin Endpoints -------------------
@router.get("/admin/all", response_model=List[schemas.ApplicationOut])
def list_all_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    List all applications (Admin only).
    """
    return crud.list_all_applications(db, skip=skip, limit=limit)


@router.put("/admin/{application_id}/status", response_model=schemas.ApplicationOut)
def update_application_status(
    application_id: int,
    status: str,  # expects "APPROVED" or "REJECTED"
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Approve or reject an application (Admin only).
    """
    app = crud.update_application_status(db, application_id, status,actor_user_id=current_user.id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.get("/logs", response_model=List[schemas.AuditLogOut])
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
):
    return crud.list_audit_logs(db, skip=skip, limit=limit)

@router.get("/applications/{application_id}/logs", response_model=List[schemas.AuditLogOut])
def get_application_logs(
    application_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
):
    return crud.list_audit_logs_for_application(db, application_id)


# ------------------- Documents -------------------
@router.post("/{application_id}/documents", response_model=schemas.DocumentOut)
def upload_document(
    application_id: int,
    kind: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Upload a document (ID_SCAN, PROOF_OF_RESIDENCE, PAYSLIP, SIGNATURE).
    Stores file and metadata.
    """
    app = crud.get_application_by_id(db, application_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return crud.add_document(db, application_id, file, kind,actor_user_id=current_user.id)


@router.get("/{application_id}/documents", response_model=List[schemas.DocumentOut])
def list_documents(
    application_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    List uploaded documents for an application.
    """
    app = crud.get_application_by_id(db, application_id)
    if not app or (app.user_id != current_user.id and current_user.role != "ADMIN"):
        raise HTTPException(status_code=403, detail="Not authorized")

    return crud.get_documents_by_application(db, application_id)


# ---- Update application (Applicant can only update their own, Admin can update any) ----
@router.put("/{application_id}", response_model=schemas.ApplicationOut)
def update_application(application_id: int, app_update: schemas.ApplicationUpdate,
                       db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role != "ADMIN" and app.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this application")

    for key, value in app_update.dict(exclude_unset=True).items():
        setattr(app, key, value)

    db.commit()
    db.refresh(app)
    return app


# ---- Delete application ----
@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role != "ADMIN" and app.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this application")

    db.delete(app)
    db.commit()
    return

    