from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from matamata.database import get_session
from matamata.models import Match
from matamata.schemas import MatchSchema, WinnerPayloadSchema
from matamata.services import register_match_result as register_match_result_service
from matamata.services.exceptions import (
    MatchAlreadyRegisteredResult,
    MatchMissingCompetitorFromPreviousMatch,
    MatchShouldHaveAutomaticWinner,
    MatchTargetCompetitorIsNotMatchCompetitor,
)

router = APIRouter(prefix="/match", tags=["match"])


@router.get("/{match_uuid}", response_model=MatchSchema, status_code=200)
def get_match_detail(
    match_uuid: UUID,
    session: Session = Depends(get_session),
):
    match = session.scalar(
        select(Match)
        .where(Match.uuid == match_uuid)
        .options(
            joinedload(Match.tournament),
            joinedload(Match.competitor_a),
            joinedload(Match.competitor_b),
        )
    )

    if not match:
        raise HTTPException(status_code=404, detail="Target Match does not exist")

    return match


@router.post("/{match_uuid}", response_model=MatchSchema, status_code=200)
def register_match_result(
    match_uuid: UUID,
    winner_payload: WinnerPayloadSchema,
    session: Session = Depends(get_session),
):
    match = session.scalar(
        select(Match)
        .where(Match.uuid == match_uuid)
        .options(
            joinedload(Match.tournament),
            joinedload(Match.competitor_a),
            joinedload(Match.competitor_b),
        )
    )

    if not match:
        raise HTTPException(status_code=404, detail="Target Match does not exist")

    try:
        match = register_match_result_service(
            match_with_tournament_and_competitors=match,
            winner_uuid=winner_payload.winner_uuid,
            session=session,
        )
    except MatchAlreadyRegisteredResult:
        raise HTTPException(
            status_code=409,
            detail="Target Match has already registered its result",
        )
    except MatchShouldHaveAutomaticWinner:
        raise HTTPException(
            status_code=409,
            detail=("Target Match should have elected an automatic winner"),
        )
    except MatchMissingCompetitorFromPreviousMatch:
        raise HTTPException(
            status_code=422,
            detail=(
                "Target Match is not ready to register a result due to"
                " registered previous Matches but missing Competitor"
            ),
        )
    except MatchTargetCompetitorIsNotMatchCompetitor:
        raise HTTPException(
            status_code=409,
            detail="Target Competitor is not a target Match competitor",
        )

    return match
