from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.streaming.drowsiness_streaming import (
    stream_processed_drowsiness_feed,
    stream_raw_camera_feed,
)
from src.utils.frame_buffer import FrameBuffer


def drowsiness_router(frame_buffer : FrameBuffer):
    router = APIRouter()

    @router.get("/raw")
    def video_feed():
        return StreamingResponse(
            stream_raw_camera_feed(frame_buffer),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )

    @router.get("/processed")
    def video_drowsiness_feed():
        return StreamingResponse(
            stream_processed_drowsiness_feed(frame_buffer),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )

    return router