"""Adapter registry — maps format names to adapter instances."""

from __future__ import annotations

from blindspot.data_adapters.base import DataAdapter
from blindspot.data_adapters.csv_adapter import CsvAdapter
from blindspot.data_adapters.directory_adapter import DirectoryAdapter
from blindspot.data_adapters.json_adapter import JsonAdapter
from blindspot.data_adapters.jsonl_adapter import JsonlAdapter
from blindspot.data_adapters.markdown_adapter import MarkdownAdapter


class AdapterRegistry:
    """Maps format name strings to DataAdapter instances."""

    def __init__(self) -> None:
        self._adapters: dict[str, DataAdapter] = {}

    def register(self, adapter: DataAdapter) -> None:
        self._adapters[adapter.format_name] = adapter

    def get(self, format_name: str) -> DataAdapter:
        adapter = self._adapters.get(format_name)
        if adapter is None:
            raise KeyError(f"No adapter registered for format {format_name!r}")
        return adapter

    def available_formats(self) -> list[str]:
        return sorted(self._adapters.keys())


def get_default_registry() -> AdapterRegistry:
    """Create and return an AdapterRegistry with all built-in adapters registered."""
    reg = AdapterRegistry()
    reg.register(JsonAdapter())
    reg.register(JsonlAdapter())
    reg.register(CsvAdapter())
    reg.register(MarkdownAdapter())
    reg.register(DirectoryAdapter())

    # Register Parquet only if available
    try:
        from blindspot.data_adapters.parquet_adapter import ParquetAdapter, _PARQUET_AVAILABLE
        if _PARQUET_AVAILABLE:
            reg.register(ParquetAdapter())
    except ImportError:
        pass

    return reg
