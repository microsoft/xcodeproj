"""Xcode project file management."""

import hashlib
import json
import os
import pathlib
import pickle
import subprocess
import weakref
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version
from typing import (
    Any,
    TypeVar,
    cast,
)

import deserialize
import platformdirs

from .buildphases import (
    PBXBuildPhase,
    PBXCopyFilesBuildPhase,
    PBXFrameworksBuildPhase,
    PBXHeadersBuildPhase,
    PBXResourcesBuildPhase,
    PBXShellScriptBuildPhase,
    PBXSourcesBuildPhase,
)
from .buildrules import PBXBuildRule
from .files import PBXBuildFile
from .objects import Objects
from .other import (
    PBXContainerItemProxy,
    PBXFileSystemSynchronizedBuildFileExceptionSet,
    PBXTargetDependency,
)
from .pathobjects import (
    PBXFileReference,
    PBXFileSystemSynchronizedRootGroup,
    PBXGroup,
    PBXPathObject,
    PBXReferenceProxy,
    PBXVariantGroup,
    XCVersionGroup,
)
from .pbxobject import PBXObject
from .pbxproject import PBXProject
from .schemes import Scheme
from .targets import PBXAggregateTarget, PBXNativeTarget, PBXProductType, PBXTarget
from .xcobjects import XCBuildConfiguration, XCConfigurationList

try:
    __version__ = _version("xcodeproj")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    "Objects",
    "PBXAggregateTarget",
    "PBXBuildFile",
    "PBXBuildPhase",
    "PBXBuildRule",
    "PBXContainerItemProxy",
    "PBXCopyFilesBuildPhase",
    "PBXFileReference",
    "PBXFileSystemSynchronizedBuildFileExceptionSet",
    "PBXFileSystemSynchronizedRootGroup",
    "PBXFrameworksBuildPhase",
    "PBXGroup",
    "PBXHeadersBuildPhase",
    "PBXNativeTarget",
    "PBXObject",
    "PBXObjectType",
    "PBXPathObject",
    "PBXProductType",
    "PBXProject",
    "PBXReferenceProxy",
    "PBXResourcesBuildPhase",
    "PBXShellScriptBuildPhase",
    "PBXSourcesBuildPhase",
    "PBXTarget",
    "PBXTargetDependency",
    "PBXVariantGroup",
    "Scheme",
    "XCBuildConfiguration",
    "XCConfigurationList",
    "XCVersionGroup",
    "XcodeProject",
    "__version__",
]

PBXObjectType = TypeVar("PBXObjectType", bound=PBXObject)


def _load_pbxproj_as_json(path: str) -> dict[str, Any]:
    """Load a pbxproj as JSON.

    :param path: The path to the pbxproj

    :returns: A deserialized representation of the pbxproj
    """

    content = subprocess.run(
        [
            "plutil",
            "-convert",
            "json",
            os.path.join(path, "project.pbxproj"),
            "-o",
            "-",
        ],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    return cast(dict[str, Any], json.loads(content))


class XcodeProject:
    """Represents an Xcodeproject.

    :param path: The path to the pbxproj file
    """

    path: str
    source_root: str
    objects: Objects
    project: PBXProject
    _cached_items: dict[str, dict[str, PBXObject]]
    _schemes: list[Scheme] | None
    _is_populated: bool

    def __init__(self, path: str, *, ignore_deserialization_errors: bool = False) -> None:
        self.path = path
        self.source_root = os.path.dirname(path)
        tree = _load_pbxproj_as_json(path)

        for key, value in tree["objects"].items():
            value["object_key"] = key

        self.objects = Objects(
            **deserialize.deserialize(
                dict[str, PBXObject],
                tree["objects"],
                throw_on_unhandled=not ignore_deserialization_errors,
                raw_storage_mode=deserialize.RawStorageMode.ALL,
            )
        )

        self.project = cast(PBXProject, self.objects[tree["rootObject"]])
        self._cached_items = {}
        self._schemes = None
        self._is_populated = False

        self._set_weak_refs()

    @staticmethod
    def from_cache(project_path: str, *, ignore_deserialization_errors: bool = False) -> "XcodeProject":
        """Attempt to load the project from a cached folder if possible.

        :param project_path: The path to the actual project (in case it's a cache miss)

        :returns: The loaded XcodeProj
        """

        cache_folder = platformdirs.user_cache_dir("xcodeproj")

        try:
            project_hash = hashlib.md5(
                pathlib.Path(os.path.join(project_path, "project.pbxproj")).read_bytes(),
                usedforsecurity=False,
            ).hexdigest()

            with open(os.path.join(cache_folder, f"{project_hash}.dat"), "rb") as cached_file:
                return pickle.load(cached_file)
        except Exception:
            return XcodeProject(
                project_path,
                ignore_deserialization_errors=ignore_deserialization_errors,
            )

    def write_cache(self) -> None:
        """Write out this file to a cache

        :param cache_folder: The folder to store the cached project in.
        """
        self.populate_paths()

        cache_folder = platformdirs.user_cache_dir("xcodeproj")
        os.makedirs(cache_folder, exist_ok=True)

        project_hash = hashlib.md5(
            pathlib.Path(os.path.join(self.path, "project.pbxproj")).read_bytes(), usedforsecurity=False
        ).hexdigest()

        with open(os.path.join(cache_folder, f"{project_hash}.dat"), "wb") as cached_file:
            pickle.dump(self, cached_file)

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Restore state from the unpickled state values."""
        self.__dict__ = state
        self._set_weak_refs()

    def _set_weak_refs(self) -> None:
        """Setup the weak references."""
        for obj in self.objects.values():
            obj.objects_ref = weakref.ref(self.objects)
            obj.project_ref = weakref.ref(self)

    def _populate_cache(self, object_type: type[PBXObject]) -> None:
        """Populate the cache of items specified.

        This just avoids a full dictionary scan

        :param object_type: The type of objects to populate
        """

        if object_type.__name__ in self._cached_items:
            return

        cached_items: dict[str, PBXObject] = {}

        for object_key, project_object in self.objects.items():
            if not isinstance(project_object, object_type):
                continue

            cached_items[object_key] = project_object

        self._cached_items[object_type.__name__] = cached_items

    def _populate(
        self,
        parent_group: PBXPathObject,
        path: str | None,
        non_set: list[PBXPathObject],
    ) -> None:
        if path is not None:
            parent_group._relative_path = path

        if not isinstance(parent_group, PBXGroup):
            return

        for subgroup in parent_group.children:
            if subgroup.source_tree == "SOURCE_ROOT":
                self._populate(subgroup, subgroup.path, non_set)
            elif subgroup.source_tree == "<group>":
                if subgroup.path is None:
                    if path is None:
                        self._populate(subgroup, path, non_set)
                    else:
                        non_set.append(subgroup)
                elif path is not None:
                    self._populate(subgroup, os.path.join(path, subgroup.path), non_set)
                else:
                    self._populate(subgroup, subgroup.path, non_set)
            else:
                non_set.append(subgroup)

    def populate_paths(self) -> None:
        """Pre-emptively populate group paths.

        This method is from the top down so is much quicker.
        """

        if self._is_populated:
            return

        non_set: list[PBXPathObject] = []

        root_group = cast(PBXPathObject, self.objects[self.project.main_group_id])
        self._populate(root_group, None, non_set)

        for item in non_set:
            _ = item.relative_path()

        self._is_populated = True

    def fetch_type(self, object_type: type[PBXObjectType]) -> dict[str, PBXObjectType]:
        """Load the items specified from the cache, populating the cache if required.

        :param object_type: The type of objects to get

        :returns: The type from the cache
        """
        self._populate_cache(object_type)
        return cast(dict[str, PBXObjectType], self._cached_items[object_type.__name__])

    def targets(self) -> list[PBXNativeTarget]:
        """Get the targets.

        :returns: A list of targets
        """
        return list(self.fetch_type(PBXNativeTarget).values())

    def target_by_name(self, name: str) -> PBXNativeTarget | None:
        """Get a target by name.

        :param str name: The name of the target to find

        :returns: The target if found, else None
        """
        for target in self.fetch_type(PBXNativeTarget).values():
            if target.name == name:
                return target
        return None

    def target_containing_phase(self, source_build_phase_ref: str) -> PBXNativeTarget | None:
        """Find the target containing the Source Build Phase
        :param source_build_phase_ref: The reference of the parent

        :returns: The target containing the source build phase
        """
        for native_target in self.fetch_type(PBXNativeTarget).values():
            for build_phase in native_target.build_phases:
                if build_phase.object_key == source_build_phase_ref:
                    return native_target
        return None

    def build_configuration_list_for_target(self, native_target_name: str) -> XCConfigurationList | None:
        """Searches for build configuration via a target's name

        :param native_target_name: The name of the native target to find

        :returns: The build configuration
        """

        for native_target in self.fetch_type(PBXNativeTarget).values():
            if native_target_name != native_target.name:
                continue

            return native_target.build_configuration_list

        return None

    @property
    def schemes(self) -> list[Scheme]:
        """Load the schemes for the project.

        :returns: A list of schemes
        """
        if self._schemes is not None:
            return self._schemes

        scheme_paths: list[str] = []

        for path, _, files in os.walk(self.path):
            for file_path in files:
                if not file_path.endswith(".xcscheme"):
                    continue
                scheme_paths.append(os.path.join(path, file_path))

        all_schemes: list[Scheme] = []

        for scheme_path in scheme_paths:
            all_schemes.append(Scheme.from_file(scheme_path))

        self._schemes = all_schemes

        return all_schemes
