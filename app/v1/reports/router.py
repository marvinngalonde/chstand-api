from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...deps import get_db
from ...auth.security import get_current_admin
from ...models import Application, Payment
from sqlalchemy import func

router = APIRouter()    

@router.get("/applications/status")
def applications_by_status(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(Application.status, func.count(Application.id)).group_by(Application.status).all()

@router.get("/payments/summary")
def payment_summary(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    total = db.query(func.sum(Payment.amount)).scalar()
    count = db.query(func.count(Payment.id)).scalar()
    return {"total": total or 0, "count": count}
