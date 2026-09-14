"""Software-ops domain tools."""

from blindspot.domains.software_ops.tools.list_pipelines import ListPipelinesTool
from blindspot.domains.software_ops.tools.list_incidents import ListIncidentsTool
from blindspot.domains.software_ops.tools.acknowledge_incident import AcknowledgeIncidentTool
from blindspot.domains.software_ops.tools.inspect_policy import SoftwareOpsInspectPolicyTool

ALL_SOFTWAREOPS_TOOLS = [
    ListPipelinesTool(),
    ListIncidentsTool(),
    AcknowledgeIncidentTool(),
    SoftwareOpsInspectPolicyTool(),
]
