"""Counterfactual branching subsystem."""

from blindspot.counterfactuals.candidates import CounterfactualCandidate, select_critical_steps
from blindspot.counterfactuals.branching import (
    BranchComparison, BranchResult, CounterfactualBranchSpec,
)
from blindspot.counterfactuals.execution import BranchExecutor, compare_branches
from blindspot.counterfactuals.storage import BranchStore

__all__ = [
    "CounterfactualCandidate", "select_critical_steps",
    "BranchComparison", "BranchResult", "CounterfactualBranchSpec",
    "BranchExecutor", "compare_branches", "BranchStore",
]
