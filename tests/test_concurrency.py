import threading
import uuid
from decimal import Decimal

from sqlalchemy.orm import sessionmaker

from app.schemas.user import UserCreate
from app.services import accounts as account_service
from app.services import users as user_service
from app.services.transactions import create_deposit, create_withdrawal
from app.utils.exceptions import InsufficientFundsError


def test_concurrent_withdrawals_never_overdraw_account(engine):
    """
    Test to ensure that concurrent withdrawals from the same account do not result in an overdrawn balance.
    """
    SessionLocal = sessionmaker(bind=engine)

    
    setup_session = SessionLocal()
    suffix = uuid.uuid4().hex[:11]  
    user = user_service.create_user(
        setup_session,
        UserCreate(
            name="Usuario Concorrencia",
            document=suffix,
            email=f"concorrencia_{suffix}@teste.com",
            password="senha1234",
        ),
    )
    account = account_service.create_account(setup_session, user.id, "current")
    create_deposit(setup_session, account.id, Decimal("100.00"), f"seed-{suffix}")
    account_id = account.id
    setup_session.close()


    barrier = threading.Barrier(2) #SINCRONIZAÇÃO
    results: dict[str, object] = {}

    def attempt_withdrawal(thread_name: str, idempotency_key: str):
        session = SessionLocal()  # CONEXÃO PRÓPRIA
        try:
            barrier.wait()
            create_withdrawal(session, account_id, Decimal("80.00"), idempotency_key)
            results[thread_name] = "success"
        except InsufficientFundsError:
            results[thread_name] = "rejected"
        except Exception as e:  # captura qualquer outro erro inesperado
            results[thread_name] = f"unexpected_error: {e!r}"
        finally:
            session.close()

    thread_a = threading.Thread(
        target=attempt_withdrawal, args=("thread_a", f"withdraw-a-{suffix}")
    )
    thread_b = threading.Thread(
        target=attempt_withdrawal, args=("thread_b", f"withdraw-b-{suffix}")
    )

    thread_a.start()
    thread_b.start()
    thread_a.join()
    thread_b.join()

    # --- Verificação ----------------------------------------------------
    outcomes = list(results.values())
    assert "unexpected_error" not in str(outcomes), f"Erro inesperado: {outcomes}"

    successes = outcomes.count("success")
    rejections = outcomes.count("rejected")

    assert successes == 1, f"Esperado exatamente 1 sucesso, obteve {successes} ({outcomes})"
    assert rejections == 1, f"Esperado exatamente 1 rejeição, obteve {rejections} ({outcomes})"

    final_balance = account_service.get_balance(setup_session := SessionLocal(), account_id)
    setup_session.close()

    assert final_balance == Decimal("20.00"), (
        f"Saldo final deveria ser 20.00 (100 - 80), veio {final_balance}. "
        "Se vier negativo ou diferente, o lock NÃO está protegendo a concorrência."
    )
