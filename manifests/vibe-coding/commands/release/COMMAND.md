# /release

Release a project initialized with the vibe-coding manifest. The selected provider is the one used during initialization (`git`, `github`, `gitlab`, or `gitee`).

## Usage

`/release <major|minor|patch|X.Y.Z[-prerelease]> [--dry-run]`

1. Read `VERSION`; calculate the requested SemVer. Never treat a Git tag or a package manifest as the sole source of truth.
2. Update `VERSION`, every existing package version field, and `CHANGELOG.md` **in the same change**. Add `## [X.Y.Z] - YYYY-MM-DD` with at least one meaningful bullet under `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, or `Security`. Keep `Unreleased` for future changes. Do not insert generic placeholder notes.
3. Run `python3 scripts/version_guard.py check --base-ref <base-commit>` and project checks (`sh scripts/ci.sh` if present). For `--dry-run`, report proposed edits and checks without writing or tagging.
4. Merge the reviewed change, then run `python3 scripts/version_guard.py check --tag vX.Y.Z` on the release commit. Sign an annotated tag (`git tag -s vX.Y.Z -m "Release vX.Y.Z"`) and push it to the selected remote. Never move an existing release tag.
5. On GitHub, GitLab, and Gitee the selected tag pipeline creates a Release from the exact Changelog section. Git-only mode: run `python3 scripts/version_guard.py notes --tag vX.Y.Z --output release_notes.md` and publish notes manually if desired. Build/test hooks are `scripts/build.sh` and `scripts/ci.sh` (POSIX shell); no deployment is implied.

For hotfixes, validate the branch's VERSION and Changelog before creating its signed tag. The hotfix workflow does not create tags or deploy automatically.

See `.cursor/references/release-process.md` for provider setup, CI credentials, and verification.
