from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from matamata.database import get_session
from matamata.models import Competitor
from matamata.schemas import CompetitorPayloadSchema, CompetitorListSchema, CompetitorSchema


router = APIRouter(prefix='/competitor', tags=['competitor'])


@router.post('/', response_model=CompetitorSchema, status_code=201)
def create_competitor(
    competitor_payload: CompetitorPayloadSchema,
    session: Session = Depends(get_session),
):
    competitor = Competitor(
        label=competitor_payload.label,
    )
    session.add(competitor)
    session.commit()
    session.refresh(competitor)

    return competitor


@router.get('/', response_model=CompetitorListSchema, status_code=200)
def list_competitors(
    session: Session = Depends(get_session),
):
    competitors = session.scalars(
        select(Competitor)
    ).all()

    data = {
        'competitors': competitors,
    }

    return data
