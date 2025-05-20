import os

hailo_inference_engine = None
if os.name == "posix":
    try:
        from src.models.hailo.hailo_runtime.hailo_inference_engine import HailoInferenceEngine
        hailo_inference_engine = HailoInferenceEngine()
    except ImportError:
        hailo_inference_engine = None


def get_face_model(config_path : str):
    if os.name == "nt":
        from src.models.mediapipe_wrappers.mediapipe_face_model import (
            MediapipeFaceMeshModel,
        )
        return MediapipeFaceMeshModel(config_path)
    try:
        from src.models.hailo.blaze_model.face_mesh.blaze_face_pipeline import (
            BlazeFacePipeline,
        )
        return BlazeFacePipeline(config_path, hailo_inference_engine)
    
    except ImportError or NotImplementedError:
        from src.models.mediapipe_wrappers.mediapipe_face_model import (
            MediapipeFaceMeshModel,
        )
        return MediapipeFaceMeshModel(config_path)

def get_body_pose_model(config_path : str, model_path : str = None):
    if os.name == "nt":
        from src.models.mediapipe_wrappers.mediapipe_body_model import (
            MediapipeBodyPoseModel,
        )
        return MediapipeBodyPoseModel(config_path)
    try:
        # TODO : Implemented for Hailo Acceleration
        from src.models.mediapipe_wrappers.mediapipe_body_model import (
            MediapipeBodyPoseModel,
        )
        return MediapipeBodyPoseModel(config_path)
    
    except ImportError or NotImplementedError:
        from src.models.mediapipe_wrappers.mediapipe_body_model import (
            MediapipeBodyPoseModel,
        )
        return MediapipeBodyPoseModel(config_path)
        
def get_hands_pose_model(config_path : str, model_path : str = None):
    if os.name == "nt":
        from src.models.mediapipe_wrappers.mediapipe_hands_model import (
            MediapipeHandsModel,
        )
        return MediapipeHandsModel(config_path)
    try:
        from src.models.hailo.blaze_model.hands.blaze_hands_pipeline import (
            BlazeHandsPipeline,
        )
        return BlazeHandsPipeline(config_path, hailo_inference_engine)
    
    except ImportError or NotImplementedError:
        from src.models.mediapipe_wrappers.mediapipe_hands_model import (
            MediapipeHandsModel,
        )
        return MediapipeHandsModel(config_path)
        