---
name: vibe-coding
description: >-
  Multi-language development manifest with task-sized workflows: direct vibe coding for simple requests, focused debugging for bugs, and staged specification/ticket planning for complex features. Applies domain, language, testing, and delivery guidance only when relevant.
model: sonnet
triggers:
  - pattern: "build a (system|service|API|CLI|app|tool|pipeline|platform)"
    description: Full-stack development request across any supported language
  - pattern: "create a project in (Go|Rust|Python|TypeScript|Java|Kotlin|C++|C#|Dart)"
    description: Language-specific project initialization
  - pattern: "(grill|specify|ticket|scaffold|deploy|release) (a |the )?(complex )?(feature|project|service)"
    description: Workflow selection or coordinated development task; simple coding changes stay lightweight
  - pattern: "deploy to (vercel|cloudflare|tencent|alibaba|huawei)"
    description: Cloud platform deployment request
  - pattern: "(create|setup|configure) (PR|release|CI|workflow|GitHub|GitLab|Gitee)"
    description: GitHub/enterprise operations request
---
