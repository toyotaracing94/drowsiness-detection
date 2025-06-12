"""
====================================================================================================
                                      IMPORTANT NOTICE
====================================================================================================

This script is intended to be run on Linux systems only (Raspberry Pi 5).

It includes platform-specific logic and system-level functionality that are supported exclusively
on Unix-like operating systems. Running this script on Windows or macOS may result in errors or 
unsupported behavior.

Please ensure you are already created the virtual environment before executing this script.

Reference:
Google MediaPipe v0.10 models
https://github.com/google/mediapipe/blob/master/docs/solutions/models.md

====================================================================================================
"""

# All downloaded MediaPipe TFLite models should be placed under the following directory:
# 
#     hailo_model/tflite_model/
#     ├── hailo_model/
#     │   ├── tflite_model
#     │   ├── hef_model
#
# This allows the rest of the system to programmatically load models from a consistent path,
# especially when integrating with Hailo acceleration or fallback pipelines.

echo "Creating model directory structure..."

# Create target directory
cd ..
mkdir -p hailo_model/tflite_model

cd hailo_model/tflite_model

echo "Downloading MediaPipe TFLite models..."


## Face Mesh Detection Model from Mediapipe
wget https://storage.googleapis.com/mediapipe-assets/face_landmark.tflite
# [BlazeFaceLandmark.load_model] Model File :  ./models/face_landmark.tflite
# [BlazeFaceLandmark.load_model] Number of Inputs :  1
# [BlazeFaceLandmark.load_model] Input[ 0 ] Shape :  [  1 192 192   3]  ( input_1 )
# [BlazeFaceLandmark.load_model] Number of Outputs :  2
# [BlazeFaceLandmark.load_model] Output[ 0 ] Shape :  [   1    1    1 1404]  ( conv2d_21 )
# [BlazeFaceLandmark.load_model] Output[ 1 ] Shape :  [1 1 1 1]  ( conv2d_31 )

# wget https://storage.googleapis.com/mediapipe-assets/face_landmark_with_attention.tflite
# [BlazeFaceLandmark.load_model] Model File :  ./face_landmark_with_attention.tflite
# RuntimeError: Encountered unresolved custom op: Landmarks2TransformMatrix.


## Body Pose Detection Model from Mediapipe
wget https://storage.googleapis.com/mediapipe-assets/pose_landmark_full.tflite
# [BlazePoseLandmark.load_model] Model File :  ./models/pose_landmark_lite.tflite
# [BlazePoseLandmark.load_model] Number of Inputs :  1
# [BlazePoseLandmark.load_model] Input[ 0 ] Shape :  [  1 256 256   3]  ( input_1 )
# [BlazePoseLandmark.load_model] Number of Outputs :  5
# [BlazePoseLandmark.load_model] Output[ 0 ] Shape :  [  1 195]  ( Identity )
# [BlazePoseLandmark.load_model] Output[ 1 ] Shape :  [1 1]  ( Identity_1 )
# [BlazePoseLandmark.load_model] Output[ 2 ] Shape :  [  1 256 256   1]  ( Identity_2 )
# [BlazePoseLandmark.load_model] Output[ 3 ] Shape :  [ 1 64 64 39]  ( Identity_3 )
# [BlazePoseLandmark.load_model] Output[ 4 ] Shape :  [  1 117]  ( Identity_4 )

## Hand Detection Model from Mediapipe
wget https://storage.googleapis.com/mediapipe-assets/hand_landmark_full.tflite
# [BlazeHandLandmark.load_model] Model File :  ./models/hand_landmark_lite.tflite
# [BlazeHandLandmark.load_model] Number of Inputs :  1
# [BlazeHandLandmark.load_model] Input[ 0 ] Shape :  [  1 224 224   3]  ( input_1 )
# [BlazeHandLandmark.load_model] Number of Outputs :  4
# [BlazeHandLandmark.load_model] Output[ 0 ] Shape :  [ 1 63]  ( Identity )
# [BlazeHandLandmark.load_model] Output[ 1 ] Shape :  [1 1]  ( Identity_1 )
# [BlazeHandLandmark.load_model] Output[ 2 ] Shape :  [1 1]  ( Identity_2 )
# [BlazeHandLandmark.load_model] Output[ 3 ] Shape :  [ 1 63]  ( Identity_3 )

# Convert Face Landmark model
hailo_convert --tflite_model hailo_model/tflite_model/face_landmark.tflite --output_dir hailo_model/hef_models --output_model_name face_landmark.hef

# Convert Pose Landmark model
hailo_convert --tflite_model hailo_model/tflite_model/pose_landmark_full.tflite --output_dir hailo_model/hef_models --output_model_name pose_landmark_full.hef

# Convert Hand Landmark model
hailo_convert --tflite_model hailo_model/tflite_model/hand_landmark_full.tflite --output_dir hailo_model/hef_models --output_model_name hand_landmark_full.hef

echo "Conversion complete. .hef models are stored in hailo_model/hef_models."

# Final output
echo "All operations completed successfully."