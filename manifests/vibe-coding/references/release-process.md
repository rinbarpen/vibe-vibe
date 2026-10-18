# Version and Release Process

## Single source of truth

`VERSION` contains one SemVer value without a `v` prefix. Existing `package.json`, `pyproject.toml`, `Cargo.toml`, and direct `pom.xml` project/package versions must match it. Initializing an existing project adopts its one unambiguous package version; conflicting values stop initialization before files are copied. New projects start at `0.1.0` and `CHANGELOG.md` with `Unreleased`. This is not an automatic first release.

Every version bump is one reviewed change containing the new `VERSION`, aligned package versions, and a new `CHANGELOG.md` section such as:

```markdown
## [1.2.3] - 2026-10-01

### Fixed
- Correct the failed export path for empty reports.
```

A section needs a real categorized bullet. Placeholder text, missing/duplicate headings, and a section prepared in an earlier commit fail the version-bump check. Release tags use `v` plus the exact VERSION, including `-rc.1` or `-hotfix.1` when applicable. `Unreleased` is not a release note.

## Local and CI checks

```bash
python3 scripts/version_guard.py check --base-ref origin/main
python3 scripts/version_guard.py check --tag "v$(cat VERSION)"
python3 scripts/version_guard.py notes --tag "v$(cat VERSION)" --output release_notes.md
```

`--base-ref` compares the current change against a Git commit. Run it in the PR pipeline and after pushing to the protected branch. CI always validates version syntax and known package metadata; the tag pipeline additionally validates the exact Changelog section and creates release notes. If present, POSIX `scripts/ci.sh` runs in validation and `scripts/build.sh` runs before publication. Put distributable files in `dist/`; an empty `dist/` yields a notes-only Release. Neither hook performs deployment by default.

## Provider activation

| Provider | Pipeline | Release credentials and setup |
|---|---|---|
| Git | Local commands only | Configure any Git remote yourself; no hosted Release is created. |
| GitHub | 12 bundled Actions workflows | Enable Actions and branch/tag protection. `GITHUB_TOKEN` is scoped by each workflow; the tag workflow creates the Release. |
| GitLab | `.gitlab-ci.yml` | Enable runners and protect tags. The tag job uses `CI_JOB_TOKEN` with Releases API permissions; the triggering user needs release access. |
| Gitee | `.workflow/vibe-ci.yml` and `vibe-release.yml` | First enable Gitee Go in the repository UI and connect the supplied YAML pipelines. Set `GITEE_OWNER`, `GITEE_REPO`, and a secret `GITEE_TOKEN` with Release permission. |

GitHub, GitLab, and Gitee run validation for PRs and branch pushes, and publish a Release on version-tag push. The Gitee tag pipeline verifies the tag points to the checked-out commit before calling the Release API. Keep protected branches and tags; especially on Gitee, use PR review for multi-commit pushes so each version bump is compared with the target branch. Credentials live in the host's secret store, not committed files. No pipeline creates a remote repository, tag, or production deployment.

## Publishing and rollback

1. Merge the version-and-Changelog change after CI passes.
2. On the release commit, run the tag check and create a GPG-signed tag: `git tag -s "v$(cat VERSION)" -m "Release v$(cat VERSION)"`.
3. Push the tag and confirm the selected provider's release job and Release notes. Git-only projects produce notes locally.
4. If publication fails, correct the pipeline or credentials and rerun it. Do not move or delete a published tag. Revert a faulty code release in a new commit and publish a new patch/hotfix version.

Provider references: [GitHub reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows), [GitLab Releases API](https://docs.gitlab.com/api/releases/), [Gitee Go triggers](https://help.gitee.com/gitee-go/pipeline/trigger), [Gitee Go activation](https://help.gitee.com/gitee-go/get-started-in-3-steps).
