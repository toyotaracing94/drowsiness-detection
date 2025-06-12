import ngrok
from ngrok.datatypes import *

client = ngrok.Client("2jH5FjbHIXd9ydBF7FNGVzuX170_6d2YNPrfoeqfiQHuNNpc")

url = ""
for t in client.tunnels.list():
    if t.forwards_to == "http://localhost:80" and ".ngrok.app" in t.public_url:
        url = t.public_url
        break

print(f"final url >>> {url}")
