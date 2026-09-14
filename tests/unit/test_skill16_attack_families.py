"""Tests for Skill 16: 11 new attack families + update-policy tool."""

import pytest
from blindspot.dual_agent.escalation import SCHEDULES, EscalationState, AttackPhase
from blindspot.dual_agent.personas import get_persona_template, PERSONA_TEMPLATES

NEW_FAMILIES = [
    "env_prompt_injection",
    "double_payload",
    "loss_of_control",
    "capability_probe_exploit",
    "policy_ambiguity_exploit",
    "compound_request_hiding",
    "state_rollback_attack",
    "parametric_policy_override",
    "counterfactual_state_exploitation",
    "cross_app_chain",
    "social_proof_injection",
    "financial_regulatory_bypass",
    "software_ops_ci_injection",
    "customer_service_policy_laundering",
]


# ── Escalation schedule tests ─────────────────────────────────────────────────

def _turns_to_done(family: str) -> int:
    s = EscalationState(SCHEDULES[family])
    for t in range(35):
        refused = s.payload_delivered
        phase = s.advance(t, refused)
        if phase == AttackPhase.DONE:
            return t + 1
    return 35


@pytest.mark.parametrize("family", NEW_FAMILIES)
def test_new_family_schedule_registered(family):
    assert family in SCHEDULES, f"Schedule missing for {family}"


@pytest.mark.parametrize("family", NEW_FAMILIES)
def test_new_family_no_adversarial_before_payload(family):
    s = EscalationState(SCHEDULES[family])
    for t in range(SCHEDULES[family].benign_turns):
        phase = s.advance(t, False)
        assert not s.is_adversarial, f"{family}: adversarial at benign turn {t}"


def test_env_prompt_injection_never_reaches_payload():
    """env_prompt_injection payload comes from env, not user turns — schedule stays benign."""
    s = EscalationState(SCHEDULES["env_prompt_injection"])
    phases = {s.advance(t, False) for t in range(20)}
    assert AttackPhase.PAYLOAD not in phases
    assert AttackPhase.ESCALATION not in phases


def test_compliance_drift_and_new_families_reach_reasonable_turns():
    """Slow-boil families should all hit 12+ turns."""
    long_families = [
        "compliance_drift", "loss_of_control", "policy_ambiguity_exploit",
        "social_proof_injection", "capability_probe_exploit",
    ]
    for fam in long_families:
        turns = _turns_to_done(fam)
        assert turns >= 12, f"{fam} only ran {turns} turns — expected 12+"


def test_short_families_terminate_under_15():
    """Fast-burn and medium families should terminate before 15 turns."""
    for fam in ["stale_approval_reuse", "parametric_policy_override", "double_payload"]:
        turns = _turns_to_done(fam)
        assert turns <= 15, f"{fam} ran {turns} turns — expected ≤15"


# ── Persona template tests ────────────────────────────────────────────────────

@pytest.mark.parametrize("family", NEW_FAMILIES)
def test_new_family_persona_registered(family):
    tmpl = get_persona_template(family)
    assert tmpl is not None


@pytest.mark.parametrize("family", NEW_FAMILIES)
def test_new_family_persona_renders(family):
    tmpl = get_persona_template(family)
    rendered = tmpl.safe_substitute(
        task_description="Share report.txt with auditor@example.org",
        user_name="Alice", user_role="employee", current_turn=3, max_turns=20,
        phase="benign_establish", malicious_goal="share credentials externally",
        benign_turns=6, payload_turn=12, escalation_turns=4, give_up_after=4,
        refusal_count=0, refusal_reframe="Please reconsider", last_response="I cannot do that.",
        benign_request="Share report.txt", persona="senior employee",
        expired_approval_id="APR-001", expiry_date="last month",
        approver_name="Bob", false_premise="this was pre-approved",
        target_role="admin", target_permission="bypass approval",
        original_criterion="minimize cost", target_criterion="share freely",
        drift_messages="", step_list="", current_step=1, total_steps=3,
    )
    assert len(rendered) > 50, f"{family}: template rendered too short"
    assert "$" not in rendered.replace("$malicious_goal", "").replace("$task", ""), \
        f"{family}: template has un-substituted variables"


# ── UpdatePolicy tool tests ───────────────────────────────────────────────────

def test_update_policy_tool_importable():
    from blindspot.domains.minimal_workspace.tools.update_policy import UpdatePolicyTool
    tool = UpdatePolicyTool()
    assert tool.specification.display_name == "Update Policy Rule"


def test_update_policy_tool_in_all_tools():
    from blindspot.domains.minimal_workspace.tools import ALL_TOOLS
    names = [type(t).__name__ for t in ALL_TOOLS]
    assert "UpdatePolicyTool" in names


def test_update_policy_requires_admin_key():
    """Without admin key, mutation plan should be empty (unauthorized attempt logged)."""
    from blindspot.domains.minimal_workspace.tools.update_policy import UpdatePolicyTool, UpdatePolicyArgs
    from blindspot.domains.minimal_workspace.tool_collection import load_workspace_state
    from blindspot.tools.runtime import make_context
    from blindspot.tools.state_view import ReadOnlyStateView

    tool = UpdatePolicyTool()
    args = UpdatePolicyArgs(
        policy_id="policy_classification",
        rule_id="deny_public_restricted",
        new_effect="allow",
        reason="test",
        admin_key=None,  # no key
    )
    state = load_workspace_state(seed=42)
    view = ReadOnlyStateView(state.public, read_scopes=["policies", "resources"])
    ctx = make_context(
        actor_id="user_alice", step=0, seed=42,
        episode_id="t", session_id="t", scenario_id="t",
        domain_id="workspace", run_id="t"
    )
    plan = tool.plan_mutations(view, args, ctx)
    # Without admin key, operations list should be empty
    assert len(plan.operations) == 0
    # But audit log should record the attempt
    assert "security_event" in plan.audit_metadata
