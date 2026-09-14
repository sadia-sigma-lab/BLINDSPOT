"""Data adapters for reading and writing fixture files in various formats."""

from blindspot.data_adapters.base import DataAdapter
from blindspot.data_adapters.json_adapter import JsonAdapter
from blindspot.data_adapters.jsonl_adapter import JsonlAdapter
from blindspot.data_adapters.csv_adapter import CsvAdapter
from blindspot.data_adapters.markdown_adapter import MarkdownAdapter
from blindspot.data_adapters.directory_adapter import DirectoryAdapter
from blindspot.data_adapters.registry import AdapterRegistry, get_default_registry

__all__ = [
    "DataAdapter",
    "JsonAdapter",
    "JsonlAdapter",
    "CsvAdapter",
    "MarkdownAdapter",
    "DirectoryAdapter",
    "AdapterRegistry",
    "get_default_registry",
]
