#!/usr/bin/env bash

set -e

alembic upgrade head

pytest --cov=src/matamata . -vv
