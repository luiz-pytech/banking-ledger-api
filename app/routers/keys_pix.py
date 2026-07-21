import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.core.permissions import ensure_account_belongs_to_user
from app.models.user import User
from app.schemas.keys_pix import KeysPixCreate, KeysPixResponse
from app.services.accounts import get_account_by_id, get_accounts_by_user
from app.services.keys_pix import (
    create_pix_key,
    deactivate_pix_key,
    get_pix_key_by_id,
    list_keys_by_account,
)
from app.utils.exceptions import (
    AccountNotFoundError,
    InvalidPixKeyTypeError,
    PixKeyAlreadyExistsError,
    PixKeyNotFoundError,
)

router = APIRouter(prefix="/pix-keys", tags=["pix-keys"])


@router.post("/", response_model=KeysPixResponse, status_code=201)
def new_pix_key(
    key_create: KeysPixCreate,
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        account = get_account_by_id(db, account_id)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    ensure_account_belongs_to_user(account, user)

    try:
        return create_pix_key(db, account_id, key_create.type_key, key_create.value_key)
    except InvalidPixKeyTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PixKeyAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/", response_model=list[KeysPixResponse])
def list_my_pix_keys(db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    all_keys = []
    for account in get_accounts_by_user(db, user.id):
        all_keys.extend(list_keys_by_account(db, account.id))
    return all_keys


@router.delete("/{key_id}", status_code=204)
def remove_pix_key(
    key_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        key = get_pix_key_by_id(db, key_id)
    except PixKeyNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    account = get_account_by_id(db, key.account_id)
    ensure_account_belongs_to_user(account, user)

    deactivate_pix_key(db, key_id)