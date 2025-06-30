import os

from backend.settings.detection_config import PhoneDetectionConfig
from backend.settings.model_config import FaceMeshConfig, HandsConfig

hailo_inference_engine = None
if os.name == "posix":
    try:
        from src.models.hailo.hailo_runtime.hailo_inference_engine import (
            HailoInferenceEngine,
        )
        hailo_inference_engine = HailoInferenceEngine()
    except ImportError:
        hailo_inference_engine = None


def get_face_model(config : FaceMeshConfig, inference_engine : str):
    if os.name == "nt":
        from backend.models.mediapipe_wrappers.mediapipe_face_model import (
            MediapipeFaceMeshModel,
        )
        return MediapipeFaceMeshModel(config)
    try:
        if inference_engine == "hailo":
            from src.models.hailo.blaze_model.face_mesh.blaze_face_pipeline import (
                BlazeFacePipeline,
            )
            return BlazeFacePipeline(hailo_inference_engine)
        
        from src.models.mediapipe_wrappers.mediapipe_face_model import (
            MediapipeFaceMeshModel,
        )
        return MediapipeFaceMeshModel(config)
    
    except ImportError or NotImplementedError:
        from src.models.mediapipe_wrappers.mediapipe_face_model import (
            MediapipeFaceMeshModel,
        )
        return MediapipeFaceMeshModel(config)

def get_body_pose_model(config : PhoneDetectionConfig, inference_engine : str):
    if os.name == "nt":
        from backend.models.mediapipe_wrappers.mediapipe_body_model import (
            MediapipeBodyPoseModel,
        )
        return MediapipeBodyPoseModel(config)
    try:
        # TODO : Implement Body Pose Model run for Hailo Acceleration
        from src.models.mediapipe_wrappers.mediapipe_body_model import (
            MediapipeBodyPoseModel,
        )
        return MediapipeBodyPoseModel(config)
    
    except ImportError or NotImplementedError:
        from src.models.mediapipe_wrappers.mediapipe_body_model import (
            MediapipeBodyPoseModel,
        )
        return MediapipeBodyPoseModel(config)
        
def get_hands_pose_model(config : HandsConfig, inference_engine : str):
    if os.name == "nt":
        from backend.models.mediapipe_wrappers.mediapipe_hands_model import (
            MediapipeHandsModel,
        )
        return MediapipeHandsModel(config)
    try:
        if inference_engine == "hailo":
            from src.models.hailo.blaze_model.hands.blaze_hands_pipeline import (
                BlazeHandsPipeline,
            )
            return BlazeHandsPipeline(hailo_inference_engine)

        from src.models.mediapipe_wrappers.mediapipe_hands_model import (
            MediapipeHandsModel,
        )
        return MediapipeHandsModel(config)
    
    except ImportError or NotImplementedError:
        from src.models.mediapipe_wrappers.mediapipe_hands_model import (
            MediapipeHandsModel,
        )
        return MediapipeHandsModel(config)
        