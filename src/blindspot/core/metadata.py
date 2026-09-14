"""Component metadata contract."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from blindspot.core.identifiers import ComponentID


class ComponentMetadata(BaseModel):
    """Metadata attached to every registered benchmark component."""

    model_config = ConfigDict(frozen=True)

    component_id: ComponentID
    display_name: str
    description: str
    source_package: str
    tags: list[str] = []
    deprecated: bool = False
