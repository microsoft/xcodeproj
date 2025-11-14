"""PBX build phases"""

import deserialize

from .pbxobject import PBXObject


@deserialize.auto_snake()
@deserialize.parser("isEditable", lambda x: {"0": False, "1": True}[x])
@deserialize.downcast_identifier(PBXObject, "PBXBuildRule")
class PBXBuildRule(PBXObject):
    """Represents a PBXBuildRule."""

    compiler_spec: str
    file_type: str
    input_files: list[str]
    output_files: list[str]
    is_editable: bool
    script: str
