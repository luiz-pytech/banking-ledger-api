import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import *  

from app.services import accounts as account_service

load_dotenv()

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]


@pytest.fixture(scope="session")
def engine():
    """
    Fixture of engine for the test database. Creates all tables before tests and drops them after all tests are
    """
    test_engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture
def db(engine):
    """
    Fixture of database session.

    Here is lanced a transaction for each test, and after the test is finished,
    the transaction is rolled back, so the database is not modified by the tests.
    In final, the database are cleaned and ready for the next test.
    """
    connection = engine.connect()
    external_transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    external_transaction.rollback()
    connection.close()

@pytest.fixture
def sample_user(db):
    from app.schemas.user import UserCreate
    from app.services import users as user_service

    return user_service.create_user(
        db,
        UserCreate(
            name="Usuario Teste",
            document="11111111111",
            email="teste@teste.com",
            password="senha1234",
        ),
    )

@pytest.fixture
def sample_account(db, sample_user):

    return account_service.create_account(db, sample_user.id, "current")