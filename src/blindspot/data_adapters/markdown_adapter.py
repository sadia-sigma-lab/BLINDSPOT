"""Markdown adapter with YAML front matter."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Type

import yaml
from pydantic import BaseModel

from blindspot.data_adapters.base import DataAdapter


def _parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Split YAML front matter from markdown body."""
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end = i
            break
    if end == -1:
        return {}, text
    front_matter = yaml.safe_load("\n".join(lines[1:end])) or {}
    body = "\n".join(lines[end + 1:]).lstrip("\n")
    return front_matter, body


class MarkdownDocument:
    """A parsed Markdown document with YAML front matter."""

    def __init__(self, front_matter: dict[str, Any], body: str) -> None:
        self.front_matter = front_matter
        self.body = body

    def to_text(self) -> str:
        fm = yaml.dump(self.front_matter, default_flow_style=False, allow_unicode=True)
        return f"---\n{fm}---\n\n{self.body}"


class MarkdownAdapter(DataAdapter):
    """Read/write Markdown files with optional YAML front matter."""

    format_name = "markdown"

    def load(self, path: Path, schema: Type[BaseModel] | None = None) -> MarkdownDocument:
        text = path.read_text(encoding="utf-8")
        front_matter, body = _parse_front_matter(text)
        return MarkdownDocument(front_matter=front_matter, body=body)

    def dump(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, MarkdownDocument):
            path.write_text(data.to_text(), encoding="utf-8")
        elif isinstance(data, str):
            path.write_text(data, encoding="utf-8")
        else:
            raise TypeError(f"MarkdownAdapter.dump expects MarkdownDocument or str, got {type(data)}")

    def validate(self, path: Path, schema: Type[BaseModel] | None = None) -> None:
        doc = self.load(path)
        if schema is not None:
            schema(**doc.front_matter)
