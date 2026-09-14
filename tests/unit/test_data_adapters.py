"""Unit tests for data adapters."""

import json
import pytest
from pathlib import Path

from blindspot.data_adapters.json_adapter import JsonAdapter
from blindspot.data_adapters.jsonl_adapter import JsonlAdapter
from blindspot.data_adapters.csv_adapter import CsvAdapter
from blindspot.data_adapters.markdown_adapter import MarkdownAdapter, MarkdownDocument
from blindspot.data_adapters.directory_adapter import DirectoryAdapter
from blindspot.data_adapters.registry import get_default_registry


def test_json_round_trip(tmp_path):
    adapter = JsonAdapter()
    data = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    p = tmp_path / "test.json"
    adapter.dump(p, data)
    loaded = adapter.load(p)
    assert loaded == data


def test_jsonl_append_read(tmp_path):
    adapter = JsonlAdapter()
    p = tmp_path / "test.jsonl"
    adapter.dump(p, [{"step": 1}, {"step": 2}])
    loaded = adapter.load(p)
    assert len(loaded) == 2
    assert loaded[0]["step"] == 1


def test_jsonl_append_only(tmp_path):
    adapter = JsonlAdapter()
    p = tmp_path / "test.jsonl"
    adapter.dump(p, [{"step": 1}])
    adapter.append(p, {"step": 2})
    loaded = adapter.load(p)
    assert len(loaded) == 2


def test_csv_typed_load(tmp_path):
    p = tmp_path / "test.csv"
    p.write_text("name,age\nAlice,30\nBob,25\n")
    adapter = CsvAdapter()
    rows = adapter.load(p)
    assert rows[0]["name"] == "Alice"
    assert rows[1]["age"] == "25"  # CSV loads as str without schema


def test_csv_dump_deterministic_columns(tmp_path):
    adapter = CsvAdapter()
    p = tmp_path / "test.csv"
    data = [{"z": 1, "a": 2, "m": 3}]
    adapter.dump(p, data)
    lines = p.read_text().splitlines()
    assert lines[0] == "a,m,z"  # sorted


def test_markdown_front_matter(tmp_path):
    p = tmp_path / "doc.md"
    doc = MarkdownDocument(
        front_matter={"document_id": "doc1", "trust_level": "internal"},
        body="# Title\n\nContent here.",
    )
    adapter = MarkdownAdapter()
    adapter.dump(p, doc)
    loaded = adapter.load(p)
    assert loaded.front_matter["document_id"] == "doc1"
    assert "# Title" in loaded.body


def test_markdown_no_front_matter(tmp_path):
    p = tmp_path / "plain.md"
    p.write_text("# Just a title\nNo front matter here.")
    adapter = MarkdownAdapter()
    doc = adapter.load(p)
    assert doc.front_matter == {}
    assert "Just a title" in doc.body


def test_directory_adapter(tmp_path):
    d = tmp_path / "repo"
    d.mkdir()
    (d / "file1.txt").write_text("hello")
    (d / "subdir").mkdir()
    (d / "subdir" / "file2.txt").write_text("world")
    adapter = DirectoryAdapter()
    entries = adapter.load(d)
    paths = [e.relative_path for e in entries]
    assert "file1.txt" in paths
    assert "subdir/file2.txt" in paths


def test_parquet_graceful_when_unavailable():
    from blindspot.data_adapters.parquet_adapter import ParquetAdapter, _PARQUET_AVAILABLE
    if not _PARQUET_AVAILABLE:
        adapter = ParquetAdapter()
        with pytest.raises(ImportError):
            adapter.load(Path("nonexistent.parquet"))


def test_default_registry_has_core_formats():
    reg = get_default_registry()
    assert "json" in reg.available_formats()
    assert "jsonl" in reg.available_formats()
    assert "csv" in reg.available_formats()
    assert "markdown" in reg.available_formats()
    assert "directory" in reg.available_formats()
