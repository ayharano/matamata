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

[asciinema](https://asciinema.org/) demo from cloning to running the project:

[![*matamata* Docker Compose demo from cloning to running](https://asciinema.org/a/83KC37qmHsZ1d1XMy2VH5gI0n.svg)](https://asciinema.org/a/83KC37qmHsZ1d1XMy2VH5gI0n)

While running the project, it is possible to access the interactive OpenAPI documentation.

![OpenAPI Interactive Page Screenshot](docs/openapi.png "Interactive OpenAPI page")


# Project Configuration
This project uses [the twelve-factor app](https://12factor.net/) methodology.

Environment variables in this project can be stored using a `.env` (dot env) file.
For initial setup, a sample is provided as [`.env.sample`](.env.sample).
However, because the currently recommended way to run this project in development mode relies on
[Docker Compose](https://docs.docker.com/compose/),
it is preferable to adjust the values in
the [`docker-compose.yml`](docker-compose.yml) file.

A description of each of the variables is provided as the following list.

- `DATABASE_URL`: a string value to be used as an [Engine Configuration](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) URL

# Project Installation
First, clone this repo:

```shell
$ git clone https://github.com/ayharano/matamata.git
```

After cloning the repository, change the directory to the project root.
All instructions below, including configuring the virtual environment and running the project, depend on being
in the project root directory.

## Consistency of contributions using `pre-commit`

To maintain consistency between individual commits,
this repo is adopting the use of [`pre-commit`](https://pre-commit.com/).

The recommended way to install it for this repo is by installing via [`pipx`](https://pipx.pypa.io/stable/).
After installing `pipx`, issue the following commands:

```shell
$ pipx install pre-commit
$ pre-commit install --install-hooks --overwrite
```

`pre-commit` is configured to also run per push and pull requests in GitHub workflow.

## Run the project using Docker Compose (recommended way)

After [installing Docker Compose](https://docs.docker.com/compose/install/),
open a terminal pointing to the project root and run:

```shell
$ docker compose up web
```

It will launch the FastAPI app using uvicorn backed by a PostgreSQL instance as the app's
[RDBMS](https://en.wikipedia.org/wiki/Relational_database).
This way, we don't need local setup of the project, besides the use of Docker containers.

Note that this Docker Compose setup was chosen to facilitate development.
An actual deployment of the app in a production environment would require some changes.

One of the configurations to facilitate the development process is to
bind the
[`migrations`](migrations),
[`tests`](tests) and
[source code](src) container directories and
some project root files to the Docker host filesystem,
meaning that whenever a change is applied after editing,
they will be instantly replicated within a running container.

### Docker Compose file and Dockerfiles structure

The [`docker-compose.yml`](docker-compose.yml) file provides four services:

1. Test database container (PostgreSQL 16)
2. App database container (PostgreSQL 16)
3. Tests container
4. Web app container

Tests and Web app containers are built using
a [multi-stage build](https://docs.docker.com/build/building/multi-stage/)
strategy in a single [`app.Dockerfile`](app.Dockerfile).

#### Test Database PostgreSQL container
The Test Database PostgreSQL container uses an ephemeral volume to
create the storage only during the test suite running.

#### App Database PostgreSQL container
The App Database PostgreSQL container uses a local `postgresql-data` volume to
persist database data between runs.

#### Base container
The base container prepared in `app.Dockerfile` has
a non-[root user](https://en.wikipedia.org/wiki/Superuser) on
a [Debian distro](https://www.debian.org/) instance with
Python 3.12 configured and provides a
[virtual environment](https://docs.python.org/3/library/venv.html)
with some Python package building/installation dependencies.

Although we don't refer to the base container in the Docker Compose file,
it is prepared as a base image for other Python-based containers.

#### Tests container
The tests container installs Python packages to run the test suite,
apply the pending migrations in a test database, and
runs the test suite.
It binds the project's
[`migrations`](migrations),
[`src`](src),
and
[`tests`](tests)
directories, and some project root files within the container.

We established the successful run of the tests suite a requirement for
running the Web app container.

#### Web app container
The Web app container installs the required Python packages for the FastAPI app to run,
apply the pending migrations in an app database, and
runs the [ASGI](https://asgi.readthedocs.io/) web server `uvicorn` with
this project application.
It binds the project's
[`migrations`](migrations),
and
[`src`](src)
directories, and some project root files within the container.


### Using the Project in a Local Environment without Docker Compose

As we replaced the local development setup of the project to relying on the use of
[Docker Compose](https://docs.docker.com/compose/),
we have moved and adjusted the previous instructions in
[a separate document](docs/local_environment_without_docker_compose.md).

# Running the test suite

Whenever we feel like running the test suite, issue the following command in the project root:

```shell
$ docker compose up tests
```

# Running the application

To run the FastAPI `matamata` application, issue the following command in the project root:

```shell
$ docker compose up web
```

The Web app container will run the [ASGI](https://asgi.readthedocs.io/) web server `uvicorn` with
this project application.

By default, it will run on http://127.0.0.1:8000

To access the interactive OpenAPI documentation, just access http://127.0.0.1:8000/docs/

All the client access can be done in the URL that the server is running as the root of the system.

# Project Dependencies
- [Python](https://www.python.org/) 3.12+
- [uvicorn](https://www.uvicorn.org/) 0.27+
- [FastAPI](https://fastapi.tiangolo.com/) 0.109+
- [Pydantic Settings](https://docs.pydantic.dev/2.5/concepts/pydantic_settings/) 2.1

## Database Dependencies
- [SQLAlchemy](https://docs.sqlalchemy.org/en/20/) 2.0
- [SQLAlchemy-Utils](https://sqlalchemy-utils.readthedocs.io/) 0.41
- [Alembic](https://alembic.sqlalchemy.org/) 1.13
- [psycopg](https://www.psycopg.org/) 3.1

## Test Dependencies
- [pytest](https://docs.pytest.org/) 7.4
- [pytest-cov](https://pytest-cov.readthedocs.io/) 4.1
- [factory_boy](https://factoryboy.readthedocs.io/) 3.3

## Integrated Solution Dependencies

- [PostgreSQL](https://www.postgresql.org/) 16
- [Docker Compose](https://docs.docker.com/compose/)
