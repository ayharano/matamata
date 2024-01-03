# **matamata** REST API for single-elimination tournament management

> Code repository author: [Alexandre Harano](mailto:email@ayharano.dev)

[*Mata-mata*](https://pt.wikipedia.org/wiki/Competi%C3%A7%C3%B5es_eliminat%C3%B3rias) is
a popular expression for [single-elimination tournament](https://en.wikipedia.org/wiki/Single-elimination_tournament)
in Brazil.

This project provides a simple REST API implementation of
single-elimination tournament management with features as
creating new tournaments, registering competitors,
retrieving the matches lists, win-lose management, and
other actions.

Documentation for this project are stored in [`docs`](./docs) directory
with a descriptive [`index.md file`](./docs/index.md).

# Project Dependencies
- [Python](https://www.python.org/) 3.12+
- [uvicorn](https://www.uvicorn.org/) 0.25+
- [FastAPI](https://fastapi.tiangolo.com/) 0.108+
- [Pydantic Settings](https://docs.pydantic.dev/2.5/concepts/pydantic_settings/) 2.1

## Database Dependencies
- [SQLAlchemy](https://docs.sqlalchemy.org/en/20/) 2.0

## Test Dependencies
- [pytest](https://docs.pytest.org/) 7.4
- [pytest-cov](https://pytest-cov.readthedocs.io/) 4.1

# Project Configuration
This project uses [the twelve-factor app](https://12factor.net/) methodology.

Environment variables in this project can be stored using a `.env` (dot env) file.
For initial setup, a sample is provided as [`.env.sample`](.env.sample).
If you prefer to use a `.env` file, copy that sample as `.env` and modify the values accordingly.

A description of each of the variables is provided as the following list.

<EMPTY FOR NOW>
