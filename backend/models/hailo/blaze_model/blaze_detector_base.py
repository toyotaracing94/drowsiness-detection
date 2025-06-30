import cv2
import numpy as np

from backend.models.hailo.blaze_model.box_utils import (
    calculate_scale,
    overlap_similarity,
)
from backend.models.hailo.blaze_model.utils import get_anchor_options, get_model_config


class BlazeDetectorBase():
    """ 
    Base class for detector models.
    
    Notes
    ---------
    Based on code from 
     - https://github.com/tkat0/PyTorch_BlazeFace/
     - https://github.com/hollance/BlazeFace-PyTorch
     - https://github.com/google/mediapipe/
    """

    def __init__(self):
        super(BlazeDetectorBase, self).__init__()
            
    def config_model(self, anchors_config : str, inference_config : str):
        """
        Load the anchors config used in for decoding the boxes result from the detection
        and the model config of the tracking of the model

        Parameters
        ----------
        anchors_config : str
            The config path on the model anchors
        inference_config : str
            The config path on the model inference config
        """
        # Generate the anchors
        self.anchors_options = get_anchor_options(anchors_config)
        self.anchors = self.generate_detector_anchors(self.anchors_options)

        # Get the configs of the model
        self.config = get_model_config(inference_config)
      
        # Set model config
        self.num_classes = self.config["num_classes"]
        self.num_anchors = self.config["num_anchors"]
        self.num_coords = self.config["num_coords"]
        self.score_clipping_thresh = self.config["score_clipping_thresh"]

        #self.back_model = ...
        self.x_scale = self.config["x_scale"]
        self.y_scale = self.config["y_scale"]
        self.h_scale = self.config["h_scale"]
        self.w_scale = self.config["w_scale"]
        self.min_score_thresh = self.config["min_score_thresh"]
        self.min_suppression_threshold = self.config["min_suppression_threshold"]
        self.num_keypoints = self.config["num_keypoints"]
        
        self.detection2roi_method = self.config["detection2roi_method"]
        self.kp1 = self.config["kp1"]
        self.kp2 = self.config["kp2"]
        self.theta0 = self.config["theta0"]
        self.dscale = self.config["dscale"]
        self.dy = self.config["dy"]

    def generate_detector_anchors(self, options : dict):
        """
        Generates anchor boxes based on the configuration options.

        Anchor boxes are predefined bounding boxes of various scales and aspect ratios
        used by object detection models (like SSD or BlazeFace) to predict final bounding boxes.
        This function implements the anchor generation logic as described in MediaPipe's object
        detection models.

        Parameters
        ----------
        options : dict
            A dictionary containing configuration parameters for anchor generation. Keys include:
            - "num_layers" (int): Number of feature map layers used.
            - "min_scale" (float): Minimum scale of anchor boxes.
            - "max_scale" (float): Maximum scale of anchor boxes.
            - "strides" (List[int]): Stride values for each layer (must match num_layers).
            - "aspect_ratios" (List[float]): List of aspect ratios to apply to anchors.
            - "interpolated_scale_aspect_ratio" (float): Aspect ratio used for interpolated scale anchors (or 0 to disable).
            - "input_size_height" (int): Input image height.
            - "input_size_width" (int): Input image width.
            - "anchor_offset_x" (float): Horizontal center offset for anchor grid.
            - "anchor_offset_y" (float): Vertical center offset for anchor grid.
            - "fixed_anchor_size" (bool): If True, all anchors are fixed to size 1.0x1.0.
            - "reduce_boxes_in_lowest_layer" (bool): If True, use smaller predefined anchors in the first layer.

        Returns
        -------
        anchors : np.ndarray
            A NumPy array of shape (N, 4), where each row is an anchor box in the format:
            [x_center, y_center, width, height], all normalized to [0, 1] relative to input image size.
        """
        strides_size = len(options["strides"])
        assert options["num_layers"] == strides_size

        anchors = []
        layer_id = 0
        while layer_id < strides_size:
            anchor_height = []
            anchor_width = []
            aspect_ratios = []
            scales = []

            # For same strides, we merge the anchors in the same order.
            last_same_stride_layer = layer_id
            while (last_same_stride_layer < strides_size) and \
                (options["strides"][last_same_stride_layer] == options["strides"][layer_id]):
                scale = calculate_scale(options["min_scale"],
                                        options["max_scale"],
                                        last_same_stride_layer,
                                        strides_size)

                if last_same_stride_layer == 0 and options["reduce_boxes_in_lowest_layer"]:
                    # For first layer, it can be specified to use predefined anchors.
                    aspect_ratios.append(1.0)
                    aspect_ratios.append(2.0)
                    aspect_ratios.append(0.5)
                    scales.append(0.1)
                    scales.append(scale)
                    scales.append(scale)                
                else:
                    for aspect_ratio in options["aspect_ratios"]:
                        aspect_ratios.append(aspect_ratio)
                        scales.append(scale)

                    if options["interpolated_scale_aspect_ratio"] > 0.0:
                        scale_next = 1.0 if last_same_stride_layer == strides_size - 1 \
                                        else calculate_scale(options["min_scale"],
                                                            options["max_scale"],
                                                            last_same_stride_layer + 1,
                                                            strides_size)
                        scales.append(np.sqrt(scale * scale_next))
                        aspect_ratios.append(options["interpolated_scale_aspect_ratio"])

                last_same_stride_layer += 1

            for i in range(len(aspect_ratios)):
                ratio_sqrts = np.sqrt(aspect_ratios[i])
                anchor_height.append(scales[i] / ratio_sqrts)
                anchor_width.append(scales[i] * ratio_sqrts)            
                
            stride = options["strides"][layer_id]
            feature_map_height = int(np.ceil(options["input_size_height"] / stride))
            feature_map_width = int(np.ceil(options["input_size_width"] / stride))

            for y in range(feature_map_height):
                for x in range(feature_map_width):
                    for anchor_id in range(len(anchor_height)):
                        x_center = (x + options["anchor_offset_x"]) / feature_map_width
                        y_center = (y + options["anchor_offset_y"]) / feature_map_height

                        new_anchor = [x_center, y_center, 0, 0]
                        if options["fixed_anchor_size"]:
                            new_anchor[2] = 1.0
                            new_anchor[3] = 1.0
                        else:
                            new_anchor[2] = anchor_width[anchor_id]
                            new_anchor[3] = anchor_height[anchor_id]
                        anchors.append(new_anchor)

            layer_id = last_same_stride_layer

        anchors = np.asarray(anchors)

        return anchors

    def resize_pad(self, img : np.ndarray) -> tuple[np.ndarray, float, tuple[int, int]]:
        """
        resize and pad images to be input to the detectors

        The face and palm detector networks take 256x256 and 128x128 images
        as input. As such the input image is padded and resized to fit the
        size while maintaing the aspect ratio.

        Parameters
        ----------
        img : np.ndarray
            The image of the frame or want to be padded

        Returns
        ----------
        img : HxW

        scale : float
            scale factor between original image and 256x256 image
        pad : int
            pixels of padding in the original image
        """

        size = img.shape
        if size[0] >= size[1]:
            h1 = int(self.h_scale)
            w1 = int(self.w_scale * size[1] // size[0])
            padh = 0
            padw = int(self.w_scale - w1)
            scale = size[1] / w1
        else:
            h1 = int(self.h_scale * size[0] // size[1])
            w1 = int(self.w_scale)
            padh = int(self.h_scale - h1)
            padw = 0
            scale = size[0] / h1
        
        padh1 = padh//2
        padh2 = padh//2 + padh % 2
        padw1 = padw//2
        padw2 = padw//2 + padw % 2
        img = cv2.resize(img, (w1, h1))
        img = np.pad(img, ((padh1, padh2), (padw1, padw2), (0, 0)), mode='constant')
        pad = (int(padh1 * scale), int(padw1 * scale))
        return img, scale, pad

    def denormalize_detections(self, detections, scale, pad):
        """ 
        maps detection coordinates from [0,1] to image coordinates

        The face and palm detector networks take 256x256 and 128x128 images
        as input. As such the input image is padded and resized to fit the
        size while maintaing the aspect ratio. This function maps the
        normalized coordinates back to the original image coordinates.

        Parameters
        ----------
        detections : np.ndarray
            Array of shape (N, M), where:
            - N is the number of detections.
            - M = 4 + 2 * K, where:
                - The first 4 values are [ymin, xmin, ymax, xmax]
                - The remaining values are K keypoints in the format (x1, y1, x2, y2, ..., xK, yK)

        scale : float
            The scale factor used when resizing the image before detection.

        pad : Tuple[float, float]
            Tuple (pad_x, pad_y) representing the number of pixels padded on 
            the x and y axes when resizing the original image to square input.

        Returns
        -------
        detections : np.ndarray
            The input array with all coordinates transformed back to the original image space.
            The operation is done in-place and the same array is returned.
        """
        detections[:, 0] = detections[:, 0] * scale * self.x_scale - pad[0]
        detections[:, 1] = detections[:, 1] * scale * self.x_scale - pad[1]
        detections[:, 2] = detections[:, 2] * scale * self.x_scale - pad[0]
        detections[:, 3] = detections[:, 3] * scale * self.x_scale - pad[1]

        detections[:, 4::2] = detections[:, 4::2] * scale * self.x_scale - pad[1]
        detections[:, 5::2] = detections[:, 5::2] * scale * self.x_scale - pad[0]
        return detections
        
    def detection2roi(self, detection) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """ 
        Convert detections from detector to an oriented bounding box.
        The center and size of the box is calculated from the center 
        of the detected box. Rotation is calcualted from the vector
        between kp1 and kp2 relative to theta0. The box is scaled
        and shifted by dscale and dy.

        Notes
        ---------
        Adapted from:
         - mediapipe/modules/face_landmark/face_detection_front_detection_to_roi.pbtxt

        Parameters
        ----------
        detection : np.ndarray, shape (N, D)
            Array of detections, where each row contains:
            - For 'box' method: [ymin, xmin, ymax, xmax, ...]
            - For 'alignment' method: [ymin, xmin, ymax, xmax, kp1_x, kp1_y, kp2_x, kp2_y, ...]  
            N is the number of detections. D must be at least 4 (for bounding boxes) and larger for keypoints.

        Returns
        -------
        xc : np.ndarray, shape (N,)
            x-coordinate of the ROI center for each detection.
        yc : np.ndarray, shape (N,)
            y-coordinate of the ROI center for each detection (after vertical shift).
        scale : np.ndarray, shape (N,)
            Scale (size) of the ROI, optionally scaled by `dscale`.
        theta : np.ndarray, shape (N,)
            Rotation angle (in radians) of the ROI relative to the horizontal axis.
        """
        if self.detection2roi_method == 'box':
            # compute box center and scale
            # use mediapipe/calculators/util/detections_to_rects_calculator.cc
            xc = (detection[:,1] + detection[:,3]) / 2
            yc = (detection[:,0] + detection[:,2]) / 2
            scale = (detection[:,3] - detection[:,1]) # assumes square boxes

        elif self.detection2roi_method == 'alignment':
            # compute box center and scale
            # use mediapipe/calculators/util/alignment_points_to_rects_calculator.cc
            xc = detection[:,4+2*self.kp1]
            yc = detection[:,4+2*self.kp1+1]
            x1 = detection[:,4+2*self.kp2]
            y1 = detection[:,4+2*self.kp2+1]
            scale = np.sqrt(((xc-x1)**2 + (yc-y1)**2)) * 2
        else:
            raise NotImplementedError(
                "detection2roi_method [%s] not supported"%self.detection2roi_method)

        yc += self.dy * scale
        scale *= self.dscale

        # compute box rotation
        x0 = detection[:,4+2*self.kp1]
        y0 = detection[:,4+2*self.kp1+1]
        x1 = detection[:,4+2*self.kp2]
        y1 = detection[:,4+2*self.kp2+1]
        theta = np.arctan2(y0-y1, x0-x1) - self.theta0

        return xc, yc, scale, theta

    def tensors_to_detections(self, raw_box_tensor : np.ndarray, raw_score_tensor : np.ndarray, anchors : np.ndarray):
        """
        The output of the neural network is an array of shape (b, 896, 12)
        containing the bounding box regressor predictions, as well as an array 
        of shape (b, 896, 1) with the classification confidences.

        This function converts these two "raw" arrays into proper detections.
        Returns a list of (num_detections, 13) arrays, one for each image in
        the batch.

        Each detection row contains 13 values:
        [ymin, xmin, ymax, xmax, kp0_x, kp0_y, kp1_x, kp1_y, ..., kp4_x, kp4_y, score]


        Notes
        ----------
        This is based on the source code from:
         - mediapipe/calculators/tflite/tflite_tensors_to_detections_calculator.cc
         - mediapipe/calculators/tflite/tflite_tensors_to_detections_calculator.proto

        Parameters
        ----------
        raw_box_tensor : np.ndarray
            Array of shape (batch_size, num_anchors, 12) containing the raw bounding box 
            regression outputs of the neural network. Each box has:
            [y_center, x_center, height, width, keypoints (10 values)]

        raw_score_tensor : np.ndarray
            Array of shape (batch_size, num_anchors, 1) containing classification confidence 
            scores for each anchor box.

        anchors : np.ndarray
            Array of shape (num_anchors, 4) containing anchor box definitions.
            Each anchor box has: [y_center, x_center, height, width]

        Returns
        -------
        List[np.ndarray]
            A list of NumPy arrays (one per image in the batch), each of shape 
            (num_detections, 13). Each row corresponds to a detected object and includes:
            bounding box coordinates, 5 keypoints (x, y), and a detection score.
        """        
        detection_boxes = self.decode_boxes(raw_box_tensor, anchors)

        thresh = self.score_clipping_thresh
        clipped_score_tensor = np.clip(raw_score_tensor,-thresh,thresh)

        detection_scores = 1/(1 + np.exp(-clipped_score_tensor))
        detection_scores = np.squeeze(detection_scores, axis=-1)        
       
        # Note: we stripped off the last dimension from the scores tensor
        # because there is only has one class. Now we can simply use a mask
        # to filter out the boxes with too low confidence.
        mask = detection_scores >= self.min_score_thresh

        # Because each image from the batch can have a different number of
        # detections, process them one at a time using a loop.
        output_detections = []
        for i in range(raw_box_tensor.shape[0]):
            boxes = detection_boxes[i, mask[i]]

            scores = detection_scores[i, mask[i]]
            scores = np.expand_dims(scores,axis=-1) 

            boxes_scores = np.concatenate((boxes,scores),axis=-1)
            output_detections.append(boxes_scores)

        return output_detections

    def decode_boxes(self, raw_boxes : np.ndarray, anchors : np.ndarray) -> np.ndarray:
        """
        Converts the predictions into actual coordinates using
        the anchor boxes. Processes the entire batch at once.

        The raw box predictions from the model are in a normalized and 
        encoded format. This function decodes them into absolute coordinates 
        (ymin, xmin, ymax, xmax) and keypoint positions relative to the image.

        Parameters
        ----------
        raw_boxes : np.ndarray
            Array of shape (num_anchors, 4 + 2 * num_keypoints) or 
            (batch_size, num_anchors, 4 + 2 * num_keypoints), containing:
                - 4 box coordinates (encoded center-x, center-y, width, height)
                - followed by 2 values per keypoint: (x, y)

        anchors : np.ndarray
            Array of shape (num_anchors, 4), where each row is an anchor box:
                [x_center, y_center, width, height]

        Returns
        -------
        boxes : np.ndarray
            Array of the same shape as `raw_boxes`, with decoded coordinates:
                - boxes[..., 0:4] contain [ymin, xmin, ymax, xmax]
                - boxes[..., 4:] contain decoded keypoint (x, y) positions
                for `num_keypoints`
        """
        boxes = np.zeros( raw_boxes.shape )

        x_center = raw_boxes[..., 0] / self.x_scale * anchors[:, 2] + anchors[:, 0]
        y_center = raw_boxes[..., 1] / self.y_scale * anchors[:, 3] + anchors[:, 1]

        w = raw_boxes[..., 2] / self.w_scale * anchors[:, 2]
        h = raw_boxes[..., 3] / self.h_scale * anchors[:, 3]

        boxes[..., 0] = y_center - h / 2.  # ymin
        boxes[..., 1] = x_center - w / 2.  # xmin
        boxes[..., 2] = y_center + h / 2.  # ymax
        boxes[..., 3] = x_center + w / 2.  # xmax

        for k in range(self.num_keypoints):
            offset = 4 + k*2
            keypoint_x = raw_boxes[..., offset    ] / self.x_scale * anchors[:, 2] + anchors[:, 0]
            keypoint_y = raw_boxes[..., offset + 1] / self.y_scale * anchors[:, 3] + anchors[:, 1]
            boxes[..., offset    ] = keypoint_x
            boxes[..., offset + 1] = keypoint_y

        return boxes

    def weighted_non_max_suppression(self, detections : np.ndarray) -> list:
        """
        The alternative NMS method as mentioned in the [BlazeFace paper](https://arxiv.org/pdf/1907.05047):

            "We replace the suppression algorithm with a blending strategy that
            estimates the regression parameters of a bounding box as a weighted
            mean between the overlapping predictions."

        The original MediaPipe code assigns the score of the most confident
        detection to the weighted detection, but we take the average score
        of the overlapping detections.

        The input detections should be a Tensor of shape (count, 17).
        Returns a list of PyTorch tensors, one for each detected face.
        
        Notes
        ----------
        This is based on the source code from:
         - mediapipe/calculators/util/non_max_suppression_calculator.cc
         - mediapipe/calculators/util/non_max_suppression_calculator.proto

        Parameters
        ----------
        detections : np.ndarray
            A NumPy array of shape (N, 17), where each row represents a detected face

        Returns
        -------
        List[torch.Tensor]
            A list of PyTorch tensors, each representing a single, blended detection
            after applying weighted non-maximum suppression. Each tensor has shape (17,)
            and maintains the same format as the input detections.
        """
        if len(detections) == 0: 
           return []

        output_detections = []

        # Sort the detections from highest to lowest score.
        # argsort() returns ascending order, therefore read the array from end
        remaining = np.argsort(detections[:, self.num_coords])[::-1]    

        while len(remaining) > 0:
            detection = detections[remaining[0]]

            # Compute the overlap between the first box and the other 
            # remaining boxes. (Note that the other_boxes also include
            # the first_box.)
            first_box = detection[:4]
            other_boxes = detections[remaining, :4]
            ious = overlap_similarity(first_box, other_boxes)

            # If two detections don't overlap enough, they are considered
            # to be from different faces.
            mask = ious > self.min_suppression_threshold
            overlapping = remaining[mask]
            remaining = remaining[~mask]

            # Take an average of the coordinates from the overlapping
            # detections, weighted by their confidence scores.
            weighted_detection = detection.copy()
            if len(overlapping) > 1:
                coordinates = detections[overlapping, :self.num_coords]
                scores = detections[overlapping, self.num_coords:self.num_coords+1]
                total_score = scores.sum()
                weighted = np.sum(coordinates * scores, axis=0) / total_score
                weighted_detection[:self.num_coords] = weighted
                weighted_detection[self.num_coords] = total_score / len(overlapping)

            output_detections.append(weighted_detection)

        return output_detections   