"""Unit tests for tool discovery."""

from blindspot.domains.minimal_workspace.tools import ALL_TOOLS
from blindspot.tools.discovery import ToolDiscoveryService


def test_all_public_tools_listed():
    svc = ToolDiscoveryService(ALL_TOOLS)
    schemas = svc.list_tools(actor_id="user_alice", scenario=None, state=None)
    names = [s["name"] for s in schemas]
    assert "list-files" in names
    assert "share-file" in names


def test_hidden_tools_excluded():
    from blindspot.core.identifiers import ComponentID
    from blindspot.tools.specification import ToolSpecification
    from blindspot.tools.base import PythonTool
    from blindspot.tools.mutation import MutationPlan

    class HiddenTool(PythonTool):
        specification = ToolSpecification(
            tool_id=ComponentID(namespace="core", name="hidden-op", version="1.0.0"),
            display_name="Hidden", description="hidden",
            read_scopes=[], write_scopes=[], side_effect_level="none",
            visibility="hidden",
        )
        args_model = __import__("pydantic").BaseModel
        output_model = __import__("pydantic").BaseModel
        def read(self, view, args, ctx): return {}
        def plan_mutations(self, view, args, ctx): return MutationPlan()

    svc = ToolDiscoveryService(ALL_TOOLS + [HiddenTool()])
    schemas = svc.list_tools(actor_id="user_alice", scenario=None, state=None)
    names = [s["name"] for s in schemas]
    assert "hidden-op" not in names


def test_get_tool_by_name():
    svc = ToolDiscoveryService(ALL_TOOLS)
    t = svc.get_tool("list-files")
    assert t is not None
    assert t.specification.tool_id.name == "list-files"
