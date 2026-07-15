import logging
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.ledger import Ledger
from app.models.transaction import Transaction
from app.services.accounts import get_balance
from app.utils.exceptions import (
    AccountNotActiveError,
    AccountNotFoundError,
    InsufficientFundsError,
    InvalidTransactionAmountError,
    SelfTransferError,
    TransactionIntegrityError,
)

logger = logging.getLogger(__name__)


# Helpers privados
def _get_transaction_by_idempotency_key(
    db: Session, idempotency_key: str
) -> Transaction | None:
    command = select(Transaction).where(Transaction.idempotency_key == idempotency_key)
    transaction = db.execute(command).scalar_one_or_none()

    if not transaction:
        logger.info("No transaction found with idempotency key: %s", idempotency_key)
    else:
        logger.info("Transaction found with idempotency key: %s", idempotency_key)

    return transaction


def _return_existing_transaction(
    db: Session, idempotency_key: str, transaction_type: str
) -> Transaction | None:
    existing_transaction = _get_transaction_by_idempotency_key(db, idempotency_key)
    if existing_transaction:
        logger.info(
            "Returning existing %s transaction for idempotency key: %s",
            transaction_type,
            idempotency_key,
        )
    return existing_transaction


def _validate_positive_value(value: Decimal, message: str) -> None:
    if value <= 0:
        raise InvalidTransactionAmountError(message)


def _validate_account_active(account: Account, operation: str) -> None:
    if account.status != "active":
        logger.error(
            "Account %s is not active (status=%s), %s rejected.",
            account.id,
            account.status,
            operation,
        )
        raise AccountNotActiveError(
            f"Conta {account.id} não está ativa (status: {account.status})."
        )


def _get_locked_account(db: Session, account_id: uuid.UUID, operation: str) -> Account:
    command = select(Account).where(Account.id == account_id).with_for_update()
    account = db.execute(command).scalar_one_or_none()

    if not account:
        logger.error("Account with ID %s not found for %s.", account_id, operation)
        raise AccountNotFoundError(f"Account with ID {account_id} not found.")

    _validate_account_active(account, operation)
    return account


def _get_locked_accounts(
    db: Session, account_ids: list[uuid.UUID], operation: str
) -> list[Account]:
    accounts = db.execute(
        select(Account)
        .where(Account.id.in_(account_ids))
        .order_by(Account.id)
        .with_for_update()
    ).scalars().all()

    if len(accounts) != len(account_ids):
        logger.error("One or more accounts not found: %s", account_ids)
        raise AccountNotFoundError("Uma ou mais contas não foram encontradas.")

    for account in accounts:
        _validate_account_active(account, operation)

    return list(accounts)


def _validate_sufficient_funds(
    db: Session, account_id: uuid.UUID, value: Decimal
) -> None:
    balance = get_balance(db, account_id)
    if value > balance:
        logger.error(
            "Insufficient funds for account ID %s. Available: %s, Required: %s",
            account_id,
            balance,
            value,
        )
        raise InsufficientFundsError(
            f"Saldo insuficiente na conta {account_id}. "
            f"Disponível: {balance}, solicitado: {value}"
        )


def _create_transaction(
    db: Session,
    *,
    transaction_type: str,
    value: Decimal,
    idempotency_key: str,
    account_origin_id: uuid.UUID | None = None,
    account_destination_id: uuid.UUID | None = None,
) -> Transaction:
    transaction = Transaction(
        account_origin_id=account_origin_id,
        account_destination_id=account_destination_id,
        value=value,
        idempotency_key=idempotency_key,
        status="finished",
        type=transaction_type,
    )
    db.add(transaction)
    db.flush()
    return transaction


def _add_ledger_entry(
    db: Session,
    *,
    account_id: uuid.UUID,
    transaction_id: uuid.UUID,
    entry_type: str,
    value: Decimal,
    description: str,
) -> None:
    db.add(
        Ledger(
            account_id=account_id,
            transaction_id=transaction_id,
            type=entry_type,
            value=value,
            description=description,
        )
    )


def _commit_transaction(
    db: Session,
    transaction: Transaction,
    *,
    idempotency_key: str,
    operation: str,
    integrity_message: str,
) -> Transaction:
    try:
        db.commit()
        db.refresh(transaction)
    except IntegrityError as e:
        db.rollback()
        logger.error("Error committing %s: %s", operation, e)
        existing = _get_transaction_by_idempotency_key(db, idempotency_key)
        if existing:
            return existing
        raise TransactionIntegrityError(integrity_message) from e

    logger.info(
        "Created new %s transaction with ID %s for idempotency key: %s",
        operation,
        transaction.id,
        idempotency_key,
    )
    return transaction


# Funções públicas

def create_pix_transfer(
    db: Session,
    account_origin_id: uuid.UUID,
    account_destination_id: uuid.UUID,
    value: Decimal,
    idempotency_key: str,
) -> Transaction:
    if account_origin_id == account_destination_id:
        raise SelfTransferError("Conta de origem e destino não podem ser iguais.")
    _validate_positive_value(
        value, "O valor da transferência deve ser maior que zero."
    )

    existing_transaction = _return_existing_transaction(
        db, idempotency_key, "transfer_pix"
    )
    if existing_transaction:
        return existing_transaction

    _get_locked_accounts(
        db, [account_origin_id, account_destination_id], "transfer"
    )
    _validate_sufficient_funds(db, account_origin_id, value)

    transaction = _create_transaction(
        db,
        transaction_type="transfer_pix",
        account_origin_id=account_origin_id,
        account_destination_id=account_destination_id,
        value=value,
        idempotency_key=idempotency_key,
    )
    _add_ledger_entry(
        db,
        account_id=account_origin_id,
        transaction_id=transaction.id,
        entry_type="debit",
        value=value,
        description="Transferência Pix enviada",
    )
    _add_ledger_entry(
        db,
        account_id=account_destination_id,
        transaction_id=transaction.id,
        entry_type="credit",
        value=value,
        description="Transferência Pix recebida",
    )

    return _commit_transaction(
        db,
        transaction,
        idempotency_key=idempotency_key,
        operation="Pix transfer",
        integrity_message=(
            "Não foi possível concluir a transferência devido a um erro de integridade."
        ),
    )


def create_deposit(
    db: Session,
    account_destination_id: uuid.UUID,
    value: Decimal,
    idempotency_key: str,
) -> Transaction:
    _validate_positive_value(value, "O valor do depósito deve ser maior que zero.")

    existing_transaction = _return_existing_transaction(db, idempotency_key, "deposit")
    if existing_transaction:
        return existing_transaction

    _get_locked_account(db, account_destination_id, "deposit")

    transaction = _create_transaction(
        db,
        transaction_type="deposit",
        account_destination_id=account_destination_id,
        value=value,
        idempotency_key=idempotency_key,
    )
    _add_ledger_entry(
        db,
        account_id=account_destination_id,
        transaction_id=transaction.id,
        entry_type="credit",
        value=value,
        description="Depósito",
    )

    return _commit_transaction(
        db,
        transaction,
        idempotency_key=idempotency_key,
        operation="deposit",
        integrity_message=(
            "Não foi possível concluir o depósito devido a um erro de integridade."
        ),
    )


def create_withdrawal(
    db: Session,
    account_origin_id: uuid.UUID,
    value: Decimal,
    idempotency_key: str,
) -> Transaction:
    _validate_positive_value(value, "O valor do saque deve ser maior que zero.")

    existing_transaction = _return_existing_transaction(db, idempotency_key, "withdrawal")
    if existing_transaction:
        return existing_transaction

    _get_locked_account(db, account_origin_id, "withdrawal")
    _validate_sufficient_funds(db, account_origin_id, value)

    transaction = _create_transaction(
        db,
        transaction_type="withdrawal",
        account_origin_id=account_origin_id,
        value=value,
        idempotency_key=idempotency_key,
    )
    _add_ledger_entry(
        db,
        account_id=account_origin_id,
        transaction_id=transaction.id,
        entry_type="debit",
        value=value,
        description="Saque",
    )

    return _commit_transaction(
        db,
        transaction,
        idempotency_key=idempotency_key,
        operation="withdrawal",
        integrity_message=(
            "Não foi possível concluir o saque devido a um erro de integridade."
        ),
    )