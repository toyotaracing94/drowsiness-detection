import json

from pydantic import BaseModel


class PipelineSettings(BaseModel):
    drowsiness_model_run: bool
    phone_detection_model_run: bool
    hands_detection_model_run: bool

class ConnectionStrings(BaseModel):
    db_connections: str

class ApiSettings(BaseModel):
    vehicle_id: str
    server: str
    device: str
    send_to_server: bool

class AppConfig(BaseModel):
    PipelineSettings: PipelineSettings
    ConnectionStrings: ConnectionStrings
    ApiSettings: ApiSettings

    @classmethod
    def load(cls, path: str = "config/app_settings.json"):
        with open(path) as f:
            data = json.load(f)
        return cls(**data)

# Load the config once
settings = AppConfig.load()
