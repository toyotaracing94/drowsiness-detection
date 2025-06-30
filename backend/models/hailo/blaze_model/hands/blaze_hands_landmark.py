import numpy as np

from backend.models.hailo.blaze_model.blaze_landmark_base import BlazeLandmarkBase
from backend.models.hailo.hailo_runtime.hailo_inference_engine import (
    HailoInferenceEngine,
)


class BlazeHandsLandmark(BlazeLandmarkBase):
    """
    BlazeHandsLandmark performs Hands landmark regression using a precompiled Hailo model.
    It receives a cropped/normalized ROI (e.g., from a hands detector), 
    and outputs keypoint predicted positions of the landmark positition.
    """

    def __init__(self, model_path : str, hailo_engine : HailoInferenceEngine):
        super(BlazeHandsLandmark, self).__init__()

        self.engine = hailo_engine

        # Load the model into the engine
        self.load_model(model_path)

    def load_model(self, model_path : str):
        """
        Loads the model and its associated metadata from Hailo runtime.

        Parameters
        ----------
        model_path : str
            Path to the compiled HEF model file.
        """
        self.hef_id = self.engine.load_model(model_path)
        self.hef = self.engine.hef_list[self.hef_id]

        # Define dataset params
        self.input_vstream_infos = self.hef.get_input_vstream_infos()
        self.output_vstream_infos = self.hef.get_output_vstream_infos()

        #Get input/output tensors dimensions
        self.num_inputs = len(self.input_vstream_infos)
        self.num_outputs = len(self.output_vstream_infos)

        # Set the network Input output shape according to mediapipe model
        self.inputShape = self.input_vstream_infos[0].shape
        self.outputShape1 = tuple(self.output_vstream_infos[2].shape)
        self.outputShape2 = tuple(self.output_vstream_infos[0].shape)

        self.resolution = self.inputShape[1]

    def preprocess(self, image : np.ndarray):
        """
        Converts the normalized float32 image back to uint8 for inference.

        Notes
        -----
        Input is expected to be in range [0, 1], float32.
        Output is in range [0, 255], uint8.

        Parameters
        ----------
        image : np.ndarray
            Normalized RGB image of shape (H, W, 3), dtype=float32.

        Returns
        -------
        np.ndarray
            Image in uint8 format, ready for inference.
        """
        image = image * 255.0
        image = image.astype(np.uint8)
        return image
    
    def process(self, image : np.ndarray, preprocessed = True):
        """
        Processes one or more face crops to predict landmarks and presence flags.

        Parameters
        ----------
        image : np.ndarray
            Batched input images, shape (N, H, W, 3), float32 in [0, 1].
        preprocessed : bool, optional
            If False, applies preprocessing to convert input to uint8 (default is True).

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            - `flag` : np.ndarray of shape (N, 2304, 1)
              Detection confidence or presence flag for each anchor/keypoint.
            - `landmarks` : np.ndarray of shape (N, 356, 3)
              Normalized landmark coordinates in the ROI image space.
        """
        if not preprocessed:
            image = self.preprocess(image)

        output1_list = []
        output2_list = []
        
        nb_images = image.shape[0]
        for i in range(nb_images):

            # Preprocess the images into tensors:
            image_input = np.expand_dims(image[i,:,:,:], axis=0)
        
            # Run the neural network on Hailo
            """ Execute model on Hailo-8 """
            outputs = self.engine.run_all(image_input, self.hef_id)

            # The output will give us something like this
            #   Output hand_landmark/fc1 UINT8, NC (63)
            #   Output hand_landmark/fc4 UINT8, NC (1)
            #   Output hand_landmark/fc3 UINT8, NC (1)
            #   Output hand_landmark/fc2 UINT8, NC (63)
            # And we dont want that

            output1 = outputs[self.output_vstream_infos[2].name]
            output2 = outputs[self.output_vstream_infos[0].name]

            # Reshape to match what mediapipe postprocess expects from hailo
            output2 = output2.reshape(1,21,-1) # 42 => [1,21,2] | 63 => [1,21,3]
            output2 = output2 / self.resolution                                      

            output1_list.append(output1.squeeze(0))
            output2_list.append(output2.squeeze(0))

        flag = np.asarray(output1_list)
        landmarks = np.asarray(output2_list)        

        return flag,landmarks