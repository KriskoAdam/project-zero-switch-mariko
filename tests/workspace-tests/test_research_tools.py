import hashlib, importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
class ResearchToolsTests(unittest.TestCase):
 def test_manifest_hash_and_sensitive_filter(self):
  m=load('create_sha256_manifest')
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); (root/'ok.txt').write_text('abc'); (root/'title.keys').write_text('secret'); (root/'sub').mkdir(); (root/'sub'/'b').write_bytes(b'123')
   rows=list(m.iter_files(root)); self.assertEqual([p.name for p in rows],['ok.txt','b']); self.assertEqual(m.digest(root/'ok.txt'),hashlib.sha256(b'abc').hexdigest())
 def test_compare_manifest(self):
  m=load('compare_manifests')
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); a=root/'a.json'; b=root/'b.json'
   a.write_text(json.dumps({'files':[{'path':'same','sha256':'a'},{'path':'gone','sha256':'b'}]})); b.write_text(json.dumps({'files':[{'path':'same','sha256':'c'},{'path':'new','sha256':'d'}]}))
   x,y=m.load(a),m.load(b); states={}
   for k in sorted(x.keys()|y.keys()): states[k]='added' if k not in x else 'removed' if k not in y else 'changed' if x[k].get('sha256')!=y[k].get('sha256') else 'unchanged'
   self.assertEqual(states,{'gone':'removed','new':'added','same':'changed'})
 def test_capstone_arm64_decode(self):
  from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
  md=Cs(CS_ARCH_ARM64,CS_MODE_ARM); ins=list(md.disasm(bytes.fromhex('1f0000aac0035fd6'),0x1000)); self.assertEqual([i.mnemonic for i in ins],['orr','ret'])
 def test_vulnerability_database_schema(self):
  d=json.loads((ROOT/'reports/vulnerabilities.json').read_text()); required={'id','component','affected_hardware','affected_firmware_versions','fixed_firmware_versions','required_access_level','arbitrary_code_execution_documented','privilege_escalation_documented','applicable_to_mariko','primary_source','evidence_confidence'}
  self.assertGreaterEqual(len(d['vulnerabilities']),10)
  for row in d['vulnerabilities']:
   self.assertTrue(required.issubset(row)); self.assertTrue(row['primary_source']); self.assertTrue(all(x in d['sources'] for x in row['primary_source']))
 def test_elf_metadata_parse(self):
  m=load('inspect_binary_metadata')
  import struct
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'arm64.elf'; ident=b'\x7fELF'+bytes([2,1,1,0])+bytes(8); header=struct.pack('<HHIQQQIHHHHHH',2,183,1,0x400078,64,128,0,64,56,1,64,1,0); phdr=struct.pack('<IIQQQQQQ',1,5,120,0x400078,0,4,4,4); f.write_bytes(ident+header+phdr+bytes.fromhex('c0035fd6')+bytes(4)+bytes(64))
   result=m.inspect(f); self.assertEqual(result['format'],'ELF'); self.assertIn('AARCH64',result['architectures'][0])
 def test_metadata_hash_unknown_file(self):
  m=load('inspect_binary_metadata')
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'plain'; f.write_bytes(b'not an executable'); result=m.inspect(f); self.assertEqual(result['sha256'],hashlib.sha256(f.read_bytes()).hexdigest()); self.assertEqual(result['format'],'unknown')
if __name__=='__main__': unittest.main()
