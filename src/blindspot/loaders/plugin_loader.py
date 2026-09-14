"""Plugin discovery and loading from explicit module paths or entry points."""

from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING

from blindspot.exceptions import DuplicateRegistrationError, PluginLoadError

if TYPE_CHECKING:
    from blindspot.core.plugin import BenchmarkPlugin
    from blindspot.registry import RegistryHub

logger = logging.getLogger(__name__)


def load_plugin_from_path(dotted_path: str) -> BenchmarkPlugin:
    """Import ``module:ClassName`` and return an instance."""
    try:
        module_path, class_name = dotted_path.rsplit(":", 1)
    except ValueError as exc:
        raise PluginLoadError(
            dotted_path, ValueError("Expected 'module.path:ClassName' format")
        ) from exc

    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise PluginLoadError(dotted_path, exc) from exc

    cls = getattr(module, class_name, None)
    if cls is None:
        raise PluginLoadError(
            dotted_path, AttributeError(f"Class {class_name!r} not found in {module_path!r}")
        )

    try:
        instance: BenchmarkPlugin = cls()
    except Exception as exc:
        raise PluginLoadError(dotted_path, exc) from exc

    return instance


def load_plugins(
    plugin_paths: list[str],
    registries: RegistryHub,
) -> list[BenchmarkPlugin]:
    """Load and register plugins from a list of dotted paths.

    A single failed plugin does not prevent others from loading.
    """
    loaded: list[BenchmarkPlugin] = []
    errors: list[tuple[str, Exception]] = []

    # Sort for deterministic order
    for path in sorted(plugin_paths):
        try:
            plugin = load_plugin_from_path(path)
            plugin.validate()
            plugin.register(registries)
            loaded.append(plugin)
            logger.info("Loaded plugin %s (%s)", path, plugin.metadata.component_id.canonical())
        except DuplicateRegistrationError as exc:
            errors.append((path, exc))
            logger.error("Plugin %s caused duplicate registration: %s", path, exc)
            raise  # duplicate registrations are fatal — fail fast
        except PluginLoadError as exc:
            errors.append((path, exc))
            logger.error("Plugin load failure: %s", exc)
        except Exception as exc:
            wrapped = PluginLoadError(path, exc)
            errors.append((path, wrapped))
            logger.error("Unexpected error loading plugin %s: %s", path, exc)

    if errors and not loaded:
        # All plugins failed — surface the first error
        raise errors[0][1]

    return loaded
