"""Governance domain plugin."""
from __future__ import annotations
from blindspot.core.identifiers import ComponentID
from blindspot.core.metadata import ComponentMetadata


class GovernanceDomainPlugin:
    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="core", name="governance-plugin", version="1.0.0"),
        display_name="Governance Domain Plugin",
        description="Registers the governance domain for loss-of-control safety testing.",
        source_package="blindspot.domains.governance",
    )

    def register(self, registries) -> None:
        import blindspot.domains.governance.validators
        from blindspot.domains.governance.tools import ALL_GOVERNANCE_TOOLS
        for tool in ALL_GOVERNANCE_TOOLS:
            tool_id = tool.specification.tool_id.canonical()
            if not registries.tools.contains(tool_id):
                registries.tools.register(tool_id, tool)
            short = tool.specification.tool_id.name
            if not registries.tools.contains(f"gov-{short}"):
                registries.tools.register(f"gov-{short}", tool)

    def validate(self) -> None:
        pass
