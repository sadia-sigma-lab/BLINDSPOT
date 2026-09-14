"""Core runtime engine: reset, step, tool execution, state transitions."""

from __future__ import annotations

import logging
import uuid
from typing import Any, Callable

from pydantic import BaseModel

from blindspot.core.action import AgentAction
from blindspot.core.observation import Observation
from blindspot.core.scenario import ScenarioSpec
from blindspot.core.state import WorldState
from blindspot.core.state_diff import StateDiff, StateMutation, apply_diff
from blindspot.core.tool import ExecutionContext
from blindspot.core.tool_result import ToolResult
from blindspot.core.trajectory import TrajectoryStep
from blindspot.exceptions import ComponentNotFoundError, ToolExecutionError
from blindspot.registry import RegistryHub
from blindspot.runtime.session import Session, _hash_state

logger = logging.getLogger(__name__)


class RuntimeHooks(BaseModel):
    """Lifecycle hooks for extending the engine without modifying core logic."""

    model_config = {"arbitrary_types_allowed": True}

    before_observation: list[Callable[..., None]] = []
    after_observation: list[Callable[..., None]] = []
    before_action: list[Callable[..., None]] = []
    after_action: list[Callable[..., None]] = []
    before_tool: list[Callable[..., None]] = []
    after_tool: list[Callable[..., None]] = []
    before_event: list[Callable[..., None]] = []
    after_event: list[Callable[..., None]] = []
    on_episode_end: list[Callable[..., None]] = []

    def _fire(self, hooks: list[Callable[..., None]], **kwargs: Any) -> None:
        for hook in hooks:
            try:
                hook(**kwargs)
            except Exception as exc:
                logger.warning("Hook %s raised: %s", hook, exc)


class BenchmarkEngine:
    """Domain-agnostic runtime engine for benchmark episodes."""

    def __init__(
        self,
        registries: RegistryHub,
        hooks: RuntimeHooks | None = None,
    ) -> None:
        self._registries = registries
        self._hooks = hooks or RuntimeHooks()
        self._session: Session | None = None
        self._trajectory: list[TrajectoryStep] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self, scenario: ScenarioSpec, seed: int) -> tuple[Observation, dict[str, Any]]:
        """Initialize a new episode; return the first observation."""
        domain = self._registries.domains.get(scenario.domain_id.canonical())
        initial_state = domain.initial_state(scenario, seed)
        self._session = Session(scenario, initial_state, seed)
        self._trajectory = []

        obs = self._build_observation(domain, initial_state)
        return obs, {"episode_id": self._session.episode_id, "seed": seed}

    def step(
        self, action: AgentAction
    ) -> tuple[Observation, dict[str, float], dict[str, float], bool, bool, dict[str, Any]]:
        """Apply one agent action; return (obs, rewards, costs, terminated, truncated, info)."""
        if self._session is None:
            raise ToolExecutionError("Engine not reset — call reset() first")

        session = self._session
        self._hooks._fire(self._hooks.before_action, action=action, session=session)

        pre_hash = session.current_state_hash
        tool_result: ToolResult | None = None
        state_diff = StateDiff(mutations=[])
        events_processed: list[str] = []

        if action.action_type == "tool_call" and action.name:
            tool_result = self._execute_tool(action, session)
            state_diff = tool_result.state_diff
            if not state_diff.is_empty:
                new_dict = apply_diff(
                    {
                        "public": session.state.public,
                        "private": session.state.private,
                        "hidden": session.state.hidden,
                        "audit_log": session.state.audit_log,
                    },
                    state_diff,
                )
                session.state = WorldState(
                    schema_version=session.state.schema_version,
                    episode_id=session.state.episode_id,
                    step=session.step,
                    session_id=session.state.session_id,
                    random_seed=session.state.random_seed,
                    public=new_dict.get("public", session.state.public),
                    private=new_dict.get("private", session.state.private),
                    hidden=new_dict.get("hidden", session.state.hidden),
                    audit_log=new_dict.get("audit_log", session.state.audit_log),
                )
                if tool_result.audit_entries:
                    session.state.audit_log.extend(tool_result.audit_entries)

        # Process due events
        for event in session.event_queue.due_events(session.step):
            self._hooks._fire(self._hooks.before_event, event=event, session=session)
            events_processed.append(event.event_id)
            self._hooks._fire(self._hooks.after_event, event=event, session=session)

        post_hash = session.current_state_hash
        session.step += 1

        # Record trajectory
        domain = self._registries.domains.get(session.scenario.domain_id.canonical())
        obs = self._build_observation(domain, session.state)

        step_record = TrajectoryStep(
            episode_id=session.episode_id,
            step=session.step - 1,
            session_id=session.session_id,
            observation=obs,
            raw_agent_output=action.model_dump(),
            parsed_action=action,
            tool_result=tool_result,
            pre_state_hash=pre_hash,
            post_state_hash=post_hash,
            state_diff=state_diff,
            events_processed=events_processed,
        )
        self._trajectory.append(step_record)

        self._hooks._fire(self._hooks.after_action, action=action, session=session)

        # Termination check
        if action.action_type in ("message", "no_op", "refuse", "escalate"):
            session.terminate()
        if session.step >= session.max_steps:
            session.truncate()

        terminated = session.terminated
        truncated = session.truncated

        if terminated or truncated:
            self._hooks._fire(
                self._hooks.on_episode_end, session=session, trajectory=self._trajectory
            )

        return obs, {}, {}, terminated, truncated, {"step": session.step}

    def snapshot(self) -> str:
        """Create and store a runtime snapshot; return its ID."""
        from blindspot.core.snapshot import RuntimeState

        if self._session is None:
            raise ToolExecutionError("Cannot snapshot: no active session")
        s = self._session
        snap = RuntimeState(
            snapshot_id=str(uuid.uuid4()),
            scenario_id=s.scenario.scenario_id.canonical(),
            session_id=s.session_id,
            step=s.step,
            world_state=s.state.model_dump(),
            event_queue=s.event_queue.to_list(),
            rng_state=s.rng_state_dict(),
            plugin_versions={},
            package_version="0.1.0",
        )
        self._last_snapshot = snap
        return snap.snapshot_id

    def get_trajectory(self) -> list[TrajectoryStep]:
        return list(self._trajectory)

    def get_session(self) -> Session | None:
        return self._session

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _execute_tool(self, action: AgentAction, session: Session) -> ToolResult:
        tool_name = action.name
        assert tool_name is not None
        ctx = ExecutionContext(
            session_id=session.session_id,
            actor_id=session.scenario.actors[0].get("id", "agent") if session.scenario.actors else "agent",
            step=session.step,
        )
        try:
            tool = self._registries.tools.get(tool_name)
        except ComponentNotFoundError:
            diff = StateDiff(mutations=[])
            return ToolResult(
                success=False,
                error_code="TOOL_NOT_FOUND",
                error_message=f"Tool {tool_name!r} is not registered",
                state_diff=diff,
            )

        self._hooks._fire(self._hooks.before_tool, tool=tool, action=action, session=session)

        try:
            result = tool.execute(session.state, ctx.actor_id, action.arguments, ctx)
        except Exception as exc:
            logger.exception("Tool %s raised during execution", tool_name)
            diff = StateDiff(mutations=[])
            result = ToolResult(
                success=False,
                error_code="TOOL_EXECUTION_ERROR",
                error_message=str(exc),
                state_diff=diff,
            )

        self._hooks._fire(self._hooks.after_tool, tool=tool, result=result, session=session)
        return result

    def _build_observation(self, domain: Any, state: WorldState) -> Observation:
        actor_id = "agent"
        if self._session and self._session.scenario.actors:
            actor_id = self._session.scenario.actors[0].get("id", "agent")

        obs = domain.build_observation(state, actor_id)
        self._hooks._fire(self._hooks.before_observation, observation=obs)
        return obs
