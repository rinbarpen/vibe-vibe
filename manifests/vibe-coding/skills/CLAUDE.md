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

- Route simple/local requests directly; bug fixes use `grilling` → `implement`; complex features use `grill-with-docs` → `to-spec` → `to-tickets` → `implement`.
- For persistent notes on complex work, choose `planning-with-files` (English) or `planning-with-files-zh` (Chinese).
- Use `vibe-check` to verify changes before submission.
