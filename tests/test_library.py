import os
import unittest

from ephim.library import Library
from .utils.fs import Tree, YamlFile


class LibraryTests(unittest.TestCase):
    def test_find_library(self):
        base = Tree.create({
            'library.yaml': YamlFile({}),
            'subdirectory': {},
        })
        self.assertEqual(str(Library.find_library(base)), base)
        self.assertEqual(str(Library.find_library(os.path.join(base, 'subdirectory'))), base)

    def test_library_not_found(self):
        base = Tree.create({})
        self.assertRaises(FileNotFoundError, Library.find_library, base)
