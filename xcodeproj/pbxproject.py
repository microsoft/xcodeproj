"""PBXProject object."""

from typing import Any, cast, Dict, List, Optional

import deserialize

from .pathobjects import PBXGroup
from .pbxobject import PBXObject
from .targets import PBXTarget
from .xcobjects import XCConfigurationList


@deserialize.downcast_identifier(PBXObject, "PBXProject")
@deserialize.parser("has_scanned_for_encodings", lambda x: {"0": False, "1": True}[x])
@deserialize.key("target_ids", "targets")
@deserialize.key("main_group_id", "mainGroup")
@deserialize.key("build_configuration_list_id", "buildConfigurationList")
@deserialize.auto_snake()
class PBXProject(PBXObject):
    """Represents a PBXProject.

    This is the root object.
    """

    attributes: Dict[str, Any]
    build_configuration_list_id: str
    compatibility_version: str
    development_region: str
    has_scanned_for_encodings: bool
    known_regions: List[str]
    main_group_id: str
    product_ref_group: Optional[str]
    project_dir_path: str
    project_root: str
    target_ids: List[str]

    @property
    def targets(self) -> List[PBXTarget]:
        """Get the targets in the project."""
        return [cast(PBXTarget, self.objects()[target_id]) for target_id in self.target_ids]

    @property
    def main_group(self) -> PBXGroup:
        """Get the main group in the project."""
        return cast(PBXGroup, self.objects()[self.main_group_id])

    @property
    def build_configuration_list(self) -> XCConfigurationList:
        """Get the build configuration list for the project."""
        return cast(XCConfigurationList, self.objects()[self.build_configuration_list_id])
