#!/bin/bash

pushd "${VIRTUAL_ENV}/.." > /dev/null

python -m black -l 100 xcodeproj/*.py tests/*.py
python -m pylint --rcfile=pylintrc xcodeproj tests
python -m mypy --ignore-missing-imports xcodeproj/ tests/

popd > /dev/null

