"""Base abstract component interface."""

from abc import ABC, abstractmethod

from blindspot.core.metadata import ComponentMetadata


class BenchmarkComponent(ABC):
    """Base class for all registered benchmark components."""

    metadata: ComponentMetadata

    @abstractmethod
    def validate(self) -> None:
        """Raise if the component is misconfigured."""
        ...
