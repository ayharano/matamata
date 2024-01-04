import uuid

import pytest
from pydantic import BaseModel, ValidationError

from matamata.schemas import (
    LabelSchema,
    TournamentCompetitorPayloadSchema,
    TrimmedString,
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


def test_competitor_payload_schema():
    schema = TournamentCompetitorPayloadSchema(
        competitor_uuid='01234567-89ab-cdef-0123-456789abcdef'
    )
    assert schema.competitor_uuid == uuid.UUID('01234567-89ab-cdef-0123-456789abcdef')


def test_winner_payload_schema():
    schema = WinnerPayloadSchema(
        winner_uuid='01234567-89ab-cdef-0123-456789abcdef'
    )
    assert schema.winner_uuid == uuid.UUID('01234567-89ab-cdef-0123-456789abcdef')
