---
name: vibe-coding
description: Unified full-stack multi-language development manifest covering the complete
  engineering lifecycle from idea to deployed system across Go, Rust, Python, TypeScript,
  Java, Kotlin, C++, C#, and Dart/Flutter. Integrates 14 domain rules, language selection
  decision trees, 12 commands, 5 quality gates, 5 cloud platforms, enterprise GitHub
  governance, and TDD workflow with parallel subagent execution.
model: sonnet
triggers:
  - pattern: "build a (system|service|API|CLI|app|tool|pipeline|platform)"
    description: Full-stack development request across any supported language
  - pattern: "create a project in (Go|Rust|Python|TypeScript|Java|Kotlin|C++|C#|Dart)"
    description: Language-specific project initialization
  - pattern: "(design|implement|deploy|refactor|test|optimize|review|scaffold) the"
    description: Domain-specific engineering task
  - pattern: "deploy to (vercel|cloudflare|tencent|alibaba|huawei)"
    description: Cloud platform deployment request
  - pattern: "(create|setup|configure) (PR|release|CI|workflow|GitHub)"
    description: GitHub/enterprise operations request
---
