"""MCP server - the registry door.
stdio:  python -m steel_brain.mcp_server
HTTP:   mounted at /mcp by http_api.py (streamable HTTP, for remote agents).
Requires mcp SDK 2.x (MCPServer); HTTP transport settings (stateless_http,
json_response, transport_security) go to streamable_http_app(), not the server."""
import os
from . import __version__
from .kb import KB, KB_DIR
from .tools import Tools

SERVE_UNVERIFIED = os.environ.get("SB_SERVE_UNVERIFIED", "0") == "1"
_kb = KB(KB_DIR, serve_unverified=SERVE_UNVERIFIED)
_tools = Tools(_kb)

INSTRUCTIONS = ("Steel domain knowledge from a verified trade knowledge base: grade properties, "
                "substitution verdicts, mill cert guidance. Never guesses - unknown grades return "
                "an honest not-in-KB response.")


def build_server(on_call=None, tools=None, **settings):
    """on_call(tool_name) runs before each tool call (metering / limits); it may raise to refuse.
    Extra settings pass to the MCPServer constructor."""
    t = tools or _tools
    from mcp.server import MCPServer
    from mcp.server.mcpserver.exceptions import ToolError
    srv = MCPServer(name="steel-brain", instructions=INSTRUCTIONS, version=__version__, **settings)

    def _hit(name):
        if on_call:
            try:
                on_call(name)
            except Exception as e:
                # mcp 2.x replaces unexpected tool errors with a generic message; ToolError
                # keeps ours, so callers still see e.g. "daily limit reached".
                raise ToolError(str(e)) from e

    @srv.tool()
    def grade_lookup(grade: str) -> dict:
        """Look up a steel grade: properties, chemistry, forms, applications, weldability. Aliases accepted (e.g. 4140 = 42CrMo4 = SCM440)."""
        _hit("grade_lookup")
        return t.grade_lookup(grade)

    @srv.tool()
    def substitution_check(from_grade: str, to_grade: str, application: str) -> dict:
        """Check if one steel grade can substitute another for a given application (machined / welded-structural / pressure). Returns verdict + reasoning from verified trade rules."""
        _hit("substitution_check")
        return t.substitution_check(from_grade, to_grade, application)

    @srv.tool()
    def cert_guide(grade: str, use_case: str) -> dict:
        """Which mill cert type applies for a grade + use case (e.g. EH36 shipbuilding), and what fields to check on the cert."""
        _hit("cert_guide")
        return t.cert_guide(grade, use_case)

    return srv


if __name__ == "__main__":
    build_server().run()
