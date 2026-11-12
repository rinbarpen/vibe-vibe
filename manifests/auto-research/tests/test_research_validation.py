"""Contract regressions, not an automated judge of scientific novelty/truth."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

MANIFEST = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validation_stage_contract', MANIFEST / 'scripts/stage_contract.py')
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)
CONFIG = json.loads((MANIFEST / 'lifecycle/defaults.json').read_text())
STAGES = {stage['id']: stage for stage in CONFIG['stages']}
AFFECTED = (
    'literature/position/novelty', 'idea/hypotheses/candidates',
    'idea/hypotheses/comparison', 'idea/method/mechanism', 'idea/method/claims',
    'design/ablation/coverage', 'analysis/interpretation/failures',
    'analysis/interpretation/claims', 'analysis/interpretation/audit',
)


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
            for p in root.rglob('*') if p.is_file()}


class ValidationContractTests(unittest.TestCase):
    def test_dual_entrypoints_share_identical_validation_rules(self):
        sections = []
        for name in ('AGENTS.md', 'CLAUDE.md'):
            content = (MANIFEST / name).read_text()
            section = content.split('## Idea 验证与迭代保真\n', 1)[1].split('\n## ', 1)[0]
            sections.append(section)
            for required in ('high_overlap', 'unverified', 'refuted_in_scope',
                             '部分实验', '思想启迪', '语义 diff', 'checkpoint'):
                self.assertIn(required, section)
        self.assertEqual(sections[0], sections[1])

    def test_new_criteria_and_handoff_are_in_canonical_contracts_and_docs(self):
        document = (MANIFEST / 'references/lifecycle-leaf-contracts.md').read_text()
        for stage_id in AFFECTED:
            with self.subTest(stage=stage_id):
                stage = STAGES[stage_id]
                self.assertEqual(stage['contract_revision'], 2)
                self.assertIn('semantic_diff', stage['handoff']['include'])
                self.assertIn('negative_results_and_insight_refs', stage['handoff']['include'])
                section = document.split('## ' + stage_id + '\n', 1)[1].split('\n## ', 1)[0]
                for rule in stage['acceptance']:
                    self.assertIn(rule, section)
        self.assertEqual(STAGES['idea/hypotheses/comparison']['approval'], 'human_confirmation')

    def test_keywords_partial_runs_and_inspiration_have_distinct_criteria(self):
        novelty = '\n'.join(STAGES['literature/position/novelty']['acceptance'])
        claims = '\n'.join(STAGES['analysis/interpretation/claims']['acceptance'])
        failures = '\n'.join(STAGES['analysis/interpretation/failures']['acceptance'])
        for term in ('研究思路', '关键方法', '原始方法证据', 'high_overlap', 'unverified'):
            self.assertIn(term, novelty)
        for term in ('冻结矩阵', '实跑有效证据', 'inconclusive', 'refuted_in_scope', '提前停止', '资源中止'):
            self.assertIn(term, claims)
        for term in ('实现', '协议', 'method', 'hypothesis', '待验证启发', '后续验证/cycle'):
            self.assertIn(term, failures)

    def test_old_attestation_fails_new_criteria_current_passes_then_hash_drift_fails(self):
        for stage_id in AFFECTED:
            with self.subTest(stage=stage_id), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                stage = STAGES[stage_id]
                for name in stage['outputs']:
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text('{}' if path.suffix == '.json' else 'FIXTURE only: raw evidence reference\n')
                report = dict(stage_id=stage_id, contract_hash=sc.contract_hash(stage),
                              reviewer='fixture-reviewer', reviewed_at='2026-11-08',
                              artifacts=sc.check_stage(root, stage)['artifacts'],
                              checks=[dict(criterion=c, status='pass', evidence='FIXTURE review declaration')
                                      for c in stage['acceptance'][:2]])
                if stage['approval'] == 'human_confirmation':
                    report['approval'] = dict(approved=True, approved_by='fixture-user', approved_at='2026-11-08')
                path = root / stage['review_path']
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(report))
                failed = sc.check_stage(root, stage)
                self.assertEqual(failed['status'], 'fail')
                self.assertTrue(any('Unconfirmed criterion' in error for error in failed['errors']))
                for criterion in stage['acceptance'][2:]:
                    report['checks'].append(dict(criterion=criterion, status='pass', evidence='FIXTURE attestation, not science'))
                path.write_text(json.dumps(report))
                self.assertEqual(sc.check_stage(root, stage)['status'], 'pass')
                output = root / stage['outputs'][0]
                output.write_text('{"changed":true}' if output.suffix == '.json' else 'changed scientific revision')
                self.assertEqual(sc.check_stage(root, stage)['status'], 'fail')
                report['artifacts'] = sc.check_stage(root, stage)['artifacts']
                report['contract_hash'] = 'obsolete-contract-hash'
                path.write_text(json.dumps(report))
                self.assertIn('Stale contract review', sc.check_stage(root, stage)['errors'])

    def test_new_document_links_and_record_templates_exist(self):
        document = MANIFEST / 'references/idea-validation.md'
        for relative in re.findall(r'\]\(([^)]+)\)', document.read_text()):
            self.assertTrue((document.parent / relative).is_file(), relative)
        for name in ('NOVELTY', 'FAILURE_ANALYSIS'):
            self.assertTrue((MANIFEST / f'templates/{name}.md.example').is_file())
        log = (MANIFEST / 'templates/EXPERIMENT_LOG.md.example').read_text()
        for term in ('Context Handoff', 'semantic diff', 'unchanged invariants', 'insight ID'):
            self.assertIn(term, log)


class ValidationWorkflowTests(unittest.TestCase):
    def render(self, root, *extra):
        return subprocess.run([sys.executable, str(root / 'scripts/render_idea_workflow.py'),
                               '--source', str(root / 'references/validation-workflow.json'),
                               '--output', str(root / 'references/validation-workflow.svg'), *extra],
                              text=True, capture_output=True)

    def test_svg_current_and_check_is_read_only(self):
        before = snapshot(MANIFEST / 'references')
        result = self.render(MANIFEST, '--check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(MANIFEST / 'references'), before)
        ET.parse(MANIFEST / 'references/validation-workflow.svg')

    def test_drift_missing_graph_and_broken_edge_fail_without_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ('scripts/render_idea_workflow.py', 'references/validation-workflow.json',
                             'references/validation-workflow.svg'):
                p = root / relative; p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes((MANIFEST / relative).read_bytes())
            source = root / 'references/validation-workflow.json'
            svg = root / 'references/validation-workflow.svg'
            graph = json.loads(source.read_text())
            graph['description'] += ' changed'
            source.write_text(json.dumps(graph))
            before = snapshot(root)
            self.assertEqual(self.render(root, '--check').returncode, 1)
            self.assertEqual(snapshot(root), before)
            svg.unlink()
            before = snapshot(root)
            self.assertEqual(self.render(root, '--check').returncode, 1)
            self.assertEqual(snapshot(root), before)
            graph['edges'][0]['to'] = 'missing'
            source.write_text(json.dumps(graph))
            before = snapshot(root)
            self.assertEqual(self.render(root, '--check').returncode, 2)
            self.assertEqual(snapshot(root), before)

    def test_branch_routes_cover_rebuild_supplement_and_human_resume(self):
        graph = json.loads((MANIFEST / 'references/validation-workflow.json').read_text())
        edges = {(e['from'], e['to']) for e in graph['edges']}
        for route in (('context', 'restore'), ('restore', 'novelty'), ('coverage', 'design'),
                      ('coverage', 'decision'), ('decision', 'design'), ('decision', 'archive'),
                      ('audit', 'learn'), ('archive', 'context')):
            self.assertIn(route, edges)
        human = next(n for n in graph['nodes'] if n['id'] == 'decision')
        self.assertIn('未答复等待', human['resume'])


if __name__ == '__main__':
    unittest.main()
