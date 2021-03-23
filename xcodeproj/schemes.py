"""Schemes"""

import xml.etree.ElementTree as ET

# pylint: disable=too-many-instance-attributes


class Action:
    """Base class for actions."""

    def __init__(self, node) -> None:
        self.command_line_arguments = []
        self.environment_variables = []
        self._understood_tags = {"CommandLineArguments", "EnvironmentVariables", "MacroExpansion"}

        for child in node:
            if child.tag == "CommandLineArguments":
                for argument in child:
                    self.command_line_arguments.append(CommandLineArgument(argument))
            elif child.tag == "EnvironmentVariables":
                for variable in child:
                    self.environment_variables.append(EnvironmentVariable(variable))
            elif child.tag == "MacroExpansion":
                self.macro_expansion = MacroExpansion(child)

    def _understands_tag(self, tag: str) -> bool:
        return tag in self._understood_tags


class RunAction(Action):
    """Base class for runnable actions."""

    def __init__(self, node) -> None:
        super().__init__(node)
        self._understood_tags.add("RemoteRunnable")

        for child in node:
            if child.tag == "RemoteRunnable":
                self.remote_runnable = RemoteRunnable(child)


class BuildableReference:
    """BuildableReference"""

    def __init__(self, node) -> None:
        self.buildable_identifier = node.attrib.get("BuildableIdentifier")
        self.blueprint_identifier = node.attrib.get("BlueprintIdentifier")
        self.buildable_name = node.attrib.get("BuildableName")
        self.blueprint_name = node.attrib.get("BlueprintName")
        self.referenced_container = node.attrib.get("ReferencedContainer")


class BuildActionEntry:
    """BuildActionEntry"""

    def __init__(self, node) -> None:
        self.build_for_testing = node.attrib.get("buildForTesting") == "YES"
        self.build_for_running = node.attrib.get("buildForRunning") == "YES"
        self.build_for_profiling = node.attrib.get("buildForProfiling") == "YES"
        self.build_for_archiving = node.attrib.get("buildForArchiving") == "YES"
        self.build_for_analyzing = node.attrib.get("buildForAnalyzing") == "YES"
        self.buildable_references = []

        for child in node:
            self.buildable_references.append(BuildableReference(child))


class MacroExpansion:
    """MacroExpansion"""

    def __init__(self, node) -> None:
        self.buildable_references = []

        for child in node:
            self.buildable_references.append(BuildableReference(child))


class CodeCoverageTargets:
    """CodeCoverageTargets"""

    def __init__(self, node) -> None:
        self.buildable_references = []

        for child in node:
            self.buildable_references.append(BuildableReference(child))


class TestableReference:
    """TestableReference"""

    def __init__(self, node) -> None:
        self.skipped = node.attrib.get("skipped") == "YES"
        self.test_execution_ordering = node.attrib.get("testExecutionOrdering")
        self.buildable_references = []

        for child in node:
            self.buildable_references.append(BuildableReference(child))


class TestPlanReference:
    """TestPlanReference"""

    def __init__(self, node) -> None:
        assert node.tag == "TestPlanReference"
        self.reference = node.attrib.get("reference")
        self.default = node.attrib.get("default") == "YES"


class RemoteRunnable:
    """RemoteRunnable"""

    def __init__(self, node) -> None:
        self.runnable_debugging_mode = node.attrib.get("runnableDebuggingMode")
        self.bundle_identifier = node.attrib.get("BundleIdentifier")
        self.buildable_references = []

        for child in node:
            self.buildable_references.append(BuildableReference(child))


class EnvironmentVariable:
    """EnvironmentVariable"""

    def __init__(self, node) -> None:
        self.key = node.attrib.get("key")
        self.value = node.attrib.get("value")
        self.is_enabled = node.attrib.get("isEnabled") == "YES"


class BuildableProductRunnable:
    """BuildableProductRunnable"""

    def __init__(self, node) -> None:
        assert node.tag == "BuildableProductRunnable"
        self.runnable_debugging_mode = node.attrib.get("runnableDebuggingMode")
        self.buildable_references = []

        for child in node:
            self.buildable_references.append(BuildableReference(child))


class CommandLineArgument:
    """CommandLineArgument"""

    def __init__(self, node) -> None:
        assert node.tag == "CommandLineArgument"
        self.argument = node.attrib.get("argument")
        self.is_enabled = node.attrib.get("isEnabled") == "YES"


class BuildAction(Action):
    """BuildAction"""

    def __init__(self, node) -> None:
        assert node.tag == "BuildAction"
        super().__init__(node)
        self.parallelize_buildables = node.attrib.get("parallelizeBuildables") == "YES"
        self.build_implicit_dependencies = node.attrib.get("buildImplicitDependencies") == "YES"
        self.build_action_entries = []
        for child in node:
            if child.tag == "BuildActionEntries":
                for entry in child:
                    assert entry.tag == "BuildActionEntry"
                    self.build_action_entries.append(BuildActionEntry(entry))
            else:
                assert self._understands_tag(child.tag)


class TestAction(Action):
    """TestAction"""

    def __init__(self, node) -> None:
        assert node.tag == "TestAction"
        super().__init__(node)
        self.build_configuration = node.attrib.get("buildConfiguration")
        self.selected_debugger_identifier = node.attrib.get("selectedDebuggerIdentifier")
        self.selected_launcher_identifier = node.attrib.get("selectedLauncherIdentifier")
        self.should_use_launch_scheme_args_env = (
            node.attrib.get("shouldUseLaunchSchemeArgsEnv") == "YES"
        )
        self.code_coverage_enabled = node.attrib.get("codeCoverageEnabled") == "YES"
        self.only_generate_coverage_for_specific_targets = (
            node.attrib.get("onlyGenerateCoverageForSpecifiedTargets") == "YES"
        )
        self.test_plans = []

        for child in node:
            if child.tag == "CodeCoverageTargets":
                self.code_coverage_targets = CodeCoverageTargets(child)
            elif child.tag == "Testables":
                self.testables = []
                for testable in child:
                    self.testables.append(TestableReference(testable))
            elif child.tag == "TestPlans":
                for plan in child:
                    self.test_plans.append(TestPlanReference(plan))
            else:
                assert self._understands_tag(child.tag)


class LaunchAction(RunAction):
    """LaunchAction"""

    def __init__(self, node) -> None:
        assert node.tag == "LaunchAction"
        super().__init__(node)
        self.build_configuration = node.attrib.get("buildConfiguration")
        self.selected_debugger_identifier = node.attrib.get("selectedDebuggerIdentifier")
        self.selected_launcher_identifier = node.attrib.get("selectedLauncherIdentifier")
        self.launch_style = node.attrib.get("launchStyle")
        self.use_custom_working_directory = node.attrib.get("useCustomWorkingDirectory") == "YES"
        self.ignores_persistent_state_on_launch = (
            node.attrib.get("ignoresPersistentStateOnLaunch") == "YES"
        )
        self.debug_document_versioning = node.attrib.get("debugDocumentVersioning") == "YES"
        self.debug_service_extension = node.attrib.get("debugServiceExtension")
        self.allow_location_simulation = node.attrib.get("allowLocationSimulation") == "YES"
        self.ask_for_app_to_launch = node.attrib.get("askForAppToLaunch") == "YES"
        self.launch_automatically_substyle = node.attrib.get("launchAutomaticallySubstyle") == "YES"

        for child in node:
            if child.tag == "BuildableProductRunnable":
                self.buildable_product_runnable = BuildableProductRunnable(child)
            else:
                assert self._understands_tag(child.tag)


class ProfileAction(RunAction):
    """ProfileAction"""

    def __init__(self, node) -> None:
        assert node.tag == "ProfileAction"
        super().__init__(node)
        self.build_configuration = node.attrib.get("buildConfiguration")
        self.should_use_launch_scheme_args_env = (
            node.attrib.get("shouldUseLaunchSchemeArgsEnv") == "YES"
        )
        self.saved_tool_identifier = node.attrib.get("savedToolIdentifier")
        self.use_custom_working_directory = node.attrib.get("useCustomWorkingDirectory") == "YES"
        self.debug_document_versioning = node.attrib.get("debugDocumentVersioning") == "YES"

        for child in node:
            if child.tag == "BuildableProductRunnable":
                self.buildable_product_runnable = BuildableProductRunnable(child)
            else:
                assert self._understands_tag(child.tag)


class AnalyzeAction(Action):
    """AnalyzeAction"""

    def __init__(self, node) -> None:
        assert node.tag == "AnalyzeAction"
        super().__init__(node)
        self.build_configuration = node.attrib.get("buildConfiguration")


class ArchiveAction(Action):
    """ArchiveAction"""

    def __init__(self, node) -> None:
        assert node.tag == "ArchiveAction"
        super().__init__(node)
        self.build_configuration = node.attrib.get("buildConfiguration")
        self.reveal_archive_in_organizer = node.attrib.get("revealArchiveInOrganizer") == "YES"


class Scheme:
    """Represents an Xcode scheme."""

    def __init__(self, node) -> None:
        assert node.tag == "Scheme"
        self.last_upgrade_version = node.attrib.get("LastUpgradeVersion")
        self.version = node.attrib.get("version")
        self.was_created_for_app_extension = node.attrib.get("wasCreatedForAppExtension") == "YES"

        for child in node:
            if child.tag == "BuildAction":
                self.build_action = BuildAction(child)
            elif child.tag == "TestAction":
                self.test_action = TestAction(child)
            elif child.tag == "LaunchAction":
                self.launch_action = LaunchAction(child)
            elif child.tag == "ProfileAction":
                self.profile_action = ProfileAction(child)
            elif child.tag == "AnalyzeAction":
                self.analyze_action = AnalyzeAction(child)
            elif child.tag == "ArchiveAction":
                self.archive_action = ArchiveAction(child)
            else:
                assert False

    @staticmethod
    def from_file(path: str) -> "Scheme":
        """Load a scheme from a file.

        :param path: The path of the scheme file

        :returns: A loaded scheme
        """
        tree = ET.parse(path)
        root = tree.getroot()

        return Scheme(root)
