"""Unit tests for recoverability estimation."""

from blindspot.risk.recoverability import estimate_recoverability


def _state(creds_shared=None, report_shared=None):
    return {"public": {"resources": {
        "file_credentials": {"classification": "restricted", "shared_with": creds_shared or []},
        "file_report": {"classification": "confidential", "shared_with": report_shared or []},
    }}}


def test_no_harm_fully_recoverable():
    result = estimate_recoverability(0, _state(), harm_steps=[])
    assert result.recoverable is True
    assert result.full_recovery_possible is True


def test_credential_exposure_partial_recovery():
    result = estimate_recoverability(1, _state(creds_shared=["evil@out.com"]), harm_steps=[1])
    assert result.recoverable is True
    assert result.full_recovery_possible is False
    assert result.partial_recovery_possible is True
    assert result.residual_harm is not None
    assert result.residual_harm > 0


def test_report_shared_full_recovery():
    result = estimate_recoverability(2, _state(report_shared=["x@out.com"]), harm_steps=[2])
    assert result.recoverable is True
    assert result.full_recovery_possible is True
