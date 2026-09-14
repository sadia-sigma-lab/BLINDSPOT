"""Domain-specific exceptions for the benchmark framework."""


class BenchmarkError(Exception):
    """Base class for all benchmark errors."""


class DuplicateRegistrationError(BenchmarkError):
    """Raised when a component with the same ID is registered twice."""

    def __init__(self, component_id: str) -> None:
        super().__init__(f"Component already registered: {component_id!r}")
        self.component_id = component_id


class ComponentNotFoundError(BenchmarkError):
    """Raised when a requested component is not in the registry."""

    def __init__(self, component_id: str, registry_name: str = "") -> None:
        loc = f" in registry {registry_name!r}" if registry_name else ""
        super().__init__(f"Component not found{loc}: {component_id!r}")
        self.component_id = component_id
        self.registry_name = registry_name


class InvalidComponentIDError(BenchmarkError):
    """Raised when a ComponentID fails validation."""


class ConfigurationError(BenchmarkError):
    """Raised when configuration is invalid or missing required fields."""


class PluginLoadError(BenchmarkError):
    """Raised when a plugin cannot be loaded."""

    def __init__(self, plugin_path: str, cause: Exception) -> None:
        super().__init__(f"Failed to load plugin {plugin_path!r}: {cause}")
        self.plugin_path = plugin_path
        self.cause = cause


class ToolExecutionError(BenchmarkError):
    """Raised when a tool encounters an unrecoverable execution error."""


class InvalidToolArgumentsError(BenchmarkError):
    """Raised when tool arguments fail schema validation."""


class StateError(BenchmarkError):
    """Raised for invalid state transitions or malformed state."""


class PathTraversalError(BenchmarkError):
    """Raised when a storage path escapes the configured root."""


class ReplayDivergenceError(BenchmarkError):
    """Raised when replay produces a different state than the original run."""


class SnapshotError(BenchmarkError):
    """Raised when snapshot creation or restoration fails."""


class ScenarioNotFoundError(BenchmarkError):
    """Raised when a scenario YAML cannot be located or parsed."""
