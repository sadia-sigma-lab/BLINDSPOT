"""Minimal workspace domain — complete vertical-slice example."""

from examples.minimal_domain.domain import MinimalWorkspaceDomain
from examples.minimal_domain.evaluator import ShareEvaluator

__all__ = ["MinimalWorkspaceDomain", "ShareEvaluator", "MinimalDomainPlugin"]


class MinimalDomainPlugin:
    """Plugin that registers the minimal workspace domain."""

    from blindspot.core.identifiers import ComponentID
    from blindspot.core.metadata import ComponentMetadata

    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="examples", name="minimal-domain-plugin", version="1.0.0"),
        display_name="Minimal Domain Plugin",
        description="Registers the minimal_workspace domain for testing.",
        source_package="examples.minimal_domain",
    )

    def register(self, registries: "RegistryHub") -> None:  # noqa: F821
        from examples.minimal_domain.domain import MinimalWorkspaceDomain
        from examples.minimal_domain.evaluator import ShareEvaluator
        from examples.minimal_domain.tools import ListFilesTool, ReadFileTool, ShareFileTool

        domain = MinimalWorkspaceDomain()
        registries.domains.register(domain.metadata.component_id.canonical(), domain)

        for tool in domain.tools():
            tool_id = tool.metadata.component_id.canonical()
            if not registries.tools.contains(tool_id):
                registries.tools.register(tool_id, tool)
            # also register by short name for convenience
            short = tool.metadata.component_id.name
            if not registries.tools.contains(short):
                registries.tools.register(short, tool)

        evaluator = ShareEvaluator()
        registries.evaluators.register(
            evaluator.metadata.component_id.canonical(), evaluator
        )

    def validate(self) -> None:
        pass
