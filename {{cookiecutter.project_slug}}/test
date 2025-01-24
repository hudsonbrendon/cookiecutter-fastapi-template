#!/usr/bin/env bash

set -e
set -x

uv run pytest --cov=app --cov-report=term-missing app/tests "${@}"
