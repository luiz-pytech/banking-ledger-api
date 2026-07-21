import uuid, logging

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.account import Account
from app.models.keys_pix import KeysPix
from app.utils.exceptions import PixKeyNotFoundError, PixKeyAlreadyExistsError, InvalidPixKeyTypeError

from app.services.accounts import get_account_by_id

logger = logging.getLogger(__name__)

VALID_PIX_KEY_TYPES = ("cpf", "email", "phone", "random")


def create_pix_key(db: Session, account_id: uuid.UUID, type_key: str, value_key: str) -> KeysPix:
    if type_key not in VALID_PIX_KEY_TYPES:
        raise InvalidPixKeyTypeError(
            f"Tipo de chave inválido: {type_key}. Use um de {VALID_PIX_KEY_TYPES}."
        )

    get_account_by_id(db, account_id)

    new_pix_key = KeysPix(
        account_id=account_id,
        type_key=type_key,
        value_key=value_key,
        status="active",
    )

    try:
        db.add(new_pix_key)
        db.commit()
        db.refresh(new_pix_key)
    except IntegrityError as e:
        db.rollback()
        logger.error("Failed to create Pix key %s for account %s: %s", value_key, account_id, e)
        raise PixKeyAlreadyExistsError("Esta chave Pix já está cadastrada.") from e

    return new_pix_key

def get_account_by_pix_key(db: Session, value_key: str) -> Account:
    command =select(Account).join(KeysPix).where(
    KeysPix.value_key == value_key,
    KeysPix.status == "active",
    )  
    account = db.execute(command).scalar_one_or_none()

    if not account:
        logger.error("Pix key with value %s not found.", value_key)
        raise PixKeyNotFoundError(f"Pix key with value {value_key} not found.")

    logger.info("Pix key with value %s found for account ID %s.", value_key, account.id)
    return account

def deactivate_pix_key(db: Session, key_id: uuid.UUID) -> None:
    command = select(KeysPix).where(KeysPix.id == key_id)
    pix_key = db.execute(command).scalar_one_or_none()

    if not pix_key:
        logger.error("Pix key with ID %s not found.", key_id)
        raise PixKeyNotFoundError(f"Pix key with ID {key_id} not found.")
    
    logger.info("Deactivating Pix key with ID %s.", key_id)
    pix_key.status = "inactive"
    db.commit()
    
def list_keys_by_account(db: Session, account_id: uuid.UUID) -> list[KeysPix]:
    command = select(KeysPix).where(KeysPix.account_id == account_id)
    keys = db.execute(command).scalars().all()
    
    logger.info("Found %d Pix keys for account ID %s.", len(keys), account_id)
    return list(keys)

def get_pix_key_by_id(db: Session, key_id: uuid.UUID) -> KeysPix:
    command = select(KeysPix).where(KeysPix.id == key_id)
    key = db.execute(command).scalar_one_or_none()
    if not key:
        raise PixKeyNotFoundError(f"Pix key with ID {key_id} not found.")
    return key
