"""Simulator registry."""

from __future__ import annotations

from blindspot.simulators.base import ActorSimulator
from blindspot.simulators.scripted import (
    ApproverSimulator, BackgroundActorSimulator, MonitorSimulator,
    ScriptedSimulator, UserSimulator,
)


class SimulatorRegistry:
    def __init__(self) -> None:
        self._simulators: dict[str, ActorSimulator] = {}

    def register(self, simulator_id: str, simulator: ActorSimulator) -> None:
        self._simulators[simulator_id] = simulator

    def get(self, simulator_id: str) -> ActorSimulator:
        s = self._simulators.get(simulator_id)
        if s is None:
            raise KeyError(f"No simulator registered for {simulator_id!r}")
        return s

    def list(self) -> list[str]:
        return list(self._simulators.keys())


def get_default_simulator_registry() -> SimulatorRegistry:
    reg = SimulatorRegistry()
    reg.register("scripted", ScriptedSimulator())
    reg.register("user", UserSimulator())
    reg.register("approver", ApproverSimulator())
    reg.register("monitor", MonitorSimulator())
    reg.register("background", BackgroundActorSimulator())
    return reg
