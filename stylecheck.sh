#!/bin/bash

set -e

uv run ruff check xcodeproj tests scripts
uv run ruff format --check xcodeproj tests scripts
uv run mypy xcodeproj/ tests/ scripts/
