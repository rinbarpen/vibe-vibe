# CLAUDE.md

## Architecture
- **Framework**: LangChain / LangGraph / AutoGPT / Custom Loop
- **Memory**: Redis / VectorDB (Chroma/Pinecone)
- **Tools**: API / Shell / Browser / Database

## Agent Commands
| Command | Description |
|---------|-------------|
| `uv run python main.py --debug` | Run agent in debug mode |
| `uv run pytest tests/tools` | Test agent tools |
| `vibe-check agent` | Verify agent state machine & safety |
| `tail -f logs/agent.log` | Monitor agent thinking process |

## Development Standards
- **Schema First**: Define tool inputs using Pydantic or JSON Schema.
- **Safety**: High-risk tools require `require_approval: true`.
- **Observability**: Use LangSmith or custom traces for debugging.

## Key Files
- `src/agents/` - Agent logic and prompt templates
- `src/tools/` - Tool implementations
- `src/memory/` - Memory management logic

## Skills

Actively dispatch these skills for agent development tasks:

| Skill | Use When |
|-------|----------|
| `planning-with-files` / `planning-with-files-zh` | Persistent planning notes for complex work (choose by conversation language) |
| `Agent-Skills-for-Context-Engineering` | Context engineering, multi-agent architecture, production agent optimization |
| `agent-skills` | General agent coding guidelines, Vercel agent patterns |
| `claude-api` | Anthropic SDK integration, prompt caching, tool use, streaming |
| `agentic-engineering` | Eval-first execution, cost-aware model routing, agent decomposition |
