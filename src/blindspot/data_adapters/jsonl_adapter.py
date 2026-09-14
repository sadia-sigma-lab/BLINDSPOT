"""JSONL adapter — append-only line-delimited JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Type

from pydantic import BaseModel

from blindspot.data_adapters.base import DataAdapter


class JsonlAdapter(DataAdapter):
    """Read/write JSONL (newline-delimited JSON) files."""

    format_name = "jsonl"

    def load(self, path: Path, schema: Type[BaseModel] | None = None) -> list[Any]:
        records: list[Any] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if schema is not None:
                obj = schema(**obj)
            records.append(obj)
        return records

    def dump(self, path: Path, data: Any) -> None:
        """Append records to a JSONL file (write mode creates fresh file)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, BaseModel):
                item = item.model_dump()
            lines.append(json.dumps(item, default=str))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def append(self, path: Path, record: Any) -> None:
        """Append a single record without overwriting existing content."""
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(record, BaseModel):
            record = record.model_dump()
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")

    def validate(self, path: Path, schema: Type[BaseModel] | None = None) -> None:
        self.load(path, schema)
