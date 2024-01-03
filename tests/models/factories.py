from datetime import datetime, timedelta

import factory

from matamata.models import Competitor


class TimestampedFactory(factory.Factory):
    created = factory.LazyFunction(datetime.now)
    updated = factory.LazyAttribute(lambda obj: obj.created + timedelta(seconds=0.01))


class CompetitorFactory(TimestampedFactory):
    class Meta:
        model = Competitor

    label = factory.Faker('name')
