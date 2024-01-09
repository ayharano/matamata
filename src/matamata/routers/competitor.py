from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from matamata.database import get_session
from matamata.models import Competitor, Tournament, TournamentCompetitor
from matamata.schemas import (
    CompetitorDetailSchema,
    CompetitorListSchema,
    CompetitorPayloadSchema,
    CompetitorSchema,
)


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


@router.get('/{competitor_uuid}', response_model=CompetitorDetailSchema, status_code=200)
def get_competitor_data(
    competitor_uuid: UUID,
    session: Session = Depends(get_session),
):
    competitor = session.scalar(
        select(Competitor)
        .where(Competitor.uuid == competitor_uuid)
    )

    if not competitor:
        raise HTTPException(status_code=404, detail='Target Competitor does not exist')

    base_tournament_query = (
        select(Tournament)
        .select_from(TournamentCompetitor)
        .join(TournamentCompetitor.tournament)
        .where(TournamentCompetitor.competitor_id == competitor.id)
    )

    past_tournaments_query = (
        base_tournament_query
        .where(
            Tournament.startingRound.is_not(None),
            TournamentCompetitor.next_match_id.is_(None),
        )
    )
    ongoing_tournaments_query = (
        base_tournament_query
        .where(
            Tournament.startingRound.is_not(None),
            TournamentCompetitor.next_match_id.is_not(None),
        )
    )
    upcoming_tournaments_query = (
        base_tournament_query
        .where(
            Tournament.startingRound.is_(None),
        )
    )

    past_tournaments = session.scalars(past_tournaments_query).all()
    ongoing_tournaments = session.scalars(ongoing_tournaments_query).all()
    upcoming_tournaments = session.scalars(upcoming_tournaments_query).all()

    data = {
        'competitor': competitor,
        'tournaments': {
            'past': past_tournaments,
            'ongoing': ongoing_tournaments,
            'upcoming': upcoming_tournaments,
        }
    }

    return data
