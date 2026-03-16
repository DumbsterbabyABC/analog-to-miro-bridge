import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("MIRO_API_TOKEN")
board_id = os.getenv("MIRO_BOARD_ID")

url = f"https://api.miro.com/v2/boards/{board_id}/sticky_notes"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {token}"
}

payload = {
    "data": {
        "content": "FIck Benke",
        "shape": "square"
    },
    "position": {
        "x": 0,
        "y": 0,
        "origin": "center"
    }
}

response = requests.post(url, headers=headers, json=payload)

print(response.text)