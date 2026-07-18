from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services import users as user_service
from app.utils.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_service.create_user(db, user)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        user = user_service.authenticate_user(db, credentials.email, credentials.password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))

    access_token = create_access_token(user_id=user.id)
    return {"access_token": access_token, "token_type": "bearer"}