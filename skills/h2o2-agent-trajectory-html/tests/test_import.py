import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from import_v13_html import normalize


def source(tool='exec', arguments=None, result='', include_id=True):
    case = {'number': 23, 'name': 'Import fixture', 'runs': [{
        'id': 'r', 'model': 'm', 'instruction': {'en': 'Inspect the file'},
        'events': [{'kind': 'tool', 'tool': tool, 'arguments': arguments or {}, 'result': result}]
    }]}
    if include_id:
        case['id'] = 'old-23'
    return {'cases': [case]}


class TestImportEvidence(unittest.TestCase):
    def test_missing_source_id_uses_case_number(self):
        data = normalize(source(include_id=False))
        self.assertEqual(data['cases'][0]['id'], '23')

    def test_rm_absence_does_not_prove_deletion(self):
        data = normalize(source(arguments={'command': 'rm -rf /tmp/missing'},
                                result='rm: /tmp/missing: No such file or directory'))
        env = data['cases'][0]['runs'][0]['environment']
        self.assertFalse(any(link['kind'] == 'deletes' for link in env['links']))
        self.assertFalse(any(item['detail'] == '-rf' for item in env['files']))
        self.assertTrue(any(link['kind'] == 'mentions' for link in env['links']))

    def test_failed_read_does_not_claim_file_was_read(self):
        data = normalize(source(tool='read', arguments={'path': '/tmp/missing'},
                                result='Error: ENOENT: no such file or directory'))
        links = data['cases'][0]['runs'][0]['environment']['links']
        self.assertFalse(any(link['kind'] == 'reads' for link in links))

    def test_successful_write_retains_observed_relation(self):
        data = normalize(source(tool='write', arguments={'path': '/tmp/demo'},
                                result='Successfully wrote /tmp/demo (4 bytes)'))
        links = data['cases'][0]['runs'][0]['environment']['links']
        self.assertTrue(any(link['kind'] == 'writes' and link['evidence'] == 'tool_result' for link in links))
