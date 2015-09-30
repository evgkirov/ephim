from pathlib import Path


class Masters:
    def __init__(self, location: Path):
        self.location = location


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
