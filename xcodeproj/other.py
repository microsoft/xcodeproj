"""PBX object types"""

from typing import Optional

import deserialize

from .pbxobject import PBXObject


@deserialize.auto_snake()
@deserialize.downcast_identifier(PBXObject, "PBXTargetDependency")
class PBXTargetDependency(PBXObject):
    """Represents a PBXTargetDependency.

    Tracks dependencies between targets.
    """

    name: Optional[str]
    platform_filter: Optional[str]
    target: Optional[str]
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
@deserialize.downcast_identifier(PBXObject, "PBXReferenceProxy")
class PBXReferenceProxy(PBXObject):
    """Represents a PBXReferenceProxy.

    It's not clear what this one is. As far as I can tell, it references
    something in another project in the same workspace.
    """

    file_type: str
    path: str
    remote_ref: str
    source_tree: str


@deserialize.auto_snake()
class ProjectReference:
    """A reference to another project."""

    product_group: str
    project_ref: str
