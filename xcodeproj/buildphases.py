"""PBX build phases"""

from typing import cast, List, Optional

import deserialize

from .pbxobject import PBXObject
from .files import PBXBuildFile


@deserialize.key("build_action_mask", "buildActionMask")
@deserialize.key("file_ids", "files")
@deserialize.key("run_only_for_deployment_post_processing", "runOnlyForDeploymentPostprocessing")
@deserialize.parser("runOnlyForDeploymentPostprocessing", lambda x: {"0": False, "1": True}[x])
@deserialize.downcast_identifier(PBXObject, "PBXBuildPhase")
class PBXBuildPhase(PBXObject):
    """Represents a PBXBuildPhase."""

    file_ids: List[str]
    build_action_mask: str
    run_only_for_deployment_post_processing: bool

    @property
    def files(self) -> List[PBXBuildFile]:
        """Get the files in the build phase."""
        return [cast(PBXBuildFile, self.objects()[file_id]) for file_id in self.file_ids]


@deserialize.downcast_identifier(PBXObject, "PBXSourcesBuildPhase")
class PBXSourcesBuildPhase(PBXBuildPhase):
    """Represents a PBXSourcesBuildPhase.

    This is a specific build phase for building sources. Several other phases
    exist.
    """


@deserialize.downcast_identifier(PBXObject, "PBXResourcesBuildPhase")
class PBXResourcesBuildPhase(PBXBuildPhase):
    """Represents a PBXResourcesBuildPhase.

    This is a specific build phase for copying resources. Several other phases
    exist.
    """


@deserialize.key("input_paths", "inputPaths")
@deserialize.key("output_paths", "outputPaths")
@deserialize.key("input_file_list_paths", "inputFileListPaths")
@deserialize.key("output_file_list_paths", "outputFileListPaths")
@deserialize.key("shell_path", "shellPath")
@deserialize.key("shell_script", "shellScript")
@deserialize.key("show_env_vars_in_log", "showEnvVarsInLog")
@deserialize.key("always_out_of_date", "alwaysOutOfDate")
@deserialize.key("dependency_file", "dependencyFile")
@deserialize.parser("showEnvVarsInLog", lambda x: {"0": False, "1": True}.get(x, True))
@deserialize.parser("alwaysOutOfDate", lambda x: {"0": False, "1": True}.get(x, True))
@deserialize.downcast_identifier(PBXObject, "PBXShellScriptBuildPhase")
class PBXShellScriptBuildPhase(PBXBuildPhase):
    """Represents a PBXShellScriptBuildPhase.

    This is a specific build phase for running shell scripts resources. Several
    other phases exist.
    """

    input_paths: Optional[List[str]]
    output_paths: Optional[List[str]]
    input_file_list_paths: Optional[List[str]]
    output_file_list_paths: Optional[List[str]]
    name: str
    shell_path: str
    shell_script: str
    show_env_vars_in_log: Optional[bool]
    always_out_of_date: Optional[bool]
    dependency_file: Optional[str]


@deserialize.key("destination_path", "dstPath")
@deserialize.key("destination_subfolder_spec", "dstSubfolderSpec")
@deserialize.parser("dstSubfolderSpec", int)
@deserialize.downcast_identifier(PBXObject, "PBXCopyFilesBuildPhase")
class PBXCopyFilesBuildPhase(PBXBuildPhase):
    """Represents a PBXShellScriptBuildPhase.

    This is a specific build phase for running shell scripts resources. Several
    other phases exist.
    """

    destination_path: Optional[str]
    destination_subfolder_spec: int
    name: Optional[str]


@deserialize.downcast_identifier(PBXObject, "PBXFrameworksBuildPhase")
class PBXFrameworksBuildPhase(PBXBuildPhase):
    """Represents a PBXFrameworksBuildPhase.

    The phase responsible on linking with frameworks. Known as Link Binary With Libraries in the UI.
    """


@deserialize.downcast_identifier(PBXObject, "PBXHeadersBuildPhase")
class PBXHeadersBuildPhase(PBXBuildPhase):
    """Represents a PBXHeadersBuildPhase

    This phase copies headers.
    """
