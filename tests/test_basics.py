"""Tests for the package."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import xcodeproj


# Fixtures work by redefining names, so we need to disable this
# pylint: disable=redefined-outer-name

COLLATERAL_PATH = os.path.join(
    os.path.abspath(os.path.join(os.path.abspath(__file__), "..")), "collateral"
)


@pytest.fixture(scope="session")
def one() -> xcodeproj.XcodeProject:
    """Load the project

    :returns: The project
    """
    one_path = os.path.join(COLLATERAL_PATH, "One.xcodeproj")
    return xcodeproj.XcodeProject(one_path)


@pytest.fixture(scope="session")
def two() -> xcodeproj.XcodeProject:
    """Load the project

    :returns: The project
    """
    two_path = os.path.join(COLLATERAL_PATH, "Two.xcodeproj")
    return xcodeproj.XcodeProject(two_path)


def test_base_references(one: xcodeproj.XcodeProject) -> None:
    """Test that references work

    :param one: The project
    """

    for target in one.project.targets():
        for build_phase in target.build_phases():
            for build_file in build_phase.files():
                assert build_file is not None


def test_targets(one: xcodeproj.XcodeProject) -> None:
    """Test that targets work

    :param one: The project
    """

    targets = one.targets()
    assert len(targets) == 4

    watch_extension = targets[0]
    assert watch_extension.product_name == "wat WatchKit Extension"
    assert watch_extension.object_key == "DD624D2E25B05EEE0081F68F"

    cljtest = targets[1]
    assert cljtest.product_name == "CLJTest"
    assert cljtest.object_key == "DD74C32525AF302A00C4A922"

    watch_app = targets[2]
    assert watch_app.product_name == "wat WatchKit App"
    assert watch_app.object_key == "DD624D1F25B05EED0081F68F"

    watch_container = targets[3]
    assert watch_container.product_name == "wat"
    assert watch_container.object_key == "DD624D1C25B05EED0081F68F"


def test_target_by_name(one: xcodeproj.XcodeProject) -> None:
    """Test that targets work

    :param one: The project
    """
    cljtest = one.target_by_name("CLJTest")
    assert cljtest is not None
    assert cljtest.product_name == "CLJTest"
    assert cljtest.object_key == "DD74C32525AF302A00C4A922"

    other = one.target_by_name("other")
    assert other is None


def test_get_paths(one: xcodeproj.XcodeProject, two: xcodeproj.XcodeProject) -> None:
    """Test that path determination works

    :param one: The project
    :param two: A different project
    """

    expected = [
        "wat WatchKit App/Info.plist",
        "wat WatchKit Extension/ComplicationController.swift",
        "wat WatchKit Extension/InterfaceController.swift",
        "CLJTest/SceneDelegate.swift",
        "CLJTest/Info.plist",
        "CLJTest/CLJTest-Bridging-Header.h",
        "wat WatchKit Extension/Info.plist",
        "wat WatchKit App/Assets.xcassets",
        "Carthage/Build/CocoaLumberjack.xcframework",
        "wat WatchKit Extension/NotificationController.swift",
        "CLJTest/AppDelegate.swift",
        "$(BUILT_PRODUCTS_DIR)",
        "$(BUILT_PRODUCTS_DIR)",
        "CLJTest/Base.lproj/LaunchScreen.storyboard",
        "wat WatchKit App/Base.lproj/Interface.storyboard",
        "wat WatchKit Extension/Assets.xcassets",
        "CLJTest/Assets.xcassets",
        "CLJTest/test.m",
        "wat WatchKit Extension/PushNotificationPayload.apns",
        "CLJTest/ViewController.swift",
        "wat WatchKit Extension/ExtensionDelegate.swift",
        "$(BUILT_PRODUCTS_DIR)",
        "CLJTest/Base.lproj/Main.storyboard",
        "$(BUILT_PRODUCTS_DIR)",
    ]

    for index, item in enumerate(one.fetch_type(xcodeproj.PBXFileReference).values()):
        assert item.relative_path() == expected[index]
        assert item.absolute_path() == os.path.join(COLLATERAL_PATH, expected[index])

    groups = [
        "wat WatchKit App",
        None,
        "CLJTest",
        "CLJTest",
        "wat WatchKit App",
        "CLJTest",
        None,
        None,
        "wat WatchKit Extension",
        "wat WatchKit Extension",
    ]

    for index, group in enumerate(one.fetch_type(xcodeproj.PBXGroup).values()):
        value = groups[index]
        assert group.relative_path() == value
        if value is None:
            continue
        assert group.absolute_path() == os.path.join(COLLATERAL_PATH, value)

    for index, version_group in enumerate(two.fetch_type(xcodeproj.XCVersionGroup).values()):
        if index == 0:
            with pytest.raises(Exception):
                _ = version_group.relative_path()
            with pytest.raises(Exception):
                _ = version_group.absolute_path()
        else:
            assert version_group.relative_path() is None
            assert version_group.absolute_path() is None


def test_get_parents(two: xcodeproj.XcodeProject) -> None:
    """Test that getting parents works.

    :param two: The Xcode project
    """

    scene_delegate = two.objects["DD74C32B25AF302A00C4A922"]
    scene_delegate_parent = scene_delegate.parent_group()
    assert scene_delegate_parent is not None
    assert scene_delegate_parent.object_key == "DD74C32825AF302A00C4A922"

    test_m = two.objects["DD62471D25AF30BE0081F68F"]
    try:
        _ = test_m.parent_group()
    except xcodeproj.MultipleParentException:
        pass
    except Exception:
        pytest.fail("Failed to get MultipleParentException")


def test_build_configuration(one: xcodeproj.XcodeProject) -> None:
    """Test that build configuration works

    :param one: The project
    """

    list1 = one.build_configuration_list_for_target("CLJTest")
    assert list1 is not None
    assert sorted(list1.build_configurations) == sorted(
        ["DD74C33B25AF302C00C4A922", "DD74C33C25AF302C00C4A922"]
    )

    list2 = one.build_configuration_list_for_target("hodor")
    assert list2 is None


def test_code_file_paths(one: xcodeproj.XcodeProject) -> None:
    """Test that code files are found (.swift and .m)

    :param one: The project
    """

    expected_code_files = [
        "wat WatchKit Extension/ComplicationController.swift",
        "wat WatchKit Extension/InterfaceController.swift",
        "CLJTest/SceneDelegate.swift",
        "wat WatchKit Extension/NotificationController.swift",
        "CLJTest/AppDelegate.swift",
        "CLJTest/test.m",
        "CLJTest/ViewController.swift",
        "wat WatchKit Extension/ExtensionDelegate.swift",
    ]

    for index, item in enumerate(one.generate_code_file_paths()):
        assert item == os.path.join(COLLATERAL_PATH, expected_code_files[index])


def test_code_files(two: xcodeproj.XcodeProject) -> None:
    """Test that code files are found (.swift and .m)

    :param two: The project
    """

    for item in two.fetch_type(xcodeproj.PBXFileReference).values():
        is_code_file = item.is_code_file()
        if item.path is None:
            continue
        assert is_code_file == item.path.endswith(".swift") or item.path.endswith(".m")


def test_build_file_references(two: xcodeproj.XcodeProject) -> None:
    """Test that build file references are correct

    :param two: The project
    """

    references = {
        "DD62471E25AF30BE0081F68F": "DD62471D25AF30BE0081F68F",
        "DD624D2125B05EED0081F68F": "DD624D2025B05EED0081F68F",
        "DD624D2725B05EED0081F68F": "DD624D2525B05EED0081F68F",
        "DD624D2925B05EEE0081F68F": "DD624D2825B05EEE0081F68F",
        "DD624D3025B05EEE0081F68F": "DD624D2F25B05EEE0081F68F",
        "DD624D3525B05EEE0081F68F": "DD624D3425B05EEE0081F68F",
        "DD624D3725B05EEE0081F68F": "DD624D3625B05EEE0081F68F",
        "DD624D3925B05EEE0081F68F": "DD624D3825B05EEE0081F68F",
        "DD624D3B25B05EEE0081F68F": "DD624D3A25B05EEE0081F68F",
        "DD624D3D25B05EEE0081F68F": "DD624D3C25B05EEE0081F68F",
        "DD624D4E25B05EF90081F68F": "DD624D1825B05ED30081F68F",
        "DD74C32A25AF302A00C4A922": "DD74C32925AF302A00C4A922",
        "DD74C32C25AF302A00C4A922": "DD74C32B25AF302A00C4A922",
        "DD74C32E25AF302A00C4A922": "DD74C32D25AF302A00C4A922",
        "DD74C33125AF302A00C4A922": "DD74C32F25AF302A00C4A922",
        "DD74C33325AF302C00C4A922": "DD74C33225AF302C00C4A922",
        "DD74C33625AF302C00C4A922": "DD74C33425AF302C00C4A922",
    }

    for item in two.fetch_type(xcodeproj.PBXBuildFile).values():
        assert item.file_ref.object_key == references[item.object_key]


def test_file_paths(one: xcodeproj.XcodeProject) -> None:
    """Check that generating file paths works.

    :param one: The project
    """

    for key, pbxobj in one.objects.items():
        if not isinstance(pbxobj, xcodeproj.PBXPathObject):
            continue

        if isinstance(pbxobj, xcodeproj.XCVersionGroup):
            continue

        if key in [
            "DD74C31D25AF302A00C4A922",  # Root of the project
            "DD74C32725AF302A00C4A922",  # Products
            "DD62471925AF30980081F68F",  # Frameworks
        ]:
            continue

        path = pbxobj.relative_path()
        assert path is not None, f"Failed to get a path for: {key}"
        assert len(path) > 0, f"Failed to generate a path for: {key}"


def test_target_containing_phase(one: xcodeproj.XcodeProject) -> None:
    """Check that finding targets containing a specific phase works.

    :param one: The project
    """

    target = one.target_containing_phase("DD74C32225AF302A00C4A922")
    assert target is not None
    assert target.name == "CLJTest"
    assert target.object_key == "DD74C32525AF302A00C4A922"

    target2 = one.target_containing_phase("hodor")
    assert target2 is None
