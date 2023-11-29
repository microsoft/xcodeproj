#!/bin/bash

pushd "${VIRTUAL_ENV}/.." > /dev/null

python3 -m black -l 100 xcodeproj/*.py tests/*.py
python3 -m pylint --rcfile=pylintrc xcodeproj tests
python3 -m mypy --ignore-missing-imports xcodeproj/ tests/

popd > /dev/null

