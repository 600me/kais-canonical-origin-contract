import importlib.util
import unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location('canonical', Path(__file__).resolve().parents[1] / 'check_canonical.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Contract(unittest.TestCase):
    def check(self, tags, page='https://preview.example/products/a', expected='https://production.example'):
        return m.evaluate('<html><head>'+tags+'</head><body></body></html>',page,expected)
    def test_explicit_production_canonical_passes(self):
        self.assertTrue(self.check('<link rel="canonical" href="https://production.example/products/a">')['passed'])
    def test_preview_host_blocks(self):
        self.assertFalse(self.check('<link rel="canonical" href="https://preview.example/products/a">')['passed'])
    def test_missing_blocks(self):
        self.assertFalse(self.check('<title>Product</title>')['passed'])
    def test_duplicates_block_even_if_equal(self):
        self.assertFalse(self.check('<link rel="canonical" href="https://production.example/a">'*2)['passed'])
    def test_relative_canonical_uses_preview_origin(self):
        self.assertFalse(self.check('<link rel="canonical" href="/products/a">')['passed'])
    def test_scheme_relative_resolves(self):
        self.assertTrue(self.check('<link rel="alternate CANONICAL" href="//production.example/a">')['passed'])
    def test_base_affects_relative_resolution(self):
        self.assertTrue(self.check('<base href="https://production.example/catalog/"><link rel="canonical" href="a">')['passed'])
    def test_multiple_base_urls_block(self):
        self.assertFalse(self.check('<base href="https://production.example"><base href="https://preview.example"><link rel="canonical" href="/a">')['passed'])
    def test_credentials_fragments_and_bad_ports_block(self):
        for value in ['https://u:secret@production.example/a','https://production.example/a#part','https://production.example:broken/a','javascript:alert(1)','https://production.example.evil/a','http://production.example/a','https://production.example:444/a','https://production.example:0/a']:
            with self.subTest(value=value): self.assertFalse(self.check(f'<link rel="canonical" href="{value}">')['passed'])
    def test_origin_requires_exact_contract(self):
        for origin in ['https://production.example/path','https://production.example/?x=1','https://u:p@production.example','https://production.example#frag','not-url']:
            with self.subTest(origin=origin): self.assertFalse(self.check('<link rel="canonical" href="https://production.example/a">',expected=origin)['passed'])
    def test_default_port_and_case_normalized(self):
        self.assertTrue(self.check('<link rel="canonical" href="https://PRODUCTION.example:443/a">')['passed'])
    def test_body_canonical_is_not_head_contract(self):
        self.assertFalse(m.evaluate('<html><head></head><body><link rel="canonical" href="https://production.example/a"></body></html>','https://preview.example/a','https://production.example')['passed'])
    def test_script_text_does_not_count_as_canonical(self):
        self.assertFalse(self.check('<script>var x=\'<link rel="canonical" href="https://production.example/a">\'</script>')['passed'])
    def test_empty_href_blocks(self):
        self.assertFalse(self.check('<link rel="canonical" href="">')['passed'])
    def test_empty_or_oversized_document_blocks(self):
        self.assertFalse(m.evaluate('', 'https://preview.example/a', 'https://production.example')['passed'])
        self.assertFalse(self.check('x'*(2*1024*1024)+'<link rel="canonical" href="https://production.example/a">')['passed'])

if __name__ == '__main__': unittest.main()
