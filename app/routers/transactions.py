import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.core.permissions import ensure_account_belongs_to_user
from app.models.user import User
from app.schemas.transaction import (
    DepositRequest,
    TransactionRead,
    TransferRequest,
    WithdrawalRequest,
)
from app.services.accounts import get_account_by_id
from app.services.transactions import (
    create_deposit,
    create_pix_transfer,
    create_withdrawal,
    get_transaction_by_id,
)
from app.utils.exceptions import (
    AccountNotActiveError,
    AccountNotFoundError,
    InsufficientFundsError,
    InvalidTransactionAmountError,
    SelfTransferError,
    TransactionIntegrityError,
    TransactionNotFoundError,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _handle_transaction_errors(func, *args, **kwargs):

    try:
        return func(*args, **kwargs)
    except SelfTransferError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InvalidTransactionAmountError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccountNotActiveError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except InsufficientFundsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionIntegrityError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/transfer", response_model=TransactionRead, status_code=201)
def transfer(
    data: TransferRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        origin_account = get_account_by_id(db, data.account_origin_id)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    ensure_account_belongs_to_user(origin_account, user)

    return _handle_transaction_errors(
        create_pix_transfer,
        db,
        data.account_origin_id,
        data.account_destination_id,
        data.value,
        data.idempotency_key,
    )


@router.post("/deposit", response_model=TransactionRead, status_code=201)
def deposit(
    data: DepositRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        account = get_account_by_id(db, data.account_destination_id)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    ensure_account_belongs_to_user(account, user)

    return _handle_transaction_errors(
        create_deposit, db, data.account_destination_id, data.value, data.idempotency_key
    )


@router.post("/withdrawal", response_model=TransactionRead, status_code=201)
def withdrawal(
    data: WithdrawalRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        account = get_account_by_id(db, data.account_origin_id)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    ensure_account_belongs_to_user(account, user)

    return _handle_transaction_errors(
        create_withdrawal, db, data.account_origin_id, data.value, data.idempotency_key
    )


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        transaction = get_transaction_by_id(db, transaction_id)
    except TransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    accounts = _get_accounts_for_ownership_check(db, user.id)
    if transaction.account_origin_id not in accounts and transaction.account_destination_id not in accounts:
        raise HTTPException(status_code=403, detail="Você não tem acesso a esta transação.")

    return transaction


def _get_accounts_for_ownership_check(db: Session, user_id: uuid.UUID) -> set:
    from app.services.accounts import get_accounts_by_user
    return {a.id for a in get_accounts_by_user(db, user_id)}