import uuid
from decimal import Decimal

import pytest

from app.schemas.user import UserCreate
from app.services import accounts as account_service
from app.services import users as user_service
from app.services.transactions import (
    create_pix_transfer,
    create_deposit,
    create_withdrawal,
)
from app.utils.exceptions import (
    AccountNotFoundError,
    AccountNotActiveError,
    InsufficientFundsError,
    InvalidTransactionAmountError,
    SelfTransferError,
)


def _create_account_for_new_user(db, *, document: str, email: str):
    """
    Helper function to create a new user and account for testing purposes.
    """
    user = user_service.create_user(
        db,
        UserCreate(
            name="Usuario Destino",
            document=document,
            email=email,
            password="senha1234",
        ),
    )
    return account_service.create_account(db, user.id, "current")


def test_create_deposit_success_credits_balance(db, sample_account):
    create_deposit(db, sample_account.id, Decimal("100.00"), "deposit-1")

    balance = account_service.get_balance(db, sample_account.id)
    assert balance == Decimal("100.00")


def test_create_deposit_rejects_non_positive_value(db, sample_account):
    with pytest.raises(InvalidTransactionAmountError):
        create_deposit(db, sample_account.id, Decimal("0.00"), "deposit-2")

    with pytest.raises(InvalidTransactionAmountError):
        create_deposit(db, sample_account.id, Decimal("-10.00"), "deposit-3")


def test_create_deposit_rejects_nonexistent_account(db):
    with pytest.raises(AccountNotFoundError):
        create_deposit(db, uuid.uuid4(), Decimal("10.00"), "deposit-4")


def test_create_deposit_is_idempotent(db, sample_account):
    first = create_deposit(db, sample_account.id, Decimal("50.00"), "deposit-5")
    second = create_deposit(db, sample_account.id, Decimal("50.00"), "deposit-5")

    assert first.id == second.id
    balance = account_service.get_balance(db, sample_account.id)
    assert balance == Decimal("50.00")  # não duplicou


def test_create_withdrawal_success_debits_balance(db, sample_account):
    create_deposit(db, sample_account.id, Decimal("100.00"), "seed-1")

    create_withdrawal(db, sample_account.id, Decimal("30.00"), "withdrawal-1")

    balance = account_service.get_balance(db, sample_account.id)
    assert balance == Decimal("70.00")


def test_create_withdrawal_rejects_insufficient_funds(db, sample_account):
    create_deposit(db, sample_account.id, Decimal("10.00"), "seed-2")

    with pytest.raises(InsufficientFundsError):
        create_withdrawal(db, sample_account.id, Decimal("999.00"), "withdrawal-2")


def test_create_withdrawal_rejects_non_positive_value(db, sample_account):
    with pytest.raises(InvalidTransactionAmountError):
        create_withdrawal(db, sample_account.id, Decimal("-5.00"), "withdrawal-3")


def test_create_withdrawal_rejects_nonexistent_account(db):
    with pytest.raises(AccountNotFoundError):
        create_withdrawal(db, uuid.uuid4(), Decimal("10.00"), "withdrawal-4")


def test_create_withdrawal_is_idempotent(db, sample_account):
    create_deposit(db, sample_account.id, Decimal("100.00"), "seed-3")

    first = create_withdrawal(db, sample_account.id, Decimal("20.00"), "withdrawal-5")
    second = create_withdrawal(db, sample_account.id, Decimal("20.00"), "withdrawal-5")

    assert first.id == second.id
    balance = account_service.get_balance(db, sample_account.id)
    assert balance == Decimal("80.00")  # não duplicou o débito


def test_create_pix_transfer_success_moves_balance(db, sample_account):
    destination = _create_account_for_new_user(
        db, document="22222222222", email="destino@teste.com"
    )
    create_deposit(db, sample_account.id, Decimal("100.00"), "seed-transfer-1")

    create_pix_transfer(
        db, sample_account.id, destination.id, Decimal("30.00"), "transfer-1"
    )

    assert account_service.get_balance(db, sample_account.id) == Decimal("70.00")
    assert account_service.get_balance(db, destination.id) == Decimal("30.00")


def test_create_pix_transfer_rejects_self_transfer(db, sample_account):
    with pytest.raises(SelfTransferError):
        create_pix_transfer(
            db, sample_account.id, sample_account.id, Decimal("10.00"), "transfer-2"
        )


def test_create_pix_transfer_rejects_non_positive_value(db, sample_account):
    destination = _create_account_for_new_user(
        db, document="33333333333", email="destino2@teste.com"
    )

    with pytest.raises(InvalidTransactionAmountError):
        create_pix_transfer(
            db, sample_account.id, destination.id, Decimal("-1.00"), "transfer-3"
        )


def test_create_pix_transfer_rejects_insufficient_funds(db, sample_account):
    destination = _create_account_for_new_user(
        db, document="44444444444", email="destino3@teste.com"
    )
    create_deposit(db, sample_account.id, Decimal("10.00"), "seed-transfer-2")

    with pytest.raises(InsufficientFundsError):
        create_pix_transfer(
            db, sample_account.id, destination.id, Decimal("999.00"), "transfer-4"
        )


def test_create_pix_transfer_rejects_nonexistent_account(db, sample_account):
    with pytest.raises(AccountNotFoundError):
        create_pix_transfer(
            db, sample_account.id, uuid.uuid4(), Decimal("10.00"), "transfer-5"
        )


def test_create_pix_transfer_rejects_blocked_destination_account(db, sample_account):
    destination = _create_account_for_new_user(
        db, document="55555555555", email="destino4@teste.com"
    )
    create_deposit(db, sample_account.id, Decimal("100.00"), "seed-transfer-3")
    destination.status = "blocked"
    db.commit()

    with pytest.raises(AccountNotActiveError):
        create_pix_transfer(
            db, sample_account.id, destination.id, Decimal("10.00"), "transfer-6"
        )


def test_create_pix_transfer_is_idempotent(db, sample_account):
    destination = _create_account_for_new_user(
        db, document="66666666666", email="destino5@teste.com"
    )
    create_deposit(db, sample_account.id, Decimal("100.00"), "seed-transfer-4")

    first = create_pix_transfer(
        db, sample_account.id, destination.id, Decimal("40.00"), "transfer-7"
    )
    second = create_pix_transfer(
        db, sample_account.id, destination.id, Decimal("40.00"), "transfer-7"
    )

    assert first.id == second.id
    assert account_service.get_balance(db, sample_account.id) == Decimal("60.00")
    assert account_service.get_balance(db, destination.id) == Decimal("40.00")