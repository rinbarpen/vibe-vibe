#!/usr/bin/env python3
"""Render Claude Code/Codex game-design roles from agents.json; --check is read-only."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

HOME = Path(__file__).resolve().parents[1]
ROLE_ID = re.compile(r'game-design-[a-z][a-z0-9-]*\Z')

COMMON = '''## 共享执行与交接契约

- 先读取 `.game-design/references/parallel.md`、已领取任务包和已确认决策，只加载所选类型/引擎/工作包。任务包的 attempt、领取 token、冻结输入/hash、写入范围、资源键与预期输出是当前执行边界；有歧义先向主代理报告。
- 主代理是共享调度与状态的唯一写者。worker 在领取的专属路径操作并回传结果/状态建议；不直接改其他任务、领取记录、共享 status/work/decisions/evidence 或调度状态文件。结果文件、日志与审查报告也须位于分配的任务路径。
- 使用当前宿主真实 subagent/消息/等待/结束工具；记录实际 host run ID，不将角色文件、Python 队列、提示词或模拟脚本当作已运行的代理。角色数量不是并发数量；并行数以当前宿主空闲额度和任务计划的较小值为准。
- 不相交代码/文档/独立资产可并行；同一 Scene/World/Prefab、`.blend`/骨架、事件数据库、云场景、项目配置或 Editor 会话采用一个写入 owner。资源认领只是协调规则，不是隔离沙箱；独立 worktree 也不隔离共享外部 DCC/云资源。
- 原输入先保留基线、hash/commit/资产快照；只在分配副本/目录修改。源、生成物、缓存、导出与原始证据分开，保持资源 ID/依赖闭包。跨域变更先交主代理重分范围，保持用户已有修改。
- 交付实际路径、输入/产物 hash、命令 cwd/env/版本/输入、字面 stdout/stderr/exit 或其原始证据路径，以及风险、阻断、回退和下游建议。按任务当前结果协议回传；源或产物变化后重新冻结/复验，旧 attempt/token/过期结果交状态机处理。
- 只声明实际发生的执行。文档/模拟/文件检查、软件 doctor、DCC 几何制作、引擎导入、实际游玩、设备测量和真人反馈分别登记。缺软件/SDK/设备/连接记 not_run 与 waiting_dependency，缺人的取舍记 waiting_human；不制造占位文件充当完成资产。
- 作者自检、集成、QA 与独立审查是不同的门；作者不自批自己的结果。独立 reviewer 使用不同于作者/QA 的宿主执行身份并绑定产物 hash，缺独立上下文明确标记限制。提交结束不解锁后继，主代理依据已验证状态推进。
- 超时或失联先向主代理报告；原 worker 已停止并留证后再回收任务/资源，保留现场，避免两个 attempt 同时写同一对象。技术问题先实验/复测并交原 owner 返工；高影响目标/预算/引擎升级/付费/外发/不可逆迁移走人决策门。
- design-only 交规格与计划；实际工程/资产/设备/发布只在已明确的实现范围进行。方向、垂直切片和发布决定由人明确给出；未答复保持等待，确认后由 AI 从记录恢复点继续。
'''


def load_roles():
    data = json.loads((HOME / 'references/agents.json').read_text(encoding='utf-8'))
    if (not isinstance(data, dict) or type(data.get('schema_version')) is not int
            or data['schema_version'] != 1 or not isinstance(data.get('roles'), list)
            or not data['roles']):
        raise ValueError('invalid agent catalog schema')
    production = json.loads((HOME / 'references/production.json').read_text(encoding='utf-8'))
    areas = {area['id'] for area in production['areas']}
    seen, covered = set(), set()
    for role in data['roles']:
        if not isinstance(role, dict):
            raise ValueError('role must be an object')
        if set(role) != {'id', 'name', 'description', 'areas', 'instructions'}:
            raise ValueError('role requires id/name/description/areas/instructions only')
        for field in ('id', 'name', 'description', 'instructions'):
            if not isinstance(role[field], str) or not role[field].strip():
                raise ValueError('role requires non-empty ' + field)
        if not ROLE_ID.fullmatch(role['id']) or role['id'] in seen:
            raise ValueError('invalid or duplicate role ID')
        seen.add(role['id'])
        if not isinstance(role['areas'], list) or any(not isinstance(a, str) or a not in areas for a in role['areas']):
            raise ValueError('role areas must reference production catalog')
        if len(role['areas']) != len(set(role['areas'])):
            raise ValueError('duplicate role area')
        covered.update(role['areas'])
    if covered != areas:
        raise ValueError('role catalog misses production areas: ' + ', '.join(sorted(areas - covered)))
    for required in ('coordinator', 'integrator', 'qa', 'reviewer'):
        if 'game-design-' + required not in seen:
            raise ValueError('missing required orchestration role: ' + required)
    return data


def generated(data):
    # Installed resources live under .game-design; native role files live at project root.
    native = HOME.parent if HOME.name == '.game-design' else HOME
    files = {}
    index = ['# Game Design 原生 subagent 角色', '',
             '> 由 [agents.json](../references/agents.json) 确定性生成；角色是职责目录，不代表同时运行数量。', '',
             '原生文件位于项目根 `.claude/agents/<id>.md` 与 `.codex/agents/<id>.toml`。安装器保留既有未归属文件；角色定义本身不启动代理，主代理按实际宿主工具派发并登记运行 ID。', '',
             '主代理维护调度事务与共享状态；worker 只写任务分配范围。工作包返回结果后还需集成、QA、独立审查，后继任务以实际验收状态为准。', '',
             '[并行执行协议](../references/parallel.md) · [生产工作包](../references/production.md)', '',
             '| ID | 职责 | 主路由领域 |', '|---|---|---|']
    for role in data['roles']:
        index.append(f'| `{role["id"]}` | {role["name"]} | {", ".join(role["areas"]) or "跨领域独立审查"} |')
        body = role['instructions'].rstrip() + '\n\n' + COMMON
        frontmatter = ('---\nname: ' + role['id'] + '\ndescription: '
                       + json.dumps(role['description'], ensure_ascii=False) + '\n---\n')
        files[native / '.claude/agents' / (role['id'] + '.md')] = frontmatter + body
        files[native / '.codex/agents' / (role['id'] + '.toml')] = (
            'name = ' + json.dumps(role['id']) + '\n'
            + 'description = ' + json.dumps(role['description'], ensure_ascii=False) + '\n'
            + 'developer_instructions = ' + json.dumps(body, ensure_ascii=False) + '\n')
        index += ['', '## ' + role['id'], '', role['description'], '',
                  '主路由：' + (', '.join(role['areas']) or '无单一生产领域，跨阶段独立复核') + '。', '',
                  role['instructions'].rstrip(), '']
    index += ['', '## 再生成与校验', '',
              '安装后从项目根运行；模板源码将 `.game-design/` 换成 `manifests/game-design/`：', '',
              '```bash', 'python3 .game-design/scripts/render_agents.py',
              'python3 .game-design/scripts/render_agents.py --check', '```', '',
              'check 模式只读；缺失/漂移返回 1。源目录出现旧的 game-design 前缀角色文件时报告残留，不自动删除；人工确认移除或迁移后再生成。', '']
    files[HOME / 'agents/subagent-roles.md'] = '\n'.join(index)
    return files


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def render(check=False):
    data = load_roles()
    expected = generated(data)
    native = HOME.parent if HOME.name == '.game-design' else HOME
    # Preflight the complete output set before any mutation; never follow a
    # symlinked role directory into the user's external configuration.
    for path in expected:
        current = native
        for part in path.relative_to(native).parts:
            current = current / part
            if current.is_symlink():
                raise ValueError('symlink generated destination: ' + str(current))
            if current != path and current.exists() and not current.is_dir():
                raise ValueError('generated destination parent is not a directory: ' + str(current))
    extras = set()
    for directory, pattern in (('.claude/agents', 'game-design-*.md'), ('.codex/agents', 'game-design-*.toml')):
        extras.update(set((native / directory).glob(pattern)) - set(expected))
    drift = [str(path.relative_to(native if path.is_relative_to(native) else HOME))
             for path, content in expected.items()
             if not path.is_file() or path.read_bytes() != content.encode('utf-8')]
    if extras:
        drift.extend('stale: ' + str(path.relative_to(native)) for path in sorted(extras))
    if not check:
        if extras:
            raise ValueError('stale generated role files: ' + ', '.join(str(p) for p in sorted(extras)))
        for path, content in expected.items():
            if not path.is_file() or path.read_bytes() != content.encode('utf-8'):
                atomic_write(path, content)
    return {'status': 'drift' if check and drift else 'ok', 'roles': len(data['roles']),
            'native_files': len(data['roles']) * 2, 'changed': drift}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Read-only missing/drift check')
    args = parser.parse_args()
    try:
        result = render(args.check)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result['status'] == 'drift' else 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
