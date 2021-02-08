"""PBX object types"""

import enum
from typing import cast, Iterator, List, Optional

import deserialize

from .pbxobject import PBXObject
from .buildphases import PBXBuildPhase


class PBXProductType(enum.Enum):
    """The different product types available."""

    # fmt: off
    application          = "com.apple.product-type.application"
    bundle               = "com.apple.product-type.bundle"
    uitesting_bundle     = "com.apple.product-type.bundle.ui-testing"
    unit_test            = "com.apple.product-type.bundle.unit-test"
    static_library       = "com.apple.product-type.library.static"
    library_bundle       = "com.apple.product-type.library.bundle"
    framework            = "com.apple.product-type.framework"
    app_extension        = "com.apple.product-type.app-extension"
    watch_app2           = "com.apple.product-type.application.watchapp2"
    watch_app2_container = "com.apple.product-type.application.watchapp2-container"
    watchkit2_extension  = "com.apple.product-type.watchkit2-extension"
    # fmt: on


@deserialize.key("build_phases_ids", "buildPhases")
@deserialize.auto_snake()
class PBXTarget(PBXObject):
    """Represents a PBXAggregateTarget."""

    build_configuration_list: str
    build_phases_ids: List[str]
    dependencies: List[str]
    name: str
    product_name: Optional[str]

    def build_phases(self) -> Iterator[PBXBuildPhase]:
        """Get the build phases in the target."""
        for phase_id in self.build_phases_ids:
            yield cast(PBXBuildPhase, self.objects()[phase_id])


@deserialize.downcast_identifier(PBXObject, "PBXAggregateTarget")
class PBXAggregateTarget(PBXTarget):
    """Represents a PBXAggregateTarget."""


@deserialize.auto_snake()
@deserialize.downcast_identifier(PBXObject, "PBXNativeTarget")
class PBXNativeTarget(PBXTarget):
    """Represents a PBXNativeTarget.

    This is the corresponding target type to an aggregate target.
    """

    build_rules: Optional[List[str]]
    product_reference: str
    product_type: PBXProductType
