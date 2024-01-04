from typing import Annotated
from uuid import UUID

from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator


# Adapted from https://docs.pydantic.dev/2.5/concepts/validators/#annotated-validators
def strip_string(raw: str) -> str:
    return raw.strip()


def non_empty_trimmed_string(trimmed: str) -> str:
    if trimmed == '':
        raise ValueError('must not be empty or contain only whitespace characters')
    return trimmed


TrimmedString = Annotated[str, AfterValidator(strip_string)]
NonEmptyTrimmedString = Annotated[TrimmedString, AfterValidator(non_empty_trimmed_string)]


class LabelSchema(BaseModel):
    label: NonEmptyTrimmedString


TournamentPayloadSchema = LabelSchema
CompetitorPayloadSchema = LabelSchema


class TournamentCompetitorPayloadSchema(BaseModel):
    competitor_uuid: UUID


class WinnerPayloadSchema(BaseModel):
    winner_uuid: UUID
