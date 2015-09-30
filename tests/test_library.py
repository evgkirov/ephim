import unittest

from ephim.library import Library
from .utils.fs import Tree, YamlFile


class LibraryTests(unittest.TestCase):
    tree = Tree({
        'library.yaml': YamlFile({}),
        'masters': {
            '2014-02 Vacation': {
                'My photos': {
                    'metadata.yaml': YamlFile({}),
                },
                'Not my photos': {
                    'metadata.yaml': YamlFile({}),
                },
            },
            '2015-01 New Year': {
                'metadata.yaml': YamlFile({}),
            },
            'Nothing here': {},
        },
    })

    def setUp(self):
        self.base = self.tree.populate()

    def test_find_library(self):
        self.assertEqual(Library.find_library(self.base), self.base)
        self.assertEqual(Library.find_library(self.base / 'masters'), self.base)

    def test_library_not_found(self):
        base = Tree.create({})
        self.assertRaises(FileNotFoundError, Library.find_library, base)

    def test_library_init(self):
        library = Library(self.base)
        self.assertEqual(self.base, library.location)
        self.assertTrue(library.location.is_dir())
        self.assertTrue(library.masters_location.is_dir())
        self.assertEqual(self.base / 'masters', library.masters_location)

    def test_masters_discovery(self):
        library = Library(self.base)
        expected_paths = map(str, [
            library.masters_location / '2014-02 Vacation' / 'My photos',
            library.masters_location / '2014-02 Vacation' / 'Not my photos',
            library.masters_location / '2015-01 New Year',
        ])
        paths = map(lambda m: str(m.location), library.discover_masters())
        self.assertSequenceEqual(sorted(expected_paths), sorted(paths))
