"""Scenario composition engine — assembles atoms into a full FullScenarioSpec."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.scenarios.atoms import ALL_ATOMS, ScenarioAtom
from blindspot.scenarios.exceptions import ScenarioCompositionError
from blindspot.scenarios.schema import FullScenarioSpec


class ScenarioCompositionSpec(BaseModel):
    model_config = ConfigDict(frozen=True)
    composition_id: str
    atom_ids: list[str]
    bindings: dict[str, Any] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)
    generation_seed: int = 42


class ScenarioComposer:
    """Builds scenario specs by composing atomic components."""

    def __init__(self, atom_library: dict[str, ScenarioAtom] | None = None) -> None:
        self._atoms = atom_library or ALL_ATOMS

    def compose(self, spec: ScenarioCompositionSpec) -> dict[str, Any]:
        """Return a partial scenario dict from the given composition spec."""
        resolved_atoms: list[ScenarioAtom] = []
        for atom_id in spec.atom_ids:
            atom = self._atoms.get(atom_id)
            if atom is None:
                raise ScenarioCompositionError(f"Atom {atom_id!r} not found in library")
            resolved_atoms.append(atom)

        # Collect required capabilities
        all_capabilities: set[str] = set()
        for atom in resolved_atoms:
            all_capabilities.update(atom.required_capabilities)

        # Check constraint compatibility
        for constraint in spec.constraints:
            if constraint not in [c for atom in resolved_atoms for c in atom.constraints]:
                # Additional external constraint — record but don't fail
                pass

        return {
            "composition_id": spec.composition_id,
            "atom_ids": spec.atom_ids,
            "bindings": spec.bindings,
            "required_capabilities": sorted(all_capabilities),
            "generation_seed": spec.generation_seed,
        }
