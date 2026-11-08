# /frontend-check

Check whether users can understand the interface and complete real tasks, as well
as accessibility, performance, bundle size, and visual regression. This is an agent
command contract, not a bundled test runner or a promise that tools are installed.

## Usage

```text
/frontend-check <mode>
```

Omitting mode selects `all`. Use only relevant modes for a small, bounded change.

### Modes

| Mode | Tools / method | What it checks |
|------|----------------|----------------|
| `usability` | Task walkthrough, rendered UI, before/after evidence | Information priority, discoverable actions, settings clarity, interaction cost |
| `interaction` | Existing component/E2E suite, real browser or platform test harness | User tasks, outcomes, persistence, failure and recovery paths |
| `accessibility` | Existing axe-core, pa11y-ci, jsx-a11y setup + keyboard walkthrough | Project accessibility target; WCAG 2.1 AA by default |
| `performance` | Existing Lighthouse CI, Web Vitals setup | Project page/device budgets; default LCP < 2.5s, INP < 200ms, CLS < 0.1 |
| `bundle` | Existing build analyzer | Project size budgets; fallback JS < 150KB (landing) / 300KB (app), CSS < 30KB / 50KB gzip |
| `visual` | Existing Playwright screenshots or component visual tests | Intentional changes and unexpected regressions against a reviewed baseline |
| `all` | All six modes above | Full frontend check; report each mode separately |

All paths mentioned below are relative to the project root. Read
`references/ui-usability.md` for the task contract and report fields.

## Execution

1. Identify the changed pages, primary user tasks, affected states and project
   acceptance criteria. Reuse known context; do not start a new interview for a
   clear request. Capture a baseline before editing when available.
2. Inspect actual project scripts, test configuration, startup command and URL.
   Reuse a running instance or start an isolated local instance only when needed;
   do not assume `pnpm dev`, port 3000, or a specific framework.
3. Run the selected modes against the rendered interface. Use an available browser
   tool or the existing test harness. Webview/desktop changes require an appropriate
   platform harness for native behavior; browser results alone do not prove it.
4. Record commands/actions, inputs, environment, expected and observed outcomes,
   evidence paths and literal exit statuses where commands exist. Investigate and
   fix implementation/test defects within the agreed scope, then rerun affected checks.
5. Report `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`, or `N/A` per mode and task. Explain
   prerequisites or applicability. Missing tools, server or fixtures are not a pass;
   do not silently install dependencies or replace a browser run with source inspection.
   `all` completes only when every applicable required mode passes; a scoped run is
   reported as scoped, not a full pass.

## Check Details

### Usability (`usability`)

- Identify the primary task, the information users need first, and the visible next
  action. Avoid equal-weight information panels that compete with the task.
- Audit redundant secondary labels, descriptions, repeated heading explanations
  and slogan-like copy. Let grouping, alignment and hierarchy explain the interface
  instead of compensating for unclear design with more text. Keep necessary form
  labels, accessible names, errors, risk warnings, units and essential help. Verify
  the task remains understandable after removing or merging unnecessary copy.
- Check progressive disclosure: essential status/results/errors stay visible;
  details and advanced options remain discoverable rather than disappearing.
- Walk settings: meaningful grouping, reasonable defaults, conditional fields,
  understandable labels, current value, save state, validation and reset scope.
- Compare the baseline and changed task path: steps, backtracking, repeated inputs,
  discoverability and relevant viewport screenshots. Use project-specific targets,
  not a universal click count, card limit, or density score.
- Record AI walkthrough observations separately from actual user feedback. Do not
  call an AI walkthrough user research, or claim measured user time without evidence.

### Interaction (`interaction`)

- Walk affected critical tasks end to end: locate entry -> act -> verify result.
  Clicking successfully is not the acceptance condition.
- Assert visible outcome plus underlying state where relevant: mutations, navigation,
  settings persistence after refresh/reopen, cancellation and state preservation.
- Exercise applicable empty/loading/slow/error states, invalid input, duplicate
  submission and retry. Include keyboard use and relevant narrow viewports.
- Reuse semantic selectors such as `getByRole` / `getByLabel`; use auto-waiting actions
  and outcome assertions, isolated fixtures and cleanup rather than fixed delays.
- Browser-mocked tests prove client behavior only. Label mocked dependencies and
  separately verify required real integration/persistence in an isolated environment.
- Retain a failure screenshot and trace where supported, together with exact
  reproduction steps. Reuse `ui-testing` conventions if installed; a separate
  manifest installation is not a prerequisite for using these principles.

### Accessibility (`accessibility`)

- Use project-installed audit tools and lint scripts; capture actual results.
- Keyboard: reach, activate and leave controls/dialogs; check focus return, visible
  focus, labels and errors. For WCAG 2.1 AA, normal text contrast >= 4.5:1 and
  large text >= 3:1. Respect the project's stronger target if present.

### Performance (`performance`)

- Use project per-page budgets and relevant mobile/desktop profiles. Record the
  device/network profile and build mode. Field INP and lab proxies are different;
  absent field data is `NOT RUN`, not an invented passing measurement.

### Bundle (`bundle`)

- Measure the production build with the project's analyzer and compression basis.
  Compare project budgets; inspect duplicate or unexpectedly large dependencies.

### Visual (`visual`)

- Compare affected states with the existing baseline: default, focus, disabled,
  loading, empty, error and other states relevant to the change.
- Include applicable themes and viewports. Document intended differences; use
  project diff tolerances and investigate unexpected changes. Do not bless all
  changed screenshots simply to make the comparison pass.

## Exit Criteria

- [ ] Selected tasks and mode scope are explicit; primary information/actions are clear.
- [ ] Affected interactions produce the expected result and applicable persisted state.
- [ ] Selected accessibility/performance/bundle/visual checks meet project criteria.
- [ ] Failures are resolved and rerun; unresolved prerequisites and unrun checks remain visible.
- [ ] Evidence includes baseline/changed observations, commands/actions, outputs/statuses,
      screenshots/traces where applicable, and rollback or remaining limitations.

For the reproducible workflow, use the existing standalone renderer:

```bash
python3 scripts/render_codegraph_workflow.py --source references/ui-usability-workflow.json --output references/ui-usability-workflow.svg --check
```
