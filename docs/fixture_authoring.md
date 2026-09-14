# Fixture Authoring

## Structure

Each fixture bundle lives in a directory containing:
- `manifest.yaml` — declares all files, checksums, invariants, provenance
- `users.json`, `resources.json`, etc. — data files by collection
- `hidden/` — grading and attack state (never visible to agent)

## Adding a Fixture File

1. Create the data file (JSON, JSONL, CSV, or Markdown)
2. Compute its SHA-256 checksum: `python -c "import hashlib; print(hashlib.sha256(open('file').read().encode()).hexdigest())"`
3. Add an entry to `manifest.yaml`
4. Run `blindspot fixtures validate --fixture <id>` to confirm

## Checksums

Checksums are verified on load. To recompute all checksums: `blindspot fixtures checksum --fixture <id>`
