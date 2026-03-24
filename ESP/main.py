import time
import machine
from config import WIFI_SSID, WIFI_PASSWORD
from config import ACCESS_TOKEN, BOARD_ID
from config import SCAN_INTERVAL_S, MATRIX_ROWS, MATRIX_COLS, MAX_SLOTS
from config import X_SPACING, Y_SPACING, CACHE_FILE
from config import DEFAULT_SHAPE_WIDTH, DEFAULT_SHAPE_HEIGHT, SENSOR_DISPLAY_OVERRIDES
from config import ADDR_PINS, ID_ZONE_PINS
from config import ZONE_LAYOUT, ZONE_SLOT_ROWS, ZONE_SLOT_COLS, CHANNELS_PER_ZONE
from config import PCF8575_ENABLED, I2C_SDA_PIN, I2C_SCL_PIN, I2C_FREQ
from config import PCF8575_ADDRESSES, PCF8575_LINK_SCAN_ENABLED, PCF8575_LINK_SETTLE_MS
from config import PCF8575_ZONE_PIN_ORDER
from wifi_utils import connect_wifi
from matrix_scanner import MatrixScanner
from miro_sync import MiroSync
from pcf8575 import PCF8575
from pcf_link_scanner import PCFLinkScanner, format_link_pair, link_pair_to_slots


def init_pcf8575():
    if not PCF8575_ENABLED:
        return [], [], []

    i2c = machine.I2C(
        0,
        scl=machine.Pin(I2C_SCL_PIN),
        sda=machine.Pin(I2C_SDA_PIN),
        freq=I2C_FREQ,
    )
    devices = i2c.scan()
    device_hex = ["0x{:02X}".format(addr) for addr in devices]
    print("I2C devices:", device_hex)

    found_addresses = []
    expanders = []
    found_zone_indices = []
    for zone_index in range(len(PCF8575_ADDRESSES)):
        address = PCF8575_ADDRESSES[zone_index]
        if address in devices:
            expander = PCF8575(i2c, address)
            expander.set_all_inputs()
            print("PCF8575 ready at 0x{:02X}, state=0x{:04X}".format(address, expander.read16()))
            expanders.append(expander)
            found_addresses.append(address)
            found_zone_indices.append(zone_index)
        else:
            print("PCF8575 missing at 0x{:02X}".format(address))

    return expanders, found_addresses, found_zone_indices

# --- HAUPTPROGRAMM ---

try:
    # pcf_expanders, pcf_addresses, pcf_zone_indices = init_pcf8575()
    # link_scanner = None
    # last_links = None
    # last_slot_links = None
    # if PCF8575_LINK_SCAN_ENABLED and pcf_expanders:
    #     link_scanner = PCFLinkScanner(pcf_expanders, settle_ms=PCF8575_LINK_SETTLE_MS)

    connect_wifi(WIFI_SSID, WIFI_PASSWORD)

    scanner = MatrixScanner(
        address_pins=ADDR_PINS,
        id_zone_pins=ID_ZONE_PINS,
        zone_layout=ZONE_LAYOUT,
        zone_slot_rows=ZONE_SLOT_ROWS,
        zone_slot_cols=ZONE_SLOT_COLS,
        channels_per_zone=CHANNELS_PER_ZONE,
        matrix_cols=MATRIX_COLS,
    )
    miro = MiroSync(
        token=ACCESS_TOKEN,
        board_id=BOARD_ID,
        cache_file=CACHE_FILE,
        rows=MATRIX_ROWS,
        cols=MATRIX_COLS,
        x_spacing=X_SPACING,
        y_spacing=Y_SPACING,
        default_shape_width=DEFAULT_SHAPE_WIDTH,
        default_shape_height=DEFAULT_SHAPE_HEIGHT,
        display_overrides=SENSOR_DISPLAY_OVERRIDES,
    )

    cache = miro.load_cache()
    last_snapshot = None

    print("Start ID sync (ESP32 -> Miro)...")
    print("=" * 50)
    while True:
        current_ids = scanner.scan_ids_once(MAX_SLOTS)
        cache_dirty = False
        id_pairs = []

        if current_ids != last_snapshot:
            print("Change detected. IDs:", len(current_ids))
            miro.sync_ids(current_ids, cache)
            cache_dirty = True
            last_snapshot = current_ids
        else:
            print("No ID changes. IDs:", len(current_ids))

        # if link_scanner is not None:
        #     links = link_scanner.scan_links_once()
        #     if links != last_links:
        #         print("PCF links:", len(links))
        #         for pair in links:
        #             print("  ", format_link_pair(pair, pcf_addresses))
        #         last_links = links

        #     slot_pairs = []
        #     for pair in links:
        #         slot_pair = link_pair_to_slots(
        #             pair,
        #             pcf_zone_indices,
        #             PCF8575_ZONE_PIN_ORDER,
        #             scanner.zone_channel_to_slot,
        #             MAX_SLOTS,
        #         )
        #         if slot_pair is not None and slot_pair not in slot_pairs:
        #             slot_pairs.append(slot_pair)

        #     slot_pairs.sort()

            id_by_slot = {}
            for element_id, slot_index in current_ids.items():
                id_by_slot[slot_index] = element_id

        #     id_pairs = []
        #     for left_slot, right_slot in slot_pairs:
        #         left_id = id_by_slot.get(left_slot)
        #         right_id = id_by_slot.get(right_slot)
        #         if left_id is not None and right_id is not None:
        #             id_pairs.append((left_id, right_id))

        #     if slot_pairs != last_slot_links:
        #         print("PCF slot links:", len(slot_pairs))
        #         for left_slot, right_slot in slot_pairs:
        #             print("   Slot {} <-> Slot {}".format(left_slot, right_slot))

        #         if id_pairs:
        #             print("PCF ID links:", id_pairs)

        #         last_slot_links = slot_pairs

        # if link_scanner is not None:
        #     if miro.sync_connections(id_pairs, cache):
        #         cache_dirty = True

        if cache_dirty:
            miro.save_cache(cache)

        time.sleep(SCAN_INTERVAL_S)
except Exception as err:
    print("Program aborted:", err)