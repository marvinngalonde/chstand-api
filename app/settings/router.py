from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..auth.security import get_current_admin
from ..models import Application, Payment
from sqlalchemy import func

router = APIRouter()

@router.get("/", response_model=dict)
def get_settings(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    settings = db.query(Setting).all()
    return {s.key: s.value for s in settings}

@router.put("/{key}")
def update_setting(key: str, value: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        setting = Setting(key=key, value=value)
        db.add(setting)
    else:
        setting.value = value
    db.commit()
    return {"key": key, "value": value}
