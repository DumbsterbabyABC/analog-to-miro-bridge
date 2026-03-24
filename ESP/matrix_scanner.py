import time
import machine
import onewire
import ds18x20


class MatrixScanner:
    def __init__(
        self,
        address_pins,
        id_zone_pins,
        zone_layout,
        zone_slot_rows,
        zone_slot_cols,
        channels_per_zone,
        matrix_cols,
    ):
        # Shared address lines for all multiplexers.
        self.s0 = machine.Pin(address_pins[0], machine.Pin.OUT)
        self.s1 = machine.Pin(address_pins[1], machine.Pin.OUT)
        self.s2 = machine.Pin(address_pins[2], machine.Pin.OUT)
        self.s3 = machine.Pin(address_pins[3], machine.Pin.OUT)

        self.zone_layout = zone_layout
        self.zone_slot_rows = zone_slot_rows
        self.zone_slot_cols = zone_slot_cols
        self.channels_per_zone = channels_per_zone
        self.matrix_cols = matrix_cols

        # EN pins are hardware-wired to GND (always enabled).

        self.id_zone_sensors = []

        zone_count = min(len(zone_layout), len(id_zone_pins))
        if zone_count == 0:
            raise RuntimeError("No zones configured: provide ID pins.")

        for zone_index in range(zone_count):
            id_pin = machine.Pin(id_zone_pins[zone_index])
            sensor = ds18x20.DS18X20(onewire.OneWire(id_pin))
            self.id_zone_sensors.append(sensor)

        self.zone_count = zone_count

    def set_channel(self, channel):
        self.s0.value(channel & 0b0001)
        self.s1.value((channel >> 1) & 0b0001)
        self.s2.value((channel >> 2) & 0b0001)
        self.s3.value((channel >> 3) & 0b0001)
        time.sleep_ms(5)

    def _zone_channel_to_slot(self, zone_index, channel):
        zone_row, zone_col = self.zone_layout[zone_index]

        local_row = channel // self.zone_slot_cols
        local_col = channel % self.zone_slot_cols

        global_row = zone_row * self.zone_slot_rows + local_row
        global_col = zone_col * self.zone_slot_cols + local_col
        return (global_row * self.matrix_cols) + global_col

    def zone_channel_to_slot(self, zone_index, channel):
        return self._zone_channel_to_slot(zone_index, channel)

    def scan_ids_once(self, max_slots):
        # Scan all configured zone ID muxes and map channel -> global slot.
        found_by_id = {}
        for zone_index in range(self.zone_count):
            sensor = self.id_zone_sensors[zone_index]

            for ch in range(self.channels_per_zone):
                self.set_channel(ch)
                time.sleep_ms(10)

                try:
                    roms = sensor.scan()
                    if roms:
                        for rom in roms:
                            hex_id = "".join(["%02x" % b for b in rom])
                            slot_index = self._zone_channel_to_slot(zone_index, ch)
                            if slot_index < max_slots and hex_id not in found_by_id:
                                found_by_id[hex_id] = slot_index
                except Exception:
                    pass

        return found_by_id
