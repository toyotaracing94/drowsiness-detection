import json


def get_anchor_options(anchor_model_path : str) -> dict:
    with open(anchor_model_path, 'r') as f:
        return json.load(f)
    
def get_model_config(inference_model_config : str) -> dict:
    with open(inference_model_config, 'r') as f:
        return json.load(f)