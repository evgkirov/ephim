from datetime import datetime, date
import os
from pathlib import Path
import shutil
import string

import piexif

from .utils import datetime_to_string, to_base
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
        self.masters_location = self.location / 'masters'
        self.events_location = self.location / 'events'
        self.all_location = self.location / 'all'

    def discover_masters(self):
        for metadata_file in self.masters_location.rglob('_metadata.yaml'):
            yield Masters(metadata_file.parent)

    def organize_all(self):
        self.organize_events()

    def organize_events(self):
        shutil.rmtree(str(self.events_location), ignore_errors=True)
        shutil.rmtree(str(self.all_location), ignore_errors=True)
        for masters in self.discover_masters():
            for photo in masters.discover_photos():
                # if photo.metadata.get('event'):
                #     event = Event(self.events_location,
                #                   photo.metadata.get('event'),
                #                   photo.metadata.get('event_start') or photo.datetime,
                #                   photo.metadata.get('event_end'))
                #     event.mkdir()
                #     photo.link(event.location)
                event = Event(self.events_location,
                              photo.metadata['event'],
                              photo.metadata['event_start'] or photo.datetime,
                              photo.metadata['event_end'])
                event.mkdir()
                photo.link(event.location)
                os.makedirs(str(self.all_location), exist_ok=True)
                photo.link(self.all_location)


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
        metadata_store = MetadataFile(self.location.with_name('_metadata.yaml'))
        self.metadata = metadata_store.get_section(self.location.stem)
        info = piexif.load(str(self.location))
        self.exif = info['Exif']
        self.zeroth = info['0th']

    def new_filename(self, counter: int):
        fn = datetime_to_string(self.datetime)
        fn += to_base(counter, 36, string.digits + string.ascii_uppercase)
        if self.metadata.get('title'):
            fn += ' - ' + self.metadata['title']
        fn += self.location.suffix.lower()
        return fn

    @property
    def datetime(self):
        if piexif.ImageIFD.DateTime in self.zeroth:
            return datetime.strptime(self.zeroth[piexif.ImageIFD.DateTime].decode(),
                                     '%Y:%m:%d %H:%M:%S')
        elif piexif.ExifIFD.DateTimeOriginal in self.exif:
            return datetime.strptime(self.exif[piexif.ExifIFD.DateTimeOriginal].decode(),
                                     '%Y:%m:%d %H:%M:%S')
        elif piexif.ExifIFD.DateTimeDigitized in self.exif:
            return datetime.strptime(self.exif[piexif.ExifIFD.DateTimeDigitized].decode(),
                                     '%Y:%m:%d %H:%M:%S')
        return datetime.fromtimestamp(self.location.stat().st_ctime)

    def link(self, to: Path):
        counter = 0
        while True:
            try:
                return os.link(str(self.location), str(to / self.new_filename(counter)))
            except FileExistsError:
                counter += 1


class Event:
    def __init__(self, events_location: Path, name: str, start: date, end: (date, None)):
        self.events_location = events_location
        self.name = name
        self.start = start
        self.end = end or start

    @property
    def location(self):
        dirname = self.start.strftime('%Y-%m-%d')
        if self.start != self.end:
            dirname += '...' + self.end.strftime('%Y-%m-%d')
        dirname += ' ' + self.name
        return self.events_location / str(self.start.year) / dirname

    def mkdir(self):
        return os.makedirs(str(self.location), exist_ok=True)
