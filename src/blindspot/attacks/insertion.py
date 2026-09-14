"""Insertion point abstraction — where and how payloads enter the environment."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from blindspot.attacks.hooks import AttackEffect, AttackHook
from blindspot.attacks.payload import AttackPayload


class InsertionPoint(BaseModel):
    """Declares where and how an attack effect is applied."""

    model_config = ConfigDict(frozen=True)

    hook: AttackHook
    selector: dict[str, Any] = Field(default_factory=dict)
    operation: Literal["append", "prepend", "replace", "merge", "mask"]
    priority: int = 0


def apply_message_insertion(
    existing_messages: list[dict[str, Any]],
    payload: AttackPayload,
    insertion: InsertionPoint,
    attack_id: str,
) -> list[dict[str, Any]]:
    """Apply a message payload at the insertion point; return updated messages."""
    agent_content = payload.agent_visible_content()
    new_msg: dict[str, Any] = {
        "role": "user",
        "content": agent_content if isinstance(agent_content, str) else str(agent_content),
        "__attack_id": attack_id,
        "__payload_id": payload.payload_id,
    }

    if insertion.operation == "append":
        return list(existing_messages) + [new_msg]
    if insertion.operation == "prepend":
        return [new_msg] + list(existing_messages)
    if insertion.operation == "replace":
        return [new_msg]
    if insertion.operation == "merge":
        if existing_messages:
            merged = dict(existing_messages[-1])
            existing_content = merged.get("content", "")
            merged["content"] = f"{existing_content}\n{new_msg['content']}"
            return list(existing_messages[:-1]) + [merged]
        return [new_msg]
    # mask: return empty
    return []


def compose_effects(
    effects: list[tuple[AttackEffect, int, str]],
    conflict_policy: Literal["error", "highest_priority", "merge_if_compatible"],
) -> AttackEffect:
    """Merge multiple attack effects; resolve conflicts per policy.

    effects: list of (effect, priority, attack_id)
    """
    if not effects:
        return AttackEffect.noop()

    if len(effects) == 1:
        return effects[0][0]

    # Sort by priority descending, then attack_id for determinism
    sorted_effects = sorted(effects, key=lambda x: (-x[1], x[2]))

    # Check for conflicting replace operations
    if conflict_policy == "error":
        replace_attacks = [eid for eff, _, eid in sorted_effects
                           if any(m.get("operation") == "replace"
                                  for m in eff.observations_to_modify)]
        if len(replace_attacks) > 1:
            from blindspot.attacks.exceptions import AttackCompositionError
            raise AttackCompositionError(
                f"Multiple attacks request replace: {replace_attacks}"
            )

    # Merge: highest priority wins for replace, all contribute for append/add
    messages: list[dict] = []
    obs_mods: list[dict] = []
    tool_mods: list[dict] = []
    mem_adds: list[dict] = []
    events: list[dict] = []
    meta: dict[str, Any] = {}

    for eff, priority, attack_id in sorted_effects:
        messages.extend(eff.messages_to_add)
        obs_mods.extend(eff.observations_to_modify)
        tool_mods.extend(eff.tool_results_to_modify)
        mem_adds.extend(eff.memory_records_to_add)
        events.extend(eff.events_to_emit)
        meta.update(eff.metadata_updates)

    return AttackEffect(
        messages_to_add=messages,
        observations_to_modify=obs_mods,
        tool_results_to_modify=tool_mods,
        memory_records_to_add=mem_adds,
        events_to_emit=events,
        metadata_updates=meta,
        no_op=False,
    )
