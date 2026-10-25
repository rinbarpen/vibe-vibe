"""CLI definition and dispatch for vibe-tool."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import __version__
from .config import CONFIG_FILE, find_repo_root, save_repo_path
from .discovery import discover_manifests, discover_skills
from .update import (
    UNMANAGED_SUBMODULES,
    build_update_command,
    discover_submodule_paths,
    filter_managed_submodule_paths,
)


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except (ValueError, OSError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vibe",
        description="Unified CLI for managing manifests and skills in the vibe-coding ecosystem.",
    )
    parser.add_argument("--version", action="version", version=f"vibe-tool {__version__}")

    subs = parser.add_subparsers(dest="command")

    # ── init ──
    init_p = subs.add_parser("init", help="Initialize a new project from a manifest")
    init_p.add_argument("manifest", help="Manifest name")
    init_p.add_argument("target", nargs="?", default=".", help="Target directory (default: current)")
    init_p.add_argument("--scenario", default="", help="Comma-separated scenario names")
    init_p.add_argument("--provider", choices=("git", "github", "gitlab", "gitee"), default="github", help="Code hosting provider (default: github)")
    init_p.add_argument("-f", "--force", action="store_true", help="Overwrite existing files")
    init_p.add_argument("-n", "--dry-run", action="store_true", help="Preview changes without writing")
    init_p.add_argument("-o", "--owner", default="", help="Default owner (github-enterprise)")
    init_p.add_argument("--org", default="", help="GitHub organization (github-enterprise)")
    init_p.add_argument("--repo", default="", help="GitHub repository (github-enterprise)")
    init_p.add_argument("--email", default="", help="Security contact (github-enterprise)")
    init_p.set_defaults(func=_cmd_init)

    # ── add ──
    add_p = subs.add_parser("add", help="Add a manifest or skill to a project")
    add_subs = add_p.add_subparsers(dest="add_target")

    # add manifest
    am_p = add_subs.add_parser("manifest", help="Add a manifest to an existing project")
    am_p.add_argument("manifest_name", help="Manifest name")
    am_p.add_argument("target", nargs="?", default=".", help="Target directory (default: current)")
    am_p.add_argument("--scenario", default="", help="Comma-separated scenario names")
    am_p.add_argument("-f", "--force", action="store_true", help="Overwrite existing files")
    am_p.add_argument("-n", "--dry-run", action="store_true", help="Preview changes without writing")
    am_p.add_argument("--provider", choices=("git", "github", "gitlab", "gitee"), default="github", help="Code hosting provider (default: github)")
    am_p.add_argument("-o", "--owner", default="", help="Default owner (github-enterprise)")
    am_p.add_argument("--org", default="", help="GitHub organization (github-enterprise)")
    am_p.add_argument("--repo", default="", help="GitHub repository (github-enterprise)")
    am_p.add_argument("--email", default="", help="Security contact (github-enterprise)")
    am_p.set_defaults(func=_cmd_add_manifest)

    # add skill
    ask_p = add_subs.add_parser("skill", help="Add a skill to a project")
    ask_p.add_argument("skill_name", nargs="?", default=None, help="Skill name (omit with --all)")
    ask_p.add_argument("target", nargs="?", default=".", help="Target directory (default: current)")
    ask_p.add_argument("--all", action="store_true", help="Install all skills")
    ask_p.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt for --all")
    ask_p.add_argument("-f", "--force", action="store_true", help="Overwrite existing skills")
    ask_p.add_argument("-n", "--dry-run", action="store_true", help="Preview changes without writing")
    ask_p.set_defaults(func=_cmd_add_skill)

    # ── list ──
    list_p = subs.add_parser("list", help="List available manifests and skills")
    list_p.add_argument("what", nargs="?", default="all", choices=["manifests", "skills", "all"])
    list_p.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    list_p.set_defaults(func=_cmd_list)

    # ── update ──
    upd_p = subs.add_parser("update", help="Update managed submodules or installed project resources")
    upd_p.set_defaults(func=_cmd_update)
    upd_subs = upd_p.add_subparsers(dest="update_target")
    for kind in ("skill", "manifest"):
        child = upd_subs.add_parser(kind, help=f"Update one installed {kind} from local sources, with backup")
        child.add_argument("name", help=f"Installed {kind} name")
        child.add_argument("target", nargs="?", default=".", help="Target project (default: current)")
        child.add_argument("-n", "--dry-run", action="store_true", help="Preview without changing the project or backups")
        if kind == "manifest":
            child.add_argument("--provider", choices=("", "git", "github", "gitlab", "gitee"), default=None,
                               help="Override recorded provider; required for applicable legacy projects")
            child.add_argument("--scenario", default=None, help="Override recorded scenario (empty means no scenario)")
            child.add_argument("-o", "--owner", default=None, help="Override recorded owner")
            for option in ("org", "repo", "email"):
                child.add_argument(f"--{option}", default=None, help=f"Override recorded {option}")
        child.set_defaults(func=_cmd_update_project)

    # ── config ──
    cfg_p = subs.add_parser("config", help="Manage vibe-tool configuration")
    cfg_subs = cfg_p.add_subparsers(dest="config_action")

    csr_p = cfg_subs.add_parser("set-repo", help="Set the vibe-coding repository path")
    csr_p.add_argument("path", help="Path to the vibe-coding repository")
    csr_p.set_defaults(func=_cmd_config_set_repo)

    csh_p = cfg_subs.add_parser("show", help="Show current configuration")
    csh_p.set_defaults(func=_cmd_config_show)

    # ── mcp ──
    mcp_p = subs.add_parser("mcp", help="Manage MCP servers (list available, install into projects)")
    mcp_subs = mcp_p.add_subparsers(dest="mcp_action")

    mcp_list_p = mcp_subs.add_parser("list", help="List available MCP servers in this repo")
    mcp_list_p.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    mcp_list_p.set_defaults(func=_cmd_mcp_list)

    mcp_add_p = mcp_subs.add_parser("add", help="Add MCP server(s) to a project (merge, never overwrite)")
    mcp_add_p.add_argument("server_name", nargs="?", default=None, help="Server name (omit with --all)")
    mcp_add_p.add_argument("target", nargs="?", default=".", help="Target project directory (default: current)")
    mcp_add_p.add_argument("--all", action="store_true", help="Install all MCP servers")
    mcp_add_p.add_argument("-f", "--force", action="store_true", help="Overwrite existing server config")
    mcp_add_p.add_argument("-n", "--dry-run", action="store_true", help="Preview changes without writing")
    mcp_add_p.set_defaults(func=_cmd_mcp_add)

    # ── hook ──
    hook_p = subs.add_parser("hook", help="Manage hooks (list available, install into projects)")
    hook_subs = hook_p.add_subparsers(dest="hook_action")

    hook_list_p = hook_subs.add_parser("list", help="List available hook sets in this repo")
    hook_list_p.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    hook_list_p.set_defaults(func=_cmd_hook_list)

    hook_add_p = hook_subs.add_parser("add", help="Install hook set(s) into a project")
    hook_add_p.add_argument("hook_name", nargs="?", default=None, help="Hook set name (omit with --all)")
    hook_add_p.add_argument("target", nargs="?", default=".", help="Target project directory (default: current)")
    hook_add_p.add_argument("--all", action="store_true", help="Install all hook sets")
    hook_add_p.add_argument("-f", "--force", action="store_true", help="Overwrite existing hook set")
    hook_add_p.add_argument("-n", "--dry-run", action="store_true", help="Preview without writing")
    hook_add_p.set_defaults(func=_cmd_hook_add)

    # ── stats ──
    stats_p = subs.add_parser("stats", help="Show or manage skill usage statistics")
    stats_subs = stats_p.add_subparsers(dest="stats_action")

    stats_show_p = stats_subs.add_parser("show", help="Display skill usage statistics")
    stats_show_p.add_argument("--by-tool", action="store_true", help="Group by tool name")
    stats_show_p.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    stats_show_p.set_defaults(func=_cmd_stats_show)

    stats_reset_p = stats_subs.add_parser("reset", help="Reset all skill statistics")
    stats_reset_p.add_argument("--yes", action="store_true", help="Skip confirmation")
    stats_reset_p.set_defaults(func=_cmd_stats_reset)

    return parser


# ── Command handlers ──

def _get_repo_paths(args) -> tuple[Path, Path, tuple[Path, Path]]:
    """Resolve repo root, manifests dir, and skill roots (skills/ + mine/)."""
    root = find_repo_root()
    return root, root / "manifests", (root / "skills", root / "mine")


def _cmd_init(args) -> int:
    from .manifest import init_manifest

    _, manifests_dir, _ = _get_repo_paths(args)
    target = Path(args.target or ".")

    kwargs = _collect_kwargs(args)
    return init_manifest(
        manifests_dir,
        args.manifest,
        target,
        force=args.force,
        dry_run=args.dry_run,
        **kwargs,
    )


def _cmd_add_manifest(args) -> int:
    from .manifest import add_manifest

    _, manifests_dir, _ = _get_repo_paths(args)
    target = Path(args.target).resolve()

    kwargs = _collect_kwargs(args, source_attr="manifest_name")
    return add_manifest(
        manifests_dir,
        args.manifest_name,
        target,
        force=args.force,
        dry_run=args.dry_run,
        **kwargs,
    )


def _cmd_add_skill(args) -> int:
    from .skill import add_all_skills, add_skill

    _, _, skills_root = _get_repo_paths(args)
    target = Path(args.target).resolve()

    if args.all:
        if not args.yes and not args.dry_run:
            skills = discover_skills(*skills_root)
            print(f"This will install {len(skills)} skills into {target}/.agents/skills/")
            response = input("Continue? [y/N] ").strip().lower()
            if response not in ("y", "yes"):
                print("Aborted.")
                return 0
        return add_all_skills(skills_root, target, force=args.force, dry_run=args.dry_run)

    if not args.skill_name:
        print("Error: specify a skill name or use --all", file=sys.stderr)
        return 1

    return add_skill(skills_root, args.skill_name, target, force=args.force, dry_run=args.dry_run)


def _cmd_list(args) -> int:
    try:
        _, manifests_dir, skills_root = _get_repo_paths(args)
    except RuntimeError as e:
        if args.json_out:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.what in ("manifests", "all"):
        _list_manifests(manifests_dir, args.json_out)

    if args.what in ("skills", "all"):
        if args.what == "all":
            print()
        _list_skills(skills_root, args.json_out)

    return 0


def _list_manifests(manifests_dir: Path, json_out: bool) -> None:
    manifests = discover_manifests(manifests_dir)
    if json_out:
        print(json.dumps([asdict(m) for m in manifests], indent=2, default=str))
        return

    if not manifests:
        print("No manifests found.")
        return

    print(f"{'MANIFEST':<24} {'INIT':<6} {'DESCRIPTION'}")
    print("-" * 78)
    for m in manifests:
        marker = "script" if m.has_init_script else "generic"
        print(f"  {m.name:<22} {marker:<6} {m.description}")


def _list_skills(skills_root, json_out: bool) -> None:
    skills = discover_skills(*skills_root)
    if json_out:
        # Only print basic info to keep JSON manageable
        print(json.dumps([
            {"name": s.name, "id_path": s.id_path, "source": str(s.source_path)}
            for s in skills
        ], indent=2))
        return

    if not skills:
        print("No skills found.")
        return

    print(f"{len(skills)} skills found:")
    width = max(len(s.name) for s in skills[:50]) + 2 if skills else 20
    for s in skills[:50]:
        print(f"  {s.name:<{width}} ({s.id_path})")
    if len(skills) > 50:
        print(f"  ... and {len(skills) - 50} more")


def _cmd_update_project(args) -> int:
    from .project_update import update_manifest, update_skill

    root = find_repo_root()
    target = Path(args.target)
    if args.update_target == "skill":
        return update_skill(root, args.name, target, dry_run=args.dry_run)
    options = {key: getattr(args, key) for key in ("provider", "scenario", "owner", "org", "repo", "email")
               if getattr(args, key) is not None}
    return update_manifest(root, args.name, target, dry_run=args.dry_run, **options)


def _cmd_update(args) -> int:
    try:
        root = find_repo_root()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    import subprocess

    try:
        paths = discover_submodule_paths(root)
    except subprocess.CalledProcessError as exc:
        print(f"Unable to read .gitmodules (exit {exc.returncode})", file=sys.stderr)
        return exc.returncode or 1

    managed_paths = filter_managed_submodule_paths(paths)
    skipped_paths = [path for path in paths if path in UNMANAGED_SUBMODULES]
    print("Updating managed skill submodules...")
    if skipped_paths:
        print("Skipping unmanaged submodules: " + ", ".join(skipped_paths))

    command = build_update_command(managed_paths)
    if not command:
        print("No managed submodules to update.")
        return 0

    result = subprocess.run(command, cwd=str(root), check=False)
    return result.returncode


def _cmd_config_set_repo(args) -> int:
    try:
        repo_path = save_repo_path(args.path)
        print(f"vibe-coding repository set to: {repo_path}")
        return 0
    except (NotADirectoryError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _cmd_config_show(args) -> int:
    if CONFIG_FILE.exists():
        print(CONFIG_FILE.read_text(encoding="utf-8"))
    else:
        print(f"No config file at {CONFIG_FILE}")
        print("Use 'vibe config set-repo /path/to/vibe-coding' to create one.")
    return 0


def _cmd_mcp_list(args) -> int:
    from .mcp import discover_mcp_servers

    root = find_repo_root()
    servers = discover_mcp_servers(root / "mcp.json")
    if not servers:
        print("No MCP servers found.")
        return 0

    if args.json_out:
        print(json.dumps(servers, indent=2))
        return 0

    print(f"{'SERVER':<24} {'TYPE':<8} {'TARGET'}")
    print("-" * 60)
    for name, cfg in servers.items():
        typ = "url" if "url" in cfg else "command"
        target = cfg.get("url", "") or " ".join(cfg.get("args", [])) if "command" in cfg else ""
        print(f"  {name:<22} {typ:<8} {target}")
    return 0


def _cmd_mcp_add(args) -> int:
    from .mcp import add_mcp_servers

    root = find_repo_root()
    target = Path(args.target).resolve()
    names = [args.server_name] if args.server_name else None

    if not args.all and not args.server_name:
        print("Error: specify a server name or use --all", file=sys.stderr)
        return 1

    return add_mcp_servers(
        root / "mcp.json",
        target,
        names=names,
        all_servers=args.all,
        force=args.force,
        dry_run=args.dry_run,
    )


def _cmd_hook_list(args) -> int:
    from .hook import discover_hooks

    root = find_repo_root()
    hooks = discover_hooks(root)
    if not hooks:
        print("No hook sets found.")
        return 0

    if args.json_out:
        import json as j
        print(j.dumps(hooks, indent=2))
        return 0

    print("Available hook sets:")
    for h in hooks:
        print(f"  {h}")
    return 0


def _cmd_hook_add(args) -> int:
    from .hook import add_hooks

    root = find_repo_root()
    target = Path(args.target).resolve()
    names = [args.hook_name] if args.hook_name else None

    if not args.all and not args.hook_name:
        print("Error: specify a hook name or use --all", file=sys.stderr)
        return 1

    return add_hooks(
        root,
        target,
        names=names,
        all_hooks=args.all,
        force=args.force,
        dry_run=args.dry_run,
    )


def _cmd_stats_show(args) -> int:
    from .stats import format_stats, get_usage_stats

    data = get_usage_stats()
    if args.json_out:
        import json as j
        print(j.dumps(data, indent=2, ensure_ascii=False))
        return 0

    print(format_stats(data, by_tool=args.by_tool))
    return 0


def _cmd_stats_reset(args) -> int:
    from .stats import reset_stats

    if reset_stats(force=args.yes):
        print("Statistics reset.")
        return 0
    return 0


def _collect_kwargs(args, source_attr: str = "manifest") -> list:
    """Collect extra keyword arguments for init scripts from parsed args."""
    kwargs: dict[str, str] = {}
    for key in ("scenario", "provider", "owner", "org", "repo", "email"):
        val = getattr(args, key, None)
        if val:
            kwargs[key] = val
    return kwargs
