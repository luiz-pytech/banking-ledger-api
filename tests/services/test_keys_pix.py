import uuid

import pytest

from app.services.keys_pix import (
    create_pix_key,
    get_account_by_pix_key,
    deactivate_pix_key,
    list_keys_by_account,
)
from app.utils.exceptions import (
    PixKeyAlreadyExistsError,
    PixKeyNotFoundError,
    AccountNotFoundError,
)


def test_create_pix_key_success(db, sample_account):
    key_pix = create_pix_key(db, sample_account.id, "cpf", "11111111111")

    assert key_pix.account_id == sample_account.id
    assert key_pix.type_key == "cpf"
    assert key_pix.value_key == "11111111111"
    assert key_pix.status == "active"


def test_create_pix_key_rejects_duplicate_value(db, sample_account):
    create_pix_key(db, sample_account.id, "cpf", "11111111111")

    with pytest.raises(PixKeyAlreadyExistsError):
        create_pix_key(db, sample_account.id, "cpf", "11111111111")


def test_create_pix_key_rejects_nonexistent_account(db):
    with pytest.raises(AccountNotFoundError):
        create_pix_key(db, uuid.uuid4(), "cpf", "11111111111")


def test_get_account_by_pix_key_resolves_correct_account(db, sample_account):
    create_pix_key(db, sample_account.id, "email", "chave@teste.com")

    found_account = get_account_by_pix_key(db, "chave@teste.com")

    assert found_account.id == sample_account.id


def test_get_account_by_pix_key_rejects_nonexistent_key(db):
    with pytest.raises(PixKeyNotFoundError):
        get_account_by_pix_key(db, "nao_existe@teste.com")


def test_get_account_by_pix_key_ignores_deactivated_key(db, sample_account):
    key_pix = create_pix_key(db, sample_account.id, "email", "chave@teste.com")
    deactivate_pix_key(db, key_pix.id)

    with pytest.raises(PixKeyNotFoundError):
        get_account_by_pix_key(db, "chave@teste.com")


def test_deactivate_pix_key_sets_status_inactive(db, sample_account):
    key_pix = create_pix_key(db, sample_account.id, "email", "chave@teste.com")

    deactivate_pix_key(db, key_pix.id)
    db.refresh(key_pix)

    assert key_pix.status == "inactive"


def test_list_keys_by_account_returns_created_keys(db, sample_account):
    create_pix_key(db, sample_account.id, "email", "chave1@teste.com")
    create_pix_key(db, sample_account.id, "phone", "11999999999")

    keys = list_keys_by_account(db, sample_account.id)

    assert len(keys) == 2
    assert {k.value_key for k in keys} == {"chave1@teste.com", "11999999999"}


def test_list_keys_by_account_returns_empty_list_when_none(db, sample_account):
    keys = list_keys_by_account(db, sample_account.id)

    assert keys == []