"""Benign control attack — no adversarial effect."""

from blindspot.attacks.controls import BenignControlAttack

# Re-export for plugin loading
__all__ = ["BenignControlAttack"]
