from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.services.drowsiness_detection_service import DrowsinessDetectionService
from src.streaming.drowsiness_streaming import (
    stream_processed_drowsiness_feed,
    stream_raw_camera_feed,
)


def drowsiness_router(drowsiness_service : DrowsinessDetectionService):
    router = APIRouter()

    @router.get("/raw")
    def video_feed():
        return StreamingResponse(
            stream_raw_camera_feed(drowsiness_service),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )

    @router.get("/processed")
    def video_drowsiness_feed():
        return StreamingResponse(
            stream_processed_drowsiness_feed(drowsiness_service),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )

    return router