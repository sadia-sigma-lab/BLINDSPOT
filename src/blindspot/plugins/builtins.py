"""Built-in plugin: registers the scripted actor."""

from __future__ import annotations

from blindspot.core.action import AgentAction
from blindspot.core.actor import Actor, ActorContext
from blindspot.core.identifiers import ComponentID
from blindspot.core.metadata import ComponentMetadata
from blindspot.core.observation import Observation
from blindspot.core.plugin import BenchmarkPlugin
from blindspot.registry import RegistryHub


class ScriptedActor(Actor):
    """Actor that executes a fixed sequence of actions; loops on the last one."""

    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="core", name="scripted-actor", version="1.0.0"),
        display_name="Scripted Actor",
        description="Replays a fixed list of AgentActions deterministically.",
        source_package="blindspot.plugins.builtins",
    )

    def __init__(self, script: list[AgentAction] | None = None) -> None:
        self._script: list[AgentAction] = script or []
        self._index = 0

    def set_script(self, script: list[AgentAction]) -> None:
        self._script = script
        self._index = 0

    def act(self, observation: Observation, context: ActorContext) -> AgentAction:
        if not self._script:
            import uuid
            return AgentAction(
                action_id=str(uuid.uuid4()),
                action_type="no_op",
            )
        idx = min(self._index, len(self._script) - 1)
        action = self._script[idx]
        self._index += 1
        return action


class BuiltinPlugin(BenchmarkPlugin):
    """Registers core built-in components."""

    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="core", name="builtin-plugin", version="1.0.0"),
        display_name="Built-in Plugin",
        description="Core built-in actors and utilities.",
        source_package="blindspot.plugins.builtins",
    )

    def register(self, registries: RegistryHub) -> None:
        actor = ScriptedActor()
        registries.actors.register(actor.metadata.component_id.canonical(), actor)

    def validate(self) -> None:
        pass
