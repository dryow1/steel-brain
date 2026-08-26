# Steel Brain

**An MCP server providing steel domain knowledge to AI agents** — grade properties, substitution verdicts, and mill-cert guidance, delivered as MCP tools your agent can call.

Also available as a REST API at `https://api.steelbrain.dev`.

---

## MCP server

Steel Brain is a [Model Context Protocol](https://modelcontextprotocol.io) server. It exposes three MCP **tools** over stdio transport:

| MCP Tool | What it does |
|----------|--------------|
| `grade_lookup` | Properties, chemistry, forms, applications, weldability for a steel grade. Aliases resolved (4140 = 42CrMo4 = SCM440; S355 = ST52). |
| `substitution_check` | Given from_grade, to_grade, application, returns a verdict (valid / conditional / invalid) with reasoning on whether one grade can substitute another. |
| `cert_guide` | Which mill certificate applies for a grade + use case (EN 10204 3.1/3.2, class certs ABS/DNV/LR/BV/NK) and what to check. |

### Running the MCP server

    pip install -r requirements.txt
    python -m steel_brain.mcp_server

Starts the MCP server on stdio transport, ready for any MCP client (Claude Desktop, Claude Code, or any MCP-compatible agent).

### Example MCP client config

    {
      "mcpServers": {
        "steel-brain": {
          "command": "python",
          "args": ["-m", "steel_brain.mcp_server"]
        }
      }
    }

Built with the official MCP SDK (mcp package), registering three tools via the standard MCP tool interface.

---

## Why Steel Brain

LLMs guess at steel. They will tell you 4140 annealed can stand in for 4140 pre-hardened, and scrap the job. Steel Brain answers from a human-verified knowledge base built by a working steel trader, and returns an honest "not in knowledge base" rather than a confident guess.

The valuable part is the substitution and cert logic:

- 4140RB to 4140QT (annealed vs pre-hardened): invalid, same alloy, opposite heat-treat
- 316L to 304L for marine: invalid, different corrosion class
- EH36 to S355 structural: valid one way, conditional the other
- Seamless vs ERW for pressure service: never interchangeable

## Coverage

23 grades across carbon, alloy, stainless. Round bar, hollow bar, plate, pipe. 39 substitution rules, 4 cert guides.

## REST API (alternative to MCP)

Same knowledge over REST at https://api.steelbrain.dev :

    curl "https://api.steelbrain.dev/v1/grade/4140QT" -H "X-API-Key: YOUR_KEY"
    curl "https://api.steelbrain.dev/v1/substitution?from_grade=316L&to_grade=304L&application=machined" -H "X-API-Key: YOUR_KEY"

Free tier at launch. Contact: dryow.jt@gmail.com

## Honesty by design

- Grade properties: published-standard ranges (ASTM/EN/JIS/API/ABS), labelled as such.
- Substitution + cert logic: trade-verified, dated rulings from a working trader.
- Unknown grades: honest "not in knowledge base," never fabricated.

## Development

    python -m pytest tests/    # 15 tests (10 acceptance + 5 domain-safety guards)

## License

Code: MIT (see LICENSE). Knowledge base (kb/): proprietary (see NOTICE).
