#!/bin/bash

set -e

poetry run pytest tests --cov=xcodeproj --cov-report html --cov-report xml --doctest-modules --junitxml=junit/test-results.xml
