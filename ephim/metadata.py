from pathlib import Path

import yaml


class MetadataFile(dict):
    def __init__(self, location: Path):
        self.location = location
        self.load()

    def load(self):
        with self.location.open('r') as stream:
            self.update(yaml.safe_load(stream))

    def save(self):
        with self.location.open('w') as stream:
            yaml.dump(self, stream)

    def get_section(self, name):
        return MetadataSection(self, name)


class MetadataSection(dict):
    def __init__(self, store: MetadataFile, name: str):
        self.store = store
        self.name = name
        self.load()

    def load(self):
        self.update(self.store.get(self.name, {}))

    def save(self):
        self.store.save()

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return self.store.get('all', {})[key]
