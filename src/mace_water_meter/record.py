import time
from struct import pack, unpack
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app_config import MaceWaterMeterConfig


class Record:
    def __init__(self, register_values, config: "MaceWaterMeterConfig"):
        self.register_values = register_values
        self.ts = time.time()
        self.config = config

    def read_both_registers(self, reg_num) -> float | None:
        if reg_num is None:
            return None
        high = self.register_values[reg_num - 1]
        low = self.register_values[reg_num]

        # big endian: two 16-bit words → 32-bit IEEE 754 float
        payload = pack("!2H", high, low)
        return unpack("!f", payload[0:4])[0]

    @property
    def velocity(self) -> float | None:
        return self.read_both_registers(self.config.velocity_register.value)

    @property
    def current_flow(self) -> float | None:
        return self.read_both_registers(self.config.flow_register.value)

    @property
    def total(self) -> float | None:
        return self.read_both_registers(self.config.total_register.value)

    @property
    def battery_volts(self) -> float | None:
        return self.read_both_registers(self.config.battery_register.value)

    @property
    def solar_volts(self) -> float | None:
        return self.read_both_registers(self.config.solar_register.value)
