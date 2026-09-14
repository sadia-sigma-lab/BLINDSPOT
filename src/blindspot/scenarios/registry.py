"""Scenario registry — only validated scenarios are registered."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any

from blindspot.scenarios.exceptions import ScenarioNotFoundError, ScenarioValidationError
from blindspot.scenarios.schema import FullScenarioSpec
from blindspot.scenarios.validation import ScenarioValidationReport, validate_scenario


class ScenarioRegistry:
    """Ordered registry that enforces validation before registration."""

    def __init__(self) -> None:
        self._store: OrderedDict[str, FullScenarioSpec] = OrderedDict()
        self._validation_reports: dict[str, ScenarioValidationReport] = {}

    def register(
        self,
        spec: FullScenarioSpec,
        attack_registry: Any | None = None,
        strict: bool = True,
    ) -> ScenarioValidationReport:
        """Validate and register a scenario. Raises on validation errors in strict mode."""
        report = validate_scenario(spec, attack_registry)
        cid = spec.metadata.scenario_id.canonical()

        if strict and not report.valid:
            errors = [i.message for i in report.errors()]
            raise ScenarioValidationError(
                f"Scenario {cid!r} failed validation: {'; '.join(errors)}"
            )

        self._store[cid] = spec
        self._validation_reports[cid] = report
        return report

    def get(self, scenario_id: str) -> FullScenarioSpec:
        spec = self._store.get(scenario_id)
        if spec is None:
            raise ScenarioNotFoundError(scenario_id)
        return spec

    def contains(self, scenario_id: str) -> bool:
        return scenario_id in self._store

    def list(self) -> list[str]:
        return list(self._store.keys())

    def list_by_domain(self, domain_id: str) -> list[str]:
        return [cid for cid, s in self._store.items() if s.metadata.domain_id == domain_id]

    def get_validation_report(self, scenario_id: str) -> ScenarioValidationReport | None:
        return self._validation_reports.get(scenario_id)

    def unregister(self, scenario_id: str) -> None:
        if scenario_id not in self._store:
            raise ScenarioNotFoundError(scenario_id)
        del self._store[scenario_id]
        self._validation_reports.pop(scenario_id, None)

    def clear(self) -> None:
        self._store.clear()
        self._validation_reports.clear()
