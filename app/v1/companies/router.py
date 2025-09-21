"""
Company management routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ... import crud, schemas, models
from ...deps import get_db
from ..auth.security import get_current_user, get_current_admin

router = APIRouter(prefix="/companies", tags=["companies"])

# ------------------- Admin Endpoints -------------------
@router.post("/", response_model=schemas.CompanyOut)
def create_company(
    company_data: schemas.CompanyCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Create a new company (Admin only).
    """
    # Check if company with this name already exists
    if crud.get_company_by_name(db, company_data.name):
        raise HTTPException(status_code=400, detail="Company with this name already exists")

    return crud.create_company(db, company_data)


@router.get("/public", response_model=List[schemas.CompanyOut])
def list_companies_public(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """
    List all companies. Public endpoint for registration.
    """
    return crud.get_companies(db, skip=skip, limit=limit, active_only=active_only)


@router.get("/", response_model=List[schemas.CompanyOut])
def list_companies(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    List all companies. Any authenticated user can view companies.
    """
    return crud.get_companies(db, skip=skip, limit=limit, active_only=active_only)


@router.get("/{company_id}", response_model=schemas.CompanyOut)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get company by ID.
    """
    company = crud.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=schemas.CompanyOut)
def update_company(
    company_id: int,
    company_update: schemas.CompanyUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Update company (Admin only).
    """
    company = crud.update_company(db, company_id, company_update)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Delete company (Admin only).
    """
    success = crud.delete_company(db, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Company not found")
    return