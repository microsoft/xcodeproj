"""Objects custom type for type hinting."""

from collections.abc import MutableMapping
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pbxobject import PBXObject


class Objects(dict[str, "PBXObject"], MutableMapping[str, "PBXObject"]):  # type: ignore
    """Holds the objects in the pbxproj."""
