"""Tests for the package."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import xcodeproj


# Fixtures work by redefining names, so we need to disable this
# pylint: disable=redefined-outer-name

COLLATERAL_PATH = os.path.join(
    os.path.abspath(os.path.join(os.path.abspath(__file__), "..")), "collateral"
)
SCHEMES_PATH = os.path.join(COLLATERAL_PATH, "schemes")


def test_load_schemes() -> None:
    """Test that loading schemes works"""

    for scheme_file in os.listdir(SCHEMES_PATH):
        scheme_path = os.path.join(SCHEMES_PATH, scheme_file)
        _ = xcodeproj.Scheme.from_file(scheme_path)
