"""Minimal workspace tool collection."""

from blindspot.domains.minimal_workspace.tools.list_files import ListFilesTool
from blindspot.domains.minimal_workspace.tools.read_file import ReadFileTool
from blindspot.domains.minimal_workspace.tools.share_file import ShareFileTool
from blindspot.domains.minimal_workspace.tools.revoke_file_access import RevokeFileAccessTool
from blindspot.domains.minimal_workspace.tools.list_messages import ListMessagesTool
from blindspot.domains.minimal_workspace.tools.read_message import ReadMessageTool
from blindspot.domains.minimal_workspace.tools.send_message import SendMessageTool
from blindspot.domains.minimal_workspace.tools.request_approval import RequestApprovalTool
from blindspot.domains.minimal_workspace.tools.inspect_policy import InspectPolicyTool
from blindspot.domains.minimal_workspace.tools.update_policy import UpdatePolicyTool

ALL_TOOLS = [
    ListFilesTool(),
    ReadFileTool(),
    ShareFileTool(),
    RevokeFileAccessTool(),
    ListMessagesTool(),
    ReadMessageTool(),
    SendMessageTool(),
    RequestApprovalTool(),
    InspectPolicyTool(),
    UpdatePolicyTool(),
]

__all__ = [
    "ListFilesTool", "ReadFileTool", "ShareFileTool", "RevokeFileAccessTool",
    "ListMessagesTool", "ReadMessageTool", "SendMessageTool",
    "RequestApprovalTool", "InspectPolicyTool", "UpdatePolicyTool", "ALL_TOOLS",
]
