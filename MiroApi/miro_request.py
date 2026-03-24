import os
import requests
from dotenv import load_dotenv

load_dotenv()

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class Element:
    def __init__(self, content, position, size, id):
        self.content = content
        self.position = position
        self.size = size
        self.id = id


def create_shape(content, position, size):
    token = os.getenv("MIRO_API_TOKEN")
    board_id = os.getenv("MIRO_BOARD_ID")
    url = f"https://api.miro.com/v2/boards/{board_id}/shapes"

    payload = {
        "data": {
            "shape": "round_rectangle",
            "content": content
        },
        "style": {
            "borderOpacity": "0",
            "fillColor": "#ffffff",
            "fontFamily": "arial",
            "fontSize": "20",
            "textAlign": "left",
            "textAlignVertical": "middle"
        },
        "position": {
            "x": position.x,
            "y": position.y
        },
        "geometry": {
            "height": size.height * 80 + 20 * (size.height-1),
            "width": size.width * 80 + 20 * (size.width-1)
        }
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {token}"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    response_data = response.json()
    shape_id = response_data.get("id")
    return shape_id

def delete_element(element_id):
    token = os.getenv("MIRO_API_TOKEN")
    board_id = os.getenv("MIRO_BOARD_ID")

    url = f"https://api.miro.com/v2/boards/{board_id}/shapes/{element_id}"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}"
    }
    requests.delete(url, headers=headers)

