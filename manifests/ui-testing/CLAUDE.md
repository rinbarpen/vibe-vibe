# UI Testing Project

> 产物记录的唯一账本是项目根目录 [`MANIFEST.md`](MANIFEST.md)；请追加记录，不要在指令文档中复制清单。

## Commands

| Command | Description |
|---------|-------------|
| `npx playwright test` | Run all Playwright E2E tests |
| `npx vitest run` | Run all Vitest unit/component tests |
| `npx vitest run --coverage` | Run with coverage report |
| `npx playwright show-report` | Serve Playwright HTML report |
| `npx axe --help` | Run accessibility audit |

## Architecture

```
src/
├── components/     # UI components
├── pages/          # Page objects (E2E)
├── hooks/          # Custom hooks
└── utils/          # Utilities

tests/
├── unit/           # Unit tests (Vitest)
├── integration/    # Integration tests (Vitest + MSW)
└── e2e/            # E2E tests (Playwright)
    ├── pages/      # Page Object Models
    ├── fixtures/   # Test fixtures
    └── specs/      # Test specifications
```

## Key Files

- `playwright.config.ts` — Playwright configuration (browsers, CI mode, retries)
- `vitest.config.ts` — Vitest configuration (coverage, environment, setup)
- `src/test-utils/test-utils.tsx` — Custom render with providers (Testing Library)

## Code Style

- E2E tests: Page Object Model pattern
- Component tests: Testing Library queries (role/label/testid)
- No `sleep()` / `waitForTimeout` — use locator actions
- Test descriptions: `'returns empty when no results match'`
- Cover happy path + error states + edge cases

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `CI` | `false` | Set `true` in CI (enables retries, disables headed) |
| `PLAYWRIGHT_BASE_URL` | `http://localhost:5173` | App base URL for E2E |
| `TEST_ENV` | `development` | Test environment label |

## Testing

- Coverage target: >= 80% lines, branches, functions, statements
- E2E: `npx playwright test` — parallel by default, shard in CI
- Component: `npx vitest run` — fast, watch mode in development
- A11y: `npx playwright test --grep @a11y` for accessibility specs

## Gotchas

- Playwright webServer config must match your dev server start command
- Vitest `environment: 'jsdom'` for component tests; `environment: 'node'` for utilities
- MSW handlers should be shared between tests, not duplicated
- Keep page objects thin — locators only, no assertions
- E2E tests run against a real server; ensure test DB is isolated

## Workflow

1. Run existing tests: `npx vitest run && npx playwright test`
2. Write test first (TDD: RED → GREEN → REFACTOR)
3. Verify coverage after implementation
4. Run full suite before commit
5. Update snapshots intentionally: `npx playwright test --update-snapshots`
