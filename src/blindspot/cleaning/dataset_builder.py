"""Dataset builder — assembles CleanTrajectories into train/val/test splits."""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any

from blindspot.cleaning.clean_trajectory import CleanTrajectory


class DatasetBuilder:
    """Builds dataset splits from clean trajectories with leakage prevention."""

    def __init__(
        self,
        artifact_root: str = "data",
        splits: dict[str, float] | None = None,
        shuffle_seed: int = 42,
    ) -> None:
        self._root = Path(artifact_root)
        self._splits = splits or {"train": 0.70, "validation": 0.15, "test": 0.15}
        self._seed = shuffle_seed

    def build(self, trajectories: list[CleanTrajectory]) -> dict[str, list[CleanTrajectory]]:
        """Split trajectories into train/val/test, preventing leakage by source episode."""
        publishable = [t for t in trajectories if t.publishable]
        if not publishable:
            return {k: [] for k in self._splits}

        # Group by source run to prevent leakage within episode families
        by_source: dict[str, list[CleanTrajectory]] = {}
        for t in publishable:
            source = t.source_trajectory_id
            by_source.setdefault(source, []).append(t)

        # Shuffle source groups deterministically
        source_keys = sorted(by_source.keys())
        rng = random.Random(self._seed)
        rng.shuffle(source_keys)

        # Split source groups
        n = len(source_keys)
        split_sizes = {k: max(1, int(v * n)) for k, v in self._splits.items()}
        result: dict[str, list[CleanTrajectory]] = {k: [] for k in self._splits}
        idx = 0
        for split_name, size in split_sizes.items():
            for key in source_keys[idx:idx + size]:
                result[split_name].extend(by_source[key])
            idx += size

        # Write splits to disk
        self._write_splits(result)
        return result

    def _write_splits(self, splits: dict[str, list[CleanTrajectory]]) -> None:
        datasets_dir = self._root / "datasets"
        datasets_dir.mkdir(parents=True, exist_ok=True)

        stats: dict[str, Any] = {}
        for split_name, trajectories in splits.items():
            out_path = datasets_dir / f"{split_name}.jsonl"
            with out_path.open("w", encoding="utf-8") as f:
                for t in trajectories:
                    f.write(json.dumps(t.to_training_record(), default=str) + "\n")

            label_dist: dict[str, int] = {}
            for t in trajectories:
                label_dist[t.safety_label] = label_dist.get(t.safety_label, 0) + 1

            stats[split_name] = {
                "count": len(trajectories),
                "label_distribution": label_dist,
                "avg_turns": sum(t.turns for t in trajectories) / max(len(trajectories), 1),
                "avg_tool_calls": sum(t.tool_calls for t in trajectories) / max(len(trajectories), 1),
            }

        # Dataset card
        card = {
            "dataset_id": "lh-agentbench-v1",
            "description": "Long-horizon agent safety benchmark — dual-agent generated trajectories",
            "splits": stats,
            "total_publishable": sum(len(t) for t in splits.values()),
            "label_schema": ["safe", "unsafe_completion", "correct_refusal", "ambiguous"],
            "episode_types": ["benign", "adversarial_safe", "adversarial_unsafe", "hazard"],
            "models": {
                "user_agent": "Claude Haiku 4.5 (via AWS Bedrock)",
                "execution_agent": "Claude Opus 4.6 (via AWS Bedrock)",
                "judge": "Claude Opus 5 (via AWS Bedrock)",
            },
        }
        (datasets_dir / "dataset_card.json").write_text(
            json.dumps(card, indent=2), encoding="utf-8"
        )


class DatasetStats:
    """Compute and display dataset statistics."""

    @staticmethod
    def compute(trajectories: list[CleanTrajectory]) -> dict[str, Any]:
        if not trajectories:
            return {}
        total = len(trajectories)
        label_dist: dict[str, int] = {}
        type_dist: dict[str, int] = {}
        for t in trajectories:
            label_dist[t.safety_label] = label_dist.get(t.safety_label, 0) + 1
            type_dist[t.episode_type] = type_dist.get(t.episode_type, 0) + 1

        turns = [t.turns for t in trajectories]
        tools = [t.tool_calls for t in trajectories]
        return {
            "total": total,
            "publishable": sum(1 for t in trajectories if t.publishable),
            "avg_turns": sum(turns) / total,
            "min_turns": min(turns),
            "max_turns": max(turns),
            "avg_tool_calls": sum(tools) / total,
            "label_distribution": label_dist,
            "episode_type_distribution": type_dist,
        }
