"""JSON adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Type

from pydantic import BaseModel

from blindspot.data_adapters.base import DataAdapter


class JsonAdapter(DataAdapter):
    """Read/write JSON objects or lists of objects."""

    format_name = "json"

    def load(self, path: Path, schema: Type[BaseModel] | None = None) -> Any:
        data = json.loads(path.read_text(encoding="utf-8"))
        if schema is not None and isinstance(data, list):
            return [schema(**item) for item in data]
        if schema is not None and isinstance(data, dict):
            return schema(**data)
        return data

    def dump(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, list):
            serializable = [
                item.model_dump() if isinstance(item, BaseModel) else item
                for item in data
            ]
        elif isinstance(data, BaseModel):
            serializable = data.model_dump()
        else:
            serializable = data
        path.write_text(json.dumps(serializable, indent=2, default=str), encoding="utf-8")

    def validate(self, path: Path, schema: Type[BaseModel] | None = None) -> None:
        self.load(path, schema)
