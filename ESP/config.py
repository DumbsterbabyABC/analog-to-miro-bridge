# Project configuration
WIFI_SSID = "MPEC-FORSCHUNGS-WLAN"
WIFI_PASSWORD = "987654321"

ACCESS_TOKEN = "eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_EwWJswwmbGHOslzMNlEDpfEssnw"
BOARD_ID = "uXjVGxepuTQ%3D"

SCAN_INTERVAL_S = 5
MATRIX_ROWS = 6
MATRIX_COLS = 10
MAX_SLOTS = MATRIX_ROWS * MATRIX_COLS

# Shared mux address lines S0..S3.
ADDR_PINS = (13, 26, 14, 27)

# Cluster layout: 4 zones, each zone is 5 columns x 3 rows.
ZONE_ROWS = 2
ZONE_COLS = 2
ZONE_SLOT_ROWS = 3
ZONE_SLOT_COLS = 5
CHANNELS_PER_ZONE = ZONE_SLOT_ROWS * ZONE_SLOT_COLS  # 15 channels used per mux

# Zone positions in the 6x10 matrix: top-left, top-right, bottom-left, bottom-right.
ZONE_LAYOUT = (
	(0, 0),
	(0, 1),
	(1, 0),
	(1, 1),
)

# One GPIO per zone for ID mux output.
# TODO: Set all four zones once hardware pins are finalized.
ID_ZONE_PINS = (4,16,17,5)

X_SPACING = 180
Y_SPACING = 150
CACHE_FILE = "miro_cache.json"

# Miro shape defaults and per-sensor overrides.
DEFAULT_SHAPE_WIDTH = 220
DEFAULT_SHAPE_HEIGHT = 120

# Key: sensor ID (hex string from DS18x20 scan)
# Values (optional):
# - content: text shown in Miro shape
# - width: shape width in px
# - height: shape height in px
# - fillColor: e.g. "#ffffff"
# - fontSize: e.g. "20"
SENSOR_DISPLAY_OVERRIDES = {
	"285bb954000000a2": {"content": "Pumpe A", "width": 320, "height": 140},
    "288461520000002b": {"content": "Heizer", "width": 320, "height": 140},
}

# PCF8575 I2C expander (A0/A1/A2 -> GND => 0x20)
PCF8575_ENABLED = True
I2C_SDA_PIN = 22
I2C_SCL_PIN = 23
I2C_FREQ = 100000
PCF8575_ADDRESSES = (0x20, 0x21, 0x22, 0x23)

# 3x5 zone mapping uses 15 pins per PCF.
# Pin indices are internal 0..15, where 8..15 correspond to labels P10..P17.
# Default uses P0..P7 and P10..P16 (leaves P17 unused).
PCF8575_ZONE_PIN_ORDER = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)

# Active link scan over all PCF pins.
PCF8575_LINK_SCAN_ENABLED = True
PCF8575_LINK_SETTLE_MS = 2
