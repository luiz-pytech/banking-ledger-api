import uuid, logging

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.hashing import hash_password, verify_password
from app.utils.exceptions import UserAlreadyExistsError, UserNotFoundError, InvalidCredentialsError, UserInactiveError

from pydantic import EmailStr
logger = logging.getLogger(__name__)

def create_user(db: Session, user: UserCreate) -> User:
    hashed = hash_password(user.password)
    new_user = User(
        name=user.name,
        document=user.document,
        email=user.email,
        password_hash=hashed,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError as e:
        db.rollback()
        logger.error("Failed to create user with email %s: %s", user.email, e)
        raise UserAlreadyExistsError(
            "Email ou documento já cadastrado."
        ) from e

    logger.info("User created successfully: %s", new_user.id)
    return new_user


def authenticate_user(db: Session, email: EmailStr, password: str) -> User:
    command = select(User).where(User.email == email)
    user = db.execute(command).scalar_one_or_none()

    if not user or  not verify_password(password, user.password_hash):
        logger.warning("Authentication failed for email %s: invalid password.", email)
        raise InvalidCredentialsError("Email ou senha inválidos.")
    if user.status == "inactive":
        logger.warning("Authentication failed for email %s: user is inactive.", email)
        raise UserInactiveError("Usuário inativo.")
    return user


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User:
    command = select(User).where(User.id == user_id)
    user = db.execute(command).scalar_one_or_none()
    if not user:
        logger.warning("User with ID %s not found.", user_id)
        raise UserNotFoundError("User not found.")
    return user


def update_user(db: Session, user_id: uuid.UUID, user_update: UserUpdate) -> User:
    user = get_user_by_id(db, user_id)
    data = user_update.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(user, key, value)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as e:
        db.rollback()
        logger.error("Failed to update user %s: %s", user_id, e)
        raise UserAlreadyExistsError("Email ou documento já cadastrado.") from e

    logger.info("User with ID %s updated successfully.", user_id)
    return user

def change_password(
    db: Session,
    user_id: uuid.UUID,
    current_password: str,
    new_password: str,
) -> None:
    user = get_user_by_id(db, user_id)

    if not verify_password(current_password, user.password_hash):
        logger.warning("Failed password change attempt for user %s: wrong current password.", user_id)
        raise InvalidCredentialsError("Senha atual incorreta.")

    user.password_hash = hash_password(new_password)
    db.commit()
    logger.info("Password changed successfully for user %s.", user_id)


def deactivate_user(db: Session, user_id: uuid.UUID) -> None:
    user = get_user_by_id(db, user_id)
    if user.status != "inactive":
        user.status = "inactive"
        db.commit()

    else:
        logger.warning("Attempted to deactivate user %s who is already inactive.", user_id)
        raise UserInactiveError("Usuário já está inativo.")

    #TODO: PROPAGAR BLOQUEIO DE CONTA DO USUÁRIO PARA TODAS AS CONTAS ASSOCIADAS A ELE



