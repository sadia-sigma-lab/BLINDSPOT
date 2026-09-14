"""E-commerce domain tools."""
from blindspot.domains.ecommerce.tools.search_products import SearchProductsTool
from blindspot.domains.ecommerce.tools.add_to_cart import AddToCartTool
from blindspot.domains.ecommerce.tools.inspect_policy import ECInspectPolicyTool

ALL_ECOMMERCE_TOOLS = [
    SearchProductsTool(),
    AddToCartTool(),
    ECInspectPolicyTool(),
]

__all__ = [
    "SearchProductsTool",
    "AddToCartTool",
    "ECInspectPolicyTool",
    "ALL_ECOMMERCE_TOOLS",
]
