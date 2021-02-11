"""PBX object types"""

from typing import Any, cast, Dict, List, Optional

import deserialize

from .pbxobject import PBXObject


@deserialize.key("base_configuration_reference_id", "baseConfigurationReference")
@deserialize.key("build_settings", "buildSettings")
@deserialize.downcast_identifier(PBXObject, "XCBuildConfiguration")
class XCBuildConfiguration(PBXObject):
    """Represents an XCBuildConfiguration.

    This is the raw build settings for a build configuration. Name is usually
    "Debug" or "Release".
    """

    base_configuration_reference_id: Optional[str]
    build_settings: Dict[str, Any]
    name: str

    @property
    def base_configuration(self) -> Optional["XCBuildConfiguration"]:
        """Get the base configuration for this build configureation.

        :returns: The base configuration
        """

        if not self.base_configuration_reference_id:
            return None

        return cast(XCBuildConfiguration, self.objects()[self.base_configuration_reference_id])


@deserialize.key("build_configuration_ids", "buildConfigurations")
@deserialize.key("default_configuration_is_visible", "defaultConfigurationIsVisible")
@deserialize.key("default_configuration_name", "defaultConfigurationName")
@deserialize.parser("defaultConfigurationIsVisible", lambda x: {"0": False, "1": True}[x])
@deserialize.downcast_identifier(PBXObject, "XCConfigurationList")
class XCConfigurationList(PBXObject):
    """Represents an XCConfigurationList.

    This is a list of build configurations. Usually associated with a target.
    """

    build_configuration_ids: List[str]
    default_configuration_is_visible: bool
    default_configuration_name: str

    @property
    def build_configurations(self) -> List[XCBuildConfiguration]:
        """Get all the build configurations for this list.

        :returns: The build configurations
        """
        return [
            cast(XCBuildConfiguration, self.objects()[build_configuration_id])
            for build_configuration_id in self.build_configuration_ids
        ]
