"""Plugin abstract interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from blindspot.core.metadata import ComponentMetadata

if TYPE_CHECKING:
    from blindspot.registry import RegistryHub


class BenchmarkPlugin(ABC):
    """Abstract interface every benchmark plugin must implement."""

    metadata: ComponentMetadata

    @abstractmethod
    def register(self, registries: RegistryHub) -> None:
        """Register all components provided by this plugin."""
        ...

    @abstractmethod
    def validate(self) -> None:
        """Raise if the plugin is misconfigured or dependencies are missing."""
        ...
