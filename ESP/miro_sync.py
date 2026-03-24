import time
import gc
import urequests as requests
import ujson as json


class MiroSync:
    def __init__(
        self,
        token,
        board_id,
        cache_file,
        rows,
        cols,
        x_spacing,
        y_spacing,
        default_shape_width=220,
        default_shape_height=120,
        display_overrides=None,
    ):
        self.token = token
        self.board_id = board_id
        self.cache_file = cache_file
        self.rows = rows
        self.cols = cols
        self.x_spacing = x_spacing
        self.y_spacing = y_spacing
        self.default_shape_width = default_shape_width
        self.default_shape_height = default_shape_height
        self.display_overrides = display_overrides or {}

    def _display_for_id(self, element_id, slot_index):
        override = self.display_overrides.get(element_id, {})

        content = override.get(
            "content",
            "ID {} | Slot {}".format(element_id, slot_index),
        )
        width = int(override.get("width", self.default_shape_width))
        height = int(override.get("height", self.default_shape_height))
        fill_color = override.get("fillColor", "#ffffff")
        font_size = str(override.get("fontSize", "20"))

        return {
            "content": content,
            "width": width,
            "height": height,
            "fillColor": fill_color,
            "fontSize": font_size,
        }

    def _request(self, method, path, payload=None, retries=3):
        url = "https://api.miro.com/v2/boards/" + self.board_id + path
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token,
        }
        body = json.dumps(payload) if payload is not None else None

        for attempt in range(1, retries + 1):
            response = None
            try:
                response = requests.request(method, url, headers=headers, data=body)
                status = response.status_code
                text = response.text
                if 200 <= status < 300:
                    if text:
                        return True, status, json.loads(text)
                    return True, status, None

                print("Miro error", status, "on", method, path)
                if text:
                    print(text)
            except Exception as err:
                print("Miro request failed (try {})".format(attempt), err)
            finally:
                if response is not None:
                    response.close()

            time.sleep(2)

        return False, 0, None

    def slot_to_xy(self, slot_index):
        row = slot_index // self.cols
        col = slot_index % self.cols
        x = int((col - (self.cols - 1) / 2) * self.x_spacing)
        y = int((row - (self.rows - 1) / 2) * self.y_spacing)
        return x, y

    def load_cache(self):
        try:
            with open(self.cache_file, "r") as file_obj:
                data = json.loads(file_obj.read())
                if "shapes" not in data:
                    data["shapes"] = {}
                if "connectors" not in data:
                    data["connectors"] = {}
                return data
        except Exception:
            return {"shapes": {}, "connectors": {}}

    def save_cache(self, cache):
        try:
            with open(self.cache_file, "w") as file_obj:
                file_obj.write(json.dumps(cache))
        except Exception as err:
            print("Could not save cache:", err)

    def create_or_update_shape(self, element_id, slot_index, cache):
        x, y = self.slot_to_xy(slot_index)
        display = self._display_for_id(element_id, slot_index)
        payload = {
            "data": {
                "content": display["content"],
                "shape": "round_rectangle",
            },
            "style": {
                "borderOpacity": "0",
                "fillColor": display["fillColor"],
                "fontFamily": "arial",
                "fontSize": display["fontSize"],
                "textAlign": "center",
                "textAlignVertical": "middle"
            },
            "geometry": {
                "width": display["width"],
                "height": display["height"],
            },
            "position": {
                "x": x,
                "y": y,
                "origin": "center",
            },
        }

        shapes = cache.get("shapes", {})
        item_id = shapes.get(element_id)

        if item_id:
            ok, _, _ = self._request("PATCH", "/shapes/" + item_id, payload)
            if not ok:
                # Fallback for boards/accounts where item patch is more permissive.
                ok, _, _ = self._request("PATCH", "/items/" + item_id, payload)
            if ok:
                print("Shape updated:", element_id)
                return True

        ok, _, data = self._request("POST", "/shapes", payload)
        if ok and data and "id" in data:
            shapes[element_id] = data["id"]
            cache["shapes"] = shapes
            print("Shape created:", element_id)
            return True

        print("Could not write shape:", element_id)
        return False

    def delete_shape(self, element_id, cache):
        shapes = cache.get("shapes", {})
        item_id = shapes.get(element_id)
        if not item_id:
            return

        ok, _, _ = self._request("DELETE", "/shapes/" + item_id, None)
        if not ok:
            ok, _, _ = self._request("DELETE", "/items/" + item_id, None)
        if ok:
            print("Shape deleted:", element_id)
        else:
            print("Shape delete failed:", element_id)

        if element_id in shapes:
            del shapes[element_id]
        cache["shapes"] = shapes

    def sync_ids(self, current_ids, cache):
        current_id_set = set(current_ids.keys())
        cached_id_set = set(cache.get("shapes", {}).keys())

        for element_id, slot_index in current_ids.items():
            self.create_or_update_shape(element_id, slot_index, cache)
            gc.collect()

        removed_ids = cached_id_set - current_id_set
        for element_id in removed_ids:
            self.delete_shape(element_id, cache)
            gc.collect()

    def _pair_key(self, left_id, right_id):
        if left_id > right_id:
            left_id, right_id = right_id, left_id
        return "{}|{}".format(left_id, right_id)

    def _parse_pair_key(self, pair_key):
        parts = pair_key.split("|")
        if len(parts) != 2:
            return None, None
        return parts[0], parts[1]

    def create_connector(self, left_element_id, right_element_id, cache):
        shapes = cache.get("shapes", {})
        connectors = cache.get("connectors", {})

        left_item_id = shapes.get(left_element_id)
        right_item_id = shapes.get(right_element_id)
        if not left_item_id or not right_item_id:
            return False

        pair_key = self._pair_key(left_element_id, right_element_id)
        if pair_key in connectors:
            return False

        payload = {
            "startItem": {
                "id": left_item_id,
                "snapTo": "bottom"
            },
            "endItem": {
                "id": right_item_id,
                "snapTo": "bottom"
            },
            "style": {
                "strokeColor": "#a00000",
                "strokeWidth": 3,
                "endStrokeCap": "none"
            },
        }

        ok, _, data = self._request("POST", "/connectors", payload)
        if ok and data and "id" in data:
            connectors[pair_key] = data["id"]
            cache["connectors"] = connectors
            print("Connector created:", pair_key)
            return True

        print("Could not create connector:", pair_key)
        return False

    def delete_connector_by_key(self, pair_key, cache):
        connectors = cache.get("connectors", {})
        connector_id = connectors.get(pair_key)
        if not connector_id:
            return False

        ok, _, _ = self._request("DELETE", "/connectors/" + connector_id, None)
        if not ok:
            ok, _, _ = self._request("DELETE", "/items/" + connector_id, None)

        if ok:
            print("Connector deleted:", pair_key)
        else:
            print("Connector delete failed:", pair_key)

        if pair_key in connectors:
            del connectors[pair_key]
        cache["connectors"] = connectors
        return True

    def remove_connectors_for_missing_shapes(self, cache):
        shapes = cache.get("shapes", {})
        connectors = cache.get("connectors", {})

        to_remove = []
        for pair_key in connectors.keys():
            left_id, right_id = self._parse_pair_key(pair_key)
            if not left_id or not right_id:
                to_remove.append(pair_key)
                continue
            if left_id not in shapes or right_id not in shapes:
                to_remove.append(pair_key)

        changed = False
        for pair_key in to_remove:
            if self.delete_connector_by_key(pair_key, cache):
                changed = True
                gc.collect()

        return changed

    def sync_connections(self, id_pairs, cache):
        desired = {}
        for left_id, right_id in id_pairs:
            if left_id == right_id:
                continue
            pair_key = self._pair_key(left_id, right_id)
            desired[pair_key] = True

        connectors = cache.get("connectors", {})
        current = {}
        for key in connectors.keys():
            current[key] = True

        changed = False

        # Remove connectors that are no longer desired.
        for pair_key in current.keys():
            if pair_key not in desired:
                if self.delete_connector_by_key(pair_key, cache):
                    changed = True
                    gc.collect()

        # Create new desired connectors.
        for pair_key in desired.keys():
            if pair_key not in current:
                left_id, right_id = self._parse_pair_key(pair_key)
                if left_id and right_id:
                    if self.create_connector(left_id, right_id, cache):
                        changed = True
                        gc.collect()

        # Cleanup stale connectors that point to missing shapes.
        if self.remove_connectors_for_missing_shapes(cache):
            changed = True

        return changed
