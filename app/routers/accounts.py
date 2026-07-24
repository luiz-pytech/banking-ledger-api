import uuid
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.models.user import User
from app.schemas.account import AccountResponse, AccountCreate
from app.database import get_db

from app.core.security import get_current_user
from app.core.permissions import ensure_account_belongs_to_user

from app.services.accounts import create_account, get_accounts_by_user, get_account_by_id, get_balance, get_account_by_number
from app.utils.exceptions import InvalidAccountTypeError, AccountAlreadyExistsError, AccountNotFoundError


router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("/", response_model=AccountResponse, status_code=201)
def new_account(account_create: AccountCreate, db = Depends(get_db), user = Depends(get_current_user)):
    try:
        return create_account(db, user.id, account_create.type_account)
    except InvalidAccountTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AccountAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/", response_model=list[AccountResponse], status_code=200)
def list_accounts(db = Depends(get_db), user = Depends(get_current_user)):
    return get_accounts_by_user(db, user.id)

@router.get("/{account_id}", response_model=AccountResponse, status_code=200)
def get_account(account_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        account = get_account_by_id(db, account_id)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    ensure_account_belongs_to_user(account, user)
    return account


@router.get("/{account_id}/balance")
def get_account_balance(account_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        account = get_account_by_id(db, account_id)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    ensure_account_belongs_to_user(account, user)
    balance = get_balance(db, account_id)
    return {"account_id": account.id, "balance": balance}

@router.get("/{number_accounts}", response_model=AccountResponse, status_code=200)
def fetch_account_by_number(number_account: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        account = get_account_by_number(db, number_account)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return account