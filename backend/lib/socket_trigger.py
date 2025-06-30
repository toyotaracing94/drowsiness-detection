
import base64
import json
import os

import cv2
import numpy as np
from websockets.sync.client import connect

from backend.settings.app_config import ApiSettings
from backend.utils.logging import logging_default


class SocketTrigger:
    def __init__(self, api_settings_path : str):
        
        # Load configurations first
        self.load_configurations(api_settings_path)


    def load_configurations(self, api_settings: ApiSettings) -> None:
        """
        Load the detection settings from a configuration JSON file.

        Parameters
        ----------
        path : str
            Path to the configuration file containing api settings to save the triggered event image.
        """ 
        logging_default.info("Loading api configs and model configuration")
                
        self.vehicle_id = api_settings.vehicle_id
        self.server_ip = api_settings.server
        self.device_name = api_settings.device
        self.send_to_server = api_settings.send_to_server
        self.image_event_path = os.path.join(api_settings.static_dir, api_settings.image_event_dir)

        # Construct the WebSocket URL
        self.ws_url = f"ws://{self.server_ip}?vehicle_id={self.vehicle_id}&device={self.device_name}"

        logging_default.info(
            f"Loaded config - Vehicle ID: {self.vehicle_id}, Server: {self.server_ip}, "\
            f"Device: {self.device_name}, Send to Server: {self.send_to_server}, WS URL: {self.ws_url}"
        )

    def save_image(self, image : np.ndarray, image_uuid : str, event, target : str = '', ws_event : str = '') -> None:
        """
        Save the image locally, encode it in base64, and send it to the WebSocket server.

        Parameters
        ----------
        image : np.ndarray
            The image to be saved and sent.
        
        event : str
            The event related to the image (e.g., "drowsiness_detected").
        
        target : str, optional
            The target associated with the event (default is '').
        
        ws_event : str, optional
            The WebSocket event type (default is '').

        Raises
        ------
        Exception
            If there is an error during the process (e.g., saving, encoding, or sending).
        """
        try:
            # Log the beginning of the process
            logging_default.info(f"Saving image for event: {event}, target: {target}, websocket event: {ws_event}")
            os.makedirs(self.image_event_path, exist_ok=True)

            # Save the file in the local system
            cv2.imwrite(f"{self.image_event_path}/{image_uuid}.jpg", image)

            if self.send_to_server:
                with connect(self.ws_url) as websocket: 
                    with open(f"{self.image_event_path}/{image_uuid}.jpg", "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                        json_data = {
                            "event" : ws_event,
                            "vehicle_id" : self.vehicle_id,
                            "target" : target,
                            "data" : {
                                "message": "Image Upload",
                                "image": encoded_string.decode("utf-8"),
                                "behavior_type" : event
                            }
                        }
                        websocket.send(json.dumps(json_data))
                        message = websocket.recv()
                        logging_default.info(f"Image saved successfully for event: {event}. Message : {message}")
            else:
                logging_default.info("Will not send any event to server. It's on DEBUG mode!")

        except Exception as e:
            logging_default.error(f"Error saving image for event: {event}. Error: {e}")
