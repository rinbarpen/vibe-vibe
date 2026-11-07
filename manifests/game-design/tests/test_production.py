"""Expanded production/asset/version/distribution contracts, never runtime gameplay tests."""
import contextlib
import copy
import hashlib
import io
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import tarfile
import unittest

HOME=Path(__file__).resolve().parents[1];ROOT=HOME.parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(HOME/'scripts'))
import production_tools as production
import asset_checks
import version_check
import install_manifest
from game_design import load_catalog,check_project


def snapshot(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and not p.is_symlink()}

class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='game production tests ');self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.project=self.base/'project';self.project.mkdir()

    def command(self,*args,cwd=None):
        return subprocess.run(list(map(str,args)),cwd=cwd or ROOT,text=True,capture_output=True,
                              env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','GIT_OPTIONAL_LOCKS':'0'})

    def install(self):
        with contextlib.redirect_stdout(io.StringIO()):install_manifest.install(self.project)

    def test_catalogs_complete_dag(self):
        genres,areas,order=production.load_data()
        self.assertGreaterEqual(len(genres['genres']),24)
        self.assertGreaterEqual(len(areas['areas']),15)
        self.assertGreaterEqual(len(order),70)
        position={value:i for i,value in enumerate(order)}
        for area in areas['areas']:
            for task in area['tasks']:
                for dependency in task['depends_on']:self.assertLess(position[dependency],position[task['id']])
        self.assertEqual(production.render(genres,areas,True)['status'],'ok')

    def test_catalog_rejects_unknown_and_cyclic_dependencies(self):
        original=production.HOME
        genres,areas,_=production.load_data()
        production.HOME=self.base
        (self.base/'references').mkdir()
        (self.base/'references/genres.json').write_text(json.dumps(genres))
        try:
            for kind in ('unknown','cycle','empty','duplicate'):
                data=copy.deepcopy(areas)
                first=data['areas'][0]['tasks'][0]
                last=data['areas'][-1]['tasks'][-1]
                if kind=='unknown':first['depends_on']=['MISSING-TASK']
                if kind=='cycle':first['depends_on']=[last['id']];last['depends_on']=[first['id']]
                if kind=='empty':first['acceptance']=[]
                if kind=='duplicate':last['id']=first['id']
                (self.base/'references/production.json').write_text(json.dumps(data))
                with self.assertRaises(ValueError):production.load_data()
        finally:production.HOME=original

    def test_genre_rejects_empty_acceptance_and_duplicate(self):
        original=production.HOME;genres,areas,_=production.load_data()
        production.HOME=self.base;(self.base/'references').mkdir()
        (self.base/'references/production.json').write_text(json.dumps(areas))
        try:
            for kind in ('empty','duplicate'):
                data=copy.deepcopy(genres)
                if kind=='empty':data['genres'][0]['acceptance']=[]
                else:data['genres'][-1]['id']=data['genres'][0]['id']
                (self.base/'references/genres.json').write_text(json.dumps(data))
                with self.assertRaises(ValueError):production.load_data()
        finally:production.HOME=original

    def test_catalog_render_check_read_only(self):
        original=production.HOME;genres,areas,_=production.load_data();production.HOME=self.base
        try:
            before=snapshot(self.base)
            self.assertEqual(production.render(genres,areas,True)['status'],'drift')
            self.assertEqual(snapshot(self.base),before)
            production.render(genres,areas)
            (self.base/'references/production.md').write_text('modified')
            before=snapshot(self.base)
            self.assertEqual(production.render(genres,areas,True)['status'],'drift')
            self.assertEqual(snapshot(self.base),before)
        finally:production.HOME=original

    def test_cli_queries_and_unknown(self):
        for command in [('genres',),('areas',),('genre','--id','roguelike'),('work','--area','modeling')]:
            result=self.command(sys.executable,HOME/'scripts/production_tools.py',*command)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        for command in [('genre','--id','missing'),('work','--id','missing')]:
            self.assertEqual(self.command(sys.executable,HOME/'scripts/production_tools.py',*command).returncode,2)

    def test_install_self_contained_canonical_payload_and_source_hash(self):
        self.install();runtime=self.project/'.game-design'
        ledger=json.loads((runtime/'install.json').read_text())
        for source,destination,_ in install_manifest.canonical_files():
            installed=self.project/destination
            self.assertEqual(installed.read_bytes(),source.read_bytes())
            self.assertEqual(ledger['canonical_sources'][destination]['sha256'],hashlib.sha256(source.read_bytes()).hexdigest())
        for args in [
            [runtime/'scripts/production_tools.py','check-production'],
            [runtime/'scripts/production_tools.py','render-production','--check'],
            [runtime/'scripts/production_tools.py','work','--area','modeling']]:
            result=self.command(sys.executable,*args,cwd=self.project)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_missing_canonical_fails_before_write(self):
        original=install_manifest.canonical_files
        install_manifest.canonical_files=lambda:[(self.base/'MISSING','.game-design/scripts/dcc_cli.py',False)]
        try:
            with self.assertRaises(ValueError),contextlib.redirect_stdout(io.StringIO()):install_manifest.install(self.project)
            self.assertEqual(snapshot(self.project),{})
        finally:install_manifest.canonical_files=original

    def test_preserved_custom_helper_is_not_claimed_as_canonical(self):
        custom=self.project/'.game-design/scripts/dcc_cli.py'
        custom.parent.mkdir(parents=True);custom.write_text('# user helper\n')
        self.install()
        info=json.loads((self.project/'.game-design/install.json').read_text())['canonical_sources']['.game-design/scripts/dcc_cli.py']
        self.assertEqual(custom.read_text(),'# user helper\n')
        self.assertEqual(info['status'],'unmanaged');self.assertFalse(info['provenance_verified'])
        self.assertNotEqual(info['installed_sha256'],info['available_source_sha256'])

    def test_kept_older_canonical_records_refresh_pending(self):
        original=install_manifest.SOURCE
        source=self.base/'source/manifests/game-design';shutil.copytree(HOME,source)
        for path,destination,_ in install_manifest.canonical_files():
            target=self.base/'source'/path.relative_to(ROOT)
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        install_manifest.SOURCE=source
        try:
            self.install()
            canonical=source.parent/'unity-game/scripts/dcc_cli.py'
            canonical.write_bytes(canonical.read_bytes()+b'\n# revised canonical fixture\n')
            self.install()
            info=json.loads((self.project/'.game-design/install.json').read_text())['canonical_sources']['.game-design/scripts/dcc_cli.py']
            self.assertEqual(info['status'],'refresh_pending');self.assertTrue(info['provenance_verified'])
            self.assertNotEqual(info['installed_sha256'],info['available_source_sha256'])
        finally:install_manifest.SOURCE=original

    def test_missing_blender_is_real_not_run(self):
        self.install();out=self.project/'Evidence/missing-blender'
        result=self.command(sys.executable,self.project/'.game-design/scripts/dcc_cli.py','doctor',
                            '--blender',self.base/'NO-BLENDER','--output-dir',out)
        self.assertEqual(result.returncode,2,result.stdout+result.stderr)
        self.assertEqual(json.loads((out/'result.json').read_text())['status'],'not_run')

    def test_legacy_project_fields_remain_compatible(self):
        self.install();path=self.project/'.game-design/state/project.json';state=json.loads(path.read_text())
        for field in ('genres','dimension','multiplayer','content_pipeline'):state.pop(field,None)
        state.update(engine='godot',engine_version='recorded',targets=['desktop'],
                     budgets={'frame_time_ms':16.67,'memory_mb':256,'download_mb':50})
        path.write_text(json.dumps(state))
        self.assertEqual(check_project(self.project,load_catalog())['status'],'configured')

    def test_upgrade_previous_manifest_preserves_project_data(self):
        archive=ROOT/'.planning/game-manifest/evidence/revision-02/baseline.tar.gz'
        if not archive.is_file():self.skipTest('historical source fixture is not part of an installed package')
        before=self.base/'previous';before.mkdir()
        with tarfile.open(archive) as tar:
            for entry in tar.getmembers():
                self.assertTrue(entry.isfile());self.assertNotIn('..',Path(entry.name).parts)
            tar.extractall(before)
        result=self.command(sys.executable,before/'manifests/game-design/scripts/install_manifest.py',self.project)
        self.assertEqual(result.returncode,0,result.stderr)
        state=self.project/'.game-design/state/project.json';original=state.read_bytes()
        source=self.project/'Art/owner-source.blend';source.parent.mkdir();source.write_bytes(b'untouched source fixture')
        result=self.command(sys.executable,HOME/'scripts/install_manifest.py',self.project,'--force')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(state.read_bytes(),original);self.assertEqual(source.read_bytes(),b'untouched source fixture')
        for item in ('state/version.json','state/work.md','references/genres.json','references/production.json','scripts/dcc_cli.py'):
            self.assertTrue((self.project/'.game-design'/item).is_file())

    def test_new_profile_fields_validated(self):
        self.install();path=self.project/'.game-design/state/project.json';original=json.loads(path.read_text())
        for field,value in [('genres',['missing']),('genres',['roguelike','roguelike']),('dimension','any'),
                            ('multiplayer','everyone'),('content_pipeline',['not-a-pipeline'])]:
            state=copy.deepcopy(original);state[field]=value;path.write_text(json.dumps(state))
            with self.assertRaises(ValueError):check_project(self.project,load_catalog())

    def assets(self):
        source=self.project/'Art/model.blend';source.parent.mkdir();source.write_bytes(b'fixture source, not a real blend')
        output=self.project/'Art/model.glb';output.write_bytes(b'fixture export, not a real glb')
        report=self.project/'review.txt';report.write_text('fixture evidence reference, not a real review')
        sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        record={'id':'ASSET-TEST','source':'Art/model.blend','source_sha256':sha(source),
                'exports':[{'path':'Art/model.glb','sha256':sha(output)}],'license':'fixture',
                'engine_import':{'status':'pass','evidence':['review.txt']},'review':{'status':'pass','evidence':['review.txt']}}
        path=self.project/'assets.json';path.write_text(json.dumps({'schema_version':1,'assets':[record]}))
        return path,record

    def test_asset_file_only_checks_do_not_claim_runtime_pass(self):
        path,record=self.assets();before=snapshot(self.project)
        result=asset_checks.inspect(self.project,path)
        self.assertEqual(result['status'],'files_verified')
        self.assertEqual(result['runtime_validation'],'not_run')
        self.assertEqual(snapshot(self.project),before)

    def test_asset_missing_hash_and_reviews_are_pending(self):
        path,record=self.assets();record['source_sha256']=None;record['review']={'status':'not_run','evidence':[]}
        path.write_text(json.dumps({'schema_version':1,'assets':[record]}))
        result=asset_checks.inspect(self.project,path)
        self.assertEqual(result['status'],'pending');self.assertTrue(result['pending'])

    def test_asset_mismatch_missing_file_evidence_and_fail(self):
        path,record=self.assets()
        for kind in ('hash','missing','evidence','fail'):
            changed=copy.deepcopy(record)
            if kind=='hash':changed['source_sha256']='0'*64
            if kind=='missing':changed['exports'][0]['path']='Art/absent.glb'
            if kind=='evidence':changed['review']['evidence']=[]
            if kind=='fail':changed['review']['status']='fail'
            path.write_text(json.dumps({'schema_version':1,'assets':[changed]}))
            self.assertEqual(asset_checks.inspect(self.project,path)['status'],'failed')

    def test_asset_traversal_duplicate_and_overwrite_rejected(self):
        path,record=self.assets()
        for kind in ('escape','duplicate','overwrite','na'):
            data={'schema_version':1,'assets':[copy.deepcopy(record)]};entry=data['assets'][0]
            if kind=='escape':entry['exports'][0]['path']='../outside.glb'
            if kind=='duplicate':data['assets'].append(copy.deepcopy(record))
            if kind=='overwrite':entry['exports'][0]['path']=entry['source']
            if kind=='na':entry['review']={'status':'not_applicable','evidence':[]}
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):asset_checks.inspect(self.project,path)

    def test_asset_symlinks_rejected(self):
        path,record=self.assets();source=self.project/'Art/model.blend';source.unlink();outside=self.base/'external'
        outside.write_bytes(b'external');source.symlink_to(outside)
        with self.assertRaises(ValueError):asset_checks.inspect(self.project,path)

    def repo(self):
        for args in [('init','.'),('config','user.email','fixture@example.invalid'),('config','user.name','Fixture')]:
            result=self.command('git',*args,cwd=self.project);self.assertEqual(result.returncode,0,result.stderr)
        (self.project/'Art').mkdir();(self.project/'Art/model.blend').write_bytes(b'test source'*100)
        (self.project/'Library').mkdir();(self.project/'Library/cache').write_text('tracked cache fixture')
        for args in [('add','.'),('commit','-m','fixture baseline')]:
            result=self.command('git','-c','core.hooksPath=/dev/null',*args,cwd=self.project);self.assertEqual(result.returncode,0,result.stderr)

    def test_version_check_read_only_flags_cache_and_binary(self):
        self.repo();before=snapshot(self.project)
        result=version_check.inspect(self.project,0.0001)
        self.assertIn('Library/cache',result['tracked_caches'])
        self.assertIn('Art/model.blend',result['large_binaries_without_lfs'])
        self.assertIn('Art/model.blend',result['single_writer_candidates'])
        self.assertEqual(snapshot(self.project),before)
        self.assertFalse(any('push' in r['command'] or 'fetch' in r['command'] for r in result['commands']))

    def test_version_missing_repo_does_not_initialize(self):
        before=snapshot(self.project);result=version_check.inspect(self.project,10)
        self.assertEqual(result['status'],'not_versioned');self.assertEqual(snapshot(self.project),before)
        self.assertFalse((self.project/'.git').exists())

    def test_version_unborn_head_is_pending_not_literal_HEAD(self):
        result=self.command('git','init','.',cwd=self.project);self.assertEqual(result.returncode,0,result.stderr)
        before=snapshot(self.project);result=version_check.inspect(self.project,10)
        self.assertIsNone(result['head'])
        self.assertTrue(any('initial commit' in p for p in result['pending']))
        self.assertEqual(snapshot(self.project),before)

    def test_nested_target_source_is_not_flagged_as_cache(self):
        self.repo();source=self.project/'Assets/target/model.blend';source.parent.mkdir(parents=True)
        source.write_bytes(b'authored source fixture')
        result=self.command('git','add','Assets',cwd=self.project);self.assertEqual(result.returncode,0,result.stderr)
        result=version_check.inspect(self.project,10)
        self.assertNotIn('Assets/target/model.blend',result['tracked_caches'])

    def test_version_metadata_and_bad_limit(self):
        self.repo();path=self.project/'.game-design/state/version.json';path.parent.mkdir(parents=True)
        state={'schema_version':1,**{key:'fixture' for key in version_check.VERSION_FIELDS}}
        path.write_text(json.dumps(state))
        result=version_check.inspect(self.project,10)
        self.assertTrue(any('source_commit' in warning for warning in result['warnings']))
        state['build_id']=False;path.write_text(json.dumps(state))
        with self.assertRaises(ValueError):version_check.inspect(self.project,10)
        result=self.command(sys.executable,HOME/'scripts/version_check.py','--project',self.project,'--large-mb','0')
        self.assertEqual(result.returncode,2)

if __name__=='__main__':unittest.main()
