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
- [FastAPI](https://fastapi.tiangolo.com/) 0.108+
- [Pydantic Settings](https://docs.pydantic.dev/2.5/concepts/pydantic_settings/) 2.1

## Test Dependencies
- [pytest](https://docs.pytest.org/) 7.4
- [pytest-cov](https://pytest-cov.readthedocs.io/) 4.1
