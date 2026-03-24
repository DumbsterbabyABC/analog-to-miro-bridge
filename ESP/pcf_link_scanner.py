import time


class PCFLinkScanner:
    def __init__(self, expanders, settle_ms=2):
        self.expanders = expanders
        self.settle_ms = settle_ms

    def _all_inputs(self):
        for expander in self.expanders:
            expander.set_all_inputs()

    def _read_states(self):
        states = []
        for expander in self.expanders:
            states.append(expander.read16())
        return states

    def scan_links_once(self):
        # Baseline with all pins released (weak high).
        self._all_inputs()
        time.sleep_ms(self.settle_ms)
        baseline = self._read_states()

        pairs = {}
        expander_count = len(self.expanders)

        for src_idx in range(expander_count):
            for src_pin in range(16):
                # Release everything, then drive exactly one pin low.
                self._all_inputs()
                self.expanders[src_idx].write16(0xFFFF & ~(1 << src_pin))
                time.sleep_ms(self.settle_ms)

                states = self._read_states()

                for dst_idx in range(expander_count):
                    for dst_pin in range(16):
                        if src_idx == dst_idx and src_pin == dst_pin:
                            continue

                        base_bit = (baseline[dst_idx] >> dst_pin) & 0x1
                        now_bit = (states[dst_idx] >> dst_pin) & 0x1

                        # If a pin falls from high to low when src is driven low,
                        # treat it as electrically connected.
                        if base_bit == 1 and now_bit == 0:
                            left = (src_idx, src_pin)
                            right = (dst_idx, dst_pin)
                            if left > right:
                                left, right = right, left
                            pairs[(left, right)] = True

        self._all_inputs()

        result = []
        for pair in pairs.keys():
            result.append(pair)
        result.sort()
        return result


def pcf_pin_label(pin):
    if pin < 8:
        return "P{}".format(pin)
    return "P1{}".format(pin - 8)


def format_link_pair(pair, addresses):
    (left_exp, left_pin), (right_exp, right_pin) = pair
    left_addr = addresses[left_exp]
    right_addr = addresses[right_exp]

    return "0x{:02X}.{} <-> 0x{:02X}.{}".format(
        left_addr,
        pcf_pin_label(left_pin),
        right_addr,
        pcf_pin_label(right_pin),
    )


def _zone_pin_to_slot(zone_index, pin_index, zone_layout, zone_slot_rows, zone_slot_cols, matrix_cols, zone_pin_order):
    try:
        local_linear = zone_pin_order.index(pin_index)
    except ValueError:
        return None

    zone_row, zone_col = zone_layout[zone_index]
    local_row = local_linear // zone_slot_cols
    local_col = local_linear % zone_slot_cols
    global_row = zone_row * zone_slot_rows + local_row
    global_col = zone_col * zone_slot_cols + local_col
    return (global_row * matrix_cols) + global_col


def link_pair_to_slots(
    pair,
    expander_zone_indices,
    zone_pin_order,
    zone_channel_to_slot,
    max_slots,
):
    (left_exp, left_pin), (right_exp, right_pin) = pair
    left_zone = expander_zone_indices[left_exp]
    right_zone = expander_zone_indices[right_exp]

    try:
        left_channel = zone_pin_order.index(left_pin)
        right_channel = zone_pin_order.index(right_pin)
    except ValueError:
        return None

    left_slot = zone_channel_to_slot(left_zone, left_channel)
    right_slot = zone_channel_to_slot(right_zone, right_channel)

    if left_slot is None or right_slot is None:
        return None
    if left_slot >= max_slots or right_slot >= max_slots:
        return None

    if left_slot > right_slot:
        left_slot, right_slot = right_slot, left_slot
    return (left_slot, right_slot)
