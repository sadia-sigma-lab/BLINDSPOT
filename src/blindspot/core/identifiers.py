"""Stable component identifiers with validation."""

import re
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, field_validator

_ID_PART_RE = re.compile(r"^[a-z0-9_.\-]+$")
_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([\w\-.]+))?(?:\+([\w\-.]+))?$"
)


class ComponentID(BaseModel):
    """Globally unique, stable identifier for a registered benchmark component."""

    model_config = ConfigDict(frozen=True)

    namespace: str
    name: str
    version: str

    @field_validator("namespace", "name")
    @classmethod
    def _validate_id_part(cls, v: str) -> str:
        if not _ID_PART_RE.match(v):
            raise ValueError(
                f"ID part {v!r} must be lowercase and contain only "
                "letters, digits, '_', '-', or '.'"
            )
        return v

    @field_validator("version")
    @classmethod
    def _validate_semver(cls, v: str) -> str:
        if not _SEMVER_RE.match(v):
            raise ValueError(f"Version {v!r} must be semver-compatible (e.g. '1.0.0')")
        return v

    def canonical(self) -> str:
        """Return the canonical string form ``namespace:name@version``."""
        return f"{self.namespace}:{self.name}@{self.version}"

    @classmethod
    def parse(cls, canonical: str) -> "ComponentID":
        """Parse a canonical string produced by :meth:`canonical`."""
        try:
            ns_name, version = canonical.split("@", 1)
            namespace, name = ns_name.split(":", 1)
        except ValueError as exc:
            raise ValueError(
                f"Cannot parse ComponentID from {canonical!r}. "
                "Expected 'namespace:name@version'."
            ) from exc
        return cls(namespace=namespace, name=name, version=version)

    def __str__(self) -> str:
        return self.canonical()
