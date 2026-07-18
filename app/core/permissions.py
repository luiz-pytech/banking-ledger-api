from fastapi import HTTPException, status

from app.models.account import Account
from app.models.user import User


def ensure_account_belongs_to_user(account: Account, user: User) -> None:
    if account.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a esta conta.",
        )