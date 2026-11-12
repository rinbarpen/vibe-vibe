from pathlib import Path
import os,re
R=Path.cwd(); T=R/'tools/vibe_tool/tests'
def put(p,s):
 t=p.with_name(p.name+'.tmp'); t.write_text(s,encoding='utf-8'); os.replace(t,p)
for p in T.glob('test_office*.py'):
 s=p.read_text(); s=re.sub(r'manifests/office/(docx|xlsx|pptx|pdf|planning)/',r'mine/office/\1/',s)
 if p.name=='test_office_runtime.py': s=s.replace('"manifests/office/scripts"','"mine/office/scripts"')
 put(p,s)
p=T/'test_office_install.py'; s=p.read_text()
s=s.replace('        self.target = self.base / "project with spaces"','        self.skill = self.repo / "mine/office"\n        self.target = self.base / "project with spaces"')
s=s.replace('        for fmt in (*FORMATS, "planning"):', '        self.write(self.skill / "SKILL.md", "---\\nname: office\\ndescription: fixture\\n---\\n")\n        for fmt in (*FORMATS, "planning"):')
for rel in ['fmt / "CLAUDE.md"','"docx/rules/patent.md"','"xlsx/scripts/recalc.sh"','"rules/quality.md"','"scripts/check_dependencies.py"','"scripts/nested/script with spaces.py"','"scripts/__pycache__/ignored.pyc"']:
 s=s.replace('self.manifest / '+rel,'self.skill / '+rel)
s=s.replace('self.manifest / "rules/office-quality.mdc", "---\\nalwaysApply: true\\n---\\nQuality\\n"','self.manifest / "rules/office-project.md", "---\\nalways: true\\n---\\nProject\\n"')
s=s.replace('self.manifest / "agents/subagent-roles"','self.skill / "agents/subagent-roles"').replace('self.manifest / ".claude/agents"','self.skill / "agents/claude"').replace('self.manifest / ".codex/agents"','self.skill / "agents/codex"')
s=s.replace('[f"anthropics/skills/{fmt}" for fmt in FORMATS] + ["office-quality"','["office"] + [f"anthropics/skills/{fmt}" for fmt in FORMATS] + ["office-quality"')
s=s.replace('"office/rules/quality.md", ".cursor/rules/office-quality.mdc",','".agents/skills/office/rules/quality.md", "office/rules/office-project.md",')
# Only runtime assets move; office/README remains project-specific.
for name in ['docx','xlsx','scripts','agents','{fmt}']:
 s=s.replace('"office/'+name+'/', '".agents/skills/office/'+name+'/')
s=s.replace('"office/scripts/install_office.py", "office/scripts/init-office.sh",','".agents/skills/office/scripts/install_office.py", ".agents/skills/office/scripts/init-office.sh",')
s=s.replace('".agents/skills/office-quality/SKILL.md"]','".agents/skills/office-quality/SKILL.md", ".agents/skills/office/SKILL.md"]')
prefix='                    "office/docx/rules/patent.md"'
# Keep MANIFEST and custom project files in their prior locations.
put(p,s)
p=T/'test_office_workflow_diagrams.py'; s=p.read_text().replace('import hashlib','import hashlib\nimport json',1)
s=s.replace('SKILL_NAMES = ("office-quality",','SKILL_NAMES = ("office", "office-quality",',1)
s=s.replace('source = base / "assets/workflow.mmd"\n                self.assertTrue(source.is_file())\n                self.assertIn("flowchart", source.read_text(encoding="utf-8"))','source = base / "assets/workflow.mmd"\n                if source.is_file():\n                    self.assertIn("flowchart", source.read_text(encoding="utf-8"))\n                else:\n                    source = base / "assets/workflow.json"\n                    self.assertEqual(json.loads(source.read_text())["schema_version"], 1)')
s=s.replace('len(required), 9','len(required), 10').replace('len(set(required)), 9','len(set(required)), 10')
s=s.replace('for relative in ("SKILL.md", "assets/workflow.svg", "assets/workflow.mmd"):', 'for relative in ("SKILL.md", "assets/workflow.svg",\n                                 "assets/workflow.json" if name == "office" else "assets/workflow.mmd"):')
put(p,s)
p=T/'test_office_word_features.py'; s=p.read_text()
# The project installer only registers the project and roles; file tools install via Skill.
s=s.replace('        expected = ["office/docx/scripts/feature_audit.py",','''        install_skill = subprocess.run(
            [sys.executable, "-m", "vibe_tool", "add", "skill", "office", str(target)],
            env={**os.environ, "VIBE_HOME": str(ROOT), "PYTHONPATH": str(ROOT / "tools/vibe_tool/src"),
                 "PYTHONDONTWRITEBYTECODE": "1", "VIBE_PROJECTS_FILE": str(self.root / "projects.json")},
            capture_output=True, text=True)
        self.assertEqual(install_skill.returncode, 0, install_skill.stdout + install_skill.stderr)
        expected = [".agents/skills/office/docx/scripts/feature_audit.py",''')
s=s.replace('"office/docx/', '".agents/skills/office/docx/')
start=s.index('        manifest = ROOT / "manifests/office"',s.index('def test_native_rules_and_eight_agent_prompts'))
end=s.index('        for role in ("planner"',start)
s=s[:start]+'''        capability = ROOT / "mine/office"
        for name in ("quality", "file-safety", "docx", "xlsx", "pptx", "pdf"):
            self.assertTrue((capability / f"rules/{name}.md").is_file())
            self.assertFalse((ROOT / f"manifests/office/rules/office-{name}.mdc").exists())
'''+s[end:]
s=s.replace('(manifest / f".claude/agents/', '(capability / f"agents/claude/').replace('(manifest / f".codex/agents/', '(capability / f"agents/codex/')
put(p,s)
print('Updated Office test resource paths and installation expectations.')
