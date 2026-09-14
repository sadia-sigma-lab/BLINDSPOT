"""Tool visibility filter for discovery."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blindspot.tools.specification import ToolSpecification


def is_visible_to_agent(spec: "ToolSpecification") -> bool:
    return spec.visibility == "public" and not spec.deprecated
