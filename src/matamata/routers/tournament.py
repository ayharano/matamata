from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from matamata.database import get_session
from matamata.models import Competitor, Match, Tournament, TournamentCompetitor
from matamata.schemas import (
    TournamentCompetitorListSchema,
    TournamentCompetitorMatchesSchema,
    TournamentCompetitorPayloadSchema,
    TournamentCompetitorSchema,
    TournamentListSchema,
    TournamentMatchesSchema,
    TournamentPayloadSchema,
    TournamentResultSchema,
    TournamentSchema,
    TournamentStartSchema,
)
from matamata.services import start_tournament as start_tournament_service

router = APIRouter(prefix="/tournament", tags=["tournament"])


@router.post("/", response_model=TournamentSchema, status_code=201)
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


@router.get("/", response_model=TournamentListSchema, status_code=200)
def list_tournaments(
    session: Session = Depends(get_session),
):
    tournaments = session.scalars(select(Tournament)).all()

    data = {
        "tournaments": tournaments,
    }

    return data


@router.post(
    "/{tournament_uuid}/competitor",
    response_model=TournamentCompetitorSchema,
    status_code=201,
)
def register_competitor_in_tournament(
    tournament_uuid: UUID,
    competitor_payload: TournamentCompetitorPayloadSchema,
    session: Session = Depends(get_session),
):
    tournament = session.scalar(
        select(Tournament).where(Tournament.uuid == tournament_uuid)
    )

    if not tournament:
        raise HTTPException(status_code=404, detail="Target Tournament does not exist")

    if tournament.matches_creation:
        raise HTTPException(
            status_code=409,
            detail="Target Tournament has already created its matches and does not allow new Competitors registration",
        )

    competitor = session.scalar(
        select(Competitor).where(Competitor.uuid == competitor_payload.competitor_uuid)
    )

    if not competitor:
        raise HTTPException(status_code=404, detail="Target Competitor does not exist")

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
            detail="Target Competitor is already registered in target Tournament",
        )

    session.refresh(tournament_competitor)

    return tournament_competitor


@router.get(
    "/{tournament_uuid}/competitor",
    response_model=TournamentCompetitorListSchema,
    status_code=200,
)
def list_competitors_in_tournament(
    tournament_uuid: UUID,
    session: Session = Depends(get_session),
):
    tournament = session.scalar(
        select(Tournament).where(Tournament.uuid == tournament_uuid)
    )

    if not tournament:
        raise HTTPException(status_code=404, detail="Target Tournament does not exist")

    competitors = session.scalars(
        select(Competitor)
        .select_from(TournamentCompetitor)
        .join(TournamentCompetitor.competitor)
        .where(
            TournamentCompetitor.tournament_id == tournament.id,
        )
    ).all()

    data = {
        "tournament": tournament,
        "competitors": competitors,
    }

    return data


@router.get(
    "/{tournament_uuid}/competitor/{competitor_uuid}",
    response_model=TournamentCompetitorMatchesSchema,
    status_code=200,
)
def list_matches_for_competitor_in_tournament(
    tournament_uuid: UUID,
    competitor_uuid: UUID,
    session: Session = Depends(get_session),
):
    tournament = session.scalar(
        select(Tournament).where(Tournament.uuid == tournament_uuid)
    )

    if not tournament:
        raise HTTPException(status_code=404, detail="Target Tournament does not exist")

    competitor = session.scalar(
        select(Competitor).where(Competitor.uuid == competitor_uuid)
    )

    if not competitor:
        raise HTTPException(status_code=404, detail="Target Competitor does not exist")

    tournament_competitor = session.scalar(
        select(TournamentCompetitor).where(
            TournamentCompetitor.tournament_id == tournament.id,
            TournamentCompetitor.competitor_id == competitor.id,
        )
    )

    if not tournament_competitor:
        if tournament.matches_creation:
            raise HTTPException(
                status_code=409,
                detail="Target Competitor is not registered for started target Tournament",
            )
        else:
            raise HTTPException(
                status_code=422,
                detail="Target Competitor is not registered for unstarted target Tournament",
            )

    if not tournament.matches_creation:
        raise HTTPException(
            status_code=422,
            detail="Target Tournament has not created its matches yet",
        )

    base_match_query = (
        select(Match)
        .where(
            Match.tournament_id == tournament.id,
            (
                (Match.competitor_a_id == competitor.id)
                | (Match.competitor_b_id == competitor.id)
            ),
        )
        .order_by(
            Match.round.desc(),
            Match.position.asc(),
        )
    )

    bare_past_matches = session.scalars(
        base_match_query.where(
            Match.result_registration.is_not(None),
            Match.winner_id.is_not(None),
        )
    ).all()
    bare_upcoming_matches = session.scalars(
        base_match_query.where(
            Match.result_registration.is_(None),
            Match.winner_id.is_(None),
        )
    ).all()

    past_matches = []
    for current_match in bare_past_matches:
        current_match.currentCompetitor = competitor
        past_matches.append(current_match)

    upcoming_matches = []
    for current_match in bare_upcoming_matches:
        current_match.currentCompetitor = competitor
        upcoming_matches.append(current_match)

    data = {
        "tournament": tournament,
        "competitor": competitor,
        "matches": {
            "past": past_matches,
            "upcoming": upcoming_matches,
        },
    }

    return data


@router.post(
    "/{tournament_uuid}/start", response_model=TournamentStartSchema, status_code=201
)
def start_tournament(
    tournament_uuid: UUID,
    session: Session = Depends(get_session),
):
    tournament = session.scalar(
        select(Tournament).where(Tournament.uuid == tournament_uuid)
    )

    if not tournament:
        raise HTTPException(status_code=404, detail="Target Tournament does not exist")

    if tournament.matches_creation:
        raise HTTPException(
            status_code=409,
            detail="Target Tournament has already created its matches",
        )

    # Reload Tournament this time to load eagerly its Competitors
    tournament = session.scalar(
        select(Tournament)
        .where(Tournament.uuid == tournament_uuid)
        .options(
            joinedload(Tournament.competitor_associations).subqueryload(
                TournamentCompetitor.competitor
            )
        )
    )

    if not tournament.competitor_associations:
        raise HTTPException(
            status_code=422,
            detail="Target Tournament does not have one Competitor registered yet",
        )

    matches = start_tournament_service(
        tournament=tournament,
        competitor_associations=tournament.competitor_associations,
        session=session,
    )

    data = {
        "tournament": tournament,
        "competitors": tournament.competitors,
        "matches": matches,
    }

    return data


@router.get(
    "/{tournament_uuid}/match", response_model=TournamentMatchesSchema, status_code=200
)
def list_tournament_matches(
    tournament_uuid: UUID,
    session: Session = Depends(get_session),
):
    tournament = session.scalar(
        select(Tournament).where(Tournament.uuid == tournament_uuid)
    )

    if not tournament:
        raise HTTPException(status_code=404, detail="Target Tournament does not exist")

    if not tournament.matches_creation:
        raise HTTPException(
            status_code=422,
            detail="Target Tournament has not created its matches yet",
        )

    base_match_query = (
        select(Match)
        .where(Match.tournament_id == tournament.id)
        .order_by(
            Match.round.desc(),
            Match.position.asc(),
        )
    )

    past_matches_query = base_match_query.where(
        Match.result_registration.is_not(None),
        Match.winner_id.is_not(None),
    )
    upcoming_matches_query = base_match_query.where(
        Match.result_registration.is_(None),
        Match.winner_id.is_(None),
    )

    past_matches = session.scalars(past_matches_query).all()
    upcoming_matches = session.scalars(upcoming_matches_query).all()

    data = {
        "tournament": tournament,
        "past": past_matches,
        "upcoming": upcoming_matches,
    }

    return data


@router.get(
    "/{tournament_uuid}/result", response_model=TournamentResultSchema, status_code=200
)
def get_tournament_top4(
    tournament_uuid: UUID,
    session: Session = Depends(get_session),
):
    tournament = session.scalar(
        select(Tournament).where(Tournament.uuid == tournament_uuid)
    )

    if not tournament:
        raise HTTPException(status_code=404, detail="Target Tournament does not exist")

    if not tournament.matches_creation:
        raise HTTPException(
            status_code=422,
            detail="Target Tournament has not created its matches yet",
        )

    round0_matches = session.scalars(
        select(Match)
        .where(
            Match.tournament_id == tournament.id,
            Match.round == 0,
            Match.result_registration.is_not(None),
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
    if tournament.number_competitors <= 2:
        if len(round0_matches) != 1:
            raise HTTPException(
                status_code=422,
                detail="Target Tournament is not ready to display the top 4 competitors",
            )
    else:
        if len(round0_matches) != 2:
            raise HTTPException(
                status_code=422,
                detail="Target Tournament is not ready to display the top 4 competitors",
            )
        top4[2] = round0_matches[1].winner
        top4[3] = round0_matches[1].loser

    top4[0] = round0_matches[0].winner
    top4[1] = round0_matches[0].loser

    data = {
        "tournament": tournament,
        "top4": top4,
    }

    return data
