import random
from collections.abc import Iterable, Sized
from datetime import datetime
from math import floor, log2

from fastapi import Depends
from sqlalchemy.orm import Session

from matamata.database import get_session
from matamata.models import Match, Tournament, TournamentCompetitor, Competitor


def calculate_tournament_parameters(competitors: Sized) -> tuple[int, int, int]:
    # We calculate again to avoid wrong parametrization
    number_of_competitors = len(competitors)
    if number_of_competitors == 1:
        starting_round = 0
        number_of_entry_matches = 1
    else:
        starting_round = int(floor(log2(number_of_competitors - 1)))
        number_of_entry_matches = 2 ** starting_round

    return number_of_competitors, starting_round, number_of_entry_matches


def calculate_match_index(*, starting_round, match_round, match_position):
    if match_round > starting_round:
        raise ValueError('invalid round values combination')

    if match_position >= 2**match_round:
        raise ValueError('invalid round/position values combination')

    offset = 0
    for current_round in range(starting_round, match_round, -1):
        offset += 2**current_round
    offset += match_position

    return offset


def process_automatic_winning(
    *,
    match_data: list[dict],
    map_competitor_next_match_index: dict[Competitor, int | None],
):
    (
        number_of_competitors,
        starting_round,
        number_of_entry_matches,
    ) = calculate_tournament_parameters(
        map_competitor_next_match_index
    )

    if number_of_competitors // 2 == number_of_entry_matches:
        # No automatic winning
        return

    for match_index in range(number_of_entry_matches):
        current_match = match_data[match_index]
        if 'competitorB' in current_match:
            continue
        # automatic winning found
        competitor = current_match['competitorA']
        current_match |= {
            'resultRegistration': datetime.utcnow(),
            'winner': competitor,
        }

        # need to set competitor as next match competitor
        if starting_round == 0:
            # corner case: single competitor in the tournament
            map_competitor_next_match_index[competitor] = None
            continue

        # calculate next match index
        next_match_round = starting_round - 1
        next_match_position, next_match_competitor_index = divmod(match_index, 2)
        next_match_index_in_match_data = calculate_match_index(
            starting_round=starting_round,
            match_round=next_match_round,
            match_position=next_match_position,
        )

        next_match_data = match_data[next_match_index_in_match_data]
        next_match_key_name = 'competitorA' if next_match_competitor_index == 0 else 'competitorB'
        next_match_data[next_match_key_name] = competitor
        map_competitor_next_match_index[competitor] = next_match_index_in_match_data


def prepare_match_data_as_list_of_dict(
    *,
    tournament: Tournament,
    starting_round: int,
    number_of_competitors: int,
) -> list[dict]:
    # Preparing all matches backbone
    # We populate entry matches, then intermediate matches and final and third place matches last
    match_data = [
        {
            'tournament_id': tournament.id,
            'round': round_,
            'position': position,
        }
        for round_ in range(starting_round, -1, -1)
        for position in range(2**round_)
    ]

    if number_of_competitors > 2:
        # The only match that doesn't follow the previous rule is the third place match
        match_data.append({'round': 0, 'position': 1})

    return match_data


def random_sequence_of_competitors(
    competitors: Iterable[Competitor],
) -> list[Competitor]:
    shuffled_competitors = list(competitors)
    random.shuffle(shuffled_competitors)

    return shuffled_competitors


def inline_random_pair_of_entry_match_competitors(
    *,
    competitors: Iterable[Competitor],
    number_of_entry_matches: int,
    match_data: list[dict],
    map_competitor_next_match_index: dict[Competitor, int | None],
):
    shuffled_competitors = random_sequence_of_competitors(
        competitors,
    )

    for index, competitor in enumerate(shuffled_competitors):
        competitor_index, match_index = divmod(index, number_of_entry_matches)

        key_name = 'competitorA' if competitor_index == 0 else 'competitorB'
        match_data[match_index][key_name] = competitor
        map_competitor_next_match_index[competitor] = match_index


def insert_and_refresh_match_data_as_match_instances(
    *,
    tournament: Tournament,
    match_data: list[dict],
    number_of_competitors: int,
    starting_round: int,
    session: Session,
) -> list[Match]:
    new_matches = [
        Match(**current_match_data)
        for current_match_data in match_data
    ]
    tournament.matches.extend(new_matches)
    tournament.matchesCreation = datetime.utcnow()
    tournament.numberCompetitors = number_of_competitors
    tournament.startingRound = starting_round
    session.add(tournament)
    session.commit()
    for match_ in new_matches:
        session.refresh(match_)
    return new_matches


def adjust_next_match_references(
    *,
    map_competitor_association: dict[Competitor, TournamentCompetitor],
    map_competitor_next_match_index: dict[Competitor, int | None],
    new_matches: list[Match],
    session: Session,
):
    for competitor, next_match_index in map_competitor_next_match_index.items():
        association = map_competitor_association[competitor]
        if next_match_index is None:
            association.next_match_id = None
        else:
            association.next_match_id = new_matches[next_match_index].id
        session.add(association)

    session.commit()


def start_tournament(
    *,
    tournament: Tournament,
    competitor_associations: list[TournamentCompetitor],
    session: Session = Depends(get_session),
):
    if not competitor_associations:
        raise ValueError("No competitors to start tournament")

    map_competitor_association = {
        association.competitor: association
        for association in competitor_associations
    }
    map_competitor_next_match_index: dict[Competitor, int | None] = {}

    (
        number_of_competitors,
        starting_round,
        number_of_entry_matches,
    ) = calculate_tournament_parameters(
        competitor_associations,
    )

    match_data = prepare_match_data_as_list_of_dict(
        tournament=tournament,
        starting_round=starting_round,
        number_of_competitors=number_of_competitors,
    )
    
    inline_random_pair_of_entry_match_competitors(
        competitors=map_competitor_association,
        number_of_entry_matches=number_of_entry_matches,
        match_data=match_data,
        map_competitor_next_match_index=map_competitor_next_match_index,
    )

    # We need to process automatic winning before the bulk insert
    process_automatic_winning(
        match_data=match_data,
        map_competitor_next_match_index=map_competitor_next_match_index,
    )

    # Batch insert Match instances
    new_matches = insert_and_refresh_match_data_as_match_instances(
        tournament=tournament,
        match_data=match_data,
        number_of_competitors=number_of_competitors,
        starting_round=starting_round,
        session=session,
    )

    # Adjust next matches
    adjust_next_match_references(
        map_competitor_association=map_competitor_association,
        map_competitor_next_match_index=map_competitor_next_match_index,
        new_matches=new_matches,
        session=session,
    )

    return new_matches
