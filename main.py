import threading
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session
from src.infrastructure.migrate import run_migrations
from src.services.drowsiness_event_service import DrowsinessEventService
from src.settings.app_config import settings
from src.infrastructure.session import init_db, engine

from src.lib.socket_trigger import SocketTrigger
from src.routers import drowsiness_realtime_router, app_version, buzzer_router, drowsiness_event_router
from src.services.drowsiness_detection_service import DrowsinessDetectionService
from src.services.phone_detection_service import PhoneDetectionService
from src.services.hand_detection_service import HandsDetectionService

from src.tasks.detection_task import DetectionTask
from src.utils.frame_buffer import FrameBuffer
from src.utils.logging import logging_default

from src.hardware.factory_hardware import (
    get_camera,
    get_buzzer
)

# Building Services and Hardware connection
logging_default.info("Building services and initiated hardwares")
socket_trigger = SocketTrigger(settings.ApiSettings)
camera = get_camera()
buzzer = get_buzzer()

# Apply Alembic migrations
run_migrations()

# Create a manual DB session and inject service
db_session = Session(engine)
drowsiness_event_service = DrowsinessEventService(db_session)

drowsiness_service = DrowsinessDetectionService(buzzer, socket_trigger, drowsiness_event_service, settings.PipelineSettings.inference_engine)
phone_detection_service = PhoneDetectionService(socket_trigger, settings.PipelineSettings.inference_engine)
hand_service = HandsDetectionService(socket_trigger, settings.PipelineSettings.inference_engine)

detection_task = DetectionTask(settings.PipelineSettings)

# Create shared frame buffer
frame_buffer = FrameBuffer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start detection loop thread that will run the drowsiness service on app startup
    # source = https://stackoverflow.com/questions/70872276/fastapi-python-how-to-run-a-thread-in-the-background 
    detection_thread = threading.Thread(
        target=detection_task.detection_loop,
        args=(drowsiness_service, phone_detection_service, hand_service, camera, frame_buffer),
        daemon=True
    )
    detection_thread.start()
    yield

    # Event when shutdown the FastAPI
    camera.release()
    buzzer.cleanup()
    db_session.close()

# Define Fast API App
logging_default.info("Run webApp")
app = FastAPI(
    title="Drowsiness Detection System",
    description="This page contains detailed info of drowsiness detection system by Capability Center Division Program",
    lifespan=lifespan
)

origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
os.makedirs(settings.ApiSettings.static_dir, exist_ok=True)
app.mount(f"/{settings.ApiSettings.static_dir}", StaticFiles(directory=f"{settings.ApiSettings.static_dir}"), name="static")

# Register router
logging_default.info("Registering API routers")
app.include_router(app_version.router, prefix="/version", tags=["Version"])
app.include_router(buzzer_router.buzzer_router(buzzer), prefix="/buzzer", tags=["Buzzer"])
app.include_router(drowsiness_realtime_router.drowsiness_realtime_router(frame_buffer), prefix="/realtime", tags=["Realtime Drowsiness"])
app.include_router(drowsiness_event_router.router, prefix="/drowsinessevent", tags=["Drowsiness Event"])