from fastapi import FastAPI

from src.routers import drowsiness_router, app_version, buzzer_router
from src.services.drowsiness_detection_service import DrowsinessDetectionService
from src.utils.logging import logging_default

from src.hardware.factory_hardware import (
    get_camera,
    get_buzzer
)

# Building Services
camera = get_camera()
buzzer = get_buzzer()
drowsiness_service = DrowsinessDetectionService(camera, buzzer)

# Define Fast API App
app = FastAPI()

# Register router
app.include_router(app_version.router, prefix="/version", tags=["Version"])
app.include_router(buzzer_router.buzzer_router(buzzer), prefix="/buzzer", tags=["Buzzer"])
app.include_router(drowsiness_router.drowsiness_router(drowsiness_service), prefix="/drowsiness", tags=["Video"])