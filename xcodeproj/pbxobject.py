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

    def __getstate__(self):
        """Return state values to be pickled."""
        new_dict = {}
        for key, value in self.__dict__.items():
            if key in ["objects_ref", "project_ref"]:
                continue
            new_dict[key] = value
        return new_dict

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

    def __eq__(self, other: object) -> bool:
        """Determine if the supplied object is equal to self.

        :param other: The object to compare to self

        :returns: True if they are equal, False otherwise.
        """

        if not isinstance(other, type(self)):
            return False

        return self.object_key == other.object_key

    def __hash__(self) -> int:
        """Calculate the hash of the object

        :returns: The hash value of the object
        """

        return hash(self.object_key)
