"""Finance domain tools."""
from blindspot.domains.finance.tools.list_payments import ListPaymentsTool
from blindspot.domains.finance.tools.list_accounts import ListAccountsTool
from blindspot.domains.finance.tools.read_payment import ReadPaymentTool
from blindspot.domains.finance.tools.inspect_policy import InspectPolicyTool

ALL_FINANCE_TOOLS = [
    ListPaymentsTool(),
    ListAccountsTool(),
    ReadPaymentTool(),
    InspectPolicyTool(),
]

__all__ = [
    "ListPaymentsTool",
    "ListAccountsTool",
    "ReadPaymentTool",
    "InspectPolicyTool",
    "ALL_FINANCE_TOOLS",
]
