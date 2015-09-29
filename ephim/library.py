from pathlib import Path


class Library(object):
    @staticmethod
    def find_library(dir):
        dir = Path(dir).absolute()
        while True:
            if dir.joinpath('library.yaml').exists():
                return dir
            parent = dir.parent
            if dir == parent:
                break
            dir = parent
        raise FileNotFoundError('Photo library is not found.')
