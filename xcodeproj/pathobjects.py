"""PBX path objects"""

import os
from typing import cast, List, Optional

import deserialize

from .pbxobject import PBXObject

# pylint: disable=no-member


@deserialize.key("source_tree", "sourceTree")
@deserialize.ignore("_parent_group_reference")
@deserialize.downcast_identifier(PBXObject, "PBXPathObject")
class PBXPathObject(PBXObject):
    """Represents an object with a path (i.e. file or group)."""

    path: Optional[str]
    source_tree: str

    _parent_group_reference: Optional[str]
    _full_path: Optional[str]

    def parent_group(self) -> Optional["PBXGroup"]:
        """Find the parent group of a reference.

        If a reference happens to be in multiple groups, only the first found
        instance will be returned.

        :returns: The parent group if found, None otherwise
        """

        if (
            hasattr(self, "_parent_group_reference")
            and getattr(self, "_parent_group_reference") is not None
        ):
            return cast(PBXGroup, self.project().objects[getattr(self, "_parent_group_reference")])

        for group in self.project().fetch_type(PBXGroup).values():
            if self in group.children:
                setattr(self, "_parent_group_reference", group.object_key)
                return group

        for group in self.project().fetch_type(PBXVariantGroup).values():
            if self in group.children:
                setattr(self, "_parent_group_reference", group.object_key)
                return group

        for group in self.project().fetch_type(XCVersionGroup).values():
            if self in group.children:
                setattr(self, "_parent_group_reference", group.object_key)
                return group

        return None

    def relative_path(self) -> Optional[str]:
        """Get the relative path for the group to the source root

        This works by getting the current references path, then searching up the
        tree, constructing the path as we go, until the root object is found.

        NOTE: This may contain a variable such as `$(BUILT_PRODUCTS_DIR)`

        :raises Exception: If an unexpected source tree is found

        :returns: The path if found, None otherwise
        """

        # pylint: disable=too-many-return-statements

        if hasattr(self, "_relative_path"):
            cached_path = getattr(self, "_relative_path")
            if cached_path is not None:
                return cast(str, cached_path)

        if self.source_tree == "SOURCE_ROOT":
            setattr(self, "_relative_path", self.path)
            return cast(str, self.path)

        if self.source_tree != "<group>":
            if self.source_tree in ["BUILT_PRODUCTS_DIR", "SDKROOT", "DEVELOPER_DIR"]:
                return f"$({self.source_tree})"
            raise Exception(f"Unexpected source tree: {self.source_tree}")

        parent = self.parent_group()

        if not parent:
            return None

        parent_path = parent.relative_path()

        if self.path is None:
            setattr(self, "_relative_path", parent_path)
            return parent_path

        if parent_path is None:
            setattr(self, "_relative_path", self.path)
            return self.path

        value = os.path.join(parent_path, self.path)
        setattr(self, "_relative_path", value)

        return value

        # pylint: enable=too-many-return-statements

    def absolute_path(self) -> Optional[str]:
        """Find the absolute path

        :returns: The absolute path of the object
        """

        path = self.relative_path()

        if path is None:
            return None

        return os.path.join(self.project().source_root, path)


@deserialize.key("indent_width", "indentWidth")
@deserialize.key("tab_width", "tabWidth")
@deserialize.key("uses_tabs", "usesTabs")
@deserialize.key("children_ids", "children")
@deserialize.ignore("_path")
@deserialize.parser("indentWidth", lambda x: int(x) if x else None)
@deserialize.parser("tabWidth", lambda x: int(x) if x else None)
@deserialize.parser("usesTabs", lambda x: int(x) > 0 if x else False)
@deserialize.downcast_identifier(PBXObject, "PBXGroup")
class PBXGroup(PBXPathObject):
    """Represents a PBXGroup.

    This is a group in the Xcode file explorer.
    """

    children_ids: List[str]
    indent_width: Optional[int]
    tab_width: Optional[int]
    uses_tabs: Optional[bool]
    name: Optional[str]

    @property
    def children(self) -> List[PBXPathObject]:
        """Get all the children for this group.

        :returns: The children for this group
        """
        return [cast(PBXPathObject, self.objects()[child_id]) for child_id in self.children_ids]


@deserialize.downcast_identifier(PBXObject, "PBXVariantGroup")
class PBXVariantGroup(PBXGroup):
    """Represents a PBXVariantGroup.

    These are similar to groups but are not backed by a folder on disk. This may
    be a deliberate choice, or it may be used to represent something like a
    .strings file, where the "file" can be expanded to see each language.
    """

    name: str


@deserialize.key("file_encoding", "fileEncoding")
@deserialize.key("last_known_file_type", "lastKnownFileType")
@deserialize.key("line_ending", "lineEnding")
@deserialize.key("indent_width", "indentWidth")
@deserialize.key("tab_width", "tabWidth")
@deserialize.key("xc_language_specification_identifier", "xcLanguageSpecificationIdentifier")
@deserialize.key("explicit_file_type", "explicitFileType")
@deserialize.key("include_in_index", "includeInIndex")
@deserialize.parser("fileEncoding", lambda x: int(x) if x else None)
@deserialize.downcast_identifier(PBXObject, "PBXFileReference")
class PBXFileReference(PBXPathObject):
    """Represents a PBXFileReference.

    The details of a particular file.
    """

    file_encoding: Optional[int]
    last_known_file_type: Optional[str]
    line_ending: Optional[str]
    indent_width: Optional[str]
    tab_width: Optional[str]
    name: Optional[str]
    xc_language_specification_identifier: Optional[str]
    explicit_file_type: Optional[str]
    include_in_index: Optional[str]


@deserialize.auto_snake()
@deserialize.key("child_ids", "children")
@deserialize.downcast_identifier(PBXObject, "XCVersionGroup")
class XCVersionGroup(PBXPathObject):
    """Represents an XCVersion group

    These groups have versioned files in them
    """

    child_ids: List[str]
    current_version: str
    version_group_type: str
    name: Optional[str]

    @property
    def children(self) -> List[PBXPathObject]:
        """Get all the children for this group.

        :returns: The children for this group
        """
        return [cast(PBXPathObject, self.objects()[child_id]) for child_id in self.child_ids]
