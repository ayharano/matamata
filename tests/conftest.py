import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from matamata.database import get_session
from matamata.main import app
from matamata.models import Base
from matamata.settings import settings
from tests.models.factories import CompetitorFactory, TournamentFactory


@pytest.fixture
def session():
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    with Session() as session:
        yield session
        session.rollback()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def competitor(session):
    competitor = CompetitorFactory()
    session.add(competitor)
    session.commit()
    session.refresh(competitor)

    return competitor


competitor1 = competitor
competitor2 = competitor
competitor3 = competitor
competitor4 = competitor
competitor5 = competitor


@pytest.fixture
def tournament(session):
    tournament = TournamentFactory()
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    return tournament


tournament1 = tournament
tournament2 = tournament
tournament3 = tournament
