#!/usr/bin/env python3
from datetime import datetime
from os import path
from PIL import Image, ExifTags
import argparse
import os
import shutil
import yaml


class MetadataStore(dict):

    def __init__(self, location):
        self.location = location
        self.load()

    def load(self):
        stream = open(self.location, 'r')
        self.update(yaml.load(stream))
        stream.close()

    def save(self):
        stream = file(self.location, 'w')
        yaml.dump(self, stream)

    def get_section(self, name):
        return MetadataSection(self, name)


class MetadataSection(dict):

    def __init__(self, store, name):
        self.store = store
        self.name = name
        self.load()

    def load(self):
        self.update(self.store.get(self.name, {}))

    def save(self):
        self.store.save()

    def __getitem__(self, key):
        try:
            return super(MetadataSection, self).__getitem__(key)
        except KeyError:
            return self.store.get('all', {})[key]


class Library(object):

    def __init__(self, location):
        self.location = location
        self.originals_location =  path.join(self.location, 'originals')
        self.events_location =  path.join(self.location, 'events')

    @property
    def originals_dirs(self):
        for (dirname, dirnames, filenames) in os.walk(self.originals_location):
            if 'metadata.yaml' in filenames:
                yield OriginalsDir(dirname)

    def organize(self):
        self.organize_events()

    def organize_events(self):
        shutil.rmtree(self.events_location, ignore_errors=True)
        for dir in self.originals_dirs:
            for photo in dir.photos:
                event_location = path.join(self.events_location,
                                           str(photo.metadata['event_date'].year),
                                           '{} {}'.format(photo.metadata['event_date'], photo.metadata['event']))
                os.makedirs(event_location, exist_ok=True)
                src = photo.location
                dest = os.path.join(event_location, photo.filename)
                os.link(src, dest)
                # src = src[len(self.location) + 1:]
                # src = os.path.join('..', '..', '..', src)
                # os.symlink(src, dest)

    @staticmethod
    def find_library(dir):
        dir = path.abspath(dir)
        while True:
            if path.exists(path.join(dir, 'library.yaml')):
                return dir
            parent = path.dirname(dir)
            if dir == parent:
                break
            dir = parent
        raise FileNotFoundError('Photo library is not found.')


class OriginalsDir(object):

    def __init__(self, location):
        self.location = location
        self.metadata = MetadataStore(path.join(self.location, 'metadata.yaml'))

    def __repr__(self):
        return '<OriginalsDir: {}>'.format(path.basename(self.location))

    @property
    def photos(self):
        for (dirname, dirnames, filenames) in os.walk(self.location):
            for filename in filenames:
                base, ext = path.splitext(filename)
                if ext.lower() not in ('.jpg', '.jpeg'):
                    continue
                yield Photo(os.path.join(dirname, filename), metadata_file=self.metadata)


class Photo(object):

    def __init__(self, location, metadata_file=None):
        self.location = location
        self.basename, self.ext = path.splitext(path.basename(self.location))
        image = Image.open(self.location)
        self.metadata = metadata_file.get_section(self.basename)
        self.exif = {
            ExifTags.TAGS[k]: v
            for k, v in image._getexif().items()
            if k in ExifTags.TAGS
        }

    @property
    def filename(self):
        fn = ''
        if self.exif.get('DateTime'):
            fn += self.exif['DateTime'].replace(':', '-', 2).replace(':', '.')
        else:
            fn += '0000-00-00 00.00.00'
        if self.metadata.get('title'):
            fn += ' ' + self.metadata['title']
        fn += self.ext
        return fn


def main():
    location = Library.find_library(os.getcwd())
    library = Library(location)
    library.organize()


if __name__ == '__main__':
    main()
