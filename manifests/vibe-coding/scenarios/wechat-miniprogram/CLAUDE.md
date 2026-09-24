# CLAUDE.md — WeChat Mini Program Scenario

Build and maintain WeChat Mini Programs using native project conventions. Activate this scenario with `--scenario=wechat-miniprogram`.

## Stack and Project Shape

- **Languages**: TypeScript or JavaScript, WXML, WXSS, and JSON configuration.
- **Runtime**: WeChat Mini Program APIs and the official WeChat Developer Tools.
- **Structure**: `app.json`, `app.ts`/`app.js`, `pages/`, reusable `components/`, and `utils/` or `services/`.
- **Build choice**: Prefer native Mini Program APIs for platform-specific features; use a framework such as Taro only when cross-platform delivery is a stated requirement.

## AI Mode Skills

Use the managed `ai-mode-skills` repository when working with Mini Program AI mode:

| Skill | Use When |
|-------|----------|
| `wxa-skills-generate` | Analyze a readable Mini Program source tree and generate AI mode skills and configuration integration. |
| `wxa-skills-validate` | Run static checks and the Developer Tools execution/render validation workflow on generated skills. |
| `wxa-skills-eval` | Evaluate Mini Program AI skill intent understanding, trajectory, and answer quality where the evaluation workflow is available. |

Read the selected skill's `SKILL.md` and referenced material before applying its workflow. Generation and validation are separate stages; use the validation skill after generation.

## Development Workflow

1. Inspect `project.config.json`, `app.json`, package scripts, and existing page/component conventions.
2. Plan page routes, component boundaries, data flow, and platform API usage before implementation.
3. Implement with TypeScript where configured; keep page, component, service, and type responsibilities distinct.
4. Validate WXML/WXSS and JSON configuration with the project toolchain and WeChat Developer Tools.
5. Test on simulator and relevant real-device environments; cover loading, empty, error, and permission states.
6. For AI mode skill work, follow the applicable `ai-mode-skills` generation, validation, or evaluation skill.

## Mini Program Conventions

- Register pages, components, subpackages, and permissions in the correct JSON configuration.
- Keep page-specific presentation in WXML/WXSS and move reusable UI into components.
- Use supported Mini Program APIs and component syntax; do not assume browser DOM APIs or full Node.js APIs exist at runtime.
- Respect package-size limits and use subpackages for independently loaded features when appropriate.
- Handle asynchronous API failures, user permission outcomes, and network state explicitly.
- Keep secrets out of client bundles; route privileged operations through a backend service.
