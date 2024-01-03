__version__ = (
    __import__('pathlib').Path(__file__).parent / 'VERSION'
).read_text().strip()
