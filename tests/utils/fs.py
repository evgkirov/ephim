import os
import tempfile

import yaml


class EmptyFile:
    def populate(self):
        return b''


class TextFile(EmptyFile):
    def __init__(self, content):
        self.content = content

    def populate(self):
        return self.content.encode()


class YamlFile(TextFile):
    def __init__(self, content):
        self.content = yaml.safe_dump(content, default_flow_style=False)


class Tree:
    def __init__(self, structure):
        self.structure = structure

    def populate(self):
        base = tempfile.mkdtemp(prefix='ephim_test_')

        def populate_file(paths, structure):
            with open(os.path.join(*paths), mode='wb') as file:
                file.write(structure.populate())

        def populate_directory(paths, structure):
            os.makedirs(os.path.join(*paths), exist_ok=True)
            for path, substructure in structure.items():
                if isinstance(substructure, dict):
                    populate_directory(paths + (path,), substructure)
                else:
                    populate_file(paths + (path,), substructure)

        populate_directory((base,), self.structure)
        return base

    @staticmethod
    def create(structure):
        return Tree(structure).populate()
