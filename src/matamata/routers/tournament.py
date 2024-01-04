from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from matamata.database import get_session
from matamata.models import Tournament
from matamata.schemas import TournamentPayloadSchema, TournamentSchema


router = APIRouter(prefix='/tournament', tags=['tournament'])


@router.post('/', response_model=TournamentSchema, status_code=201)
def create_tournament(
    tournament_payload: TournamentPayloadSchema,
    session: Session = Depends(get_session),
):
    tournament = Tournament(
        label=tournament_payload.label,
    )
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    return tournament
