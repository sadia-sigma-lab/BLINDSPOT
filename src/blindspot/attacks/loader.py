"""Attack plugin loader."""

from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING

from blindspot.attacks.exceptions import AttackRegistrationError
from blindspot.attacks.registry import AttackRegistry

if TYPE_CHECKING:
    from blindspot.attacks.base import Attack

logger = logging.getLogger(__name__)


def load_attack_from_path(dotted_path: str) -> "Attack":
    """Import ``module:ClassName`` and return an instance."""
    try:
        module_path, class_name = dotted_path.rsplit(":", 1)
    except ValueError as exc:
        raise AttackRegistrationError(
            f"Expected 'module.path:ClassName', got {dotted_path!r}"
        ) from exc

    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise AttackRegistrationError(f"Cannot import {module_path!r}: {exc}") from exc

    cls = getattr(module, class_name, None)
    if cls is None:
        raise AttackRegistrationError(f"Class {class_name!r} not found in {module_path!r}")

    return cls()


def load_attacks(paths: list[str], registry: AttackRegistry) -> list["Attack"]:
    """Load attacks from dotted paths; one failure does not block others."""
    loaded: list["Attack"] = []
    for path in sorted(paths):
        try:
            attack = load_attack_from_path(path)
            registry.register(attack)
            loaded.append(attack)
            logger.info("Loaded attack %s", attack.metadata.attack_id.canonical())
        except AttackRegistrationError as exc:
            logger.error("Attack registration error for %s: %s", path, exc)
            raise
        except Exception as exc:
            raise AttackRegistrationError(f"Failed to load attack {path!r}: {exc}") from exc
    return loaded
