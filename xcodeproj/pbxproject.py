"""PBXProject object."""

from typing import Any, cast, Dict, Iterator, List

import deserialize

from .pbxobject import PBXObject
from .targets import PBXTarget


@deserialize.downcast_identifier(PBXObject, "PBXProject")
@deserialize.parser("has_scanned_for_encodings", lambda x: {"0": False, "1": True}[x])
@deserialize.key("target_ids", "targets")
@deserialize.auto_snake()
class PBXProject(PBXObject):
    """Represents a PBXProject.

    This is the root object.
    """

    attributes: Dict[str, Any]
    build_configuration_list: str
    compatibility_version: str
    development_region: str
    has_scanned_for_encodings: bool
    known_regions: List[str]
    main_group: str
    product_ref_group: str
    project_dir_path: str
    project_root: str
    target_ids: List[str]

    def targets(self) -> Iterator[PBXTarget]:
        """Get the targets in the project."""
        for target_id in self.target_ids:
            yield cast(PBXTarget, self.objects()[target_id])
