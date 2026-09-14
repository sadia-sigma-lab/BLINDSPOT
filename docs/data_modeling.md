# Data Modeling

## Shared Canonical Models

All domain entities inherit from `BaseEntity` (timezone-aware timestamps, versioned, unique IDs). Shared types: `UserRecord`, `OrganizationRecord`, `ResourceRecord`, `PermissionRecord`, `ApprovalRecord`, `MessageRecord`, `DocumentRecord`, `PolicyDocument`, `ScheduledEventRecord`, `AuditRecord`, `MemoryRecord`, `ProvenanceRecord`.

## Domain Extension Pattern

Domains extend shared models without modifying them:

```python
class WorkspaceFileRecord(ResourceRecord):
    name: str
    content: str
    shared_with: list[str]
```

Register domain schemas in a `DomainStateBundle` — the normalized in-memory representation.

## Hidden State Isolation

Hidden fixture files (under `hidden/`) are loaded into `bundle.hidden_data` — never into observable collections. The `StateProjector` enforces this: `projection["hidden"]` is always `{}`.
