"""PBX files"""

from typing import Any, cast, Dict, Optional

import deserialize

from .pbxobject import PBXObject
from .pathobjects import PBXFileReference


@deserialize.key("file_ref_id", "fileRef")
@deserialize.key("platform_filter", "platformFilter")
@deserialize.downcast_identifier(PBXObject, "PBXBuildFile")
class PBXBuildFile(PBXObject):
    """Represents a PBXBuildFile.

    These are files which are marked as for building in a phase, and are
    effectively pointers to a PBXFileReference which is an actual file.
    """

    file_ref_id: str
    platform_filter: Optional[str]
    settings: Optional[Dict[str, Any]]

    @property
    def file_ref(self) -> PBXFileReference:
        """Get the file reference.

        :returns: The file reference
        """
        return cast(PBXFileReference, self.objects()[self.file_ref_id])
