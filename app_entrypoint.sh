#!/usr/bin/env bash

set -e

alembic upgrade head

uvicorn --host 0.0.0.0 --port 8000 matamata.main:app --reload
