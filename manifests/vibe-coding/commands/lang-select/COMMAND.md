# /lang-select

Get language recommendation for a specific use case.

## Usage

```
/lang-select "build a real-time chat API"
/lang-select "create a CLI tool for log analysis"
/lang-select "ML inference serving"
/lang-select "full-stack web application"
```

## Execution

1. Understand the user's context:
   - What is the application type? (web, CLI, API, data pipeline, mobile)
   - What are the performance requirements?
   - Is there existing infrastructure or team expertise?
   - What are the deployment constraints?

2. Walk through the decision tree in `references/decision-trees/language-selection.md`

3. Present recommendation with rationale:
   - Recommended language
   - Why this language is the best fit
   - What to consider (ecosystem, learning curve, operational concerns)
   - Alternative languages if the primary choice isn't viable

4. Show relevant language spec sheet from `references/language-specs/`

5. Suggest relevant agents and skills:
   - Relevant implementation review expectations (embedded in `implement`)
   - Which patterns skill to reference
   - Which build resolver to use if errors arise

## Example Output

```
Recommendation: Go
Why: Real-time chat API needs high concurrency (goroutines),
good throughput, and fast deployment. Go's standard library
includes an HTTP server, websocket support, and excellent
concurrency primitives.

Consider: WebSocket management at scale, connection pooling,
and Redis pub/sub for multi-instance broadcasting.

Skills: golang-patterns, backend-patterns
Agents: go-reviewer
```
