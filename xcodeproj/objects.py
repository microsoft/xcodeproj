"""Objects custom type for type hinting."""

from typing import MutableMapping
from .pbxobject import PBXObject


class Objects(dict[str, PBXObject], MutableMapping[str, PBXObject]):  # type: ignore
    """Holds the objects in the pbxproj."""
