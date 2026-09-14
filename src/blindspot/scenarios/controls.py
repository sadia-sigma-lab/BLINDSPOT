"""Safe counterfactual twin generation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SafeTwinSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_scenario_id: str
    twin_scenario_id: str
    transformations: list[dict[str, Any]]
    preserved_fields: list[str]
    changed_fields: list[str]
    expected_attack_inactive: bool = True


def generate_safe_twin(
    source_spec: dict[str, Any],
    transformation: str,
    twin_id_suffix: str = "safe",
) -> tuple[dict[str, Any], SafeTwinSpec]:
    """Generate a safe twin from a source scenario spec dict."""
    import copy

    twin = copy.deepcopy(source_spec)

    # Record what was changed
    changed: list[str] = []
    preserved: list[str] = []

    if transformation == "remove_payload":
        # Remove all attack bindings
        if "attacks" in twin:
            twin["attacks"] = []
            changed.append("attacks")

    elif transformation == "benign_payload":
        # Disable all attacks
        if "attacks" in twin:
            for atk in twin["attacks"]:
                if isinstance(atk, dict):
                    atk["enabled"] = False
            changed.append("attacks")

    elif transformation == "no_activation":
        # Disable attack activation
        if "attacks" in twin:
            for atk in twin["attacks"]:
                if isinstance(atk, dict):
                    atk.get("activation_condition", {}).update({"never": True})
            changed.append("attacks.activation_condition")

    elif transformation == "safe_target":
        # Replace any external recipients with known safe ones
        if "task" in twin and isinstance(twin["task"], dict):
            twin["task"]["instruction"] = twin["task"].get("instruction", "").replace(
                "unknown@outside.com", "auditor@example.org"
            )
            changed.append("task.instruction")

    # Record preserved fields
    preserved = [f for f in source_spec.keys() if f not in changed]

    source_id = source_spec.get("_scenario_id", "unknown")
    twin_id = f"{source_id}_{twin_id_suffix}"
    twin["_scenario_id"] = twin_id
    twin["_is_safe_twin"] = True
    twin["_source_scenario_id"] = source_id

    spec = SafeTwinSpec(
        source_scenario_id=source_id,
        twin_scenario_id=twin_id,
        transformations=[{"type": transformation}],
        preserved_fields=preserved,
        changed_fields=changed,
        expected_attack_inactive=True,
    )
    return twin, spec
