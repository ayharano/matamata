from datetime import datetime

import pytest

from matamata.models import TournamentCompetitor
from matamata.services import start_tournament


def test_start_tournament_for_no_competitor(session, tournament):
    with pytest.raises(
        ValueError,
        match="No competitors to start tournament",
    ):
        start_tournament(
            tournament=tournament,
            competitor_associations=[],
            session=session,
        )


def test_start_tournament_for_a_single_competitor(session, tournament, competitor):
    tournament_competior = TournamentCompetitor(
        tournament=tournament,
        competitor=competitor,
    )
    session.add(tournament_competior)
    session.commit()

    before_start_tournament = datetime.utcnow()
    matches = start_tournament(
        tournament=tournament,
        competitor_associations=[tournament_competior],
        session=session,
    )
    session.refresh(tournament)
    session.refresh(tournament_competior)

    assert tournament.matches_creation is not None
    assert tournament.matches_creation > before_start_tournament
    assert tournament.starting_round == 0
    assert tournament.number_competitors == 1
    assert len(matches) == 1
    match = matches[0]
    assert match.round == 0
    assert match.position == 0
    assert match.competitor_a_id is not None
    assert match.competitor_b_id is None
    assert match.result_registration is not None
    assert match.competitor_a_id == match.winner_id
    assert match.loser_id is None
    assert tournament_competior.next_match_id is None


def test_start_tournament_for_two_competitors(
    session, tournament, competitor1, competitor2
):
    competitor_set = {competitor1, competitor2}
    tournament_competitor_dict = {}
    for competitor_ in competitor_set:
        tournament_competitor = TournamentCompetitor(
            tournament=tournament,
            competitor=competitor_,
        )
        tournament_competitor_dict[competitor_.id] = tournament_competitor
        session.add(tournament_competitor)
    session.commit()

    before_start_tournament = datetime.utcnow()
    matches = start_tournament(
        tournament=tournament,
        competitor_associations=tournament_competitor_dict.values(),
        session=session,
    )
    session.refresh(tournament)
    for tournament_competitor in tournament_competitor_dict.values():
        session.refresh(tournament_competitor)

    assert tournament.matches_creation is not None
    assert tournament.matches_creation > before_start_tournament
    assert tournament.starting_round == 0
    assert tournament.number_competitors == 2
    assert len(matches) == 1
    match = matches[0]
    assert match.round == 0
    assert match.position == 0
    assert match.competitor_a_id in {competitor1.id, competitor2.id}
    assert {match.competitor_b_id} == {competitor1.id, competitor2.id}.difference(
        {match.competitor_a_id}
    )
    assert match.result_registration is None
    assert match.winner_id is None
    assert match.loser_id is None
    assert (
        tournament_competitor_dict[matches[0].competitor_a_id].next_match_id
        == matches[0].id
    )
    assert (
        tournament_competitor_dict[matches[0].competitor_b_id].next_match_id
        == matches[0].id
    )


def test_start_tournament_for_three_competitors(
    session, tournament, competitor1, competitor2, competitor3
):
    competitor_set = {competitor1, competitor2, competitor3}
    tournament_competitor_dict = {}
    for competitor_ in competitor_set:
        tournament_competitor = TournamentCompetitor(
            tournament=tournament,
            competitor=competitor_,
        )
        tournament_competitor_dict[competitor_.id] = tournament_competitor
        session.add(tournament_competitor)
    session.commit()

    before_start_tournament = datetime.utcnow()
    matches = start_tournament(
        tournament=tournament,
        competitor_associations=tournament_competitor_dict.values(),
        session=session,
    )
    session.refresh(tournament)
    for tournament_competitor in tournament_competitor_dict.values():
        session.refresh(tournament_competitor)

    assert tournament.matches_creation is not None
    assert tournament.matches_creation > before_start_tournament
    assert tournament.starting_round == 1
    assert tournament.number_competitors == 3
    assert len(matches) == 4

    # round 1 position 0 has both competitors
    assert matches[0].round == 1
    assert matches[0].position == 0
    remaining_competitor_id_set = {competitor1.id, competitor2.id, competitor3.id}
    assert matches[0].competitor_a_id in remaining_competitor_id_set
    remaining_competitor_id_set.difference_update({matches[0].competitor_a_id})
    assert matches[0].competitor_b_id in remaining_competitor_id_set
    remaining_competitor_id_set.difference_update({matches[0].competitor_b_id})
    assert matches[0].result_registration is None
    assert matches[0].winner_id is None
    assert matches[0].loser_id is None
    assert (
        tournament_competitor_dict[matches[0].competitor_a_id].next_match_id
        == matches[0].id
    )
    assert (
        tournament_competitor_dict[matches[0].competitor_b_id].next_match_id
        == matches[0].id
    )

    # round 1 position 1 has one competitor, who will compete on the final match
    assert matches[1].round == 1
    assert matches[1].position == 1
    assert {matches[1].competitor_a_id} == remaining_competitor_id_set
    assert matches[1].competitor_b_id is None
    assert matches[1].result_registration is not None
    assert matches[1].result_registration > before_start_tournament
    assert matches[1].winner_id is matches[1].competitor_a_id
    assert matches[1].loser_id is None
    assert (
        tournament_competitor_dict[matches[1].competitor_a_id].next_match_id
        != matches[1].id
    )

    # round 0 position 0 has one competitor
    assert matches[2].round == 0
    assert matches[2].position == 0
    assert matches[2].competitor_a_id is None
    assert matches[2].competitor_b_id is matches[1].competitor_a_id
    assert matches[2].result_registration is None
    assert matches[2].winner_id is None
    assert matches[2].loser_id is None
    assert (
        tournament_competitor_dict[matches[1].competitor_a_id].next_match_id
        == matches[2].id
    )

    # round 0 position 1 has no competitor
    assert matches[3].round == 0
    assert matches[3].position == 1
    assert matches[3].competitor_a_id is None
    assert matches[3].competitor_b_id is None
    assert matches[3].result_registration is None
    assert matches[3].winner_id is None
    assert matches[3].loser_id is None


def test_start_tournament_for_four_competitors(
    session, tournament, competitor1, competitor2, competitor3, competitor4
):
    competitor_set = {competitor1, competitor2, competitor3, competitor4}
    tournament_competitor_dict = {}
    for competitor_ in competitor_set:
        tournament_competitor = TournamentCompetitor(
            tournament=tournament,
            competitor=competitor_,
        )
        tournament_competitor_dict[competitor_.id] = tournament_competitor
        session.add(tournament_competitor)
    session.commit()

    before_start_tournament = datetime.utcnow()
    matches = start_tournament(
        tournament=tournament,
        competitor_associations=tournament_competitor_dict.values(),
        session=session,
    )
    session.refresh(tournament)
    for tournament_competitor in tournament_competitor_dict.values():
        session.refresh(tournament_competitor)

    assert tournament.matches_creation is not None
    assert tournament.matches_creation > before_start_tournament
    assert tournament.starting_round == 1
    assert tournament.number_competitors == 4
    assert len(matches) == 4

    # round 1 position 0 has both competitors
    assert matches[0].round == 1
    assert matches[0].position == 0
    remaining_competitor_id_set = {
        competitor1.id,
        competitor2.id,
        competitor3.id,
        competitor4.id,
    }
    assert matches[0].competitor_a_id in remaining_competitor_id_set
    remaining_competitor_id_set.difference_update({matches[0].competitor_a_id})
    assert matches[0].competitor_b_id in remaining_competitor_id_set
    remaining_competitor_id_set.difference_update({matches[0].competitor_b_id})
    assert matches[0].result_registration is None
    assert matches[0].winner_id is None
    assert matches[0].loser_id is None
    assert (
        tournament_competitor_dict[matches[0].competitor_a_id].next_match_id
        == matches[0].id
    )
    assert (
        tournament_competitor_dict[matches[0].competitor_b_id].next_match_id
        == matches[0].id
    )

    # round 1 position 1 has both competitors
    assert matches[1].round == 1
    assert matches[1].position == 1
    assert matches[1].competitor_a_id in remaining_competitor_id_set
    remaining_competitor_id_set.difference_update({matches[1].competitor_a_id})
    assert {matches[1].competitor_b_id} == remaining_competitor_id_set
    assert matches[1].result_registration is None
    assert matches[1].winner_id is None
    assert matches[1].loser_id is None
    assert (
        tournament_competitor_dict[matches[1].competitor_a_id].next_match_id
        == matches[1].id
    )
    assert (
        tournament_competitor_dict[matches[1].competitor_b_id].next_match_id
        == matches[1].id
    )

    # round 0 position 0 has no competitor
    assert matches[2].round == 0
    assert matches[2].position == 0
    assert matches[2].competitor_a_id is None
    assert matches[2].competitor_b_id is None
    assert matches[2].result_registration is None
    assert matches[2].winner_id is None
    assert matches[2].loser_id is None

    # round 0 position 1 has no competitor
    assert matches[3].round == 0
    assert matches[3].position == 1
    assert matches[3].competitor_a_id is None
    assert matches[3].competitor_b_id is None
    assert matches[3].result_registration is None
    assert matches[3].winner_id is None
    assert matches[3].loser_id is None


def test_start_tournament_for_five_competitors(
    session, tournament, competitor1, competitor2, competitor3, competitor4, competitor5
):
    competitor_set = {competitor1, competitor2, competitor3, competitor4, competitor5}
    tournament_competitor_dict = {}
    for competitor_ in competitor_set:
        tournament_competitor = TournamentCompetitor(
            tournament=tournament,
            competitor=competitor_,
        )
        tournament_competitor_dict[competitor_.id] = tournament_competitor
        session.add(tournament_competitor)
    session.commit()

    before_start_tournament = datetime.utcnow()
    matches = start_tournament(
        tournament=tournament,
        competitor_associations=tournament_competitor_dict.values(),
        session=session,
    )
    session.refresh(tournament)
    for tournament_competitor in tournament_competitor_dict.values():
        session.refresh(tournament_competitor)

    assert tournament.matches_creation is not None
    assert tournament.matches_creation > before_start_tournament
    assert tournament.starting_round == 2
    assert tournament.number_competitors == 5
    assert len(matches) == 8

    # round 2 position 0 has both competitors
    assert matches[0].round == 2
    assert matches[0].position == 0
    remaining_competitor_id_set = {
        competitor1.id,
        competitor2.id,
        competitor3.id,
        competitor4.id,
        competitor5.id,
    }
    assert matches[0].competitor_a_id in remaining_competitor_id_set
    remaining_competitor_id_set.difference_update({matches[0].competitor_a_id})
    assert matches[0].competitor_b_id in remaining_competitor_id_set
    remaining_competitor_id_set.difference_update({matches[0].competitor_b_id})
    assert matches[0].result_registration is None
    assert matches[0].winner_id is None
    assert matches[0].loser_id is None
    assert (
        tournament_competitor_dict[matches[0].competitor_a_id].next_match_id
        == matches[0].id
    )
    assert (
        tournament_competitor_dict[matches[0].competitor_b_id].next_match_id
        == matches[0].id
    )

    # round 2 position 1 has one competitor, who will compete on a semifinal match
    assert matches[1].round == 2
    assert matches[1].position == 1
    assert matches[1].competitor_a_id in remaining_competitor_id_set
    remaining_competitor_id_set.difference_update({matches[1].competitor_a_id})
    assert matches[1].competitor_b_id is None
    assert matches[1].result_registration is not None
    assert matches[1].result_registration > before_start_tournament
    assert matches[1].winner_id == matches[1].competitor_a_id
    assert matches[1].loser_id is None
    assert (
        tournament_competitor_dict[matches[1].competitor_a_id].next_match_id
        != matches[1].id
    )

    # round 2 position 2 has one competitor, who will compete on a semifinal match
    assert matches[2].round == 2
    assert matches[2].position == 2
    assert matches[2].competitor_a_id in remaining_competitor_id_set
    remaining_competitor_id_set.difference_update({matches[2].competitor_a_id})
    assert matches[2].competitor_b_id is None
    assert matches[2].result_registration is not None
    assert matches[2].result_registration > before_start_tournament
    assert matches[2].winner_id == matches[2].competitor_a_id
    assert matches[2].loser_id is None
    assert (
        tournament_competitor_dict[matches[2].competitor_a_id].next_match_id
        != matches[2].id
    )

    # round 2 position 3 has one competitor, who will compete on a semifinal match
    assert matches[3].round == 2
    assert matches[3].position == 3
    assert {matches[3].competitor_a_id} == remaining_competitor_id_set
    assert matches[3].competitor_b_id is None
    assert matches[3].result_registration is not None
    assert matches[3].result_registration > before_start_tournament
    assert matches[3].winner_id == matches[3].competitor_a_id
    assert matches[3].loser_id is None
    assert (
        tournament_competitor_dict[matches[3].competitor_a_id].next_match_id
        != matches[3].id
    )

    # round 1 position 0 has one competitor
    assert matches[4].round == 1
    assert matches[4].position == 0
    assert matches[4].competitor_a_id is None
    assert matches[4].competitor_b_id == matches[1].winner_id
    assert matches[4].result_registration is None
    assert matches[4].winner_id is None
    assert matches[4].loser_id is None
    assert (
        tournament_competitor_dict[matches[4].competitor_b_id].next_match_id
        == matches[4].id
    )

    # round 1 position 1 has two competitors
    assert matches[5].round == 1
    assert matches[5].position == 1
    assert matches[5].competitor_a_id == matches[2].winner_id
    assert matches[5].competitor_b_id == matches[3].winner_id
    assert matches[5].result_registration is None
    assert matches[5].winner_id is None
    assert matches[5].loser_id is None
    assert (
        tournament_competitor_dict[matches[5].competitor_a_id].next_match_id
        == matches[5].id
    )
    assert (
        tournament_competitor_dict[matches[5].competitor_b_id].next_match_id
        == matches[5].id
    )

    # round 0 position 0 has no competitor
    assert matches[6].round == 0
    assert matches[6].position == 0
    assert matches[6].competitor_a_id is None
    assert matches[6].competitor_b_id is None
    assert matches[6].result_registration is None
    assert matches[6].winner_id is None
    assert matches[6].loser_id is None

    # round 0 position 1 has no competitor
    assert matches[7].round == 0
    assert matches[7].position == 1
    assert matches[7].competitor_a_id is None
    assert matches[7].competitor_b_id is None
    assert matches[7].result_registration is None
    assert matches[7].winner_id is None
    assert matches[7].loser_id is None
