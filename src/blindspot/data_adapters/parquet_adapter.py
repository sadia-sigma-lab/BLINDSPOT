"""Parquet adapter — optional; gracefully absent when pyarrow is not installed."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Type

from pydantic import BaseModel

from blindspot.data_adapters.base import DataAdapter

try:
    import pyarrow  # noqa: F401
    import pyarrow.parquet as pq
    _PARQUET_AVAILABLE = True
except ImportError:
    _PARQUET_AVAILABLE = False


class ParquetAdapter(DataAdapter):
    """Read/write Parquet files using pyarrow (optional dependency)."""

    format_name = "parquet"

    def _require_parquet(self) -> None:
        if not _PARQUET_AVAILABLE:
            raise ImportError(
                "pyarrow is required for Parquet support. "
                "Install with: pip install pyarrow"
            )

    def load(self, path: Path, schema: Type[BaseModel] | None = None) -> Any:
        self._require_parquet()
        table = pq.read_table(str(path))
        records = table.to_pylist()
        if schema is not None:
            return [schema(**r) for r in records]
        return records

    def dump(self, path: Path, data: Any) -> None:
        self._require_parquet()
        import pyarrow as pa

        path.parent.mkdir(parents=True, exist_ok=True)
        items = data if isinstance(data, list) else [data]
        dicts = [item.model_dump() if isinstance(item, BaseModel) else item for item in items]
        table = pa.Table.from_pylist(dicts)
        pq.write_table(table, str(path))

    def validate(self, path: Path, schema: Type[BaseModel] | None = None) -> None:
        self._require_parquet()
        self.load(path, schema)
