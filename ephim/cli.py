import os

from .library import Library

def main():
    location = Library.find_library(os.getcwd())
    library = Library(location)
    library.organize_all()


if __name__ == '__main__':
    main()
