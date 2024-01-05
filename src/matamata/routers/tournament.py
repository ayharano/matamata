from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from matamata.database import get_session
from matamata.models import Competitor, Match, Tournament, TournamentCompetitor
from matamata.schemas import (
    TournamentCompetitorPayloadSchema,
    TournamentCompetitorSchema,
    TournamentMatchesSchema,
    TournamentPayloadSchema,
    TournamentResultSchema,
    TournamentSchema,
    TournamentStartSchema,
)
from matamata.services import start_tournament as start_tournament_service


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


@router.post('/{tournament_uuid}/start', response_model=TournamentStartSchema, status_code=201)
def start_tournament(
    tournament_uuid: UUID,
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
            detail='Target Tournament has already created its matches',
        )

    # Reload Tournament this time to load eagerly its Competitors
    tournament = session.scalar(
        select(Tournament)
        .where(Tournament.uuid == tournament_uuid)
        .options(
            joinedload(Tournament.competitor_associations)
            .subqueryload(TournamentCompetitor.competitor)
        )
    )

    if not tournament.competitor_associations:
        raise HTTPException(
            status_code=422,
            detail='Target Tournament does not have one Competitor registered yet',
        )

    matches = start_tournament_service(
        tournament=tournament,
        competitor_associations=tournament.competitor_associations,
        session=session,
    )

    data = {
        'tournament': tournament,
        'competitors': tournament.competitors,
        'matches': matches,
    }

    return data


@router.get('/{tournament_uuid}/match', response_model=TournamentMatchesSchema, status_code=200)
def list_tournament_matches(
    tournament_uuid: UUID,
    session: Session = Depends(get_session),
):
    tournament = session.scalar(
        select(Tournament)
        .where(Tournament.uuid == tournament_uuid)
    )

    if not tournament:
        raise HTTPException(status_code=404, detail='Target Tournament does not exist')

    if not tournament.matchesCreation:
        raise HTTPException(
            status_code=422,
            detail='Target Tournament has not created its matches yet',
        )

    base_match_query = (
        select(Match)
        .where(Match.tournament_id == tournament.id)
        .order_by(
            Match.round.desc(),
            Match.position.asc(),
        )
    )

    past_matches_query = (
        base_match_query
        .where(
            Match.resultRegistration.is_not(None),
            Match.winner_id.is_not(None),
        )
    )
    upcoming_matches_query = (
        base_match_query
        .where(
            Match.resultRegistration.is_(None),
            Match.winner_id.is_(None),
        )
    )

    past_matches = session.scalars(past_matches_query).all()
    upcoming_matches = session.scalars(upcoming_matches_query).all()

    data = {
        'tournament': tournament,
        'past': past_matches,
        'upcoming': upcoming_matches,
    }

    return data


@router.get('/{tournament_uuid}/result', response_model=TournamentResultSchema, status_code=200)
def get_tournament_top4(
    tournament_uuid: UUID,
    session: Session = Depends(get_session),
):
    tournament = session.scalar(
        select(Tournament)
        .where(Tournament.uuid == tournament_uuid)
    )

    if not tournament:
        raise HTTPException(status_code=404, detail='Target Tournament does not exist')

    if not tournament.matchesCreation:
        raise HTTPException(
            status_code=422,
            detail='Target Tournament has not created its matches yet',
        )

    round0_matches = session.scalars(
        select(Match)
        .where(
            Match.tournament_id == tournament.id,
            Match.round == 0,
            Match.resultRegistration.is_not(None),
        )
        .options(
            joinedload(Match.winner),
            joinedload(Match.loser),
        )
        .order_by(
            Match.position.asc(),
        )
    ).all()

    top4 = [None, None, None, None]
    if tournament.numberCompetitors <= 2:
        if len(round0_matches) != 1:
            raise HTTPException(
                status_code=422,
                detail='Target Tournament is not ready to display the top 4 competitors',
            )
    else:
        if len(round0_matches) != 2:
            raise HTTPException(
                status_code=422,
                detail='Target Tournament is not ready to display the top 4 competitors',
            )
        top4[2] = round0_matches[1].winner
        top4[3] = round0_matches[1].loser

    top4[0] = round0_matches[0].winner
    top4[1] = round0_matches[0].loser

    data = {
        'tournament': tournament,
        'top4': top4,
    }

    return data
