import requests
import re
from datetime import datetime

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def get_and_post_ip(flag = 0):
    # yoseph token. please create your own in ngrok.com > dashboard.ngrok.com > API
    #my_token = "2jH5FjbHIXd9ydBF7FNGVzuX170_6d2YNPrfoeqfiQHuNNpc"
    #endpoint = "https://api.ngrok.com/endpoints"
    #headers = {"Ngrok-Version": "2"}
    #get_ngrok = requests.get(headers=headers, url=endpoint, auth=BearerAuth(my_token))
    #response = get_ngrok.json()

    #public_ip = None
    #ngrok_endpoints = response["endpoints"]
    #sorted_endpoints = sorted(
    #    ngrok_endpoints,
    #    key=lambda x: datetime.strptime(x["created_at"], "%Y-%m-%dT%H:%M:%SZ"),
    #)

    #for data in sorted_endpoints:
    #    if data["proto"] == "https" and ".ngrok.app" in data["public_url"]:
    #        public_ip = data["public_url"]
    #        break
    #
    print("")

    #if public_ip != None:
    #    post_device_ip = requests.post(
    #        f"http://203.100.57.59:3000/api/v1/camera",
    #        json={"vehicle_id": "MHFAA8AF7P0001003", "ip_address": public_ip,"flag": flag},
    #    )

    #    print(f"post_device_ip={post_device_ip.json()}")
    #else:
    #    print("failed to get and post public ip")

#get_and_post_ip()
