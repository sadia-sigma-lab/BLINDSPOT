"""Finance domain BenchmarkPlugin."""
from __future__ import annotations
from blindspot.core.identifiers import ComponentID
from blindspot.core.metadata import ComponentMetadata


class FinanceDomainPlugin:
    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="core", name="finance-plugin", version="1.0.0"),
        display_name="Finance Domain Plugin",
        description="Registers the finance domain for testing payment and PII safety.",
        source_package="blindspot.domains.finance",
    )

    def register(self, registries) -> None:
        import blindspot.domains.finance.validators  # register invariants
        from blindspot.domains.finance.tools import ALL_FINANCE_TOOLS
        for tool in ALL_FINANCE_TOOLS:
            tool_id = tool.specification.tool_id.canonical()
            if not registries.tools.contains(tool_id):
                registries.tools.register(tool_id, tool)
            short = tool.specification.tool_id.name
            if not registries.tools.contains(short):
                registries.tools.register(short, tool)

    def validate(self) -> None:
        pass
