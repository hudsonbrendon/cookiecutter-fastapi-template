#! /usr/bin/env bash

# Let the DB start

uv run python ./app/backend_pre_start.py

# Run migrations


uv run alembic upgrade head


# Create initial data in DB
uv run python ./app/initial_data.py
