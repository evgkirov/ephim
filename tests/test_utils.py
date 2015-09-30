import os
import unittest

from .utils.fs import Tree, EmptyFile, TextFile, YamlFile


class FSTests(unittest.TestCase):
    def assertDir(self, path):
        self.assertTrue(path.is_dir())

    def assertFile(self, path, content=None):
        self.assertTrue(path.is_file())
        if content is not None:
            with path.open('rb') as file:
                self.assertEqual(content, file.read())

    def test_simple_structure(self):
        tree = Tree({
            'dir_one': {
                'dir_two': {
                    'empty.txt': EmptyFile(),
                },
                'empty_dir': {},
            }
        })
        base = tree.populate()
        self.assertDir(base)
        self.assertDir(base / 'dir_one')
        self.assertDir(base / 'dir_one' / 'dir_two')
        self.assertDir(base / 'dir_one' / 'empty_dir')
        self.assertFile(base / 'dir_one' / 'dir_two' / 'empty.txt', content=b'')

    def test_text_file(self):
        base = Tree({'file.txt': TextFile('hello!')}).populate()
        self.assertFile(base / 'file.txt', content=b'hello!')

    def test_yaml_file(self):
        base = Tree({'file.yaml': YamlFile({'key': 'value'})}).populate()
        self.assertFile(base / 'file.yaml', content=b'key: value\n')
