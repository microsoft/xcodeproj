"""PBX path objects"""

import os
from typing import cast, Optional

import deserialize

from .pbxobject import PBXObject

# pylint: disable=no-member


@deserialize.key("source_tree", "sourceTree")
@deserialize.ignore("_parent_group_reference")
@deserialize.downcast_identifier(PBXObject, "PBXPathObject")
class PBXPathObject(PBXObject):
    """Represents an object with a path (i.e. file or group)."""

    path: str | None
    source_tree: str

    _parent_group_reference: str | None
    _relative_path: str | None

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
            return cast(
                PBXGroup,
                self.project().objects[getattr(self, "_parent_group_reference")],
            )

        group_types_to_check: list[type] = [
            PBXGroup,
            PBXVariantGroup,
            XCVersionGroup,
        ]

        for group_type in group_types_to_check:
            for group in self.project().fetch_type(group_type).values():
                if self in group.children:
                    setattr(self, "_parent_group_reference", group.object_key)
                    return group

        return None

    def relative_path(self) -> str | None:
        """Get the relative path for the group to the source root

        This works by getting the current references path, then searching up the
        tree, constructing the path as we go, until the root object is found.

        NOTE: This may contain a variable such as `$(BUILT_PRODUCTS_DIR)`

        :raises Exception: If an unexpected source tree is found

        :returns: The path if found, None otherwise
        """

        # pylint: disable=too-many-return-statements

        if hasattr(self, "_relative_path") and self._relative_path is not None:
            return self._relative_path

        if self.source_tree == "SOURCE_ROOT":
            setattr(self, "_relative_path", self.path)
            return cast(str, self.path)

        if self.source_tree == "<absolute>":
            if self.path and not self.path.startswith(os.sep):
                setattr(self, "_relative_path", self.path)
            return self.path

        if self.source_tree != "<group>":
            if self.source_tree in ["BUILT_PRODUCTS_DIR", "SDKROOT", "DEVELOPER_DIR"]:
                return self.path
            raise Exception(f"Unexpected source tree: {self.source_tree}")

        # Ok, it now gets incredible hairy. Essentially, a file has either its own path, or it has
        # a path relative to its parent. However, the parent may not have a path and be "virtual".
        # In that case, we need to determine the grandparent's path to use as the base. This is a
        # recursive process. Once we get to the root, we can't make any assumptions, so assume the
        # relative path to be the empty string.

        parent = self.parent_group()

        if not parent:
            base_path_for_self = ""
        else:
            parent_folder_path = parent.relative_path()
            if parent_folder_path is None:
                # If there's no parent relative path, then we have no path relative to anything else
                base_path_for_self = ""
            elif parent.path is not None:
                # If there is a parent path and , we use it as the base path
                base_path_for_self = parent_folder_path
            else:
                # Parent is a "virtual" group (no 'path' attribute)
                child_path_includes_virtual_parent_name = False

                # Check if the child's path includes the parent's name
                if parent.name and self.path:
                    if self.path == parent.name or self.path.startswith(parent.name + os.sep):
                        child_path_includes_virtual_parent_name = True

                # If the child's path includes the parent's name, we need to determine
                # the base path for this child.
                if child_path_includes_virtual_parent_name:
                    # Child's path (e.g., "VirtualGroupName/File.swift") already includes the virtual parent's name.
                    # So, the base path for this child is the parent's container (grandparent's folder).
                    grandparent = parent.parent_group()
                    if not grandparent or grandparent.relative_path() is None:
                        # Virtual parent is main group or orphan. Either way, its container is effectively root.
                        base_path_for_self = ""
                    else:
                        base_path_for_self = grandparent.relative_path()
                else:
                    # Parent is virtual, but child's path does not start with parent's name
                    # (e.g., parent "Commands", child path "MyFile.swift").
                    # So, child is inside the folder conceptually represented by the virtual parent.
                    base_path_for_self = parent_folder_path

        # Determine the path segment contributed by this object itself
        if isinstance(self, PBXGroup):
            # For a group, if it's the main group and has no path/name, it contributes nothing.
            if (
                self.project().project.main_group_id == self.object_key
                and not self.path
                and not self.name
            ):
                current_segment_from_self = None
            else:
                current_segment_from_self = self.path
        else:  # PBXFileReference or other similar types
            current_segment_from_self = self.path

        if current_segment_from_self is None:
            calculated_path = base_path_for_self
        else:
            if base_path_for_self == "" and current_segment_from_self.startswith(os.sep):
                # Avoid os.path.join("", "/abs/path") becoming "//abs/path"
                calculated_path = current_segment_from_self
            else:
                assert base_path_for_self is not None
                calculated_path = os.path.join(base_path_for_self, current_segment_from_self)

        setattr(self, "_relative_path", calculated_path)
        return calculated_path
        # pylint: enable=too-many-return-statements

    def absolute_path(self) -> str | None:
        """Find the absolute path

        :returns: The absolute path of the object
        """

        path = self.relative_path()

        if path is None:
            return None

        if path.startswith("/"):
            return path

        if self.source_tree in ["BUILT_PRODUCTS_DIR", "SDKROOT", "DEVELOPER_DIR"]:
            if self.path:
                return os.path.join(f"$({self.source_tree})", self.path)

            return f"$({self.source_tree})"

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

    children_ids: list[str]
    indent_width: int | None
    tab_width: int | None
    uses_tabs: bool | None
    name: str | None

    @property
    def children(self) -> list[PBXPathObject]:
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

    name: str  # type: ignore


@deserialize.key("file_encoding", "fileEncoding")
@deserialize.key("last_known_file_type", "lastKnownFileType")
@deserialize.key("line_ending", "lineEnding")
@deserialize.key("indent_width", "indentWidth")
@deserialize.key("tab_width", "tabWidth")
@deserialize.key("xc_language_specification_identifier", "xcLanguageSpecificationIdentifier")
@deserialize.key("explicit_file_type", "explicitFileType")
@deserialize.key("include_in_index", "includeInIndex")
@deserialize.key("wraps_lines", "wrapsLines")
@deserialize.parser("fileEncoding", lambda x: int(x) if x else None)
@deserialize.parser("wrapsLines", lambda x: None if x is None else {"0": False, "1": True}[x])
@deserialize.downcast_identifier(PBXObject, "PBXFileReference")
class PBXFileReference(PBXPathObject):
    """Represents a PBXFileReference.

    The details of a particular file.
    """

    file_encoding: int | None
    last_known_file_type: str | None
    line_ending: str | None
    indent_width: str | None
    tab_width: str | None
    wraps_lines: bool | None
    name: str | None
    xc_language_specification_identifier: str | None
    explicit_file_type: str | None
    include_in_index: str | None


@deserialize.auto_snake()
@deserialize.key("child_ids", "children")
@deserialize.downcast_identifier(PBXObject, "XCVersionGroup")
class XCVersionGroup(PBXPathObject):
    """Represents an XCVersion group

    These groups have versioned files in them
    """

    child_ids: list[str]
    current_version: str
    version_group_type: str
    name: str | None

    @property
    def children(self) -> list[PBXPathObject]:
        """Get all the children for this group.

        :returns: The children for this group
        """
        return [cast(PBXPathObject, self.objects()[child_id]) for child_id in self.child_ids]


@deserialize.auto_snake()
@deserialize.downcast_identifier(PBXObject, "PBXReferenceProxy")
class PBXReferenceProxy(PBXPathObject):
    """Represents a PBXReferenceProxy.

    It's not clear what this one is. As far as I can tell, it references
    something in another project in the same workspace.
    """

    file_type: str
    path: str  # type: ignore
    remote_ref: str
    source_tree: str


@deserialize.auto_snake()
@deserialize.key("explicit_file_types", "explicitFileTypes")
@deserialize.key("explicit_folders", "explicitFolders")
@deserialize.key("exception_ids", "exceptions")
@deserialize.downcast_identifier(PBXObject, "PBXFileSystemSynchronizedRootGroup")
class PBXFileSystemSynchronizedRootGroup(PBXPathObject):
    """Represents a PBXFileSystemSynchronizedRootGroup.

    A new feature in Xcode 16. It follows a group of files on disk to try and
    reduce merge conflicts in the pbxproj.
    """

    exception_ids: list[str]
    explicit_file_types: dict[str, str]
    explicit_folders: list[str]
