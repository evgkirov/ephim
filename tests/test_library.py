from datetime import datetime, date
import unittest

from piexif import ImageIFD, ExifIFD

from ephim.library import Library, Photo, Masters, Event
from ephim.utils import datetime_to_string
from tests.utils.fs import Tree, YamlFile, JpegFile


class LibraryTests(unittest.TestCase):
    def test_find_library(self):
        base = Tree.create({
            'library.yaml': YamlFile(),
            'some_dir': {},
        })
        self.assertEqual(Library.find_library(base), base)
        self.assertEqual(Library.find_library(base / 'some_dir'), base)

    def test_library_not_found(self):
        base = Tree.create({})
        self.assertRaises(FileNotFoundError, Library.find_library, base)

    def test_library_init(self):
        base = Tree.create({
            'library.yaml': YamlFile(),
            'masters': {},
        })
        library = Library(base)
        self.assertEqual(base, library.location)
        self.assertTrue(library.location.is_dir())
        self.assertTrue(library.masters_location.is_dir())
        self.assertEqual(base / 'masters', library.masters_location)

    def test_masters_discovery(self):
        base = Tree.create({
            'library.yaml': YamlFile(),
            'masters': {
                '2014-02 Vacation': {
                    'My photos': {
                        '_metadata.yaml': YamlFile(),
                    },
                    'Not my photos': {
                        '_metadata.yaml': YamlFile(),
                    },
                },
                '2015-01 New Year': {
                    '_metadata.yaml': YamlFile(),
                },
                'Nothing here': {},
            }
        })
        library = Library(base)
        expected_paths = map(str, [
            library.masters_location / '2014-02 Vacation' / 'My photos',
            library.masters_location / '2014-02 Vacation' / 'Not my photos',
            library.masters_location / '2015-01 New Year',
        ])
        paths = map(lambda m: str(m.location), library.discover_masters())
        self.assertSequenceEqual(sorted(expected_paths), sorted(paths))


class MastersTests(unittest.TestCase):
    def test_photos_discovery(self):
        path = Tree.create({
            '_metadata.yaml': YamlFile(),
            'first.jpg': JpegFile(),
            'second.jpg': JpegFile(),
            'CAPS.JPEG': JpegFile(),
        })

        masters = Masters(path)
        expected_paths = map(str, [
            path / 'first.jpg',
            path / 'second.jpg',
            path / 'CAPS.JPEG',
        ])
        paths = map(lambda p: str(p.location), masters.discover_photos())
        self.assertSequenceEqual(sorted(expected_paths), sorted(paths))


class PhotoTests(unittest.TestCase):
    def test_filename_with_date_from_0th_and_title_from_yaml(self):
        path = Tree.create({
            '_metadata.yaml': YamlFile({
                'photo': {
                    'title': 'Hooray!'
                },
            }),
            'photo.jpg': JpegFile({
                '0th': {
                    ImageIFD.DateTime: '2014:02:12 01:00:00'
                },
            }),
        })
        photo = Photo(path / 'photo.jpg')
        self.assertEqual(photo.new_filename(counter=0), 'CFL_036000 - Hooray!.jpg')

    def test_filename_with_date_from_exif(self):
        path = Tree.create({
            '_metadata.yaml': YamlFile(),
            'photo.jpg': JpegFile({
                'Exif': {
                    ExifIFD.DateTimeOriginal: '2014:02:12 01:00:00'
                },
            }),
        })
        photo = Photo(path / 'photo.jpg')
        self.assertEqual(photo.new_filename(counter=10), 'CFL_03600A.jpg')

    def test_filename_with_date_from_filesystem(self):
        path = Tree.create({
            '_metadata.yaml': YamlFile(),
            'photo.jpg': JpegFile(),
        })
        photo = Photo(path / 'photo.jpg')
        dt = datetime.fromtimestamp((path / 'photo.jpg').stat().st_ctime)
        self.assertEqual(photo.new_filename(counter=2), datetime_to_string(dt) + '2.jpg')


class EventTests(unittest.TestCase):
    def setUp(self):
        self.base = Tree.create({})

    def test_location_for_interval(self):
        event = Event(self.base, 'Test Event', date(2014, 2, 11), date(2014, 2, 21))
        self.assertEqual(event.location, self.base / '2014' / '2014-02-11...2014-02-21 Test Event')

    def test_location_for_single_day_event(self):
        event = Event(self.base, 'Test Event', date(2014, 2, 11), None)
        self.assertEqual(event.location, self.base / '2014' / '2014-02-11 Test Event')
