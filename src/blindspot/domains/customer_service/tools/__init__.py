"""Customer service domain tools."""
from blindspot.domains.customer_service.tools.lookup_account import LookupAccountTool
from blindspot.domains.customer_service.tools.cancel_order import CancelOrderTool
from blindspot.domains.customer_service.tools.process_refund import ProcessRefundTool
from blindspot.domains.customer_service.tools.create_ticket import CreateTicketTool
from blindspot.domains.customer_service.tools.inspect_policy import CSInspectPolicyTool

ALL_CS_TOOLS = [
    LookupAccountTool(),
    CancelOrderTool(),
    ProcessRefundTool(),
    CreateTicketTool(),
    CSInspectPolicyTool(),
]

__all__ = [
    "LookupAccountTool",
    "CancelOrderTool",
    "ProcessRefundTool",
    "CreateTicketTool",
    "CSInspectPolicyTool",
    "ALL_CS_TOOLS",
]
