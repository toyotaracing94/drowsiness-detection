from fastapi import APIRouter, HTTPException, status

from backend.domain.dto.base_response import StandardResponse
from backend.services.detection_background_service import DetectionBackgroundService


def detection_control_router(detection_service: DetectionBackgroundService) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/start",
        description="Start the detection background thread.",
        response_model=StandardResponse
    )
    def start_detection():
        try:
            status = detection_service.start()
            return StandardResponse(status="success", message="Detection started.", data=status)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start detection: {str(e)}"
            )
        
    @router.post(
        "/restart",
        description="Re-Start the detection background thread.",
        response_model=StandardResponse
    )
    def restart_detection():
        try:
            status = detection_service.restart()
            return StandardResponse(status="success", message="Detection started.", data=status)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start detection: {str(e)}"
            )

    @router.post(
        "/pause",
        description="Pause the detection thread.",
        response_model=StandardResponse
    )
    def pause_detection():
        try:
            status = detection_service.pause()
            return StandardResponse(status="success", message="Detection paused.", data=status)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to pause detection: {str(e)}"
            )

    @router.post(
        "/resume",
        description="Resume the paused detection thread.",
        response_model=StandardResponse
    )
    def resume_detection():
        try:
            status = detection_service.resume()
            return StandardResponse(status="success", message="Detection resumed.", data=status)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to resume detection: {str(e)}"
            )

    @router.post(
        "/stop",
        description="Stop the detection thread.",
        response_model=StandardResponse
    )
    def stop_detection():
        try:
            status = detection_service.stop()
            return StandardResponse(status="success", message="Detection stopped.", data=status)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to stop detection: {str(e)}"
            )

    @router.get(
        "/status",
        description="Get the current detection status.",
        response_model=StandardResponse
    )
    def detection_status():
        try:
            is_alive_thread = detection_service.is_active()
            is_running = detection_service.is_running
            status_msg = "running" if is_alive_thread and is_running else "stopped or paused"
            
            return StandardResponse(
                status="success",
                message=f"Detection is {status_msg}.",
                data={
                    "is_alive": is_alive_thread,
                    "is_running": is_running
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get detection status: {str(e)}"
            )

    return router