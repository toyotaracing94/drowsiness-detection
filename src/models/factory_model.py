import os

from src.models.base_model import BaseModelInference

ImportError
def get_face_model(config_path : str, model_path : str = None) -> BaseModelInference:
    if os.name == "nt":
        from src.models.using_mediapipe.mediapipe_face_model import (
            MediapipeFaceMeshModel,
        )
        return MediapipeFaceMeshModel(config_path, model_path)
    try:
        # TODO : Implemented for Hailo Acceleration
        raise NotImplementedError("Not Implemented Yet!")
    except ImportError or NotImplementedError:
        from src.models.using_mediapipe.mediapipe_face_model import (
            MediapipeFaceMeshModel,
        )
        return MediapipeFaceMeshModel(config_path, model_path)

def get_body_pose_model(config_path : str, model_path : str = None) -> BaseModelInference:
    if os.name == "nt":
        from src.models.using_mediapipe.mediapipe_body_model import (
            MediapipeBodyPoseModel,
        )
        return MediapipeBodyPoseModel(config_path, model_path)
    try:
        # TODO : Implemented for Hailo Acceleration
        raise NotImplementedError("Not Implemented Yet!")
    except ImportError or NotImplementedError:
        from src.models.using_mediapipe.mediapipe_body_model import (
            MediapipeBodyPoseModel,
        )
        return MediapipeBodyPoseModel(config_path, model_path)
        
def get_hands_pose_model(config_path : str, model_path : str = None) -> BaseModelInference:
    if os.name == "nt":
        from src.models.using_mediapipe.mediapipe_hands_model import MediapipeHandsModel
        return MediapipeHandsModel(config_path, model_path)
    try:
        # TODO : Implemented for Hailo Acceleration
        raise NotImplementedError("Not Implemented Yet!")
    except ImportError or NotImplementedError:
        from src.models.using_mediapipe.mediapipe_hands_model import MediapipeHandsModel
        return MediapipeHandsModel(config_path, model_path)
        