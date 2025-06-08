import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.routers import drowsiness_router, app_version, buzzer_router
from src.services.drowsiness_detection_service import DrowsinessDetectionService
from src.tasks.detection_loop import detection_loop
from src.utils.frame_buffer import FrameBuffer
from src.utils.logging import logging_default

from src.hardware.factory_hardware import (
    get_camera,
    get_buzzer
)

# Building Services
logging_default.info("Building services and initiated hardwares")
camera = get_camera()
buzzer = get_buzzer()
drowsiness_service = DrowsinessDetectionService(camera, buzzer)

# Create shared frame buffer
frame_buffer = FrameBuffer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start detection loop thread that will run the drowsiness service on app startup
    # source = https://stackoverflow.com/questions/70872276/fastapi-python-how-to-run-a-thread-in-the-background 
    detection_thread = threading.Thread(
        target=detection_loop,
        args=(drowsiness_service, frame_buffer),
        daemon=True
    )
    detection_thread.start()
    yield

    # Event when shutdown the FastAPI
    camera.release()
    buzzer.cleanup()

# Define Fast API App
logging_default.info("Run webApp")
app = FastAPI(lifespan=lifespan)

# Register router
logging_default.info("Registering API routers")
app.include_router(app_version.router, prefix="/version", tags=["Version"])
app.include_router(buzzer_router.buzzer_router(buzzer), prefix="/buzzer", tags=["Buzzer"])
app.include_router(drowsiness_router.drowsiness_router(frame_buffer), prefix="/drowsiness", tags=["Video"])