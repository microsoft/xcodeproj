"""PBX object types"""

import deserialize

from .pbxobject import PBXObject


@deserialize.auto_snake()
@deserialize.downcast_identifier(PBXObject, "PBXTargetDependency")
class PBXTargetDependency(PBXObject):
    """Represents a PBXTargetDependency.

    Tracks dependencies between targets.
    """

    name: str | None
    platform_filter: str | None
    target: str | None
    target_proxy: str


@deserialize.key("remote_global_id_string", "remoteGlobalIDString")
@deserialize.auto_snake()
@deserialize.downcast_identifier(PBXObject, "PBXContainerItemProxy")
class PBXContainerItemProxy(PBXObject):
    """Represents a PBXContainerItemProxy.

    This lets one item be a proxy for another. This is used to link items cross
    project for the most part, but appears to be used in other cases too.
    """

    container_portal: str
    proxy_type: str
    remote_global_id_string: str
    remote_info: str


@deserialize.auto_snake()
class ProjectReference:
    """A reference to another project."""

    product_group: str
    project_ref: str


@deserialize.auto_snake()
@deserialize.key("membership_exceptions", "membershipExceptions")
@deserialize.downcast_identifier(PBXObject, "PBXFileSystemSynchronizedBuildFileExceptionSet")
class PBXFileSystemSynchronizedBuildFileExceptionSet(PBXObject):
    """Represents a PBXFileSystemSynchronizedBuildFileExceptionSet.

    A new feature in Xcode 16. It follows a group of files on disk to try and
    reduce merge conflicts in the pbxproj.
    """

    membership_exceptions: list[str]
    target: str
