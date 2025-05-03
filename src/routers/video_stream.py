from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.services.drowsiness_detection_service import generate_drowsiness_stream, generate_original_capture_stream

router = APIRouter()

@router.get(
    "/original",
    summary="Live Video Stream",
    description="Returns a live video stream (MJPEG). Use a browser instead of Swagger to view."
)
def video_feed() -> StreamingResponse:
    return StreamingResponse(generate_original_capture_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.get(
    "/drowsiness",
    summary="Live Video of Drowsiness Detection Stream",
    description="Returns a live video stream (MJPEG). Use a browser instead of Swagger to view."
)
def video_drowsiness_feed() -> StreamingResponse:
    return StreamingResponse(generate_drowsiness_stream(), media_type="multipart/x-mixed-replace; boundary=frame")