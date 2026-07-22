import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services import users as user_service
from app.services import accounts as account_service
from app.utils.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = user_service.create_user(db, user)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))

    try:
        account_service.create_account(db, new_user.id, "current")
    except Exception as e:
        logger.error(
            "Failed to auto-create account for new user %s: %s", new_user.id, e
        )
    return new_user

@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        user = user_service.authenticate_user(db, credentials.email, credentials.password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))

    access_token = create_access_token(user_id=user.id)
    return {"access_token": access_token, "token_type": "bearer"}