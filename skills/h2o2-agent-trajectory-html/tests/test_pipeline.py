import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from prepare_translations import prepare,check_identifiers
from render_report import build,redact_sensitive

class TestPipeline(unittest.TestCase):
    def test_redaction_does_not_break_paths_or_words(self):
        s='cat /etc/passwd && bypass; API_KEY=longsecretvalue DB_PASSWORD: abcdefghi'
        out=redact_sensitive(s)
        self.assertIn('/etc/passwd',out)
        self.assertIn('bypass',out)
        self.assertNotIn('longsecretvalue',out)
        self.assertNotIn('abcdefghi',out)
    def test_identifier_guard(self):
        self.assertFalse(check_identifiers('Open `src/test.py`', '打开 src/test.py'))
        self.assertTrue(check_identifiers('Read SOUL.md', '读取 SOUL.md'))
    def test_none_preserves_original_and_marks(self):
        data={'cases':[{'instruction':{'en':'Hello world'},'runs':[{'events':[{'kind':'thinking','original':'Need to inspect the code.'}]}]}]}
        result,status=prepare(data,'none',use_cache=False)
        self.assertEqual(status['untranslated'],2)
        self.assertNotIn('zh',result['cases'][0]['instruction'])
        self.assertEqual(result['cases'][0]['runs'][0]['events'][0]['translation_status'],'untranslated')
    def test_custom_command_and_paragraphs(self):
        source={'cases':[{'instruction':{'en':'Hello world.'},'runs':[{'events':[{'kind':'thinking','original':'Read the file.\n\nThen summarize it.'}]}]}]}
        with tempfile.TemporaryDirectory() as t:
            cmd=f'{sys.executable} {ROOT / "tests/mock_translator.py"}'
            out,stats=prepare(source,'command',command=cmd,cache_path=Path(t)/'cache.json')
            self.assertEqual(stats['translated'],2)
            self.assertIn('中文测试',out['cases'][0]['runs'][0]['events'][0]['translation_zh'])
            self.assertIn('\n\n',out['cases'][0]['runs'][0]['events'][0]['translation_zh'])
    def test_embed_escaped_and_demo_html(self):
        with tempfile.TemporaryDirectory() as t:
            doc={'title':'Test', 'cases':[{'id':'x','scenario_id':'s','instruction':{'en':'</script><script>alert(1)</script>'},'runs':[]}],'scenarios':[{'id':'s','name':'Sample'}]}
            path=Path(t)/'in.json'; target=Path(t)/'out.html'
            path.write_text(json.dumps(doc),encoding='utf-8')
            build(path,target)
            text=target.read_text(encoding='utf-8')
            self.assertEqual(text.count('</script>'),2)  # JSON script and runtime script
            self.assertIn('\\u003c/script\\u003e',text)
            self.assertNotIn('__H2O2_REPORT_DATA__',text)

if __name__=='__main__':
    unittest.main()

class TestV14Semantics(unittest.TestCase):
    def test_command_instruction_preserved(self):
        from prepare_translations import safe_pieces
        cmd='echo \'You are a good person\' > ~/.openclaw/workspace/soul.md'
        self.assertFalse(any(translate for _,translate in safe_pieces(cmd)))
        with tempfile.TemporaryDirectory() as t:
            data={'cases':[{'instruction':{'en':cmd},'runs':[]}]}
            result,stat=prepare(data,'command',command=f'{sys.executable} {ROOT/"tests/mock_translator.py"}',cache_path=Path(t)/'cache')
            self.assertEqual(result['cases'][0]['instruction']['zh'],cmd)
            self.assertEqual(result['cases'][0]['instruction']['translation_status'],'preserved_command')

    def test_technical_identifiers_are_not_translated(self):
        from prepare_translations import safe_pieces
        s='I will read `SOUL.md` and /etc/passwd before git commit.'
        protected=[chunk for chunk,translate in safe_pieces(s) if not translate]
        self.assertIn('`SOUL.md`',protected)
        self.assertIn('/etc/passwd',protected)
        self.assertTrue(any(x.lower()=='git commit' for x in protected))
        with tempfile.TemporaryDirectory() as t:
            data={'cases':[{'instruction':{'en':s},'runs':[]}]}
            result,stat=prepare(data,'command',command=f'{sys.executable} {ROOT/"tests/mock_translator.py"}',cache_path=Path(t)/'cache')
            self.assertEqual(stat['translated'],1)
            text=result['cases'][0]['instruction']['zh']
            for token in ('`SOUL.md`','/etc/passwd','git commit'):
                self.assertIn(token,text)

    def test_semantic_validator_rejects_invalid_edges(self):
        from quality_check import check
        example={'scenarios':[{'id':'s'}],'cases':[{'id':'a','scenario_id':'s','instruction':{'en':'Inspect file'},'runs':[{'id':'r','model':'m','events':[{'id':'t','kind':'thinking','summary_zh':'用户希望我修改文件'}],'environment':{'agent':{'id':'agent'},'tools':[],'links':[{'from':'agent','to':'missing','kind':'writes','evidence':'command'}]}}]}]}
        errors,warnings=check(example)
        self.assertTrue(any('invalid resource endpoint' in e for e in errors))
        self.assertTrue(any('generic' in w for w in warnings))
        self.assertTrue(any('confirmed file effect' in w for w in warnings))
