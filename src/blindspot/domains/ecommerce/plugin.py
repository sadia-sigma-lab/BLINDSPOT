"""E-commerce domain BenchmarkPlugin."""
from __future__ import annotations

from blindspot.core.identifiers import ComponentID
from blindspot.core.metadata import ComponentMetadata


class EcommerceDomainPlugin:
    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="core", name="ecommerce-plugin", version="1.0.0"),
        display_name="E-commerce Domain Plugin",
        description="Registers the e-commerce domain for product search, cart, and checkout safety testing.",
        source_package="blindspot.domains.ecommerce",
    )

    def register(self, registries) -> None:
        import blindspot.domains.ecommerce.validators  # register invariants
        from blindspot.domains.ecommerce.tools import ALL_ECOMMERCE_TOOLS
        for tool in ALL_ECOMMERCE_TOOLS:
            tool_id = tool.specification.tool_id.canonical()
            if not registries.tools.contains(tool_id):
                registries.tools.register(tool_id, tool)
            short = tool.specification.tool_id.name
            if not registries.tools.contains(short):
                registries.tools.register(short, tool)

    def validate(self) -> None:
        pass
