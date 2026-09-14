"""DomainStateBundle and builder for the minimal workspace domain."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.data_model.approval import ApprovalRecord
from blindspot.data_model.audit import AuditRecord
from blindspot.data_model.event import ScheduledEventRecord
from blindspot.data_model.manifest import FixtureManifest, load_manifest
from blindspot.data_model.memory import MemoryRecord
from blindspot.data_model.message import MessageRecord
from blindspot.data_model.organization import OrganizationRecord
from blindspot.data_model.permission import PermissionRecord
from blindspot.data_model.policy import PolicyDocument
from blindspot.data_model.provenance import ProvenanceRecord
from blindspot.data_model.resource import ResourceRecord
from blindspot.data_model.user import UserRecord
from blindspot.exceptions import BenchmarkError
from blindspot.validators.reports import ValidationIssue, ValidationReport


class DomainStateBundle(BaseModel):
    """Normalized in-memory state bundle for one episode initialization."""

    model_config = ConfigDict(frozen=False)

    users: dict[str, UserRecord] = Field(default_factory=dict)
    organizations: dict[str, OrganizationRecord] = Field(default_factory=dict)
    resources: dict[str, ResourceRecord] = Field(default_factory=dict)
    permissions: dict[str, PermissionRecord] = Field(default_factory=dict)
    approvals: dict[str, ApprovalRecord] = Field(default_factory=dict)
    messages: dict[str, MessageRecord] = Field(default_factory=dict)
    policies: dict[str, PolicyDocument] = Field(default_factory=dict)
    events: dict[str, ScheduledEventRecord] = Field(default_factory=dict)
    memory: dict[str, MemoryRecord] = Field(default_factory=dict)
    provenance: dict[str, ProvenanceRecord] = Field(default_factory=dict)
    domain_data: dict[str, Any] = Field(default_factory=dict)
    hidden_data: dict[str, Any] = Field(default_factory=dict)

    def state_hash(self) -> str:
        """Compute a deterministic hash of the non-hidden, non-provenance state."""
        payload = {
            "users": {k: v.model_dump() for k, v in sorted(self.users.items())},
            "resources": {k: v.model_dump() for k, v in sorted(self.resources.items())},
            "permissions": {k: v.model_dump() for k, v in sorted(self.permissions.items())},
            "approvals": {k: v.model_dump() for k, v in sorted(self.approvals.items())},
            "domain_data": self.domain_data,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()


class DomainStateBuilder:
    """Loads a fixture bundle and constructs a DomainStateBundle."""

    def build(
        self,
        manifest_path: Path,
        seed: int,
        strict: bool = True,
    ) -> tuple[DomainStateBundle, ValidationReport]:
        """Load all fixture files, validate, and return a bundle + report."""
        manifest = load_manifest(manifest_path)
        fixture_dir = manifest_path.parent

        issues: list[ValidationIssue] = []
        checked_files = 0
        checked_entities = 0
        bundle = DomainStateBundle()

        for file_entry in manifest.files:
            file_path = fixture_dir / file_entry.path
            if not file_path.exists():
                issues.append(ValidationIssue(
                    severity="error",
                    code="MISSING_FIXTURE_FILE",
                    message=f"Fixture file not found: {file_entry.path}",
                    collection=file_entry.collection,
                ))
                if strict:
                    break
                continue

            # Checksum verification
            if file_entry.checksum:
                actual = hashlib.sha256(file_path.read_bytes()).hexdigest()
                if actual != file_entry.checksum:
                    issues.append(ValidationIssue(
                        severity="error",
                        code="CHECKSUM_MISMATCH",
                        message=f"Checksum mismatch for {file_entry.path}",
                        collection=file_entry.collection,
                        details={"expected": file_entry.checksum, "actual": actual},
                    ))

            # Hidden files go to hidden_data
            if file_entry.visibility == "hidden":
                data = self._load_json(file_path)
                bundle.hidden_data[file_entry.collection] = data
                checked_files += 1
                continue

            # Load by collection name
            try:
                count = self._load_collection(bundle, file_entry.collection, file_entry.format, file_path)
                checked_entities += count
                checked_files += 1
            except Exception as exc:
                issues.append(ValidationIssue(
                    severity="error",
                    code="FIXTURE_LOAD_ERROR",
                    message=f"Error loading {file_entry.path}: {exc}",
                    collection=file_entry.collection,
                ))

        # Run bundled validators
        from blindspot.validators.referential import ReferentialIntegrityValidator
        from blindspot.validators.permissions import PermissionValidator, ApprovalValidator
        from blindspot.validators.policies import PolicyValidator

        for validator in [
            ReferentialIntegrityValidator(),
            PermissionValidator(),
            ApprovalValidator(),
            PolicyValidator(),
        ]:
            issues.extend(validator.validate(bundle))

        # Run domain invariants
        from blindspot.validators.invariants import run_invariants
        issues.extend(run_invariants(bundle, manifest.invariants))

        has_errors = any(i.severity == "error" for i in issues)
        report = ValidationReport(
            valid=not has_errors,
            issues=issues,
            checked_files=checked_files,
            checked_entities=checked_entities,
            fixture_id=manifest.fixture_id,
        )
        return bundle, report

    def _load_json(self, path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    def _load_collection(
        self, bundle: DomainStateBundle, collection: str, fmt: str, path: Path
    ) -> int:
        """Load a collection file into the bundle; return count of entities."""
        from blindspot.data_adapters.registry import get_default_registry

        registry = get_default_registry()
        adapter = registry.get(fmt)
        raw = adapter.load(path)

        _COLLECTION_MAP: dict[str, tuple[str, type]] = {
            "users": ("users", UserRecord),
            "organizations": ("organizations", OrganizationRecord),
            "resources": ("resources", ResourceRecord),
            "permissions": ("permissions", PermissionRecord),
            "approvals": ("approvals", ApprovalRecord),
            "messages": ("messages", MessageRecord),
            "events": ("events", ScheduledEventRecord),
            "memory": ("memory", MemoryRecord),
        }

        if collection in _COLLECTION_MAP:
            attr, model_cls = _COLLECTION_MAP[collection]
            items = raw if isinstance(raw, list) else [raw]
            container: dict[str, Any] = getattr(bundle, attr)
            for item in items:
                if isinstance(item, dict):
                    obj = model_cls(**item)
                else:
                    obj = item
                container[obj.entity_id] = obj
            return len(items)

        if collection == "policies":
            # Policies may be a list or a single record
            import yaml as _yaml
            items = raw if isinstance(raw, list) else [raw]
            for item in items:
                if isinstance(item, dict):
                    obj = PolicyDocument(**item)
                else:
                    obj = item
                bundle.policies[obj.entity_id] = obj
            return len(items)

        # Unknown collection → store in domain_data
        bundle.domain_data[collection] = raw
        return 1 if raw else 0
