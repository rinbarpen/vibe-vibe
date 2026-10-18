# vibe-coding manifest 发布链路验证记录

## 输入与基线

- 工作树起点：已有 `mine/omnidraw/**` 改动及 `.planning/omnidraw-review/`，未改写它们。
- 原始文件快照：`.planning/vibe-manifest-cicd/originals.tar`，SHA256 `0f2cb9677bcb90f7955852e97414389e5d4555e5441322bd272020a85443b1db`。
- 行为对比输入：两个空的临时目标目录；provider=`gitee`；`--no-git`。

### 基线命令与字面输出

```bash
mkdir -p /tmp/tmp.C3N6BnpBmK/baseline
tar -xf .planning/vibe-manifest-cicd/originals.tar -C /tmp/tmp.C3N6BnpBmK/baseline
bash /tmp/tmp.C3N6BnpBmK/baseline/manifests/vibe-coding/scripts/vibe-init.sh /tmp/tmp.C3N6BnpBmK/base-project --provider=gitee --no-git
```

命令退出状态 `0`（旧脚本把未知参数打印为帮助并以 0 退出）；捕获的关键字面输出及文件检查：

```text
Unknown option: --provider=gitee
baseline_VERSION=absent
baseline_gitee_pipeline=absent
```

### 修改后命令与字面输出

```bash
bash manifests/vibe-coding/scripts/vibe-init.sh /tmp/tmp.C3N6BnpBmK/modified-project --provider=gitee --no-git
```

命令退出状态 `0`；目标文件检查的字面输出：

```text
modified_VERSION=0.1.0
modified_gitee_pipelines=present
modified_github_config=absent
```

## 测试命令、输出与退出状态

| 命令 | 字面输出 | 状态 |
|---|---|---:|
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src pytest -q tools/vibe_tool/tests/test_vibe_manifest_release.py` | `15 passed in 7.46s` | 0 |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src pytest -q tools/vibe_tool/tests --ignore=tools/vibe_tool/tests/test_ccfa_skill_replacement.py` | `20 passed in 7.60s` | 0 |
| `uvx ruff check manifests/vibe-coding/scripts/init_version.py manifests/vibe-coding/scripts/version_guard.py tools/vibe_tool/tests/test_vibe_manifest_release.py tools/vibe_tool/src/vibe_tool/cli.py tools/vibe_tool/src/vibe_tool/manifest.py` | `All checks passed!` | 0 |
| `go run github.com/rhysd/actionlint/cmd/actionlint@v1.7.7 -oneline manifests/vibe-coding/.github/workflows/*.yml` | （空输出） | 0 |
| `bash -n manifests/vibe-coding/scripts/vibe-init.sh` | （空输出） | 0 |
| `git diff --check` | （空输出） | 0 |
| `sha256sum -c .planning/vibe-manifest-cicd/modified.sha256 >/dev/null` | （空输出） | 0 |

全套测试命令 `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src pytest -q tools/vibe_tool/tests` 的字面汇总为 `2 failed, 21 passed in 7.59s`、退出状态 `1`。两项失败均在 `test_ccfa_skill_replacement.py`：缺少 `skills/CCFA-Skills/ccf-visual-composer/SKILL.md`，以及既有 omnidraw 工作树内容含 `happy figure`。本任务范围测试全部通过。

## 补丁与回滚演练

```bash
cd /tmp/tmp.fEsOeyl18G
git apply --check /home/rczx/workspace/rinbarpen/projects/vibe-coding/.planning/vibe-manifest-cicd/changes.patch
git apply /home/rczx/workspace/rinbarpen/projects/vibe-coding/.planning/vibe-manifest-cicd/changes.patch
sha256sum -c /home/rczx/workspace/rinbarpen/projects/vibe-coding/.planning/vibe-manifest-cicd/modified.sha256 >/dev/null
```

三条命令退出状态均为 `0`；字面摘要 `patch_rebuild_and_selective_rollback_exit=0 temp=/tmp/tmp.fEsOeyl18G`。随后在隔离副本运行：

```bash
/tmp/tmp.fEsOeyl18G/.planning/vibe-manifest-cicd/rollback.sh
```

退出状态 `0`；字面输出：

```text
Checking that task files have not changed since verification...
Rollback verified: original task files restored; unrelated files untouched.
new_guard_absent_after_rollback=yes
unrelated_marker_preserved=yes
```

回滚后的 `baseline_changed.sha256` 校验通过；在隔离副本中追加到未修改文件的 `UNRELATED_MARKER` 仍存在。当前工作树中的修改仍在原位，未执行现场回滚。

## 最终复核（模板与回滚优化后）

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src pytest -q tools/vibe_tool/tests/test_vibe_manifest_release.py` → `15 passed in 7.79s`，退出 `0`。
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src pytest -q tools/vibe_tool/tests --ignore=tools/vibe_tool/tests/test_ccfa_skill_replacement.py` → `20 passed in 7.48s`，退出 `0`。
- `uvx ruff check manifests/vibe-coding/scripts/init_version.py manifests/vibe-coding/scripts/version_guard.py tools/vibe_tool/tests/test_vibe_manifest_release.py tools/vibe_tool/src/vibe_tool/cli.py tools/vibe_tool/src/vibe_tool/manifest.py` → `All checks passed!`，退出 `0`。
- `go run github.com/rhysd/actionlint/cmd/actionlint@v1.7.7 -oneline manifests/vibe-coding/.github/workflows/*.yml` → 空输出，退出 `0`。
- `bash -n manifests/vibe-coding/scripts/vibe-init.sh`、`git diff --check`、`sha256sum -c .planning/vibe-manifest-cicd/modified.sha256 >/dev/null` → 均为空输出、退出 `0`。
