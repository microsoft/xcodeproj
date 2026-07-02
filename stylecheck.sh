#!/bin/bash

set -e

uv run ruff check xcodeproj tests
uv run ruff format --check xcodeproj tests
uv run mypy xcodeproj/ tests/
