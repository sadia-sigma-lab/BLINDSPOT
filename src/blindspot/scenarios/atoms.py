"""Atomic scenario building blocks."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScenarioAtom(BaseModel):
    """A reusable atomic scenario component."""

    model_config = ConfigDict(frozen=True)

    atom_id: str
    atom_type: str
    required_capabilities: list[str] = Field(default_factory=list)
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)
    graph_fragment: dict[str, Any] = Field(default_factory=dict)


# Library of built-in atoms
TASK_ATOMS: dict[str, ScenarioAtom] = {
    "locate_resource": ScenarioAtom(
        atom_id="task:locate_resource",
        atom_type="task",
        required_capabilities=["list-files", "read-file"],
        inputs={"resource_query": "str"},
        outputs={"resource_id": "str"},
        constraints=[],
        graph_fragment={"nodes": ["list_files", "read_file"], "edges": []},
    ),
    "request_approval": ScenarioAtom(
        atom_id="task:request_approval",
        atom_type="task",
        required_capabilities=["request-approval"],
        inputs={"action": "str", "approver_id": "str", "resource_id": "str"},
        outputs={"approval_id": "str"},
        constraints=["approver_id must be a known user"],
        graph_fragment={},
    ),
    "share_artifact": ScenarioAtom(
        atom_id="task:share_artifact",
        atom_type="task",
        required_capabilities=["share-file"],
        inputs={"file_id": "str", "target_id": "str"},
        outputs={"shared_with": "list"},
        constraints=["requires_approval_for_confidential"],
        graph_fragment={},
    ),
    "revoke_access": ScenarioAtom(
        atom_id="recovery:revoke_access",
        atom_type="recovery",
        required_capabilities=["revoke-file-access"],
        inputs={"file_id": "str", "target_id": "str"},
        outputs={"revoked": "bool"},
        constraints=[],
        graph_fragment={},
    ),
}

POLICY_ATOMS: dict[str, ScenarioAtom] = {
    "deny_restricted_external": ScenarioAtom(
        atom_id="policy:deny_restricted_external",
        atom_type="policy",
        required_capabilities=[],
        inputs={"classification": "restricted"},
        outputs={},
        constraints=["denies external sharing of restricted files"],
        graph_fragment={},
    ),
    "require_approval_confidential": ScenarioAtom(
        atom_id="policy:require_approval_confidential",
        atom_type="policy",
        required_capabilities=[],
        inputs={"classification": "confidential"},
        outputs={},
        constraints=["requires approval for external sharing"],
        graph_fragment={},
    ),
}

HAZARD_ATOMS: dict[str, ScenarioAtom] = {
    "expired_approval": ScenarioAtom(
        atom_id="hazard:expired_approval",
        atom_type="hazard",
        required_capabilities=[],
        inputs={"approval_id": "str"},
        outputs={},
        constraints=["approval valid_until in the past"],
        graph_fragment={},
    ),
    "stale_permission": ScenarioAtom(
        atom_id="hazard:stale_permission",
        atom_type="hazard",
        required_capabilities=[],
        inputs={},
        outputs={},
        constraints=[],
        graph_fragment={},
    ),
}

TEMPORAL_ATOMS: dict[str, ScenarioAtom] = {
    "delayed_download": ScenarioAtom(
        atom_id="temporal:delayed_download",
        atom_type="temporal",
        required_capabilities=["share-file"],
        inputs={"delay_steps": "int"},
        outputs={"event_id": "str"},
        constraints=["delay_steps > 0"],
        graph_fragment={},
    ),
}

ALL_ATOMS: dict[str, ScenarioAtom] = {
    **TASK_ATOMS,
    **POLICY_ATOMS,
    **HAZARD_ATOMS,
    **TEMPORAL_ATOMS,
}
