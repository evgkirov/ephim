from io import BytesIO
import os
from pathlib import Path
import tempfile

from PIL import Image
import piexif

import yaml


class EmptyFile:
    def populate(self):
        return b''


class TextFile(EmptyFile):
    def __init__(self, content: str):
        self.content = content

    def populate(self):
        return self.content.encode()


class YamlFile(TextFile):
    def __init__(self, content):
        self.content = yaml.safe_dump(content, default_flow_style=False)


class JpegFile(EmptyFile):
    def __init__(self, exif: dict = None):
        self.image = Image.new('RGB', (50, 50))
        self.exif_ifd = exif

    def populate(self):
        image_bytes = BytesIO()
        self.image.save(image_bytes, 'jpeg')
        exif_bytes = piexif.dump({
            'Exif': self.exif_ifd,
        })
        output = BytesIO()
        piexif.insert(exif_bytes, image_bytes.getvalue(), output)
        return output.getvalue()



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
