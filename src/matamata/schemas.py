from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, computed_field
from pydantic.functional_validators import AfterValidator


# Adapted from https://docs.pydantic.dev/2.5/concepts/validators/#annotated-validators
def strip_string(raw: str) -> str:
    return raw.strip()


def non_empty_trimmed_string(trimmed: str) -> str:
    if trimmed == "":
        raise ValueError("must not be empty or contain only whitespace characters")
    return trimmed


TrimmedString = Annotated[str, AfterValidator(strip_string)]
NonEmptyTrimmedString = Annotated[
    TrimmedString, AfterValidator(non_empty_trimmed_string)
]


def non_negative(value: int) -> int:
    if value < 0:
        raise ValueError("must not a non-negative value")
    return value


def positive(value: int) -> int:
    if value <= 0:
        raise ValueError("must not a positive value")
    return value


NonNegativeInt = Annotated[int, AfterValidator(non_negative)]
PositiveInt = Annotated[int, AfterValidator(positive)]


class LabelSchema(BaseModel):
    label: NonEmptyTrimmedString


TournamentPayloadSchema = LabelSchema
CompetitorPayloadSchema = LabelSchema


class TournamentCompetitorPayloadSchema(BaseModel):
    competitor_uuid: UUID


class WinnerPayloadSchema(BaseModel):
    winner_uuid: UUID


class UuidLabelSchema(BaseModel):
    uuid: UUID
    label: NonEmptyTrimmedString


TournamentSchema = UuidLabelSchema
CompetitorSchema = UuidLabelSchema


class TournamentListSchema(BaseModel):
    tournaments: list[TournamentSchema]


class CompetitorListSchema(BaseModel):
    competitors: list[CompetitorSchema]


class TournamentsAccordingToCompetitorSchema(BaseModel):
    past: list[TournamentSchema]
    ongoing: list[TournamentSchema]
    upcoming: list[TournamentSchema]


class CompetitorDetailSchema(BaseModel):
    competitor: CompetitorSchema
    tournaments: TournamentsAccordingToCompetitorSchema


class TournamentCompetitorSchema(BaseModel):
    tournament: TournamentSchema
    competitor: CompetitorSchema


class TournamentCompetitorListSchema(CompetitorListSchema):
    tournament: TournamentSchema


class TournamentAfterStartSchema(UuidLabelSchema):
    startingRound: NonNegativeInt = Field(validation_alias="starting_round")
    numberCompetitors: PositiveInt = Field(validation_alias="number_competitors")


class MatchForTournamentListingWithOtherCompetitor(BaseModel):
    uuid: UUID
    round: NonNegativeInt
    position: NonNegativeInt
    competitorA: CompetitorSchema | None = Field(
        exclude=True, validation_alias="competitor_a"
    )
    competitorB: CompetitorSchema | None = Field(
        exclude=True, validation_alias="competitor_b"
    )
    currentCompetitor: CompetitorSchema | None = Field(exclude=True)

    @computed_field
    @property
    def otherCompetitor(self) -> CompetitorSchema | None:
        competitors = [self.competitorA, self.competitorB]
        competitors.remove(self.currentCompetitor)
        other_competitor = competitors.pop()
        return other_competitor


class TournamentCompetitorMatchesWithOtherCompetitorSchema(BaseModel):
    past: list[MatchForTournamentListingWithOtherCompetitor]
    upcoming: list[MatchForTournamentListingWithOtherCompetitor]


class TournamentCompetitorMatchesSchema(TournamentCompetitorSchema):
    matches: TournamentCompetitorMatchesWithOtherCompetitorSchema


class MatchSchemaForTournamentListing(BaseModel):
    uuid: UUID
    round: NonNegativeInt
    position: NonNegativeInt
    competitorA: CompetitorSchema | None = Field(validation_alias="competitor_a")
    competitorB: CompetitorSchema | None = Field(validation_alias="competitor_b")
    winner: CompetitorSchema | None
    loser: CompetitorSchema | None


class TournamentStartSchema(BaseModel):
    tournament: TournamentAfterStartSchema
    competitors: list[CompetitorSchema]
    matches: list[MatchSchemaForTournamentListing]


class TournamentMatchesSchema(BaseModel):
    tournament: TournamentAfterStartSchema
    past: list[MatchSchemaForTournamentListing]
    upcoming: list[MatchSchemaForTournamentListing]


class MatchSchema(MatchSchemaForTournamentListing):
    tournament: TournamentAfterStartSchema


class TournamentResultSchema(BaseModel):
    tournament: TournamentAfterStartSchema
    top4: list[CompetitorSchema | None]
