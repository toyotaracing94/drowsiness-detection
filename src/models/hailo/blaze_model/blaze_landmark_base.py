import cv2
import numpy as np


class BlazeLandmarkBase():
    """ 
    Base class for Blaze landmark models

    This class provides helper functions to extract aligned regions of interest (ROI) and 
    to denormalize landmark coordinates from the model's output back to the original image space.

    Notes
    ----------
    Adapted from:
     - https://github.com/AlbertaBeef/blaze_app_python
    """

    def __init__(self):
        super(BlazeLandmarkBase, self).__init__()
        
    def extract_roi(self, frame: np.ndarray, xc: np.ndarray, yc: np.ndarray, theta: np.ndarray, scale: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Extracts aligned regions of interest (ROI) from the input image using the given bounding box parameters.

        Parameters
        ----------
        frame : np.ndarray
            The input image (H, W, 3) in RGB format.
        xc : np.ndarray
            X-center coordinates of the ROIs (N,).
        yc : np.ndarray
            Y-center coordinates of the ROIs (N,).
        theta : np.ndarray
            Rotation angles for each ROI (N,) in radians.
        scale : np.ndarray
            Scale factor for each ROI (N,).

        Returns
        -------
        imgs : np.ndarray
            Aligned ROI images of shape (N, H, W, 3), where H = W = self.resolution.
        affines : np.ndarray
            The affine transformation matrices used to map landmarks back (N, 2, 3).
        points : np.ndarray
            The transformed corner points of the ROI boxes (N, 2, 4).
        """

        # Assuming scale is a NumPy array of size [N]
        scaleN = scale.reshape(-1, 1, 1).astype(np.float32)

        # Define points
        points = np.array([[-1, -1, 1, 1], [-1, 1, -1, 1]], dtype=np.float32)

        # Element-wise multiplication
        points = points * scaleN / 2
        points = points.astype(np.float32)

        R = np.zeros((theta.shape[0],2,2),dtype=np.float32)
        for i in range (theta.shape[0]):
            R[i,:,:] = [[np.cos(theta[i]), -np.sin(theta[i])], [np.sin(theta[i]), np.cos(theta[i])]]

        center = np.column_stack((xc, yc))
        center = np.expand_dims(center, axis=-1)

        points = np.matmul(R, points) + center
        points = points.astype(np.float32)

        res = self.resolution
        points1 = np.array([[0, 0], [0, res-1], [res-1, 0]], dtype=np.float32)

        affines = []
        imgs = []
        for i in range(points.shape[0]):
            pts = points[i,:,:3].T
            M = cv2.getAffineTransform(pts, points1)
            img = cv2.warpAffine(frame, M, (res, res))  # No borderValue in NumPy
            img = img.astype('float32') / 255.0
            imgs.append(img)
            affine = cv2.invertAffineTransform(M).astype('float32')
            affines.append(affine)
        if imgs:
            imgs = np.stack(imgs).astype('float32')
            affines = np.stack(affines).astype('float32')
        else:
            imgs = np.zeros((0, 3, res, res), dtype='float32')
            affines = np.zeros((0, 2, 3), dtype='float32')

        return imgs, affines, points

    def denormalize_landmarks(self, landmarks: np.ndarray, affines: np.ndarray) -> np.ndarray:
        """
        Maps normalized landmark coordinates back to original image space using the inverse affine matrices.

        Parameters
        ----------
        landmarks : np.ndarray
            Normalized landmark coordinates of shape (N, K, 3) from ROI image, where K is number of landmarks.
        affines : np.ndarray
            Affine matrices used during ROI extraction of shape (N, 2, 3).

        Returns
        -------
        landmarks : np.ndarray
            Denormalized landmark coordinates in original image space, same shape as input.
        """
        landmarks[:,:,:2] *= self.resolution
        for i in range(len(landmarks)):
            landmark, affine = landmarks[i], affines[i]
            landmark = (affine[:,:2] @ landmark[:,:2].T + affine[:,2:]).T
            landmarks[i,:,:2] = landmark
        return landmarks

    def normalized_landmark_to_orginal_image_space(self, landmarks: np.ndarray, image_shape : np.ndarray) -> np.ndarray:
        """
        Normalized coordinate in original image space into a Mediapipe normalized output [0,1]
        
        Parameters
        ----------
        landmarks : np.ndarray
            Denormalized landmark coordinates of shape (N, K, 3) original Image
        image_shape : np.ndarray
            The original image shapes

        Returns
        -------
        normalized_landmarks : np.ndarray
            Normalized landmakrs in original image space, same shape as the mediapipe output.
        """
        H, W = image_shape[:2]

        normalized_landmarks = landmarks.copy()
        for i in range(len(normalized_landmarks)):
            normalized_landmarks[i, :, 0] /= W
            normalized_landmarks[i, :, 1] /= H

        return normalized_landmarks