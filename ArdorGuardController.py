class ArdorGuardianController:
    def __init__(self):
        self.vendor_id = 0x320F
        self.product_id = 0x5055
        self.device = None
        self.path = None

    def _get_device_path(self):
        devices = hid.enumerate(self.vendor_id, self.product_id)
        mi01_devices = [d for d in devices if b'MI_01' in d['path']]

        for dev in mi01_devices:
            device = hid.device()
            try:
                device.open_path(dev['path'])
                result = device.write([0x04, 0x20, 0x00, 0x1a, 0x06] + [0x00] * 59)
                device.close()
                if result > 0:
                    return dev['path']
            except:
                try:
                    device.close()
                except:
                    pass
        return None
    
    def _sync(self):
        self.device.write([0x04, 0x01, 0x00, 0x01] + [0x00] * 60)

    def _finalize(self):
        self.device.write([0x04, 0x02, 0x00, 0x02] + [0x00] * 60)


    def connect(self):
        self.path = self._get_device_path()
        if not self.path:
            raise Exception("Ardor Guardian Not Found")

        self.device = hid.device()
        self.device.open_path(self.path)

        # init sequence
        self.device.write([0x04, 0x20, 0x00, 0x1a, 0x06] + [0x00] * 59)
        time.sleep(0.05)
        self.device.write([0x04, 0x01, 0x00, 0x01] + [0x00] * 60)
        time.sleep(0.05)
        
    def set_color(self, r, g, b, brightness=4, save_to_memory=False):
        if not self.device:
            return

        BRIGHTNESS_CODES = [0xd0, 0xd3, 0xd7, 0xdb, 0xdf]

        if not 0 <= brightness <= 4:
            brightness = 2

        code = BRIGHTNESS_CODES[brightness]

        cmd = 0x27 if not save_to_memory else 0x37

        packet = [
            0x04, cmd, 0x01, 0x06, 0x22,
            0x00, 0x00, 0x00, 0x00,
            0x06, brightness, 0x02, 0x00, 0x00,
            r, g, b
        ]

        packet += [0x00] * (64 - len(packet))
        self.device.write(packet)

    def close(self):
        if self.device:
            try:
                self.device.write([0x04, 0x02, 0x00, 0x02] + [0x00] * 60)
                self.device.close()
            except:
                pass
