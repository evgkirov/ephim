from io import BytesIO
import os
from pathlib import Path
import tempfile
import yaml
from ephim.utils import exiftool


class EmptyFile:
    def populate(self):
        return b''


class TextFile(EmptyFile):
    def __init__(self, content: str):
        self.content = content

    def populate(self):
        return self.content.encode()


class YamlFile(TextFile):
    def __init__(self, content=None):
        if content is None:
            content = {}
        self.content = yaml.safe_dump(content, default_flow_style=False)


class JpegFile(EmptyFile):
    def __init__(self, exif: dict = None):
        # empty jpeg
        self.image = (b'\xff\xd8\xff\xec\x00\x11Ducky\x00\x01\x00\x04\x00\x00\x00\x00\x00\x00\xff\xee\x00\x0eAdobe\x00d'
                      b'\xc0\x00\x00\x00\x01\xff\xdb\x00\x84\x00\x1b\x1a\x1a)\x1d)A&&AB///BG?>>?GGGGGGGGGGGGGGGGGGGGGGG'
                      b'GGGGGGGGGGGGGGGGGGGGG\x01\x1d))4&4?((?G?5?GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG'
                      b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00K\x00\x01'
                      b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x00'
                      b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                      b'\x00\x00\x00\x00\x00\x00\x00\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                      b'\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xa6\x00\x1f\xff\xd9')
        self.exif = exif or {}

    def populate(self):
        f = tempfile.NamedTemporaryFile()
        f.write(self.image)
        f.file.flush()
        fn = f.name
        params = ['-{0}={1}'.format(*item).encode('utf-8') for item in self.exif.items()]
        params.append(f.name.encode('utf-8'))
        exiftool.execute(*params)
        f = open(fn, 'rb')
        content = f.read()
        f.close()
        return content


class Tree:
    def __init__(self, structure: dict):
        self.structure = structure

    def populate(self):
        base = tempfile.mkdtemp(prefix='ephim_test_')

        def populate_file(paths, structure: EmptyFile):
            with open(os.path.join(*paths), mode='wb') as file:
                file.write(structure.populate())

        def populate_directory(paths, structure: dict):
            os.makedirs(os.path.join(*paths), exist_ok=True)
            for path, substructure in structure.items():
                if isinstance(substructure, dict):
                    populate_directory(paths + (path,), substructure)
                else:
                    populate_file(paths + (path,), substructure)

        populate_directory((base,), self.structure)
        return Path(base)

    @staticmethod
    def create(structure: dict):
        return Tree(structure).populate()
