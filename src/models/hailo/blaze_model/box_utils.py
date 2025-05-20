import numpy as np


# IOU code from https://github.com/amdegroot/ssd.pytorch/blob/master/layers/box_utils.py
def intersect(box_a : np.ndarray, box_b : np.ndarray) -> np.ndarray:
    """
    We resize both tensors to [A,B,2] without new malloc:
    ```
        [A,2] -> [A,1,2] -> [A,B,2]
        [B,2] -> [1,B,2] -> [A,B,2]
    ```
    Efficiently broadcasts both input arrays to [A, B, 2] shape without allocating new memory,
    and calculates the area of the intersection between each pair of boxes from `box_a` and `box_b`.

    Parameters
    ----------
    box_a : np.ndarray
        Array of shape (A, 4) where each row is a bounding box [ymin, xmin, ymax, xmax].
    box_b : np.ndarray
        Array of shape (B, 4) where each row is a bounding box [ymin, xmin, ymax, xmax].

    Returns
    -------
    inter_area : np.ndarray
        Array of shape (A, B) where each element is the intersection area between
        a box in `box_a` and a box in `box_b`.
    """
    a = box_a.shape[0]
    b = box_b.shape[0]
    max_xy = np.minimum(
        np.repeat(np.expand_dims(box_a[:, 2:], axis=1), b, axis=1),
        np.repeat(np.expand_dims(box_b[:, 2:], axis=0), a, axis=0),
    )
    min_xy = np.maximum(
        np.repeat(np.expand_dims(box_a[:, :2], axis=1), b, axis=1),
        np.repeat(np.expand_dims(box_b[:, :2], axis=0), a, axis=0),
    )
    inter = np.clip((max_xy - min_xy), 0, None)
    return inter[:, :, 0] * inter[:, :, 1]

def jaccard(box_a : np.ndarray, box_b : np.ndarray) -> np.ndarray:
    """
    Compute the jaccard overlap of two sets of boxes.  The jaccard overlap
    is simply the intersection over union of two boxes.  Here we operate on
    ground truth boxes and default boxes.4

    ```
        E.g.:
        A ∩ B / A ∪ B = A ∩ B / (area(A) + area(B) - A ∩ B)
    ```

    Parameters
    ----------
    box_a : np.ndarray
        Array of shape (N, 4), typically ground truth boxes.
    box_b : np.ndarray
        Array of shape (M, 4), typically anchor or prior boxes.

    Returns
    -------
    iou : np.ndarray
         jaccard overlap: (tensor) Shape: [box_a.size(0), box_b.size(0)]
    """
    inter = intersect(box_a, box_b)
    area_a = np.repeat(
        np.expand_dims( (box_a[:, 2]-box_a[:, 0]) * (box_a[:, 3]-box_a[:, 1]), 
            axis=1
        ),
        inter.shape[1],
        axis=1
    )  # [A,B]
    area_b = np.repeat(
        np.expand_dims(
            (box_b[:, 2]-box_b[:, 0]) * (box_b[:, 3]-box_b[:, 1]),
            axis=0
        ),
        inter.shape[0],
        axis=0
    )  # [A,B]
    union = area_a + area_b - inter
    return inter / union  # [A,B]

def overlap_similarity(box : np.ndarray, other_boxes : np.ndarray):
    """Computes the IOU between a bounding box and set of other boxes."""
    return jaccard(np.expand_dims(box, axis=0), other_boxes).squeeze(0)

def calculate_scale(min_scale : float, max_scale : float, stride_index : int, num_strides : int):
    """ 
    Calculates the scale value for a specific layer in the feature map hierarchy.

    If only one stride exists, returns the average of min and max scales.
    Otherwise, linearly interpolates the scale based on the stride index.

    Notes
    ----------
    Based on :
     - https://github.com/vidursatija/BlazePalm/blob/master/ML/genarchors.py
     - https://github.com/hollance/BlazeFace-PyTorch/blob/master/Anchors.ipynb

    Parameters
    ----------
    min_scale : float
        Minimum anchor box scale.
    max_scale : float
        Maximum anchor box scale.
    stride_index : int
        The index of the current feature map layer.
    num_strides : int
        Total number of feature map layers (strides).

    Returns
    -------
    scale : float
        The calculated scale value for the current stride/layer.
    """
    if num_strides == 1:
        return (max_scale + min_scale) * 0.5
    return min_scale + (max_scale - min_scale) * stride_index / (num_strides - 1.0)

