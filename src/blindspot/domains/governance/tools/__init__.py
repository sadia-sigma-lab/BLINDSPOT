"""Governance domain tools."""

from blindspot.domains.governance.tools.read_deployment_config import ReadDeploymentConfigTool
from blindspot.domains.governance.tools.update_deployment_gate import UpdateDeploymentGateTool
from blindspot.domains.governance.tools.read_approval_matrix import ReadApprovalMatrixTool
from blindspot.domains.governance.tools.update_monitoring_rule import UpdateMonitoringRuleTool
from blindspot.domains.governance.tools.read_audit_log import ReadAuditLogTool
from blindspot.domains.governance.tools.inspect_policy import GovInspectPolicyTool

ALL_GOVERNANCE_TOOLS = [
    ReadDeploymentConfigTool(),
    UpdateDeploymentGateTool(),
    ReadApprovalMatrixTool(),
    UpdateMonitoringRuleTool(),
    ReadAuditLogTool(),
    GovInspectPolicyTool(),
]
