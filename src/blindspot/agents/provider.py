"""Provider protocol — thin interface for future real provider adapters."""

from __future__ import annotations

from typing import Any, Protocol


class ModelProvider(Protocol):
    """Protocol that real provider adapters must satisfy."""

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        model: str,
        temperature: float,
        max_tokens: int | None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Invoke the model and return a raw completion dict."""
        ...
