from fastapi import FastAPI

from src.routers import video_stream
from src.routers import app_version

from src.utils.logging import logging_default

# Define Fast API App
app = FastAPI()

# Register router
app.include_router(app_version.router, prefix="/version", tags=["Version"])
app.include_router(video_stream.router, prefix="/video", tags=["Video"])
