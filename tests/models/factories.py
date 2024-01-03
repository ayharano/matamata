from datetime import datetime, timedelta

import factory

from matamata.models import Competitor, Tournament


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
