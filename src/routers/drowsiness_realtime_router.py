import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from src.streaming.drowsiness_streaming import (
    stream_processed_drowsiness_feed,
    stream_raw_camera_feed,
)
from src.utils.frame_buffer import FrameBuffer
from src.utils.logging import logging_default


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
    
    @router.websocket("/data/facialmetrics")
    async def live_video_stream(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                # Run the get_facial_metrics function in a non-blocking manner
                facial_metrics = await asyncio.to_thread(frame_buffer.get_facial_metrics)

                if facial_metrics:
                    # Send the facial metrics as JSON if available
                    await websocket.send_json(facial_metrics.model_dump_json())
                else:
                    # Default values if no metrics are available
                    await websocket.send_json({"ear": 0.0, "mar": 0.0, "is_drowsy" : False, "is_calling" : "false"})

        except WebSocketDisconnect:
            logging_default.info("A client has been disconnected from WebSocket")



    return router