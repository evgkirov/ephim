from pathlib import Path

import piexif

from .metadata import MetadataFile


class Library:
    def find_library(path: str):
        location = Path(path).absolute()
        while True:
            if (location / 'library.yaml').exists():
                return location
            parent = location.parent
            if location == parent:
                break
            location = parent
        raise FileNotFoundError('Photo library is not found.')

    def __init__(self, location: Path):
        self.location = location.absolute()
        self.masters_location = location / 'masters'
        self.events_location = location / 'events'

    def discover_masters(self):
        for metadata_file in self.masters_location.rglob('metadata.yaml'):
            yield Masters(metadata_file.parent)


class Masters:
    def __init__(self, location: Path):
        self.location = location

    def discover_photos(self):
        for file in self.location.iterdir():
            if file.suffix.lower() in ('.jpg', '.jpeg'):
                yield Photo(file)


class Photo:
    def __init__(self, location: Path):
        self.location = location
        # self.metadata = metadata_file.get_section(location.stem)
        metadata_store = MetadataFile(location.with_name('metadata.yaml'))
        self.metadata = metadata_store.get_section(location.stem)
        self.exif = piexif.load(str(location))['Exif']

    @property
    def new_filename(self):
        fn = ''
        if piexif.ExifIFD.DateTimeOriginal in self.exif:
            fn += self.exif[piexif.ExifIFD.DateTimeOriginal].decode().replace(':', '-', 2).replace(':', '.')
        else:
            fn += '0000-00-00 00.00.00'
        if 'title' in self.metadata:
            fn += ' ' + self.metadata['title']
        fn += self.location.suffix.lower()
        return fn
