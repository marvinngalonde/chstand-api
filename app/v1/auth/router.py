from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ... import crud, schemas, models
from ...deps import get_db
from .security import verify_password, create_access_token, get_current_user,get_current_admin

router = APIRouter()


# -------- Register --------
@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user and refresh to get all fields
    db_user = crud.create_user(db, user)
    db.refresh(db_user)
    return db_user


# -------- Login --------
@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id) 
    return {"access_token": token, "token_type": "bearer","user_id":user.id,"user_role":user.role}


# -------- Current User --------
@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user=Depends(get_current_user)):
    return current_user



# ---- List all users ----
@router.get("/users", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.User).all()


# ---- Update user ----
@router.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_update: schemas.UserUpdate,
                db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


# ---- Delete user ----
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    """
    Delete a user and ALL their related data.
    This will cascade delete:
    - All applications by this user
    - All next of kin records for those applications
    - All spouse records for those applications
    - All beneficiary records for those applications
    - All document records for those applications
    - All payment records for those applications
    """
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return
