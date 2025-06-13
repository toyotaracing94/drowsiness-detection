import json

from pydantic import BaseModel


class FaceMeshConfig(BaseModel):
    eye_aspect_ratio_threshold: float
    eye_aspect_ratio_consec_frames: int
    mouth_aspect_ration_threshold: float
    mouth_aspect_ration_consec_frames: int
    static_image_mode: bool
    refine_landmarks: bool
    max_number_face_detection: int
    min_detection_confidence: float
    min_tracking_confidence: float
    apply_masking: bool

class PoseConfig(BaseModel):
    min_detection_confidence: float
    min_tracking_confidence: float
    enable_segmentation: bool
    smooth_segmentation: bool
    smooth_landmarks: bool
    static_image_mode: bool

class HandsConfig(BaseModel):
    min_detection_confidence: float
    min_tracking_confidence: float

class ModelConfig(BaseModel):
    face: FaceMeshConfig
    pose: PoseConfig
    hands: HandsConfig

    @classmethod
    def load(cls, path: str = "config/model_settings.json"):
        with open(path) as f:
            data = json.load(f)
        return cls(**data)
    
# Load the config once
model_settings = ModelConfig.load()
