import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CLI(unittest.TestCase):
    def run_check(self,path):
        return subprocess.run([sys.executable,str(ROOT/'check_canonical.py'),'--html-file',str(path),'--page-url','https://preview.example/products/widget','--expected-origin','https://production.example'],capture_output=True,text=True)
    def test_fixture_pass_exit_zero(self):
        p=self.run_check(ROOT/'fixtures/production.html');self.assertEqual(p.returncode,0);self.assertEqual(json.loads(p.stdout),{'passed':True,'code':'ORIGIN_MATCH'})
    def test_preview_regression_exit_one(self):
        p=self.run_check(ROOT/'fixtures/preview.html');self.assertEqual(p.returncode,1);self.assertEqual(json.loads(p.stdout),{'passed':False,'code':'ORIGIN_MISMATCH'})
    def test_missing_file_exit_one_without_path_or_secret_leak(self):
        p=self.run_check(ROOT/'missing-secret-token.html');self.assertEqual(p.returncode,1);self.assertEqual(json.loads(p.stdout)['code'],'UNREADABLE_HTML');self.assertNotIn('secret',p.stdout+p.stderr)
    def test_invalid_utf8_and_oversize_block(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'sample.html'
            for content in [b'\xff',b'x'*(2*1024*1024+1)]:
                path.write_bytes(content);p=self.run_check(path);self.assertEqual(p.returncode,1);self.assertEqual(json.loads(p.stdout)['code'],'UNREADABLE_HTML')
    def test_missing_arguments_block(self):
        p=subprocess.run([sys.executable,str(ROOT/'check_canonical.py')],capture_output=True,text=True);self.assertEqual(p.returncode,2)
if __name__=='__main__':unittest.main()
