"""PBX object types"""

import enum
from typing import cast, List, Optional

import deserialize

from .pbxobject import PBXObject
from .buildphases import PBXBuildPhase
from .buildrules import PBXBuildRule
from .pathobjects import PBXFileReference
from .xcobjects import XCConfigurationList


class PBXProductType(enum.Enum):
    """The different product types available."""

    # fmt: off
    APPLICATION            = "com.apple.product-type.application"
    BUNDLE                 = "com.apple.product-type.bundle"
    UITESTING_BUNDLE       = "com.apple.product-type.bundle.ui-testing"
    UNIT_TEST              = "com.apple.product-type.bundle.unit-test"
    STATIC_LIBRARY         = "com.apple.product-type.library.static"
    LIBRARY_BUNDLE         = "com.apple.product-type.library.bundle"
    FRAMEWORK              = "com.apple.product-type.framework"
    STATIC_FRAMEWORK       = "com.apple.product-type.framework.static"
    APP_EXTENSION          = "com.apple.product-type.app-extension"
    APP_EXTENSION_MESSAGES = "com.apple.product-type.app-extension.messages"
    WATCH_APP2             = "com.apple.product-type.application.watchapp2"
    WATCH_APP2_CONTAINER   = "com.apple.product-type.application.watchapp2-container"
    WATCHKIT2_EXTENSION    = "com.apple.product-type.watchkit2-extension"
    # fmt: on


@deserialize.key("build_phases_ids", "buildPhases")
@deserialize.key("build_configuration_list_id", "buildConfigurationList")
@deserialize.key("dependency_ids", "dependencies")
@deserialize.auto_snake()
class PBXTarget(PBXObject):
    """Represents a PBXTarget."""

    build_configuration_list_id: str
    build_phases_ids: List[str]
    dependency_ids: List[str]
    name: str
    product_name: Optional[str]

    @property
    def build_phases(self) -> List[PBXBuildPhase]:
        """Get the build phases in the target."""
        return [cast(PBXBuildPhase, self.objects()[phase_id]) for phase_id in self.build_phases_ids]

    @property
    def build_configuration_list(self) -> XCConfigurationList:
        """Get the build configuration list for the target."""
        return cast(XCConfigurationList, self.objects()[self.build_configuration_list_id])

    @property
    def dependencies(self) -> List["PBXTarget"]:
        """Get the dependencies of the target."""
        return [
            cast(PBXTarget, self.objects()[dependency_id]) for dependency_id in self.dependency_ids
        ]


@deserialize.downcast_identifier(PBXObject, "PBXAggregateTarget")
class PBXAggregateTarget(PBXTarget):
    """Represents a PBXAggregateTarget."""


@deserialize.auto_snake()
@deserialize.key("product_reference_id", "productReference")
@deserialize.key("build_rule_ids", "buildRules")
@deserialize.downcast_identifier(PBXObject, "PBXNativeTarget")
class PBXNativeTarget(PBXTarget):
    """Represents a PBXNativeTarget.

    This is the corresponding target type to an aggregate target.
    """

    build_rule_ids: Optional[List[str]]
    product_reference_id: Optional[str]
    product_type: PBXProductType
    package_product_dependencies: Optional[List[str]]

    @property
    def product_reference(self) -> Optional[PBXFileReference]:
        """Get the product reference of the target."""
        if self.product_reference_id is None:
            return None
        return cast(PBXFileReference, self.objects()[self.product_reference_id])

    @property
    def build_rules(self) -> List[PBXBuildRule]:
        """Get the product reference of the target."""
        if self.build_rule_ids is None:
            return []

        return [
            cast(PBXBuildRule, self.objects()[build_rule_id])
            for build_rule_id in self.build_rule_ids
        ]
