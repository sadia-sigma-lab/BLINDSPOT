"""Abstract scenario generator base."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from blindspot.scenarios.templates import ScenarioTemplate


class ScenarioGenerator(ABC):
    """Abstract base for all scenario generation strategies."""

    @abstractmethod
    def generate(
        self,
        template: ScenarioTemplate,
        seed: int = 42,
        max_count: int | None = None,
    ) -> list[dict[str, Any]]:
        """Generate scenario parameter dicts from a template."""
        ...
