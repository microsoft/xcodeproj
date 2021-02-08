"""PBX object types"""

from typing import Any, Dict, List, Optional

import deserialize

from .pbxobject import PBXObject


@deserialize.key("build_configurations", "buildConfigurations")
@deserialize.key("default_configuration_is_visible", "defaultConfigurationIsVisible")
@deserialize.key("default_configuration_name", "defaultConfigurationName")
@deserialize.parser("defaultConfigurationIsVisible", lambda x: {"0": False, "1": True}[x])
@deserialize.downcast_identifier(PBXObject, "XCConfigurationList")
class XCConfigurationList(PBXObject):
    """Represents an XCConfigurationList.

    This is a list of build configurations. Usually associated with a target.
    """

    build_configurations: List[str]
    default_configuration_is_visible: bool
    default_configuration_name: str


@deserialize.key("base_configuration_reference", "baseConfigurationReference")
@deserialize.key("build_configuration_reference", "buildConfigurationReference")
@deserialize.key("build_settings", "buildSettings")
@deserialize.downcast_identifier(PBXObject, "XCBuildConfiguration")
class XCBuildConfiguration(PBXObject):
    """Represents an XCBuildConfiguration.

    This is the raw build settings for a build configuration. Name is usually
    "Debug" or "Release".
    """

    base_configuration_reference: Optional[str]
    build_configuration_reference: Optional[str]
    build_settings: Dict[str, Any]
    name: str
