"""Scenario split metadata and leakage prevention."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from blindspot.scenarios.exceptions import ScenarioLeakageError


class ScenarioSplitMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    split: Literal["train", "validation", "test", "challenge", "hidden_test", "community"]
    domain_holdout: bool = False
    attack_holdout: bool = False
    tool_composition_holdout: bool = False
    horizon_holdout: bool = False
    policy_holdout: bool = False
    actor_holdout: bool = False
    temporal_holdout: bool = False
    template_family: str = ""
    leakage_group_ids: list[str] = Field(default_factory=list)


class SplitLeakageChecker:
    """Checks for leakage across train/test boundaries."""

    def check_twin_leakage(
        self,
        unsafe_split: str,
        safe_split: str,
    ) -> None:
        """Safe twins of test scenarios must not be in train if twin_leakage not allowed."""
        bad_combinations = {
            ("hidden_test", "train"),
            ("hidden_test", "validation"),
            ("test", "train"),
        }
        if (unsafe_split, safe_split) in bad_combinations:
            raise ScenarioLeakageError(
                f"Safe twin in {safe_split!r} paired with unsafe in {unsafe_split!r} — "
                "this leaks ground truth across splits"
            )

    def check_template_leakage(
        self,
        scenarios: list[tuple[str, str, str]],
    ) -> list[str]:
        """Return leakage warnings for scenarios sharing template+params across splits.

        scenarios: list of (scenario_id, template_id, split)
        """
        from collections import defaultdict
        template_splits: dict[str, set[str]] = defaultdict(set)
        for _sid, tid, split in scenarios:
            template_splits[tid].add(split)

        warnings = []
        for tid, splits in template_splits.items():
            if "hidden_test" in splits and "train" in splits:
                warnings.append(
                    f"Template {tid!r} appears in both train and hidden_test splits"
                )
        return warnings

    def check_attack_holdout(
        self,
        attack_id: str,
        scenarios: list[tuple[str, str, str]],
    ) -> bool:
        """Return True if the attack_id is properly held out."""
        attack_splits = {split for _sid, aid, split in scenarios if aid == attack_id}
        return "hidden_test" not in attack_splits or "train" not in attack_splits
