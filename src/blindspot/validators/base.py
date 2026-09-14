"""Base validator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from blindspot.validators.reports import ValidationIssue

if TYPE_CHECKING:
    from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle


class BaseValidator(ABC):
    """Abstract validator run against a DomainStateBundle."""

    name: str

    @abstractmethod
    def validate(self, bundle: "DomainStateBundle") -> list[ValidationIssue]:
        """Return a (possibly empty) list of issues found."""
        ...
