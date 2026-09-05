"""Small synthetic checks for helpers; no real manuscript data."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


LINT_PATH = ROOT / 'skills/paper-revision-prefs/scripts/revision_lint.py'
SVG_PATH = ROOT / 'skills/scientific-diagram/scripts/check_svg.py'
LINT = module(LINT_PATH, 'revision_lint')
SVG = module(SVG_PATH, 'check_svg')
EXAMPLE = ROOT / 'skills/scientific-diagram/examples/synthetic-workflow.svg'
SPEC = json.loads(EXAMPLE.with_suffix('.json').read_text(encoding='utf-8'))


class Helpers(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def put(self, name, text):
        p = self.root / name
        p.write_text(text, encoding='utf-8')
        return p

    def test_excerpt_keeps_existing_numbers(self):
        p = self.put('excerpt.md', '合成材料分别支持两项功能[7][8]。')
        self.assertEqual(LINT.inspect(p)['findings'], [])

    def test_renumbering_is_reported_without_writing(self):
        old = self.put('old.md', '合成描述[7][8]。')
        new = self.put('new.md', '合成描述[1][2]。')
        before = new.read_bytes()
        result = LINT.inspect(new, baseline=old)
        self.assertIn('citation-change', {f['category'] for f in result['findings']})
        self.assertEqual(new.read_bytes(), before)

    def test_supported_full_references_and_ranges(self):
        p = self.put('full.md', '合成描述[1-2]。\n\n## References\n[1] 合成来源甲。\n[2] 合成来源乙。')
        self.assertEqual(LINT.inspect(p, scope='full', numbering='sequential')['findings'], [])

    def test_comments_and_code_are_not_citations(self):
        p = self.put('code.md', '<!-- [90] -->\n合成描述[7]。\n\n```text\n[20]\n```\n`[30]`')
        self.assertEqual(LINT.inspect(p)['descriptive_only']['numeric_citation_occurrences'], 1)

    def test_overlapping_terminology_is_not_a_false_pair(self):
        p = self.put('terms.md', '合成描述使用传输通道。')
        self.assertEqual(LINT.inspect(p, terms={'名称':['传输通道','通道']})['findings'], [])

    def test_missing_reference_and_image_are_clues(self):
        p = self.put('missing.md', '合成描述[8]。\n![合成图](missing.svg)\n\n## 参考文献\n[7] 合成来源。')
        kinds = {x['category'] for x in LINT.inspect(p, scope='full')['findings']}
        self.assertTrue({'references','image-path'} <= kinds)

    def test_exit_status_distinguishes_input_from_findings(self):
        p = self.put('finding.md', '合成描述[8]。\n\n## 参考文献\n[7] 合成来源。')
        run = subprocess.run([sys.executable,str(LINT_PATH),str(p),'--scope','full'],capture_output=True,text=True,timeout=15)
        self.assertEqual(run.returncode, 0)
        self.assertTrue(json.loads(run.stdout)['findings'])
        fail = subprocess.run([sys.executable,str(LINT_PATH),str(self.root/'absent.md')],capture_output=True,text=True,timeout=15)
        self.assertEqual(fail.returncode, 2)

    def test_svg_exact_labels_and_declared_edges(self):
        self.assertEqual(SVG.inspect(EXAMPLE,grayscale=True,spec=SPEC)['findings'], [])

    def test_svg_detects_label_edge_and_color_changes(self):
        data = EXAMPLE.read_text(encoding='utf-8').replace('>材料</text>','>错误标签</text>')
        data = data.replace('data-target="summary"','data-target="material"').replace('#F3F3F3','#FF0000')
        p = self.put('bad.svg',data)
        findings = SVG.inspect(p,grayscale=True,spec=SPEC)['findings']
        self.assertTrue(any('labels' in x for x in findings))
        self.assertTrue(any('endpoints' in x for x in findings))
        self.assertTrue(any('non-grayscale' in x for x in findings))

    def test_svg_external_resource_requires_review(self):
        data = EXAMPLE.read_text(encoding='utf-8').replace('</svg>','<image href="https://example.org/image.png"/></svg>')
        p = self.put('resource.svg',data)
        self.assertTrue(any('resource' in x for x in SVG.inspect(p)['findings']))


if __name__ == '__main__':
    unittest.main()
