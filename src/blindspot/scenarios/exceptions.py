"""Scenario subsystem exceptions."""

from blindspot.exceptions import BenchmarkError


class ScenarioError(BenchmarkError):
    """Base class for scenario errors."""


class ScenarioValidationError(ScenarioError):
    """Raised when a scenario fails validation."""


class ScenarioNotFoundError(ScenarioError):
    """Raised when a scenario is not in the registry."""

    def __init__(self, scenario_id: str) -> None:
        super().__init__(f"Scenario not found: {scenario_id!r}")
        self.scenario_id = scenario_id


class ScenarioCompositionError(ScenarioError):
    """Raised when atoms cannot be composed."""


class ScenarioGenerationError(ScenarioError):
    """Raised when scenario generation fails."""


class ScenarioLeakageError(ScenarioError):
    """Raised when a split leakage check fails."""


class SolvabilityError(ScenarioError):
    """Raised when no safe path can be found for a scenario."""
