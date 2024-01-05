import uuid

import pytest
from pydantic import BaseModel, ValidationError

from matamata.schemas import (
    CompetitorSchema,
    LabelSchema,
    MatchSchema,
    MatchSchemaForTournamentListing,
    TournamentAfterStartSchema,
    TournamentCompetitorPayloadSchema,
    TournamentCompetitorSchema,
    TournamentMatchesSchema,
    TournamentSchema,
    TournamentStartSchema,
    TournamentResultSchema,
    TrimmedString,
    UuidLabelSchema,
    WinnerPayloadSchema,
)


def test_trimmedstring():
    class SingleField(BaseModel):
        field: TrimmedString
    instance = SingleField(field='\r\n\t something \t\r\n')
    assert instance.field == 'something'


def test_label_schema():
    schema = LabelSchema(
        label='\t\nSouth Korea\n ',
    )
    assert schema.label == 'South Korea'


def test_labelschema_does_not_accept_whitespace_only_label_value():
    with pytest.raises(
            ValidationError,
            match='must not be empty or contain only whitespace characters',
    ):
        LabelSchema(
            label='\r\n\f\v \r\n',
        )


def test_tournament_competitor_payload_schema():
    schema = TournamentCompetitorPayloadSchema(
        competitor_uuid='01234567-89ab-cdef-0123-456789abcdef'
    )
    assert schema.competitor_uuid == uuid.UUID('01234567-89ab-cdef-0123-456789abcdef')


def test_winner_payload_schema():
    schema = WinnerPayloadSchema(
        winner_uuid='01234567-89ab-cdef-0123-456789abcdef'
    )
    assert schema.winner_uuid == uuid.UUID('01234567-89ab-cdef-0123-456789abcdef')


def test_uuid_label_schema():
    schema = UuidLabelSchema(
        uuid='01234567-89ab-cdef-0123-456789abcdef',
        label='\t\nSouth Korea\n ',
    )
    assert schema.uuid == uuid.UUID('01234567-89ab-cdef-0123-456789abcdef')
    assert schema.label == 'South Korea'


def test_tournament_schema():
    schema = TournamentSchema(
        **{
            'uuid': '03c964f8-7f5c-4224-b848-1ab6c1413c7d',
            'label': '2002 FIFA World Cup',
        }
    )
    assert schema.uuid == uuid.UUID('03c964f8-7f5c-4224-b848-1ab6c1413c7d')
    assert schema.label == '2002 FIFA World Cup'


def test_competitor_schema():
    schema = CompetitorSchema(
        **{
            'uuid': '5d1bd1d1-2679-432a-ac11-ebfebfa1bce9',
            'label': 'South Korea'
        }
    )
    assert schema.uuid == uuid.UUID('5d1bd1d1-2679-432a-ac11-ebfebfa1bce9')
    assert schema.label == 'South Korea'


def test_tournament_competitor_schema():
    schema = TournamentCompetitorSchema(
        **{
            'tournament': {
                'uuid': '03c964f8-7f5c-4224-b848-1ab6c1413c7d',
                'label': '2002 FIFA World Cup',
            },
            'competitor': {
                'uuid': '5d1bd1d1-2679-432a-ac11-ebfebfa1bce9',
                'label': 'South Korea',
            },
        }
    )
    assert isinstance(schema.tournament, TournamentSchema)
    assert isinstance(schema.competitor, CompetitorSchema)
    assert schema.tournament.uuid == uuid.UUID('03c964f8-7f5c-4224-b848-1ab6c1413c7d')
    assert schema.tournament.label == '2002 FIFA World Cup'
    assert schema.competitor.uuid == uuid.UUID('5d1bd1d1-2679-432a-ac11-ebfebfa1bce9')
    assert schema.competitor.label == 'South Korea'


def test_tournament_start_schema():
    schema = TournamentStartSchema(
        **{
            'tournament': {
                'uuid': '03c964f8-7f5c-4224-b848-1ab6c1413c7d',
                'label': '2002 FIFA World Cup',
                'startingRound': 1,
                'competitors': 4
            },
            'competitors': [
                {
                    'uuid': 'de686e37-804b-4815-a507-d5879a240af6',
                    'label': 'Germany'
                },
                {
                    'uuid': '5d1bd1d1-2679-432a-ac11-ebfebfa1bce9',
                    'label': 'South Korea'
                },
                {
                    'uuid': '7f026276-0904-4a7b-ae14-8c66b95ffc9e',
                    'label': 'Brazil'
                },
                {
                    'uuid': '15f4fe33-f317-4c4a-96e0-3b815dc481c6',
                    'label': 'Turkey'
                }
            ],
            'matches': [
                {
                    'uuid': '1e172084-ec76-4f56-bd8e-7b3c170e1221',
                    'round': 1,
                    'position': 0,
                    'competitorA': {
                        'uuid': 'de686e37-804b-4815-a507-d5879a240af6',
                        'label': 'Germany'
                    },
                    'competitorB': {
                        'uuid': '5d1bd1d1-2679-432a-ac11-ebfebfa1bce9',
                        'label': 'South Korea'
                    },
                    'winner': None,
                    'loser': None
                },
                {
                    'uuid': '3866cad6-ba40-44fb-96c6-09f1131c5649',
                    'round': 1,
                    'position': 1,
                    'competitorA': {
                        'uuid': '7f026276-0904-4a7b-ae14-8c66b95ffc9e',
                        'label': 'Brazil'
                    },
                    'competitorB': {
                        'uuid': '15f4fe33-f317-4c4a-96e0-3b815dc481c6',
                        'label': 'Turkey'
                    },
                    'winner': None,
                    'loser': None
                },
                {
                    'uuid': '1f1fc156-4382-427c-aefb-5ae10009b7ce',
                    'round': 0,
                    'position': 0,
                    'competitorA': None,
                    'competitorB': None,
                    'winner': None,
                    'loser': None
                },
                {
                    'uuid': 'a9367a16-3f64-408b-9596-4029f7f60e62',
                    'round': 0,
                    'position': 1,
                    'competitorA': None,
                    'competitorB': None,
                    'winner': None,
                    'loser': None
                }
            ]
        }
    )
    assert isinstance(schema.tournament, TournamentAfterStartSchema)
    assert isinstance(schema.competitors, list)
    assert isinstance(schema.competitors[0], CompetitorSchema)
    assert isinstance(schema.matches, list)
    assert isinstance(schema.matches[0], MatchSchemaForTournamentListing)


def test_tournament_matches_schema():
    schema = TournamentMatchesSchema(
        **{
            'tournament': {
                'uuid': '03c964f8-7f5c-4224-b848-1ab6c1413c7d',
                'label': '2002 FIFA World Cup',
                'startingRound': 1,
                'competitors': 4
            },
            'past': [
                {
                    'uuid': '1e172084-ec76-4f56-bd8e-7b3c170e1221',
                    'round': 1,
                    'position': 0,
                    'competitorA': {
                        'uuid': 'de686e37-804b-4815-a507-d5879a240af6',
                        'label': 'Germany'
                    },
                    'competitorB': {
                        'uuid': '5d1bd1d1-2679-432a-ac11-ebfebfa1bce9',
                        'label': 'South Korea'
                    },
                    'winner': {
                        'uuid': 'de686e37-804b-4815-a507-d5879a240af6',
                        'label': 'Germany'
                    },
                    'loser': {
                        'uuid': '5d1bd1d1-2679-432a-ac11-ebfebfa1bce9',
                        'label': 'South Korea'
                    }
                },
                {
                    'uuid': '3866cad6-ba40-44fb-96c6-09f1131c5649',
                    'round': 1,
                    'position': 1,
                    'competitorA': {
                        'uuid': '7f026276-0904-4a7b-ae14-8c66b95ffc9e',
                        'label': 'Brazil'
                    },
                    'competitorB': {
                        'uuid': '15f4fe33-f317-4c4a-96e0-3b815dc481c6',
                        'label': 'Turkey'
                    },
                    'winner': {
                        'uuid': '7f026276-0904-4a7b-ae14-8c66b95ffc9e',
                        'label': 'Brazil'
                    },
                    'loser': {
                        'uuid': '15f4fe33-f317-4c4a-96e0-3b815dc481c6',
                        'label': 'Turkey'
                    }
                },
                {
                    'uuid': 'a9367a16-3f64-408b-9596-4029f7f60e62',
                    'round': 0,
                    'position': 1,
                    'competitorA': {
                        'uuid': '5d1bd1d1-2679-432a-ac11-ebfebfa1bce9',
                        'label': 'South Korea'
                    },
                    'competitorB': {
                        'uuid': '15f4fe33-f317-4c4a-96e0-3b815dc481c6',
                        'label': 'Turkey'
                    },
                    'winner': {
                        'uuid': '15f4fe33-f317-4c4a-96e0-3b815dc481c6',
                        'label': 'Turkey'
                    },
                    'loser': {
                        'uuid': '5d1bd1d1-2679-432a-ac11-ebfebfa1bce9',
                        'label': 'South Korea'
                    }
                }
            ],
            'upcoming': [
                {
                    'uuid': '1f1fc156-4382-427c-aefb-5ae10009b7ce',
                    'round': 0,
                    'position': 0,
                    'competitorA': {
                        'uuid': 'de686e37-804b-4815-a507-d5879a240af6',
                        'label': 'Germany'
                    },
                    'competitorB': {
                        'uuid': '15f4fe33-f317-4c4a-96e0-3b815dc481c6',
                        'label': 'Brazil'
                    },
                    'winner': None,
                    'loser': None
                }
            ]
        }
    )
    assert isinstance(schema.tournament, TournamentAfterStartSchema)
    assert isinstance(schema.past, list)
    assert isinstance(schema.past[0], MatchSchemaForTournamentListing)
    assert isinstance(schema.upcoming, list)
    assert isinstance(schema.upcoming[0], MatchSchemaForTournamentListing)


def test_match_schema():
    schema = MatchSchema(
        **{
            'uuid': 'a9367a16-3f64-408b-9596-4029f7f60e62',
            'tournament': {
                'uuid': '03c964f8-7f5c-4224-b848-1ab6c1413c7d',
                'label': '2002 FIFA World Cup',
                'startingRound': 1,
                'competitors': 4
            },
            'round': 0,
            'position': 0,
            'competitorA': {
                'uuid': 'de686e37-804b-4815-a507-d5879a240af6',
                'label': 'Germany'
            },
            'competitorB': {
                'uuid': '15f4fe33-f317-4c4a-96e0-3b815dc481c6',
                'label': 'Brazil'
            },
            'winner': {
                'uuid': '15f4fe33-f317-4c4a-96e0-3b815dc481c6',
                'label': 'Brazil'
            },
            'loser': {
                'uuid': 'de686e37-804b-4815-a507-d5879a240af6',
                'label': 'Germany'
            }
        }
    )
    assert isinstance(schema.uuid, uuid.UUID)
    assert isinstance(schema.round, int)
    assert schema.round >= 0
    assert isinstance(schema.position, int)
    assert schema.position >= 0
    assert isinstance(schema.competitorA, CompetitorSchema | None)
    assert isinstance(schema.competitorB, CompetitorSchema | None)
    assert isinstance(schema.winner, CompetitorSchema | None)
    assert isinstance(schema.loser, CompetitorSchema | None)


def test_tournament_result_schema():
    schema = TournamentResultSchema(
        **{
            'tournament': {
                'uuid': '03c964f8-7f5c-4224-b848-1ab6c1413c7d',
                'label': '2002 FIFA World Cup',
                'startingRound': 1,
                'competitors': 4
            },
            'top4': [
                {
                    'uuid': '7f026276-0904-4a7b-ae14-8c66b95ffc9e',
                    'label': 'Brazil'
                },
                {
                    'uuid': 'de686e37-804b-4815-a507-d5879a240af6',
                    'label': 'Germany'
                },
                {
                    'uuid': '15f4fe33-f317-4c4a-96e0-3b815dc481c6',
                    'label': 'Turkey'
                },
                {
                    'uuid': '5d1bd1d1-2679-432a-ac11-ebfebfa1bce9',
                    'label': 'South Korea'
                }
            ]
        },
    )
    assert isinstance(schema.tournament, TournamentAfterStartSchema)
    assert isinstance(schema.top4, list)
    assert isinstance(schema.top4[0], CompetitorSchema)
