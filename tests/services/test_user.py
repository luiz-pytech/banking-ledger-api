import pytest

from app.schemas.user import UserCreate
from app.services import users as user_service
from app.utils.exceptions import UserAlreadyExistsError, InvalidCredentialsError


def _make_user_create(**overrides) -> UserCreate:
    """
    Helper function to create a UserCreate object with default values, allowing overrides.
    """
    data = {
        "name": "Usuario Teste",
        "document": "11111111111",
        "email": "teste@teste.com",
        "password": "senha1234",
    }
    data.update(overrides)
    return UserCreate(**data)


def test_create_user_success(db):
    user = user_service.create_user(db, _make_user_create())

    assert user.id is not None
    assert user.email == "teste@teste.com"
    assert user.password_hash != "senha1234"  # the password should be hashed


def test_create_user_rejects_duplicate_document(db):
    user_service.create_user(db, _make_user_create())

    with pytest.raises(UserAlreadyExistsError):
        user_service.create_user(
            db,
            _make_user_create(email="outro@teste.com"),  # document equals, different email
        )


def test_create_user_rejects_duplicate_email(db):
    user_service.create_user(db, _make_user_create())

    with pytest.raises(UserAlreadyExistsError):
        user_service.create_user(
            db,
            _make_user_create(document="22222222222"),  # email equals, different
        )


def test_authenticate_user_success(db):
    user_service.create_user(db, _make_user_create())

    authenticated = user_service.authenticate_user(db, "teste@teste.com", "senha1234")

    assert authenticated.email == "teste@teste.com"


def test_authenticate_user_rejects_wrong_password(db):
    user_service.create_user(db, _make_user_create())

    with pytest.raises(InvalidCredentialsError):
        user_service.authenticate_user(db, "teste@teste.com", "senha_errada")


def test_authenticate_user_rejects_nonexistent_email(db):
    with pytest.raises(InvalidCredentialsError):
        user_service.authenticate_user(db, "nao_existe@teste.com", "qualquer_senha")