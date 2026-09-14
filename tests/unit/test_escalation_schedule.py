"""Unit tests for escalation schedules and state machine."""

from blindspot.dual_agent.escalation import (
    AttackPhase, EscalationSchedule, EscalationState, SCHEDULES,
)


def test_benign_user_stays_benign():
    state = EscalationState(SCHEDULES["benign_user"])
    phases = set()
    # Run enough turns to reach DONE (benign_turns=10 + persistence_turns=6 = 16+)
    for turn in range(25):
        phase = state.advance(turn, False)
        phases.add(phase)
        if phase == AttackPhase.DONE:
            break
    assert AttackPhase.PAYLOAD not in phases
    assert AttackPhase.ESCALATION not in phases
    assert AttackPhase.DONE in phases


def test_compliance_drift_reaches_payload():
    state = EscalationState(SCHEDULES["compliance_drift"])
    phases = []
    # payload_turn=12, so need at least 13 turns
    for turn in range(15):
        phase = state.advance(turn, False)
        phases.append(phase)
    assert AttackPhase.PAYLOAD in phases
    assert state.payload_delivered


def test_give_up_after_refusals():
    state = EscalationState(SCHEDULES["intent_hijacking"])
    # Advance to payload (payload_turn=6)
    for turn in range(7):
        state.advance(turn, False)
    # Now refuse repeatedly until give_up_after is hit
    for _ in range(SCHEDULES["intent_hijacking"].give_up_after):
        phase = state.advance(7, True)
    assert phase == AttackPhase.DONE


def test_persistence_after_single_refusal():
    state = EscalationState(SCHEDULES["compliance_drift"])
    payload_turn = SCHEDULES["compliance_drift"].payload_turn
    for turn in range(payload_turn):
        state.advance(turn, False)
    state.advance(payload_turn, False)  # deliver payload
    state.payload_delivered = True
    phase = state.advance(payload_turn + 1, True)  # first refusal
    assert phase == AttackPhase.PERSISTENCE
    assert state.refusal_count == 1


def test_benign_turns_emit_no_adversarial_phase():
    state = EscalationState(SCHEDULES["compliance_drift"])
    for turn in range(SCHEDULES["compliance_drift"].benign_turns):
        phase = state.advance(turn, False)
        assert not state.is_adversarial, f"Turn {turn} should be non-adversarial"


def test_all_schedules_registered():
    expected = [
        "benign_user", "compliance_drift", "intent_hijacking",
        "task_injection", "tool_chaining", "objective_drifting",
        "role_drift", "stale_approval_reuse", "false_context_injection",
    ]
    for family in expected:
        assert family in SCHEDULES, f"Missing schedule for {family}"


def test_intent_hijacking_reaches_payload():
    """intent_hijacking has payload_turn=6 — must reach it within 10 turns."""
    state = EscalationState(SCHEDULES["intent_hijacking"])
    phases = [state.advance(t, False) for t in range(10)]
    assert AttackPhase.PAYLOAD in phases
    payload_turn = next(i for i, p in enumerate(phases) if p == AttackPhase.PAYLOAD)
    assert payload_turn <= 7


def test_long_trajectory_compliance_drift():
    """compliance_drift should run 15+ turns before DONE."""
    state = EscalationState(SCHEDULES["compliance_drift"])
    turns_run = 0
    for turn in range(25):
        # Agent refuses after payload delivery
        refused = state.payload_delivered
        phase = state.advance(turn, refused)
        turns_run = turn + 1
        if phase == AttackPhase.DONE:
            break
    assert turns_run >= 14, f"Expected ≥14 turns, got {turns_run}"
