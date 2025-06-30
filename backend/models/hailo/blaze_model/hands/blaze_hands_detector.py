import numpy as np

from backend.models.hailo.blaze_model.blaze_detector_base import BlazeDetectorBase
from backend.models.hailo.hailo_runtime.hailo_inference_engine import (
    HailoInferenceEngine,
)


class BlazeHandsDetector(BlazeDetectorBase):
    """
    BlazeFaceDetector performs hands detection using a precompiled Hailo model 
    and MediaPipe-like postprocessing.

    It loads a model onto a Hailo inference engine, preprocesses input images, 
    runs inference, and postprocesses the raw outputs (including NMS).
    """
    def __init__(self, model_path : str, anchors_config : str, inference_config : str, hailo_engine : HailoInferenceEngine):
        super(BlazeHandsDetector, self).__init__()

        self.engine = hailo_engine

        # Load the model into the engine
        self.load_model(model_path, anchors_config, inference_config)

    def load_model(self, model_path : str, anchors_config : str, inference_config : str):
        """
        Loads the model into the Hailo engine and sets up input/output parameters.

        Parameters
        ----------
        model_path : str
            Path to the HEF file to be loaded.
        anchors_config : str
            Path to the anchors configuration file.
        inference_config : str
            Path to the inference pipeline configuration file.
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
        self.inputShape = tuple(self.input_vstream_infos[0].shape)
        self.outputShape1 = tuple((1,2016,1))
        self.outputShape2 = tuple((1,2016,18))

        self.x_scale = self.inputShape[1]
        self.y_scale = self.inputShape[2]
        self.h_scale = self.inputShape[1]
        self.w_scale = self.inputShape[2]

        self.num_anchors = self.outputShape2[1]

        # Setting up the model anchors and 
        # also the inference model calculator config
        self.config_model(anchors_config, inference_config)

    def preprocess(self, image : np.ndarray):
        """
        Converts the image to the expected input format for the model.

        Parameters
        ----------
        image : np.ndarray
            Input image in RGB format (H, W, 3) or (1, H, W, 3) batch.

        Returns
        -------
        np.ndarray
            The image cast to uint8 (no normalization is done here).
        """
        return image.astype(np.uint8)
    
    def process(self, image : np.ndarray, preprocessed = True):
        """
        Runs face detection on a single image.

        Parameters
        ----------
        image : np.ndarray
            Input image of shape (H, W, 3). Expected input size: 128x128 or 256x256.
        preprocessed : bool, optional
            Whether the image has already been preprocessed (default: True).

        Returns
        -------
        np.ndarray
            Array of filtered face detections, shape depends on number of detections.
            If no detections are found, returns an empty list.
        """
        
        # Convert img.unsqueeze(0) to NumPy equivalent
        img_expanded = np.expand_dims(image, axis=0)

        if not preprocessed:
            img_expanded = self.preprocess(img_expanded)
        
        # Preprocess the images into tensors:
        image_tensor = self.preprocess(img_expanded)

        # Call the predict_on_batch function
        detections = self.predict_on_batch(image_tensor)

        # Extract the first element from the predictions
        # return predictions[0]        
        if len(detections) > 0:
            return np.array(detections)[0]
        return []
    
    def predict_on_batch(self, image_tensor: np.ndarray) -> list:
        """
        Runs inference on a batch of images and returns postprocessed detections.

        Parameters
        ----------
        image_tensor : np.ndarray
            A batch of images of shape (B, H, W, 3). The height and width should be 128 pixels.

        Returns
        -------
        list of np.ndarray
            A list of detection arrays (one per image). Each detection array has shape (N, 17),
            where N is the number of detected faces.
        """
        # Run the neural network using Hailo
        outputs = self.engine.run_all(image_tensor, self.hef_id)

        # The output will give us something like this
        #   Output palm_detection_full/conv29 UINT8, FCR(12x12x6)
        #   Output palm_detection_full/conv34 UINT8, FCR(24x24x2)
        #   Output palm_detection_full/conv30 UINT8, FCR(12x12x108)
        #   Output palm_detection_full/conv35 UINT8, FCR(24x24x36)
        # And we dont want that

        # Reshape to match what mediapipe postprocess expects from hailo
        conv_12_12_6 = outputs[self.output_vstream_infos[0].name]
        conv_1_24_24_2 = outputs[self.output_vstream_infos[1].name]
        
        reshape_1_1152_1 = conv_1_24_24_2.reshape(1,1152,1)
        reshape_1_864_1 = conv_12_12_6.reshape(1,864,1)
        concat_1_2016_1 = np.concatenate((reshape_1_1152_1,reshape_1_864_1),axis=1)
        
        conv_12_12_108 = outputs[self.output_vstream_infos[2].name]
        conv_1_24_24_36 = outputs[self.output_vstream_infos[3].name]

        reshape_1_1152_18 = conv_1_24_24_36.reshape(1,1152,18)
        reshape_1_864_18 = conv_12_12_108.reshape(1,864,18)
        concat_1_2016_18 = np.concatenate((reshape_1_1152_18,reshape_1_864_18),axis=1)

        out1 = concat_1_2016_1.astype(np.float32)
        out2 = concat_1_2016_18.astype(np.float32)

        # Postprocess the raw predictions:
        detections = self.tensors_to_detections(out2, out1, self.anchors)

        # Non-maximum suppression to remove overlapping detections:
        filtered_detections = []
        for i in range(len(detections)):
            wnms_detections = self.weighted_non_max_suppression(detections[i])
            if len(wnms_detections) > 0:
                filtered_detections.append(wnms_detections)

        return filtered_detections