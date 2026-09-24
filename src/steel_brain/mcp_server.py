"""MCP server - the registry door.
stdio:  python -m steel_brain.mcp_server
HTTP:   mounted at /mcp by http_api.py (streamable HTTP, for remote agents).
Supports mcp SDK 2.x (MCPServer) and 1.x (FastMCP)."""
import os
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
    Extra settings (stateless_http, json_response, transport_security) pass to the SDK."""
    t = tools or _tools
    try:
        from mcp.server import MCPServer as ServerClass          # mcp >= 2.0
    except ImportError:
        from mcp.server.fastmcp import FastMCP as ServerClass   # mcp 1.x
    srv = ServerClass(name="steel-brain", instructions=INSTRUCTIONS, **settings)

    def _hit(name):
        if on_call:
            on_call(name)

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
