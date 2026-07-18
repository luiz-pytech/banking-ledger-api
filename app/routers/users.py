from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserResponse, UserUpdate, PasswordChange
from app.models.user import User
from app.services.users import update_user, deactivate_user, change_password
from app.core.security import get_current_user
from app.database import get_db

from app.utils.exceptions import UserAlreadyExistsError, InvalidCredentialsError

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user

@router.put("/me", response_model=UserResponse)
def update_me(user_update: UserUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user),):
    try:
        updated_user = update_user(db, user.id, user_update=user_update)
        return updated_user
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
@router.delete("/me", response_model=UserResponse)
def deactivate_me(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    deactivate_user(db, user.id)
    return user

@router.put("/me/password", response_model=UserResponse)
def change_password_me(
    password_change: PasswordChange,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        change_password(db, user.id, password_change.old_password, password_change.new_password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return user
