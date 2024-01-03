from fastapi import FastAPI

from . import __version__ as VERSION


app = FastAPI(
    title='matamata',
    summary=(
        'REST API for single-elimination tournament management'
    ),
    version=VERSION,
)
