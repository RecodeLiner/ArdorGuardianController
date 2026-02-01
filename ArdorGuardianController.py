import hid
import time

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

    def set_effect(self, effect_type, r = 0x00, g = 0x00, b = 0x00, brightness=4, speed=0, isClockwise=False, save_to_memory=False):
        if not self.device:
            return
        
        if not 0 <= brightness <= 4:
            brightness = 4
        if not 0 <= speed <= 4:
            speed = 0
        
        cmd = 0x27 if not save_to_memory else 0x37
        
        packet = [
            0x04, cmd, 0x01, 0x06,
            0x22, 0x00, 0x00, 0x00,
            0x00, effect_type, brightness, speed,
            isClockwise, 0x00, r, g, b
        ]
        packet += [0x00] * (64 - len(packet))
        
        self.device.write(packet)

    def set_pulse_mode(self, r, g, b, brightness=4, speed=0, isClockwise=False, save_to_memory=False):
        self.set_effect(0x01, r = r, g = g, b = b, brightness = brightness, speed = speed, isClockwise=not(isClockwise), save_to_memory=save_to_memory)

    def set_impulse_mode(self, r, g, b, brightness=4, speed=0, isClockwise=False, save_to_memory=False):
        self.set_effect(0x02, r = r, g = g, b = b, brightness = brightness, speed = speed, isClockwise=not(isClockwise), save_to_memory=save_to_memory)

    def set_waterfall_mode(self, r, g, b, brightness=4, speed=0, isClockwise=False, save_to_memory=False):
        self.set_effect(0x03, r = r, g = g, b = b, brightness = brightness, speed = speed, isClockwise=isClockwise, save_to_memory=save_to_memory)

    def set_rainbow_mode(self, r, g, b, brightness=4, speed=0, save_to_memory=False):
        self.set_effect(0x04, r = r, g = g, b = b, brightness = brightness, speed = speed, save_to_memory=save_to_memory)

    def set_breath_mode(self, r, g, b, brightness=4, speed=0, save_to_memory=False):
        self.set_effect(0x05, r = r, g = g, b = b, brightness = brightness, speed = speed, save_to_memory=save_to_memory)

    def set_static_color(self, r, g, b, brightness=4, save_to_memory=False):
        self.set_effect(0x06, r = r, g = g, b = b, brightness = brightness, save_to_memory=save_to_memory)

    def set_interactive_mode(self, r, g, b, brightness=4, speed=0, save_to_memory=False):
        self.set_effect(0x07, r = r, g = g, b = b, brightness = brightness, speed = speed, save_to_memory=save_to_memory)

    def set_wave_mode(self, r, g, b, brightness=4, speed=0, save_to_memory=False):
        self.set_effect(0x08, r = r, g = g, b = b, brightness = brightness, speed = speed, save_to_memory=save_to_memory)

    def set_arrow_mode(self, r, g, b, brightness=4, speed=0, save_to_memory=False):
        self.set_effect(0x09, r = r, g = g, b = b, brightness = brightness, speed = speed, save_to_memory=save_to_memory)

    def set_flicker_mode(self, r, g, b, brightness=4, speed=0, save_to_memory=False):
        self.set_effect(0x0a, r = r, g = g, b = b, brightness = brightness, speed = speed, save_to_memory=save_to_memory)

    def close(self):
        if self.device:
            try:
                self.device.write([0x04, 0x02, 0x00, 0x02] + [0x00] * 60)
                self.device.close()
            except:
                pass
