"""PBX object types"""

from typing import Any, Callable, cast, Dict

import deserialize


@deserialize.allow_unhandled("isa")
@deserialize.downcast_field("isa")
@deserialize.allow_downcast_fallback()
@deserialize.ignore("objects_ref")
@deserialize.ignore("project_ref")
class PBXObject:
    """Base class for an object in a PBX Project file.

    :param object_key: The key for the object.
    """

    object_key: str
    objects_ref: Callable[[], Dict[str, "PBXObject"]]
    project_ref: Callable[[], Any]

    def objects(self) -> Dict[str, "PBXObject"]:
        """Resolve objects reference.

        :returns: Resolved objects dictionary
        """
        reference = getattr(self, "objects_ref")
        return cast(Dict[str, "PBXObject"], reference())

    def project(self) -> Any:
        """Resolve objects reference.

        :returns: Resolved objects dictionary
        """
        reference = getattr(self, "project_ref")
        return reference()
