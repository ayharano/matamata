import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from matamata.database import get_session
from matamata.main import app
from matamata.models import Base
from matamata.settings import settings


@pytest.fixture
def session():
    engine_kwargs = {}
    if settings.DATABASE_URL:
        engine_args = [settings.DATABASE_URL]
    else:
        from sqlalchemy.pool import StaticPool

        # Defaulting to in-memory SQLite
        engine_args = ['sqlite:///:memory:']
        engine_kwargs = {
            'connect_args': {'check_same_thread': False},
            'poolclass': StaticPool,
        }

    engine = create_engine(*engine_args, **engine_kwargs)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    yield Session()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()
