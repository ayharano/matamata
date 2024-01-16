# syntax=docker/dockerfile:1
FROM python:3.12-slim as base

# Prepare for the app
ENV APP_HOME /app
WORKDIR ${APP_HOME}
ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV=/opt/venv

# We use a non-root user for the app
ARG USER=default
ENV HOME /home/${USER}

# Install sudo and remove the apt/dpkg metadata afterwards
RUN apt-get update \
 && apt-get install -y sudo \
 && rm -rf /var/lib/apt/lists/*

# Add new user
RUN adduser --disabled-password --gecos "" ${USER} \
 && echo "${USER} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${USER} \
 && chmod 0440 /etc/sudoers.d/${USER} \
 && mkdir -p ${VIRTUAL_ENV} \
 && chown ${USER}:${USER} ${APP_HOME} ${VIRTUAL_ENV}

# Switch to use the non-root user from here
USER ${USER}

# Even in a container, we use a virtual env to isolate the project
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Install Python package build/install dependencies
RUN pip install --no-cache-dir --upgrade pip build setuptools

# Copy some project root files for building and later for volume binding
COPY alembic.ini *entrypoint.sh pyproject.toml ./

# Set Python PATH to use the src directory that will be bound later
ENV PYTHONPATH='src'


FROM base as tests

WORKDIR ${APP_HOME}
RUN pip install --no-cache-dir -e '.[test]' \
 && pip install --no-cache-dir tzdata
CMD ["pytest", "--cov=src", ".", "-vv"]


FROM base as web

WORKDIR ${APP_HOME}
RUN pip install --no-cache-dir -e '.' \
 && pip install --no-cache-dir tzdata
EXPOSE 8000
CMD ["uvicorn", "--host", "0.0.0.0", "matamata.main:app", "--reload"]


FROM base as for_fly

WORKDIR ${APP_HOME}
COPY --chown=${USER}:${USER} migrations ./migrations/
COPY --chown=${USER}:${USER} src ./src/
RUN pip install --no-cache-dir -e '.' \
 && pip install --no-cache-dir tzdata
EXPOSE 8080
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "matamata.main:app"]
