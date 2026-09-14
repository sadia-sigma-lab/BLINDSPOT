"""Policy document validator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from blindspot.validators.base import BaseValidator
from blindspot.validators.reports import ValidationIssue

if TYPE_CHECKING:
    from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle

_VALID_EFFECTS = {"allow", "deny", "require_approval", "require_verification"}


class PolicyValidator(BaseValidator):
    """Validates policy document consistency."""

    name = "policy_validator"

    def validate(self, bundle: "DomainStateBundle") -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for doc_id, doc in bundle.policies.items():
            rule_ids: list[str] = []
            for rule in doc.rules:
                if rule.rule_id in rule_ids:
                    issues.append(ValidationIssue(
                        severity="error",
                        code="DUPLICATE_RULE_ID",
                        message=f"Policy {doc_id!r} has duplicate rule_id {rule.rule_id!r}",
                        collection="policies",
                        entity_id=doc_id,
                    ))
                rule_ids.append(rule.rule_id)
                if rule.effect not in _VALID_EFFECTS:
                    issues.append(ValidationIssue(
                        severity="error",
                        code="INVALID_RULE_EFFECT",
                        message=f"Rule {rule.rule_id!r} in {doc_id!r} has invalid effect {rule.effect!r}",
                        collection="policies",
                        entity_id=doc_id,
                    ))
                if not rule.action_pattern.strip():
                    issues.append(ValidationIssue(
                        severity="error",
                        code="EMPTY_ACTION_PATTERN",
                        message=f"Rule {rule.rule_id!r} in {doc_id!r} has empty action_pattern",
                        collection="policies",
                        entity_id=doc_id,
                    ))
        return issues
