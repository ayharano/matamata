from fastapi import FastAPI

from . import __version__ as VERSION
from .routers import competitor, match, tournament


app = FastAPI(
    title='matamata',
    summary=(
        'REST API for single-elimination tournament management'
    ),
    version=VERSION,
)


app.include_router(competitor.router)
app.include_router(match.router)
app.include_router(tournament.router)
