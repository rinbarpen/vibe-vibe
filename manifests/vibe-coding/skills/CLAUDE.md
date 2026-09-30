# CLAUDE.md

Brief project description.

## Commands

| Command | Description |
|---------|-------------|
| `uv sync` | Install dependencies |
| `uv run <script>` | Run a script |
| `pytest` | Run tests |
| `ruff check` | Lint code |
| `ruff format` | Format code |

## Architecture

```
<root>/
  src/      # Source code
  tests/    # Unit tests
  docs/     # Documentation
  scripts/  # Utility scripts
```

## Key Files

- `pyproject.toml` - Project configuration
- `src/main.py` - Main entry point

## Code Style

- Use functional programming patterns where possible
- Follow PEP 8 for Python code
- Use type hints for all function signatures

## Environment

Required:
- `DATABASE_URL` - Connection string for PostgreSQL

## Testing

- `pytest` - Run all tests
- `pytest tests/unit` - Run unit tests only

## Gotchas

- Ensure `proxy_on` is executed before downloading external data.
- Matplotlib plots must use English labels.

## Workflow

- Use direct vibe coding for simple bounded changes; avoid unnecessary plan artifacts.
- For medium/large work, choose `planning-with-files-zh` for Chinese or `planning-with-files` for English.
- Use the task-sized workflow routing in the manifest; `implement` includes correctness and code-quality subagent review.
- Use `vibe-check` to verify changes when applicable.
