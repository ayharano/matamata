from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload

from matamata.database import get_session
from matamata.models import Match, TournamentCompetitor
from matamata.schemas import (
    MatchSchema,
    WinnerPayloadSchema,
)


router = APIRouter(prefix='/match', tags=['match'])


@router.post('/{match_uuid}', response_model=MatchSchema, status_code=200)
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
            joinedload(Match.competitorA),
            joinedload(Match.competitorB),
        )
    )

    if not match:
        raise HTTPException(status_code=404, detail='Target Match does not exist')

    if match.resultRegistration:
        raise HTTPException(
            status_code=409,
            detail='Target Match has already registered its result',
        )

    is_startingRound = match.round == match.tournament.startingRound

    competitorA_uuid = None
    competitorB_uuid = None
    competitor_uuid_set = set()
    map_uuid_to_competitor = {}
    if match.competitorA:
        competitorA_uuid = match.competitorA.uuid
        competitor_uuid_set.add(competitorA_uuid)
        map_uuid_to_competitor[competitorA_uuid] = match.competitorA
    if match.competitorB:
        competitorB_uuid = match.competitorB.uuid
        competitor_uuid_set.add(competitorB_uuid)
        map_uuid_to_competitor[competitorB_uuid] = match.competitorB
    has_both_competitors = competitorA_uuid and competitorB_uuid

    if not has_both_competitors:
        if is_startingRound:
            raise HTTPException(
                status_code=409,
                detail=(
                    'Target Match should have elected an automatic winner'
                ),
            )
        else:
            raise HTTPException(
                status_code=422,
                detail=(
                    'Target Match is not ready to register a result due to'
                    ' registered previous Matches but missing Competitor'
                ),
            )

    winner_uuid = winner_payload.winner_uuid
    if winner_uuid not in competitor_uuid_set:
        raise HTTPException(
            status_code=409,
            detail='Target Competitor is not a target Match competitor',
        )

    competitor_uuid_set.remove(winner_uuid)
    loser_uuid = competitor_uuid_set.pop()
    winner = map_uuid_to_competitor[winner_uuid]
    loser = map_uuid_to_competitor[loser_uuid]

    match.winner = winner
    match.loser = loser
    match.resultRegistration = datetime.utcnow()
    session.add(match)
    session.commit()
    session.refresh(match)

    next_match = session.scalar(
        select(Match)
        .where(
            Match.tournament_id == match.tournament_id,
            Match.round == (match.round - 1),
            Match.position == (match.position // 2),
        )
    )

    if not next_match:
        # Set both competitors' next match as None
        update_next_to_null = (
            update(TournamentCompetitor)
            .where(
                TournamentCompetitor.tournament_id == match.tournament_id,
                TournamentCompetitor.competitor_id.in_([winner.id, loser.id]),
            )
            .values(
                next_match_id=None,
            )
        )
        session.execute(update_next_to_null)

        return match

    # Set next match data
    competitor_key = 'competitorA_id' if match.position % 2 == 0 else 'competitorB_id'
    setattr(next_match, competitor_key, winner.id)
    session.add(next_match)
    update_winner_next = (
        update(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == match.tournament_id,
            TournamentCompetitor.competitor_id == winner.id,
        )
        .values(
            next_match_id=next_match.id,
        )
    )
    session.execute(update_winner_next)

    loser_next_match_id = None
    if match.round == 1:
        # When registering semifinal match, we need to update third place match also
        third_place_match = session.scalar(
            select(Match)
            .where(
                Match.tournament_id == match.tournament_id,
                Match.round == 0,
                Match.position == 1,
            )
        )
        setattr(third_place_match, competitor_key, loser.id)

        # Corner case: if it is a semifinal for 3 competitors,
        # the loser is automatically the winner of the third place match
        if match.tournament.numberCompetitors == 3:
            third_place_match.winner_id = loser.id
            third_place_match.resultRegistration = datetime.utcnow()
        else:
            loser_next_match_id = third_place_match.id
        session.add(third_place_match)

    update_loser_next = (
        update(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == match.tournament_id,
            TournamentCompetitor.competitor_id == loser.id,
        )
        .values(
            next_match_id=loser_next_match_id,
        )
    )
    session.execute(update_loser_next)

    session.commit()

    return match
