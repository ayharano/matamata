from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from matamata.database import get_session
from matamata.models import Competitor
from matamata.schemas import CompetitorPayloadSchema, CompetitorSchema


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
