"""Attack subsystem exceptions."""

from blindspot.exceptions import BenchmarkError


class AttackError(BenchmarkError):
    """Base class for attack subsystem errors."""


class AttackRegistrationError(AttackError):
    """Raised when an attack fails registration validation."""


class AttackConfigError(AttackError):
    """Raised when attack configuration is invalid."""


class AttackBudgetExhaustedError(AttackError):
    """Raised when an attack exceeds its budget."""


class AttackVisibilityError(AttackError):
    """Raised when an attacker accesses state outside its knowledge tier."""


class AttackEffectValidationError(AttackError):
    """Raised when an attack effect fails validation."""


class AttackCompositionError(AttackError):
    """Raised when composed attacks conflict irreconcilably."""


class AttackNotFoundError(AttackError):
    """Raised when a requested attack is not registered."""

    def __init__(self, attack_id: str) -> None:
        super().__init__(f"Attack not found: {attack_id!r}")
        self.attack_id = attack_id
