"""Software-ops domain BenchmarkPlugin."""

from __future__ import annotations

from blindspot.core.identifiers import ComponentID
from blindspot.core.metadata import ComponentMetadata


class SoftwareOpsDomainPlugin:
    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="core", name="software-ops-plugin", version="1.0.0"),
        display_name="Software-Ops Domain Plugin",
        description="Registers the software-ops domain for CI/CD and secrets safety testing.",
        source_package="blindspot.domains.software_ops",
    )

    def register(self, registries) -> None:
        import blindspot.domains.software_ops.validators  # register invariants
        from blindspot.domains.software_ops.tools import ALL_SOFTWAREOPS_TOOLS
        for tool in ALL_SOFTWAREOPS_TOOLS:
            tool_id = tool.specification.tool_id.canonical()
            if not registries.tools.contains(tool_id):
                registries.tools.register(tool_id, tool)
            short = tool.specification.tool_id.name
            if not registries.tools.contains(f"so-{short}"):
                registries.tools.register(f"so-{short}", tool)

    def validate(self) -> None:
        pass
