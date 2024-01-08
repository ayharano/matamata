# *matamata* documentation

In this project, we use Architecture decision records (ADRs) to register some of the most important decisions.
For more details, please access [joelparkerhenderson/architecture-decision-record GitHub repo](https://github.com/joelparkerhenderson/architecture-decision-record).

Such decisions are stored in [architecture/decisions](./architecture/decisions) subdirectory.

## Notes

### `datetime.datetime.utcnow`
Given that there are currently more than 500 occurrences when running the full test suite execution warning
regarding [`datetime.datetime.utcnow`](https://docs.python.org/3.12/library/datetime.html#datetime.datetime.utcnow),
it is worth clarifying why in this project it wasn't addressed, including using it in tests even with
the deprecation message.

[SQLAlchemy DateTime](https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.DateTime)
doesn't store timezone information by default and the
[SQLAlchemy-Utils Timestamp](https://sqlalchemy-utils.readthedocs.io/en/latest/models.html#module-sqlalchemy_utils.models)
recipe also doesn't store the timezone information either.

Considering the tradeoff of following the deprecation warning and dealing with the comparison between
[naive and aware timestamps](https://docs.python.org/3.12/library/datetime.html#aware-and-naive-objects),
we chose to keep using `datetime.datetime.utcnow` for now.
