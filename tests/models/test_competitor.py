from datetime import datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from matamata.models import Competitor
from matamata.models.constants import COMPETITOR_LABEL_CONSTRAINT


def test_create_and_retrieve_competitor(session):
    before_new_competitor = datetime.now()
    new_competitor = Competitor(
        label='South Korea',
    )
    session.add(new_competitor)
    session.commit()

    competitor = session.scalar(
        select(Competitor)
        .where(
            Competitor.label == 'South Korea',
        )
    )

    assert competitor.label == 'South Korea'
    assert competitor.created > before_new_competitor
    assert competitor.updated > competitor.created


def test_cannot_create_competitor_with_empty_label(session):
    empty_label_competitor = Competitor(
        label='',  # empty
    )
    session.add(empty_label_competitor)
    with pytest.raises(
        IntegrityError,
        match=COMPETITOR_LABEL_CONSTRAINT,
    ):
        session.commit()


def test_cannot_create_competitor_with_whitespace_only_label(session):
    whitespace_label_competitor = Competitor(
        label='  ',  # whitespaces
    )
    session.add(whitespace_label_competitor)
    with pytest.raises(
        IntegrityError,
        match=COMPETITOR_LABEL_CONSTRAINT,
    ):
        session.commit()


def test_can_create_duplicate_competitor(session):
    first_competitor = Competitor(
        label='Brazil',
    )
    session.add(first_competitor)
    session.commit()
    session.refresh(first_competitor)

    second_competitor = Competitor(
        label='Brazil',
    )
    session.add(second_competitor)
    session.commit()
    session.refresh(second_competitor)

    count = session.scalar(
        select(func.count('*'))
        .select_from(Competitor)
        .where(
            Competitor.label == 'Brazil',
        )
    )

    assert count == 2
