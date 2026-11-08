# CLAUDE.md — Frontend Scenario

Pure frontend application without backend dependency.

## Architecture

- **Framework**: React / Vue / Svelte / Solid
- **Build tool**: Vite / Next.js / Nuxt / SvelteKit
- **Styling**: Tailwind CSS / CSS Modules / styled-components
- **State**: Zustand / Jotai / Pinia / signals
- **Design system**: shadcn/ui / Radix UI / MUI / Ant Design / custom

## Design Skills

| Skill | Use When |
|-------|----------|
| `design-taste-frontend` | Anti-slop landing pages, portfolios, and redesigns with distinctive visual direction |
| `awesome-design-md` | Brand-specific DESIGN.md references for visual language, typography, color, and layout direction |
| `frontend-design` | Production-grade, opinionated UI with distinctive visual design |
| `ui-ux-pro-max-skill` | 58+ UI styles, smart design system generation, multi-style exploration |
| `canvas-design` | Visual art, illustrations, background textures, algorithmic design |
| `taste-skill` | Anti-slop frontend skill with configurable design variance, motion intensity, and visual density dials; includes variants for minimalist, brutalist, soft/premium, and redesign workflows |
| `img2threejs` | Image-to-3D reconstruction with quality-gated, procedural, animation-ready Three.js models |

## Commands

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start dev server |
| `pnpm build` | Production build |
| `pnpm lint` | Lint + type check |
| `pnpm test` | Unit + component tests |
| `pnpm e2e` | Playwright E2E tests |
| `/frontend-check usability` | Information priority, settings clarity, before/after task walkthrough |
| `/frontend-check interaction` | Real task outcomes, persistence and failure paths |
| `/frontend-check all` | All six checks: usability, interaction, a11y, perf, bundle, visual |

## UI Acceptance

For hierarchy, settings or workflow changes, apply the project-root contract
`references/ui-usability.md`: primary information visible, advanced details
progressively disclosed, real tasks completed and outcomes verified. Use the
project's actual startup/test commands; examples above are not generated scripts.
Select existing installed design skills as needed; the design-skill table is a
catalog, not a guarantee that every listed skill is installed. Browser checks do
not replace native desktop/mobile verification when those behaviors are affected.

## Development Standards

- Tailwind utility-first for layout/spacing. CSS Modules for component-specific styles.
- Small focused components (< 200 lines per file).
- Accessibility: axe-core or jsx-a11y on every commit.
- Images: WebP/AVIF with responsive `srcset`. Always set explicit width/height.
- Fonts: `next/font` or `@fontsource` with preload. `font-display: swap`.
- i18n: `next-intl` / `react-i18next`. No hardcoded UI strings.

## Key Directories

- `src/components/` — UI components
- `src/hooks/` — Custom React hooks
- `src/lib/` — Utilities and API clients
- `src/styles/` — Global styles + design tokens
- `src/locales/` — i18n message files
- `public/` — Static assets (icons, fonts)
