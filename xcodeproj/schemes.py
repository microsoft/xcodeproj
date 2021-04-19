"""Schemes"""

import os
import xml.etree.ElementTree as ET

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-branches


class Action:
    """Base class for actions."""

    def __init__(self, node) -> None:
        self.command_line_arguments = []
        self.environment_variables = []
        self.additional_options = []
        self.pre_actions = []
        self.post_actions = []
        self._understood_tags = {
            "CommandLineArguments",
            "EnvironmentVariables",
            "MacroExpansion",
            "AdditionalOptions",
            "PreActions",
            "PostActions",
            "buildConfiguration",
        }

        self._understood_attributes = {
            "enableAddressSanitizer",
            "enableThreadSanitizer",
            "enableUBSanitizer",
            "disableMainThreadChecker",
            "enableASanStackUseAfterReturn",
            "enableGPUValidationMode",
            "migratedStopOnEveryIssue",
            "language",
            "region",
            "allowLocationSimulation",
            "askForAppToLaunch",
            "launchAutomaticallySubstyle",
        }
        self.build_configuration = node.attrib.pop("buildConfiguration", None)
        self.enable_address_sanitizer = node.attrib.pop("enableAddressSanitizer", None) == "YES"
        self.enable_thread_sanitizer = node.attrib.pop("enableThreadSanitizer", None) == "YES"
        self.enable_ub_sanitizer = node.attrib.pop("enableUBSanitizer", None) == "YES"
        self.enable_asan_stack_use_after_return = (
            node.attrib.pop("enableASanStackUseAfterReturn", None) == "YES"
        )
        self.enable_gpu_validation_mode = node.attrib.pop("enableGPUValidationMode", None)
        self.disable_main_thread_checker = (
            node.attrib.pop("disableMainThreadChecker", None) == "YES"
        )
        self.migrated_stop_on_every_issue = (
            node.attrib.pop("migratedStopOnEveryIssue", None) == "YES"
        )
        self.language = node.attrib.pop("language", None)
        self.region = node.attrib.pop("region", None)
        self.allow_location_simulation = node.attrib.pop("allowLocationSimulation", None) == "YES"
        self.ask_for_app_to_launch = node.attrib.pop("askForAppToLaunch", None) == "YES"
        self.launch_automatically_substyle = node.attrib.pop("launchAutomaticallySubstyle", None)

        for child in node:
            if child.tag == "CommandLineArguments":
                assert len(child.attrib) == 0, f"Unhandled attributes: {list(child.attrib.keys())}"
                for argument in child:
                    if argument.tag == "CommandLineArgument":
                        self.command_line_arguments.append(CommandLineArgument(argument))
                    else:
                        assert False, f"Unknown child: {argument.tag}"
            elif child.tag == "EnvironmentVariables":
                assert len(child.attrib) == 0, f"Unhandled attributes: {list(child.attrib.keys())}"
                for variable in child:
                    if variable.tag == "EnvironmentVariable":
                        self.environment_variables.append(EnvironmentVariable(variable))
                    else:
                        assert False, f"Unknown child: {variable.tag}"
            elif child.tag == "MacroExpansion":
                self.macro_expansion = MacroExpansion(child)
            elif child.tag == "AdditionalOptions":
                assert len(child.attrib) == 0, f"Unhandled attributes: {list(child.attrib.keys())}"
                for option in child:
                    if option.tag == "AdditionalOption":
                        self.additional_options.append(AdditionalOption(option))
                    else:
                        assert False, f"Unknown child: {variable.tag}"
            elif child.tag == "PreActions":
                assert len(child.attrib) == 0, f"Unhandled attributes: {list(child.attrib.keys())}"
                for action in child:
                    if action.tag == "ExecutionAction":
                        self.pre_actions.append(ExecutionAction(action))
                    else:
                        assert False, f"Unknown child: {variable.tag}"
            elif child.tag == "PostActions":
                assert len(child.attrib) == 0, f"Unhandled attributes: {list(child.attrib.keys())}"
                for action in child:
                    if action.tag == "ExecutionAction":
                        self.post_actions.append(ExecutionAction(action))
                    else:
                        assert False, f"Unknown child: {variable.tag}"

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
        assert node.tag == "BuildableReference"
        self.buildable_identifier = node.attrib.pop("BuildableIdentifier", None)
        self.blueprint_identifier = node.attrib.pop("BlueprintIdentifier", None)
        self.buildable_name = node.attrib.pop("BuildableName", None)
        self.blueprint_name = node.attrib.pop("BlueprintName", None)
        self.referenced_container = node.attrib.pop("ReferencedContainer", None)

        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            assert False, f"Unknown child: {child.tag}"


class BuildActionEntry:
    """BuildActionEntry"""

    def __init__(self, node) -> None:
        self.build_for_testing = node.attrib.pop("buildForTesting", None) == "YES"
        self.build_for_running = node.attrib.pop("buildForRunning", None) == "YES"
        self.build_for_profiling = node.attrib.pop("buildForProfiling", None) == "YES"
        self.build_for_archiving = node.attrib.pop("buildForArchiving", None) == "YES"
        self.build_for_analyzing = node.attrib.pop("buildForAnalyzing", None) == "YES"
        self.buildable_references = []

        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            if child.tag == "BuildableReference":
                self.buildable_references.append(BuildableReference(child))
            else:
                assert False, f"Unknown child: {child.tag}"


class MacroExpansion:
    """MacroExpansion"""

    def __init__(self, node) -> None:
        self.buildable_references = []

        for child in node:
            if child.tag == "BuildableReference":
                self.buildable_references.append(BuildableReference(child))
            else:
                assert False, f"Unknown child: {child.tag}"


class CodeCoverageTargets:
    """CodeCoverageTargets"""

    def __init__(self, node) -> None:
        self.buildable_references = []

        for child in node:
            if child.tag == "BuildableReference":
                self.buildable_references.append(BuildableReference(child))
            else:
                assert False, f"Unknown child: {child.tag}"


class LocationScenarioReference:
    """LocationScenarioReference"""

    def __init__(self, node) -> None:
        assert node.tag == "LocationScenarioReference"
        self.identifier = node.attrib.pop("identifier", None) == "YES"
        self.reference_type = node.attrib.pop("referenceType", None) == "YES"
        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"


class Test:
    """Test"""

    def __init__(self, node) -> None:
        self.identifier = node.attrib.pop("Identifier", None)
        assert self.identifier is not None, "Missing identifier for Test"
        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            assert False, f"Unknown child: {child.tag}"


class TestableReference:
    """TestableReference"""

    def __init__(self, node) -> None:
        self.skipped = node.attrib.pop("skipped", None) == "YES"
        self.parallelizable = node.attrib.pop("parallelizable", None) == "YES"
        self.use_test_selection_whitelist = (
            node.attrib.pop("useTestSelectionWhitelist", None) == "YES"
        )
        self.test_execution_ordering = node.attrib.pop("testExecutionOrdering", None)
        self.buildable_references = []
        self.selected_tests = []
        self.skipped_tests = []
        self.location_scenario_reference = None

        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            if child.tag == "BuildableReference":
                self.buildable_references.append(BuildableReference(child))
            elif child.tag == "SelectedTests":
                assert len(child.attrib) == 0, f"Unhandled attributes: {list(child.attrib.keys())}"
                for test in child:
                    if test.tag == "Test":
                        self.selected_tests.append(Test(test))
                    else:
                        assert False, f"Unknown child: {test.tag}"
            elif child.tag == "SkippedTests":
                assert len(child.attrib) == 0, f"Unhandled attributes: {list(child.attrib.keys())}"
                for test in child:
                    if test.tag == "Test":
                        self.skipped_tests.append(Test(test))
                    else:
                        assert False, f"Unknown child: {test.tag}"
            elif child.tag == "LocationScenarioReference":
                self.location_scenario_reference = LocationScenarioReference(child)
            else:
                assert False, f"Unknown child: {child.tag}"


class TestPlanReference:
    """TestPlanReference"""

    def __init__(self, node) -> None:
        assert node.tag == "TestPlanReference"
        self.reference = node.attrib.pop("reference", None)
        self.default = node.attrib.pop("default", None) == "YES"
        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            assert False, f"Unknown child: {child.tag}"


class RemoteRunnable:
    """RemoteRunnable"""

    def __init__(self, node) -> None:
        self.runnable_debugging_mode = node.attrib.pop("runnableDebuggingMode", None)
        self.bundle_identifier = node.attrib.pop("BundleIdentifier", None)
        self.remote_path = node.attrib.pop("RemotePath", None)
        self.buildable_references = []
        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            if child.tag == "BuildableReference":
                self.buildable_references.append(BuildableReference(child))
            else:
                assert False, f"Unknown child: {child.tag}"


class KV:
    """KV"""

    def __init__(self, node) -> None:
        self.key = node.attrib.pop("key", None)
        self.value = node.attrib.pop("value", None)
        self.is_enabled = node.attrib.pop("isEnabled", None) == "YES"
        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            assert False, f"Unknown child: {child.tag}"


class EnvironmentVariable(KV):
    """EnvironmentVariable"""

    def __init__(self, node) -> None:
        assert node.tag == "EnvironmentVariable"
        super().__init__(node)


class AdditionalOption(KV):
    """AdditionalOption"""

    def __init__(self, node) -> None:
        assert node.tag == "AdditionalOption"
        super().__init__(node)


class BuildableProductRunnable:
    """BuildableProductRunnable"""

    def __init__(self, node) -> None:
        assert node.tag == "BuildableProductRunnable"
        self.runnable_debugging_mode = node.attrib.pop("runnableDebuggingMode", None)
        self.buildable_references = []
        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            if child.tag == "BuildableReference":
                self.buildable_references.append(BuildableReference(child))
            else:
                assert False, f"Unknown child: {child.tag}"


class CommandLineArgument:
    """CommandLineArgument"""

    def __init__(self, node) -> None:
        assert node.tag == "CommandLineArgument"
        self.argument = node.attrib.pop("argument", None)
        self.is_enabled = node.attrib.pop("isEnabled", None) == "YES"
        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            assert False, f"Unknown child: {child.tag}"


class EnvironmentBuildable:
    """EnvironmentBuildable"""

    def __init__(self, node) -> None:
        assert node.tag == "EnvironmentBuildable"
        self.buildable_references = []

        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            if child.tag == "BuildableReference":
                self.buildable_references.append(BuildableReference(child))
            else:
                assert False, f"Unknown child: {child.tag}"


class ActionContent:
    """ActionContent"""

    def __init__(self, node) -> None:
        assert node.tag == "ActionContent"
        self.title = node.attrib.pop("title", None)
        self.script_text = node.attrib.pop("scriptText", None)
        self.environment_buildable = None
        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            if child.tag == "EnvironmentBuildable":
                self.environment_buildable = EnvironmentBuildable(child)
            else:
                assert False, f"Unknown child: {child.tag}"


class ExecutionAction:
    """ExecutionAction"""

    def __init__(self, node) -> None:
        assert node.tag == "ExecutionAction"
        self.action_type = node.attrib.pop("ActionType", None)
        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"
        self.action_content = None

        for child in node:
            assert self.action_content is None
            if child.tag == "ActionContent":
                self.action_content = ActionContent(child)
            else:
                assert False, f"Unknown child: {child.tag}"


class BuildAction(Action):
    """BuildAction"""

    def __init__(self, node) -> None:
        assert node.tag == "BuildAction"
        super().__init__(node)
        self.parallelize_buildables = node.attrib.pop("parallelizeBuildables", None) == "YES"
        self.build_implicit_dependencies = (
            node.attrib.pop("buildImplicitDependencies", None) == "YES"
        )
        self.build_action_entries = []
        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            if child.tag == "BuildActionEntries":
                assert len(child.attrib) == 0, f"Unhandled attributes: {list(child.attrib.keys())}"
                for entry in child:
                    if entry.tag == "BuildActionEntry":
                        self.build_action_entries.append(BuildActionEntry(entry))
                    else:
                        assert False, f"Unknown child: {entry.tag}"
            else:
                assert self._understands_tag(child.tag)


class TestAction(Action):
    """TestAction"""

    def __init__(self, node) -> None:
        assert node.tag == "TestAction"
        super().__init__(node)
        self.build_configuration = node.attrib.pop("buildConfiguration", None)
        self.selected_debugger_identifier = node.attrib.pop("selectedDebuggerIdentifier", None)
        self.selected_launcher_identifier = node.attrib.pop("selectedLauncherIdentifier", None)
        self.should_use_launch_scheme_args_env = (
            node.attrib.pop("shouldUseLaunchSchemeArgsEnv", None) == "YES"
        )
        self.code_coverage_enabled = node.attrib.pop("codeCoverageEnabled", None) == "YES"
        self.system_attachment_lifetime = node.attrib.pop("systemAttachmentLifetime", None)
        self.only_generate_coverage_for_specific_targets = (
            node.attrib.pop("onlyGenerateCoverageForSpecifiedTargets", None) == "YES"
        )
        self.test_plans = []
        self.testables = []
        self.code_coverage_targets = None
        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            if child.tag == "CodeCoverageTargets":
                self.code_coverage_targets = CodeCoverageTargets(child)
            elif child.tag == "Testables":
                assert len(child.attrib) == 0, f"Unhandled attributes: {list(child.attrib.keys())}"
                for testable in child:
                    if testable.tag == "TestableReference":
                        self.testables.append(TestableReference(testable))
                    else:
                        assert False, f"Unknown child: {testable.tag}"
            elif child.tag == "TestPlans":
                assert len(child.attrib) == 0, f"Unhandled attributes: {list(child.attrib.keys())}"
                for plan in child:
                    if plan.tag == "TestPlanReference":
                        self.test_plans.append(TestPlanReference(plan))
                    else:
                        assert False, f"Unknown child: {plan.tag}"
            else:
                assert self._understands_tag(child.tag)


class LaunchAction(RunAction):
    """LaunchAction"""

    def __init__(self, node) -> None:
        assert node.tag == "LaunchAction"
        super().__init__(node)
        self.build_configuration = node.attrib.pop("buildConfiguration", None)
        self.selected_debugger_identifier = node.attrib.pop("selectedDebuggerIdentifier", None)
        self.selected_launcher_identifier = node.attrib.pop("selectedLauncherIdentifier", None)
        self.launch_style = node.attrib.pop("launchStyle", None)
        self.use_custom_working_directory = (
            node.attrib.pop("useCustomWorkingDirectory", None) == "YES"
        )
        self.ignores_persistent_state_on_launch = (
            node.attrib.pop("ignoresPersistentStateOnLaunch", None) == "YES"
        )
        self.debug_document_versioning = node.attrib.pop("debugDocumentVersioning", None) == "YES"
        self.debug_service_extension = node.attrib.pop("debugServiceExtension", None)
        self.debug_xpc_services = node.attrib.pop("debugXPCServices", None) == "YES"
        self.language = node.attrib.pop("language", None)
        self.notification_payload_file = node.attrib.pop("notificationPayloadFile", None)
        self.console_mode = node.attrib.pop("consoleMode", None)
        self.buildable_product_runnable = None

        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

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
        self.build_configuration = node.attrib.pop("buildConfiguration", None)
        self.should_use_launch_scheme_args_env = (
            node.attrib.pop("shouldUseLaunchSchemeArgsEnv", None) == "YES"
        )
        self.saved_tool_identifier = node.attrib.pop("savedToolIdentifier", None)
        self.use_custom_working_directory = (
            node.attrib.pop("useCustomWorkingDirectory", None) == "YES"
        )
        self.debug_document_versioning = node.attrib.pop("debugDocumentVersioning", None) == "YES"
        self.launch_automatically_substyle = (
            node.attrib.pop("launchAutomaticallySubstyle", None) == "YES"
        )
        self.buildable_product_runnable = None

        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

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
        self.build_configuration = node.attrib.pop("buildConfiguration", None)

        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            assert self._understands_tag(child.tag)


class ArchiveAction(Action):
    """ArchiveAction"""

    def __init__(self, node) -> None:
        assert node.tag == "ArchiveAction"
        super().__init__(node)
        self.build_configuration = node.attrib.pop("buildConfiguration", None)
        self.reveal_archive_in_organizer = (
            node.attrib.pop("revealArchiveInOrganizer", None) == "YES"
        )
        self.custom_archive_name = node.attrib.pop("customArchiveName", None)

        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

        for child in node:
            assert self._understands_tag(child.tag)


class Scheme:
    """Represents an Xcode scheme."""

    def __init__(self, node, name: str) -> None:
        assert node.tag == "Scheme"
        self.name = name
        self.last_upgrade_version = node.attrib.pop("LastUpgradeVersion", None)
        self.version = node.attrib.pop("version", None)
        self.was_created_for_app_extension = (
            node.attrib.pop("wasCreatedForAppExtension", None) == "YES"
        )
        self.build_action = None
        self.test_action = None
        self.launch_action = None
        self.profile_action = None
        self.analyze_action = None
        self.archive_action = None

        assert len(node.attrib) == 0, f"Unhandled attributes: {list(node.attrib.keys())}"

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
                assert False, f"Unknown child: {child.tag}"

    @staticmethod
    def from_file(path: str) -> "Scheme":
        """Load a scheme from a file.

        :param path: The path of the scheme file

        :returns: A loaded scheme
        """
        tree = ET.parse(path)
        root = tree.getroot()

        return Scheme(root, ".".join(os.path.basename(path).split(".")[:-1]))

    @staticmethod
    def from_string(contents: str, name: str) -> "Scheme":
        """Load a scheme from a string.

        :param contents: The XML string
        :param name: The name of the scheme

        :returns: A loaded scheme
        """
        root = ET.fromstring(contents)
        return Scheme(root, name)
