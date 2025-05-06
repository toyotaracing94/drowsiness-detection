
import json
import numpy as np
import cv2
import base64
import datetime

from websockets.sync.client import connect

from src.utils.logging import logging_default

class SocketTrigger:
    def __init__(self, api_settings_path : str):
        
        # Load configurations first
        self.load_configurations(api_settings_path)


    def load_configurations(self, path : str) -> None:
        """
        Load the detection settings from a configuration JSON file.

        Parameters
        ----------
        path : str
            Path to the configuration file containing api settings to save the triggered event image.
        """ 
        logging_default.info("Loading api configs and model configuration")
        
        with open(path, 'r') as f:
            config = json.load(f)
        
        self.vehicle_id = config["vehicle_id"]
        self.server_ip = config["server"]
        self.device_name = config["device"]
        self.send_to_server = config["send_to_server"]

        
        # Construct the WebSocket URL
        self.ws_url = f"ws://{self.server_ip}?vehicle_id={self.vehicle_id}&device={self.device_name}"

    def save_image(self, image : np.ndarray, event, target : str = '', wsEvent : str = '') -> None:
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
        
        wsEvent : str, optional
            The WebSocket event type (default is '').

        Raises
        ------
        Exception
            If there is an error during the process (e.g., saving, encoding, or sending).
        """
        try:
            # Log the beginning of the process
            logging_default.info(f"Saving image for event: {event}, target: {target}, websocket event: {wsEvent}")

            if self.send_to_server:
                with connect(self.ws_url) as websocket:
                    # Save the file in the local system
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    cv2.imwrite(f"image_event/frame{timestamp}.jpg", image)

                    with open(f"image_event/frame{timestamp}.jpg", "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                        jsonData = {
                            "event" : wsEvent,
                            "vehicle_id" : self.vehicle_id,
                            "target" : target,
                            "data" : {
                                "message": "Image Upload",
                                "image": "%s"%encoded_string,
                                "behavior_type" : event
                            }
                        }
                        websocket.send(json.dumps(jsonData))
                        message = websocket.recv()
                        logging_default.info(f"Image saved successfully for event: {event}. Message : {message}")
            else:
                logging_default.info(f"Will not send any event to server. It's on DEBUG mode!")

        except Exception as e:
            logging_default.error(f"Error saving image for event: {event}. Error: {e}")
