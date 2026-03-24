class PCF8575:
    def __init__(self, i2c, address=0x20):
        self.i2c = i2c
        self.address = address
        self.state = 0xFFFF

    def read16(self):
        data = self.i2c.readfrom(self.address, 2)
        return data[0] | (data[1] << 8)

    def write16(self, value):
        self.state = value & 0xFFFF
        payload = bytes((self.state & 0xFF, (self.state >> 8) & 0xFF))
        self.i2c.writeto(self.address, payload)

    def set_pin(self, pin, value):
        if pin < 0 or pin > 15:
            raise ValueError("pin must be in range 0..15")

        if value:
            self.state |= (1 << pin)
        else:
            self.state &= ~(1 << pin)

        self.write16(self.state)

    def get_pin(self, pin):
        if pin < 0 or pin > 15:
            raise ValueError("pin must be in range 0..15")

        value = self.read16()
        return 1 if (value & (1 << pin)) else 0

    def set_all_inputs(self):
        # PCF8575: writing 1 releases pin (quasi input mode).
        self.write16(0xFFFF)
