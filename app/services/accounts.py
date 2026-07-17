import uuid, random, logging
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.account import Account
from app.models.ledger import Ledger
from app.services.users import get_user_by_id
from app.utils.exceptions import AccountAlreadyExistsError, AccountNotFoundError, InvalidAccountTypeError

MAX_TENTATIVAS = 5
logger = logging.getLogger(__name__)

VALID_ACCOUNT_TYPES = ["current", "savings"]


def _generate_unique_account_number(db: Session) -> str:
    for _ in range(MAX_TENTATIVAS):
        candidate = f"{random.randint(100000, 999999)}"
        exists = db.scalar(select(Account.id).where(Account.number_account == candidate))
        if not exists:
            return candidate
    raise RuntimeError("Não foi possível gerar número de conta único após várias tentativas.")

def create_account(db: Session, user_id: uuid.UUID, type_account: str) -> Account:
    if type_account not in VALID_ACCOUNT_TYPES:
        logger.error("Invalid account type provided: %s", type_account)
        raise InvalidAccountTypeError(f"Tipo de conta inválido: {type_account}. Deve ser 'current' ou 'savings'.")
    
    user = get_user_by_id(db, user_id)
    new_account = Account(
        user_id=user.id,
        type_account=type_account,
        number_account=_generate_unique_account_number(db),
        status="active"
    )
    try:
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
    except IntegrityError as e:
        db.rollback()
        logger.error("Failed to create account for user %s: %s", user_id, e)
        raise AccountAlreadyExistsError("Não foi possível criar a conta. Verifique se você já possui uma conta desse tipo.") from e

    logger.info("Account created successfully for user ID %s with account ID %s.", user_id, new_account.id)
    return new_account

def get_balance(db: Session, account_id: uuid.UUID) -> Decimal:
    get_account_by_id(db, account_id)  

    credit_sum = db.scalar(
        select(func.coalesce(func.sum(Ledger.value), 0)).where(
            Ledger.account_id == account_id, Ledger.type == "credit"
        )
    )
    debit_sum = db.scalar(
        select(func.coalesce(func.sum(Ledger.value), 0)).where(
            Ledger.account_id == account_id, Ledger.type == "debit"
        )
    )
    if credit_sum is None:
        credit_sum = 0
    if debit_sum is None:
        debit_sum = 0
    return Decimal(credit_sum) - Decimal(debit_sum)
    
def get_account_by_id(db: Session, account_id: uuid.UUID) -> Account:
    command = select(Account).where(Account.id == account_id)
    account = db.execute(command).scalar_one_or_none()

    if not account:
        logger.error("Account with ID %s not found.", account_id)
        raise AccountNotFoundError(f"Account with ID {account_id} not found.")

    logger.info("Account with ID %s found for user ID %s.", account_id, account.user_id)
    return account

def get_accounts_by_user(db: Session, user_id: uuid.UUID) -> list[Account]:
    command = select(Account).where(Account.user_id == user_id)
    accounts = db.execute(command).scalars().all()
    
    logger.info("Found %d accounts for user ID %s.", len(accounts), user_id)
    return list(accounts)



