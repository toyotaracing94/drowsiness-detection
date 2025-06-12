from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.streaming.drowsiness_streaming import (
    stream_processed_drowsiness_feed,
    stream_raw_camera_feed,
)
from src.utils.frame_buffer import FrameBuffer


def drowsiness_realtime_router(frame_buffer : FrameBuffer):
    router = APIRouter()

    @router.get(
        "/video/raw",
        summary="Live un-edit and raw data of video feed from the camera",
        description="Returns a live video stream (MJPEG). Use a browser instead of Swagger to view."
    )
    def video_feed():
        return StreamingResponse(
            stream_raw_camera_feed(frame_buffer),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )

    @router.get(
        "/video/processed",
        summary="Live of processed detection result frame of video feed from the camera",
        description="Returns a live video stream (MJPEG). Use a browser instead of Swagger to view."
    )
    def video_drowsiness_feed():
        return StreamingResponse(
            stream_processed_drowsiness_feed(frame_buffer),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    return router