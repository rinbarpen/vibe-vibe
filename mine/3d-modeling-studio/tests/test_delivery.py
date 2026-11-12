"""Standard-library tests: opaque file fixtures do not simulate real DCC validation."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    'check_delivery', Path(__file__).resolve().parents[1] / 'scripts/check_delivery.py')
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = {'schema_version': 1, 'asset_name': 'record-test', 'profile': 'portfolio',
                     'software': [{'name': 'TEST-HOST', 'version': '1'}], 'files': [],
                     'technical_review': {'status': 'accepted', 'evidence': ['audit.json']},
                     'visual_review': {'status': 'accepted', 'evidence': ['review.md'], 'issues': []},
                     'roundtrip': {'status': 'accepted', 'evidence': ['import.md']}}
        for role, name in (('source', 'source.fixture'), ('exchange', 'exchange.fixture'),
                           ('preview', 'preview.fixture'), ('review_record', 'review.md'),
                           ('roundtrip_record', 'import.md')):
            self.add_file(role, name, b'opaque automated-test fixture, not a valid 3D asset\n')
        source_hash = self.data['files'][0]['sha256']
        self.add_file('qa_report', 'audit.json', json.dumps({
            'kind': 'blender-mesh-audit', 'status': 'pass', 'source_unchanged': True,
            'source_sha256': source_hash}).encode())

    def add_file(self, role, name, content):
        (self.root / name).write_bytes(content)
        self.data['files'].append({'path': name, 'role': role,
                                   'sha256': hashlib.sha256(content).hexdigest()})

    def errors(self, data=None, stage='final'):
        return CHECKER.validate(self.data if data is None else data, self.root, stage)[0]

    def test_complete_records_pass(self):
        self.assertEqual(self.errors(), [])

    def test_pending_template_passes_only_draft(self):
        path = Path(__file__).resolve().parents[1] / 'assets/delivery.template.json'
        data = json.loads(path.read_text())
        self.assertEqual(self.errors(data, 'draft'), [])
        self.assertTrue(self.errors(data, 'final'))

    def test_hash_mismatch_fails(self):
        (self.root / 'source.fixture').write_bytes(b'changed')
        self.assertTrue(any('sha256 mismatch' in e for e in self.errors()))

    def test_missing_file_fails(self):
        (self.root / 'preview.fixture').unlink()
        self.assertTrue(any('missing or empty' in e for e in self.errors()))

    def test_missing_roles_fail(self):
        self.data['files'] = [f for f in self.data['files'] if f['role'] != 'exchange']
        self.assertTrue(any('missing required file role: exchange' in e for e in self.errors()))

    def test_pending_review_fails(self):
        self.data['visual_review']['status'] = 'pending'
        self.assertTrue(any('visual_review needs' in e for e in self.errors()))

    def test_major_issue_fails_even_if_accepted(self):
        self.data['visual_review']['issues'] = [{'id': 'shape', 'severity': 'major', 'status': 'accepted'}]
        self.assertTrue(any('unclosed major' in e for e in self.errors()))

    def test_closed_major_and_accepted_minor_pass(self):
        self.data['visual_review']['issues'] = [
            {'id': 'shape', 'severity': 'major', 'status': 'closed'},
            {'id': 'minor', 'severity': 'minor', 'status': 'accepted'}]
        self.assertEqual(self.errors(), [])

    def test_traversal_fails(self):
        self.data['files'][0]['path'] = '../external.fixture'
        self.assertTrue(any('stay relative' in e for e in self.errors()))

    def test_external_symlink_fails(self):
        with tempfile.TemporaryDirectory() as other:
            external = Path(other) / 'external.fixture'
            external.write_bytes(b'outside')
            (self.root / 'link.fixture').symlink_to(external)
            self.data['files'][0]['path'] = 'link.fixture'
            self.assertTrue(any('outside delivery root' in e for e in self.errors()))

    def test_wrong_evidence_role_fails(self):
        self.data['visual_review']['evidence'] = ['preview.fixture']
        self.assertTrue(any('not a listed review_record' in e for e in self.errors()))

    def test_failed_blender_audit_fails(self):
        audit = json.loads((self.root / 'audit.json').read_text())
        audit['status'] = 'fail'
        content = json.dumps(audit).encode()
        (self.root / 'audit.json').write_bytes(content)
        self.data['files'][-1]['sha256'] = hashlib.sha256(content).hexdigest()
        self.assertTrue(any('audit is failed' in e for e in self.errors()))

    def test_unbound_audit_fails(self):
        audit = json.loads((self.root / 'audit.json').read_text())
        audit['source_sha256'] = '0' * 64
        content = json.dumps(audit).encode()
        (self.root / 'audit.json').write_bytes(content)
        self.data['files'][-1]['sha256'] = hashlib.sha256(content).hexdigest()
        self.assertTrue(any('does not bind' in e for e in self.errors()))

    def test_duplicate_path_fails(self):
        self.data['files'].append(copy.deepcopy(self.data['files'][0]))
        self.assertTrue(any('duplicate path' in e for e in self.errors()))

    def test_malformed_nested_audit_produces_error(self):
        audit = json.loads((self.root / 'audit.json').read_text())
        audit['source_sha256'] = []
        content = json.dumps(audit).encode()
        (self.root / 'audit.json').write_bytes(content)
        self.data['files'][-1]['sha256'] = hashlib.sha256(content).hexdigest()
        self.assertTrue(any('does not bind' in e for e in self.errors()))

    def test_malformed_types_produce_errors(self):
        for field in ('schema_version', 'asset_name', 'profile', 'software', 'files',
                      'visual_review', 'technical_review', 'roundtrip'):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data[field] = [] if field not in ('software', 'files') else 2
                self.assertTrue(self.errors(data))

    def test_validation_does_not_change_records(self):
        before = copy.deepcopy(self.data)
        self.errors()
        self.assertEqual(self.data, before)


if __name__ == '__main__':
    unittest.main()
