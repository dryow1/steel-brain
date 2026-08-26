"""MCP stdio server - the registry door. Run: python -m steel_brain.mcp_server
Supports mcp SDK 2.x (MCPServer) and 1.x (FastMCP)."""
import os
from .kb import KB, KB_DIR
from .tools import Tools

SERVE_UNVERIFIED = os.environ.get("SB_SERVE_UNVERIFIED", "0") == "1"
_kb = KB(KB_DIR, serve_unverified=SERVE_UNVERIFIED)
_tools = Tools(_kb)

def build_server():
    try:
        from mcp.server import MCPServer as ServerClass          # mcp >= 2.0
    except ImportError:
        from mcp.server.fastmcp import FastMCP as ServerClass   # mcp 1.x
    srv = ServerClass(
        name="steel-brain",
        instructions="Steel domain knowledge from a verified trade knowledge base: grade properties, substitution verdicts, mill cert guidance. Never guesses - unknown grades return an honest not-in-KB response.")

    @srv.tool()
    def grade_lookup(grade: str) -> dict:
        """Look up a steel grade: properties, chemistry, forms, applications, weldability. Aliases accepted (e.g. 4140 = 42CrMo4 = SCM440)."""
        return _tools.grade_lookup(grade)

    @srv.tool()
    def substitution_check(from_grade: str, to_grade: str, application: str) -> dict:
        """Check if one steel grade can substitute another for a given application (machined / welded-structural / pressure). Returns verdict + reasoning from verified trade rules."""
        return _tools.substitution_check(from_grade, to_grade, application)

    @srv.tool()
    def cert_guide(grade: str, use_case: str) -> dict:
        """Which mill cert type applies for a grade + use case (e.g. EH36 shipbuilding), and what fields to check on the cert."""
        return _tools.cert_guide(grade, use_case)

    return srv

if __name__ == "__main__":
    build_server().run()
