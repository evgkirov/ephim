import unittest

import piexif

from ephim.library import Library, Photo, Masters
from .utils.fs import Tree, YamlFile, JpegFile

tree = Tree({
    'library.yaml': YamlFile({}),
    'masters': {
        '2014-02 Vacation': {
            'My photos': {
                'metadata.yaml': YamlFile({
                    'first': {
                        'title': 'Hooray!',
                    },
                }),
                'first.jpg': JpegFile({
                    piexif.ExifIFD.DateTimeOriginal: '2014:02:12 12:34:56',
                }),
                'second.jpg': JpegFile({
                    piexif.ExifIFD.DateTimeOriginal: '2014:02:14 12:34:56',
                }),
                'noexif.jpg': JpegFile(),
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


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.base = tree.populate()

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


class MastersTests(unittest.TestCase):
    def setUp(self):
        self.base = tree.populate()
        self.my_photos_path = self.base / 'masters' / '2014-02 Vacation' / 'My photos'

    def test_photos_discovery(self):
        masters = Masters(self.my_photos_path)
        expected_paths = map(str, [
            self.my_photos_path / 'first.jpg',
            self.my_photos_path / 'second.jpg',
            self.my_photos_path / 'noexif.jpg',
        ])
        paths = map(lambda p: str(p.location), masters.discover_photos())
        self.assertSequenceEqual(sorted(expected_paths), sorted(paths))

class PhotoTests(unittest.TestCase):
    def setUp(self):
        self.base = tree.populate()
        self.my_photos_path = self.base / 'masters' / '2014-02 Vacation' / 'My photos'

    def test_filename_with_title(self):
        photo = Photo(self.my_photos_path / 'first.jpg')
        self.assertEqual(photo.new_filename, '2014-02-12 12.34.56 Hooray!.jpg')

    def test_filename_without_title(self):
        photo = Photo(self.my_photos_path / 'second.jpg')
        self.assertEqual(photo.new_filename, '2014-02-14 12.34.56.jpg')

    def test_filename_without_exif(self):
        photo = Photo(self.my_photos_path / 'noexif.jpg')
        self.assertEqual(photo.new_filename, '0000-00-00 00.00.00.jpg')
