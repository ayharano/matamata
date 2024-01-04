from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from matamata.database import get_session
from matamata.models import Competitor, Tournament, TournamentCompetitor
from matamata.schemas import (
    TournamentCompetitorPayloadSchema,
    TournamentCompetitorSchema,
    TournamentPayloadSchema,
    TournamentSchema,
)


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


@router.post('/{tournament_uuid}/competitor', response_model=TournamentCompetitorSchema, status_code=201)
def register_competitor_in_tournament(
    tournament_uuid: UUID,
    competitor_payload: TournamentCompetitorPayloadSchema,
    session: Session = Depends(get_session),
):
    tournament = session.scalar(
        select(Tournament)
        .where(Tournament.uuid == tournament_uuid)
    )

    if not tournament:
        raise HTTPException(status_code=404, detail='Target Tournament does not exist')

    if tournament.matchesCreation:
        raise HTTPException(
            status_code=409,
            detail='Target Tournament has already created its matches and does not allow new Competitors registration',
        )

    competitor = session.scalar(
        select(Competitor)
        .where(Competitor.uuid == competitor_payload.competitor_uuid)
    )

    if not competitor:
        raise HTTPException(status_code=404, detail='Target Competitor does not exist')

    tournament_competitor = TournamentCompetitor(
        tournament=tournament,
        competitor=competitor,
    )
    session.add(tournament_competitor)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail='Target Competitor is already registered in target Tournament',
        )

    session.refresh(tournament_competitor)

    return tournament_competitor
