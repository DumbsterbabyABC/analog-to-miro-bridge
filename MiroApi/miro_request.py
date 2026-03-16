import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("MIRO_API_TOKEN")
board_id = os.getenv("MIRO_BOARD_ID")

import requests

url = f"https://api.miro.com/v2/boards/{board_id}/shapes"

payload = {
    "data": {
        "shape": "round_rectangle",
        "content": "Test"
    },
    "style": {
        "borderOpacity": "0",
        "fillColor": "#ffffff",
        "fontFamily": "arial",
        "fontSize": "14",
        "textAlign": "center",
        "textAlignVertical": "middle"
    },
    "position": {
        "x": 100,
        "y": 100
    },
    "geometry": {
        "height": 60,
        "width": 320
    }
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {token}"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)