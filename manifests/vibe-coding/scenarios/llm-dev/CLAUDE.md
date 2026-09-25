# CLAUDE.md

## Architecture
- **Models**: OpenAI / Anthropic / Local (Ollama/vLLM)
- **Orchestration**: LangChain / LlamaIndex / DSPy
- **Eval**: RAGAS / DeepEval / Custom Judge

## LLM Commands
| Command | Description |
|---------|-------------|
| `uv run python eval.py` | Run evaluation suite |
| `uv run python data_prep.py` | Prepare training/eval datasets |
| `vibe-check llm` | Verify prompt templates & model connectivity |
| `uv run streamlit run app.py` | Launch LLM playground/demo |

## Development Standards
- **Prompt Management**: Keep prompts in `src/prompts/` as `.txt` or `.yaml`.
- **Testing**: Every major prompt change requires an evaluation report.
- **RAG**: Ensure retrieval quality (Hit Rate, Faithfulness) is monitored.

## Key Files
- `data/` - Datasets (JSONL/Parquet)
- `src/prompts/` - Versioned prompt templates
- `src/eval/` - Evaluation scripts and metrics
- `src/models/` - Model wrappers and API clients

## Skills

Actively dispatch these skills for LLM development tasks:

| Skill | Use When |
|-------|----------|
| `planning-with-files` / `planning-with-files-zh` | Persistent planning notes for complex work (choose by conversation language) |
| `Agent-Skills-for-Context-Engineering` | Prompt chain design, context window optimization, multi-model orchestration |
| `agent-skills` | Agent coding conventions, tool use patterns |
| `claude-api` | Claude API integration, prompt caching, extended thinking, streaming |
