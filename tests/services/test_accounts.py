import pytest
import uuid

from app.models.account import Account
from app.services import accounts as account_service 
from app.utils.exceptions import UserNotFoundError, AccountAlreadyExistsError, InvalidAccountTypeError


def test_create_account_success_current(db, sample_user):
    account = account_service.create_account(db, sample_user.id, "current")

    assert account.id is not None
    assert account.user_id == sample_user.id
    assert account.type_account == "current"
    assert account.status == "active"

def test_create_account_success_savings(db, sample_user):
    account = account_service.create_account(db, sample_user.id, "savings")

    assert account.id is not None
    assert account.user_id == sample_user.id
    assert account.type_account == "savings"
    assert account.status == "active"


def test_create_account_rejects_duplicate_type(db, sample_user):
    account_service.create_account(db, sample_user.id, "current")

    with pytest.raises(AccountAlreadyExistsError):
        account_service.create_account(
            db,
            sample_user.id,
            "current" 
        )

def test_create_account_rejects_invalid_type(db, sample_user):
    with pytest.raises(InvalidAccountTypeError):
        account_service.create_account(
            db,
            sample_user.id,
            "invalid_type" 
        )

def test_create_account_rejects_nonexistent_user(db):
    with pytest.raises(UserNotFoundError):
        account_service.create_account(
            db,
            uuid.uuid4(),
            "current" 
        )

def test_get_balance_initial_zero(db, sample_user):
    account = account_service.create_account(db, sample_user.id, "current")
    balance = account_service.get_balance(db, account.id)

    assert balance == 0





