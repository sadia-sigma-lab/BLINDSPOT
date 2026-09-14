"""Unit tests for ComponentRegistry and RegistryHub."""

import pytest

from blindspot.exceptions import ComponentNotFoundError, DuplicateRegistrationError
from blindspot.registry import ComponentRegistry, RegistryHub


def test_register_and_get() -> None:
    reg: ComponentRegistry[str] = ComponentRegistry("test")
    reg.register("a:b@1.0.0", "value")
    assert reg.get("a:b@1.0.0") == "value"


def test_duplicate_registration_raises() -> None:
    reg: ComponentRegistry[str] = ComponentRegistry("test")
    reg.register("a:b@1.0.0", "first")
    with pytest.raises(DuplicateRegistrationError):
        reg.register("a:b@1.0.0", "second")


def test_missing_component_raises() -> None:
    reg: ComponentRegistry[str] = ComponentRegistry("test")
    with pytest.raises(ComponentNotFoundError):
        reg.get("missing:id@1.0.0")


def test_deterministic_listing() -> None:
    reg: ComponentRegistry[str] = ComponentRegistry("test")
    for k in ["c:z@1.0.0", "a:a@1.0.0", "b:m@1.0.0"]:
        reg.register(k, k)
    ids = reg.list()
    assert ids == ["c:z@1.0.0", "a:a@1.0.0", "b:m@1.0.0"]


def test_unregister() -> None:
    reg: ComponentRegistry[str] = ComponentRegistry("test")
    reg.register("a:b@1.0.0", "v")
    reg.unregister("a:b@1.0.0")
    assert not reg.contains("a:b@1.0.0")


def test_alias_lookup() -> None:
    reg: ComponentRegistry[str] = ComponentRegistry("test")
    reg.register("a:b@1.0.0", "value")
    reg.register_alias("short", "a:b@1.0.0")
    assert reg.get("short") == "value"


def test_alias_duplicate_raises() -> None:
    reg: ComponentRegistry[str] = ComponentRegistry("test")
    reg.register("a:b@1.0.0", "value")
    reg.register_alias("short", "a:b@1.0.0")
    with pytest.raises(DuplicateRegistrationError):
        reg.register_alias("short", "a:b@1.0.0")


def test_clear() -> None:
    reg: ComponentRegistry[str] = ComponentRegistry("test")
    reg.register("a:b@1.0.0", "v")
    reg.clear()
    assert reg.list() == []


def test_registry_hub_has_all_registries() -> None:
    hub = RegistryHub()
    for name in ("domains", "tools", "attacks", "scenarios", "evaluators", "actors", "policies", "interventions"):
        assert hasattr(hub, name)


def test_registry_hub_clear_all() -> None:
    hub = RegistryHub()
    hub.domains.register("x:y@1.0.0", object())
    hub.clear_all()
    assert hub.domains.list() == []
