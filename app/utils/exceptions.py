# Exceptions users
class UserAlreadyExistsError(Exception):
    """Raised when trying to create a user that already exists."""
    pass

class UserNotFoundError(Exception):
    """Raised when a user is not found."""
    pass

class InvalidCredentialsError(Exception):
    """Raised when the provided credentials are invalid."""
    pass

class UserInactiveError(Exception):
    """Raised when trying to perform an action on an inactive user."""
    pass 

# Exceptions accounts
class AccountNotFoundError(Exception):
    """Raised when an account is not found."""
    pass

class AccountAlreadyExistsError(Exception):
    """Raised when trying to create an account that already exists."""
    pass

class AccountNotActiveError(Exception):
    """Raised when trying to perform an action on an inactive account."""
    pass

class AccountNotOwnedByUserError(Exception):
    """Raised when trying to access an account that is not owned by the user."""
    pass

# Exceptions keyspix
class PixKeyNotFoundError(Exception):
    """Raised when a Pix key is not found."""
    pass

class PixKeyAlreadyExistsError(Exception):
    """Raised when trying to create a Pix key that already exists."""
    pass

class InvalidPixKeyTypeError(Exception):
    """Raised when an invalid Pix key type is provided."""
    pass

# Exceptions transactions
class InsufficientFundsError(Exception):
    """Raised when trying to perform a transaction with insufficient funds."""
    pass

class SelfTransferError(Exception):
    """Raised when trying to transfer funds to the same account."""
    pass

class InvalidTransactionAmountError(Exception):
    """Raised when trying to perform a transaction with an invalid amount."""
    pass

class TransactionIntegrityError(Exception):
    """Raised when a transaction fails due to integrity constraints."""
    pass



