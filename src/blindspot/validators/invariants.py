"""Domain invariant registry and decorator."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from blindspot.validators.reports import ValidationIssue

if TYPE_CHECKING:
    from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle

InvariantFn = Callable[["DomainStateBundle"], list[ValidationIssue]]

_INVARIANT_REGISTRY: dict[str, InvariantFn] = {}


def register_invariant(name: str) -> Callable[[InvariantFn], InvariantFn]:
    """Decorator to register a domain invariant function."""
    def decorator(fn: InvariantFn) -> InvariantFn:
        _INVARIANT_REGISTRY[name] = fn
        return fn
    return decorator


def run_invariants(
    bundle: "DomainStateBundle",
    invariant_names: list[str],
) -> list[ValidationIssue]:
    """Run named invariants and aggregate issues."""
    issues: list[ValidationIssue] = []
    for name in invariant_names:
        fn = _INVARIANT_REGISTRY.get(name)
        if fn is None:
            issues.append(ValidationIssue(
                severity="warning",
                code="UNKNOWN_INVARIANT",
                message=f"Invariant {name!r} is not registered",
            ))
            continue
        issues.extend(fn(bundle))
    return issues


def list_invariants() -> list[str]:
    return sorted(_INVARIANT_REGISTRY.keys())
