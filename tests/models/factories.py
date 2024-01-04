from datetime import datetime, timedelta

import factory

from matamata.models import Competitor, Match, Tournament, TournamentCompetitor


class TimestampedFactory(factory.Factory):
    created = factory.LazyFunction(datetime.now)
    updated = factory.LazyAttribute(lambda obj: obj.created + timedelta(seconds=0.01))


class CompetitorFactory(TimestampedFactory):
    class Meta:
        model = Competitor

    label = factory.Faker('name')


class TournamentFactory(TimestampedFactory):
    class Meta:
        model = Tournament

    label = factory.Faker('company')
    matchesCreation = None
    numberCompetitors = None
    startingRound = None


class TournamentCompetitorFactory(TimestampedFactory):
    class Meta:
        model = TournamentCompetitor

    tournament = factory.SubFactory(TournamentFactory)
    competitor = factory.SubFactory(CompetitorFactory)


class MatchFactory(TimestampedFactory):
    class Meta:
        model = Match

    tournament = factory.SubFactory(TournamentFactory)
    round = 0
    position = 0

    competitorA = None
    competitorB = None

    resultRegistration = None

    winner = None
    loser = None
