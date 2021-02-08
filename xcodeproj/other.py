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
    target: str
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
