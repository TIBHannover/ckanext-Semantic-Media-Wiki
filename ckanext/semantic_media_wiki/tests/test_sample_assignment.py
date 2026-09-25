"""Isolated save/edit regression tests; no live CKAN, database or SMW required.

Run with: python -m unittest discover -s ckanext/semantic_media_wiki/tests -p test_sample_assignment.py
"""
import importlib.util
from pathlib import Path
from types import SimpleNamespace, ModuleType
import sys
import unittest
from unittest.mock import Mock, patch


class Form(dict):
    def getlist(self, key):
        return self.get(key, [])


class Record:
    records = []

    def __init__(self, resource_id=None, sample_url=None, sample_name=None, *args, **kwargs):
        self.resource_id = resource_id
        self.sample_url = sample_url
        self.sample_name = sample_name
        self.deleted = False

    def save(self):
        self.records.append(self)

    def commit(self):
        pass

    def delete(self):
        self.deleted = True
        self.records.remove(self)

    def get_by_resource(self, id):
        return [record for record in self.records if record.resource_id == id]

    def get_by_resource_sample(self, id, sample_url):
        return next((record for record in self.records
                     if record.resource_id == id and record.sample_url == sample_url), None)


class SampleAssignmentTest(unittest.TestCase):
    def setUp(self):
        # Load only the production helper, with CKAN and persistence boundaries stubbed.
        names = ['ckan', 'ckan.plugins', 'ckan.plugins.toolkit',
                 'ckanext.semantic_media_wiki.libs.media_wiki_api',
                 'ckanext.semantic_media_wiki.models.resource_sample_link']
        modules = {name: ModuleType(name) for name in names}
        modules[names[-2]].API = Mock()
        modules[names[-1]].ResourceSampleLink = Record
        modules['ckan.plugins.toolkit'].get_action = Mock(return_value=Mock())
        source = Path(__file__).parents[1] / 'libs' / 'sample_link.py'
        spec = importlib.util.spec_from_file_location('isolated_sample_link', source)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, modules):
            spec.loader.exec_module(module)
        self.helper = module.SampleLinkHelper
        self.available = ['A0001', 'X0005', 'X0006', 'X0008', 'X0010', 'X0011', 'X0012', 'B0045']
        self.helper.get_samples_list = Mock(return_value=[
            {'value': self.url(name), 'text': name} for name in self.available])
        Record.records = []
        self.package = {'resources': [{'id': 'r1'}, {'id': 'r2'}]}

    @staticmethod
    def url(name):
        return 'https://wiki/' + name

    def request(self, names, editing=False):
        form = Form()
        for i, name in enumerate(names, 1):
            form['sample_link' + str(i)] = self.url(name) if name else ''
            form['sample_name_' + str(i)] = name
            form['sample_resources_list' + str(i)] = [
                'r1' + ('@@@' + self.url(name) if editing else '')] if name else []
        return SimpleNamespace(form=form)

    def test_individual_and_range_values_use_existing_contract(self):
        self.assertTrue(self.helper.add_sample_links(self.request(self.available), len(self.available) + 1))
        self.assertEqual([record.sample_url for record in Record.records], [self.url(n) for n in self.available])
        self.helper.get_samples_list.assert_called_once()

    def test_duplicate_sample_resource_pairs_are_not_added(self):
        self.assertTrue(self.helper.add_sample_links(self.request(['X0005', 'X0005']), 3))
        self.assertEqual(len(Record.records), 1)

    def test_fabricated_sample_rejected_before_any_writes(self):
        self.assertFalse(self.helper.add_sample_links(self.request(['X0005', 'X0007']), 3))
        self.assertEqual(Record.records, [])

    def test_empty_selection_is_safe(self):
        self.assertTrue(self.helper.add_sample_links(self.request(['']), 2))
        self.assertEqual(Record.records, [])

    def test_edit_preserves_records_and_merges_new_range(self):
        original = Record('r1', self.url('A0001'), 'A0001')
        later = Record('r1', self.url('B0045'), 'B0045')
        original.save()
        later.save()
        request = self.request(['A0001', 'X0005', 'X0006', 'B0045'], editing=True)
        self.assertTrue(self.helper.update_resource_sample(request, 5, self.package))
        self.assertIn(original, Record.records)
        self.assertIn(later, Record.records)
        self.assertFalse(later.deleted)
        self.assertEqual(len(Record.records), 4)
        self.assertEqual(self.helper.get_sample_link('r1')['X0006'], self.url('X0006'))

    def test_edit_keeps_retired_stored_samples_without_smw(self):
        original = Record('r1', self.url('retired'), 'retired')
        original.save()
        self.helper.get_samples_list.return_value = []
        self.assertTrue(self.helper.update_resource_sample(self.request(['retired'], editing=True), 2, self.package))
        self.assertEqual(Record.records, [original])
        self.helper.get_samples_list.assert_not_called()

    def test_invalid_edit_does_not_delete_existing_relationships(self):
        original = Record('r1', self.url('A0001'), 'A0001')
        original.save()
        self.assertFalse(self.helper.update_resource_sample(self.request(['X0007']), 2, self.package))
        self.assertEqual(Record.records, [original])

    def test_clear_all_removes_existing_relationships(self):
        Record('r1', self.url('A0001'), 'A0001').save()
        self.assertTrue(self.helper.update_resource_sample(self.request(['']), 2, self.package))
        self.assertEqual(Record.records, [])


if __name__ == '__main__':
    unittest.main()
