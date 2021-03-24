"""Tests for the package."""

import base64
import datetime
import os
import sys
import time

import requests

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


def test_remote_schemes() -> None:
    """Test schemes from some popular repositories."""

    auth = (os.environ.get("GH_USERNAME"), os.environ.get("GH_PASSWORD"))

    if auth[0] is None or auth[1] is None:
        return

    repos = [
        ("Alamofire", "Alamofire"),
        ("pointfreeco", "swift-snapshot-testing"),
        ("AFNetworking", "AFNetworking"),
        ("airbnb", "lottie-ios"),
        ("mxcl", "PromiseKit"),
        ("scenee", "FloatingPanel"),
        ("Moya", "Moya"),
        ("SwiftyJSON", "SwiftyJSON"),
        ("daltoniam", "Starscream"),
        ("jonkykong", "SideMenu"),
        ("danielgindi", "Charts"),
        ("Quick", "Nimble"),
        ("exelban", "stats"),
        ("onevcat", "Kingfisher"),
        ("krzyzanowskim", "CryptoSwift"),
        ("shogo4405", "HaishinKit.swift"),
        ("JohnEstropia", "CoreStore"),
        ("xmartlabs", "Eureka"),
    ]

    def response_sleep(response) -> None:
        """Sleep for as long as needed to not exceed rate limit

        :param response: Response to get the data from.
        """
        remaining = float(response.headers["X-RateLimit-Remaining"])
        reset_time = datetime.datetime.fromtimestamp(int(response.headers["X-RateLimit-Reset"]))
        time_remaining = float((reset_time - datetime.datetime.now()).seconds)
        sleep_factor = time_remaining / remaining
        time.sleep(sleep_factor)

    for user, repo in repos:
        url = f"https://api.github.com/repos/{user}/{repo}/git/trees/master?recursive=1"
        response = requests.get(url, auth=auth)
        response_sleep(response)

        if not response.ok:
            continue

        content = response.json()

        schemes = []

        for item in content["tree"]:
            if not item["path"].endswith(".xcscheme"):
                continue
            if item["type"] != "blob":
                continue
            schemes.append(item)

        if content["truncated"]:
            raise Exception()  # TODO

        for scheme_file in schemes:
            metadata_response = requests.get(scheme_file["url"], auth=auth)
            response_sleep(metadata_response)

            if not metadata_response.ok:
                continue

            metadata = metadata_response.json()
            assert metadata["encoding"] == "base64"
            base64_content = metadata["content"]
            content = base64.b64decode(base64_content).decode("utf-8")
            parsed = xcodeproj.Scheme.from_string(
                content, os.path.basename(scheme_file["path"]).replace(".xcscheme", "")
            )
            assert parsed is not None
