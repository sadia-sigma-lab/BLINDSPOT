"""Multi-horizon label computation with proper censoring."""

from __future__ import annotations

from typing import Any

from blindspot.risk.config import RiskLabelConfig


class HorizonLabeler:
    """Computes multi-horizon labels for all steps in a trajectory."""

    def __init__(self, config: RiskLabelConfig) -> None:
        self._config = config

    def compute_future_labels(
        self,
        steps: list[dict[str, Any]],
        event_steps_by_target: dict[str, list[int]],
    ) -> dict[int, dict[str, dict[str, int | None]]]:
        """
        Returns {step -> {event_target -> {horizon -> first_event_step_or_None_if_censored}}}.

        Censoring rules:
          - Positive event in window: record its step
          - Full negative horizon observed: record 0 (no event)
          - Truncated without event: record None (censored — do NOT map to 0)
        """
        total_steps = len(steps)
        result: dict[int, dict[str, dict[str, int | None]]] = {}

        for step_dict in steps:
            step = step_dict.get("step", 0)
            result[step] = {}

            for target, event_steps in event_steps_by_target.items():
                result[step][target] = {}
                for horizon in self._config.horizons:
                    window_end = step + horizon
                    # Look for first event in (step, step+horizon]
                    first_event = next(
                        (es for es in sorted(event_steps) if step < es <= window_end),
                        None,
                    )
                    if first_event is not None:
                        result[step][target][str(horizon)] = first_event
                    elif total_steps > window_end:
                        result[step][target][str(horizon)] = 0  # confirmed negative
                    else:
                        result[step][target][str(horizon)] = None  # censored

        return result
