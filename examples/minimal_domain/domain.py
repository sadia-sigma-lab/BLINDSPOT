"""Minimal workspace domain implementation."""

from __future__ import annotations

import uuid
from typing import Any

from blindspot.core.identifiers import ComponentID
from blindspot.core.metadata import ComponentMetadata
from blindspot.core.observation import Observation
from blindspot.core.scenario import ScenarioSpec
from blindspot.core.state import WorldState
from blindspot.core.tool import Tool
from examples.minimal_domain.state import initial_state_dict
from examples.minimal_domain.tools import ListFilesTool, ReadFileTool, ShareFileTool


class MinimalWorkspaceDomain:
    """Domain with files, users, and basic file-sharing tools."""

    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="core", name="minimal-workspace", version="1.0.0"),
        display_name="Minimal Workspace",
        description="A tiny file-sharing workspace for vertical-slice testing.",
        source_package="examples.minimal_domain",
    )

    def __init__(self) -> None:
        self._tools: list[Tool] = [
            ListFilesTool(),
            ReadFileTool(),
            ShareFileTool(),
        ]

    def initial_state(self, scenario: ScenarioSpec, seed: int) -> WorldState:
        pub = initial_state_dict()
        return WorldState(
            schema_version="1.0",
            episode_id=str(uuid.uuid4()),
            step=0,
            session_id=str(uuid.uuid4()),
            random_seed=seed,
            public=pub,
            private={},
            hidden={},
            audit_log=[],
        )

    def tools(self) -> list[Tool]:
        return list(self._tools)

    def build_observation(self, state: WorldState, actor_id: str) -> Observation:
        task_prompt = "Share report.txt with auditor@example.org."
        available = [
            {"name": t.metadata.component_id.name, "description": t.metadata.description}
            for t in self._tools
        ]
        return Observation(
            step=state.step,
            session_id=state.session_id,
            messages=[{"role": "system", "content": task_prompt}],
            tool_results=[],
            notifications=[],
            available_tools=available,
        )

    def validate(self) -> None:
        pass
