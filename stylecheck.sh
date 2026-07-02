#!/bin/bash

set -e

poetry run ruff check xcodeproj tests
poetry run ruff format --check xcodeproj tests
poetry run mypy xcodeproj/ tests/
