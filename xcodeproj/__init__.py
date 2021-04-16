"""Xcode project file management."""

try:
    import _pickle as pickle
except ImportError:
    import pickle  # type: ignore

from collections import defaultdict
import functools
import hashlib
import json
import os
import pathlib
from typing import (
    Any,
    cast,
    Dict,
    List,
    MutableMapping,
    Optional,
    Type,
    TypeVar,
)
import subprocess
import weakref

import deserialize

from .pbxobject import PBXObject
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
from .pathobjects import (
    PBXPathObject,
    PBXGroup,
    PBXVariantGroup,
    PBXFileReference,
    XCVersionGroup,
)
from .pbxproject import PBXProject
from .other import PBXTargetDependency, PBXContainerItemProxy
from .schemes import Scheme
from .targets import PBXAggregateTarget, PBXNativeTarget, PBXProductType
from .xcobjects import XCBuildConfiguration, XCConfigurationList


PBXObjectType = TypeVar("PBXObjectType", bound=PBXObject)


def _load_pbxproj_as_json(path: str) -> Dict[str, Any]:
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
    return cast(Dict[str, Any], json.loads(content))


class Objects(dict, MutableMapping[str, PBXObject]):
    """Holds the objects in the pbxproj."""


class XcodeProject:
    """Represents an Xcodeproject.

    :param path: The path to the pbxproj file
    """

    path: str
    source_root: str
    objects: Objects
    project: PBXProject
    _cached_items: Dict[str, Dict[str, PBXObject]]
    _schemes: Optional[List[Scheme]]
    _is_populated: bool

    def __init__(self, path: str) -> None:
        self.path = path
        self.source_root = os.path.dirname(path)
        tree = _load_pbxproj_as_json(path)

        for key, value in tree["objects"].items():
            value["object_key"] = key

        self.objects = Objects(
            **deserialize.deserialize(
                Dict[str, PBXObject],
                tree["objects"],
                throw_on_unhandled=True,
                raw_storage_mode=deserialize.RawStorageMode.all,
            )
        )

        self.project = self.objects[tree["rootObject"]]
        self._cached_items = {}
        self._schemes = None
        self._is_populated = False

        self._set_weak_refs()

    @staticmethod
    def from_cache(cache_folder: str, project_path: str) -> "XcodeProject":
        """Attempt to load the project from a cached folder if possible.

        :param cache_folder: The folder the cached projects live in
        :param project_path: The path to the actual project (in case it's a cache miss)

        :returns: The loaded XcodeProj
        """
        try:
            project_hash = hashlib.md5(
                pathlib.Path(os.path.join(project_path, "project.pbxproj")).read_bytes()
            ).hexdigest()

            with open(os.path.join(cache_folder, f"{project_hash}.dat"), "rb") as cached_file:
                return pickle.load(cached_file)
        except Exception:
            return XcodeProject(project_path)

    def write_cache(self, cache_folder: str) -> None:
        """Write out this file to a cache

        :param cache_folder: The folder to store the cached project in.
        """
        self.populate_paths()

        project_hash = hashlib.md5(
            pathlib.Path(os.path.join(self.path, "project.pbxproj")).read_bytes()
        ).hexdigest()

        with open(os.path.join(cache_folder, f"{project_hash}.dat"), "wb") as cached_file:
            pickle.dump(self, cached_file)

    def __setstate__(self, state):
        """Restore state from the unpickled state values."""
        self.__dict__ = state
        self._set_weak_refs()

    def _set_weak_refs(self) -> None:
        """Setup the weak references."""
        for obj in self.objects.values():
            obj.objects_ref = weakref.ref(self.objects)
            obj.project_ref = weakref.ref(self)

    def _populate_cache(self, object_type: Type[PBXObject]) -> None:
        """Populate the cache of items specified.

        This just avoids a full dictionary scan

        :param object_type: The type of objects to populate
        """

        if object_type.__name__ in self._cached_items:
            return

        cached_items: Dict[str, PBXObject] = {}

        for object_key, project_object in self.objects.items():

            if not isinstance(project_object, object_type):
                continue

            cached_items[object_key] = project_object

        self._cached_items[object_type.__name__] = cached_items

    def populate_paths(self) -> None:
        """Pre-emptively populate group paths.

        This method is from the top down so is much quicker.
        """

        if self._is_populated:
            return

        non_set = []

        def populate(parent_group: PBXPathObject, path: Optional[str]) -> None:
            nonlocal non_set

            if path is not None:
                setattr(parent_group, "_relative_path", path)

            if not isinstance(parent_group, PBXGroup):
                return

            for subgroup in parent_group.children:
                if subgroup.source_tree == "SOURCE_ROOT":
                    populate(subgroup, subgroup.path)
                elif subgroup.source_tree == "<group>":
                    if subgroup.path is None:
                        if path is None:
                            populate(subgroup, path)
                        else:
                            non_set.append(subgroup)
                    else:
                        if path is not None:
                            populate(subgroup, os.path.join(path, subgroup.path))
                        else:
                            populate(subgroup, subgroup.path)
                else:
                    non_set.append(subgroup)

        root_group = self.objects[self.project.main_group_id]
        populate(root_group, None)

        for item in non_set:
            _ = item.relative_path()

        self._is_populated = True

    def fetch_type(self, object_type: Type[PBXObjectType]) -> Dict[str, PBXObjectType]:
        """Load the items specified from the cache, populating the cache if required.

        :param object_type: The type of objects to get

        :returns: The type from the cache
        """
        self._populate_cache(object_type)
        return cast(Dict[str, PBXObjectType], self._cached_items[object_type.__name__])

    def targets(self) -> List[PBXNativeTarget]:
        """Get the targets.

        :returns: A list of targets
        """
        return list(self.fetch_type(PBXNativeTarget).values())

    def target_by_name(self, name: str) -> Optional[PBXNativeTarget]:
        """Get a target by name.

        :param str name: The name of the target to find

        :returns: The target if found, else None
        """
        for target in self.fetch_type(PBXNativeTarget).values():
            if target.name == name:
                return target
        return None

    def target_containing_phase(self, source_build_phase_ref: str) -> Optional[PBXNativeTarget]:
        """Find the target containing the Source Build Phase
        :param source_build_phase_ref: The reference of the parent

        :returns: The target containing the source build phase
        """
        for native_target in self.fetch_type(PBXNativeTarget).values():
            for build_phase in native_target.build_phases:
                if build_phase.object_key == source_build_phase_ref:
                    return native_target
        return None

    def build_configuration_list_for_target(
        self, native_target_name: str
    ) -> Optional[XCConfigurationList]:
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
    def schemes(self) -> List[Scheme]:
        """Load the schemes for the project.

        :returns: A list of schemes
        """
        if self._schemes is not None:
            return self._schemes

        scheme_paths = []

        for path, _, files in os.walk(self.path):
            for file_path in files:
                if not file_path.endswith(".xcscheme"):
                    continue
                scheme_paths.append(os.path.join(path, file_path))

        all_schemes: List[Scheme] = []

        for scheme_path in scheme_paths:
            all_schemes.append(Scheme.from_file(scheme_path))

        self._schemes = all_schemes

        return all_schemes
