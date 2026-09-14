"""CSV adapter with explicit schema support."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any, Type

from pydantic import BaseModel

from blindspot.data_adapters.base import DataAdapter


class CsvAdapter(DataAdapter):
    """Read/write CSV files; no type inference without an explicit schema."""

    format_name = "csv"

    def load(self, path: Path, schema: Type[BaseModel] | None = None) -> list[Any]:
        text = path.read_text(encoding="utf-8")
        reader = csv.DictReader(io.StringIO(text))
        rows: list[Any] = []
        for row in reader:
            if schema is not None:
                rows.append(schema(**row))
            else:
                rows.append(dict(row))
        return rows

    def dump(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        items = data if isinstance(data, list) else [data]
        if not items:
            path.write_text("", encoding="utf-8")
            return
        if isinstance(items[0], BaseModel):
            dicts = [item.model_dump() for item in items]
        else:
            dicts = items

        # Deterministic column ordering
        fieldnames = sorted(dicts[0].keys()) if dicts else []
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(dicts)
        path.write_text(output.getvalue(), encoding="utf-8")

    def validate(self, path: Path, schema: Type[BaseModel] | None = None) -> None:
        self.load(path, schema)
