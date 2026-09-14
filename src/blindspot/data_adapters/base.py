"""Abstract data adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Type

from pydantic import BaseModel


class DataAdapter(ABC):
    """Reads and writes a specific file format."""

    format_name: str

    @abstractmethod
    def load(self, path: Path, schema: Type[BaseModel] | None = None) -> Any:
        """Load data from path; optionally validate against schema."""
        ...

    @abstractmethod
    def dump(self, path: Path, data: Any) -> None:
        """Write data to path."""
        ...

    @abstractmethod
    def validate(self, path: Path, schema: Type[BaseModel] | None = None) -> None:
        """Validate data at path against schema; raise on failure."""
        ...
