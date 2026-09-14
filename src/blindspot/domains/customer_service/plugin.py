"""Customer service domain BenchmarkPlugin."""
from __future__ import annotations

from blindspot.core.identifiers import ComponentID
from blindspot.core.metadata import ComponentMetadata


class CustomerServiceDomainPlugin:
    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="core", name="customer-service-plugin", version="1.0.0"),
        display_name="Customer Service Domain Plugin",
        description="Registers the customer service domain for order management and refund safety testing.",
        source_package="blindspot.domains.customer_service",
    )

    def register(self, registries) -> None:
        import blindspot.domains.customer_service.validators  # register invariants
        from blindspot.domains.customer_service.tools import ALL_CS_TOOLS
        for tool in ALL_CS_TOOLS:
            tool_id = tool.specification.tool_id.canonical()
            if not registries.tools.contains(tool_id):
                registries.tools.register(tool_id, tool)
            short = tool.specification.tool_id.name
            if not registries.tools.contains(short):
                registries.tools.register(short, tool)

    def validate(self) -> None:
        pass
