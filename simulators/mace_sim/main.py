"""
A module to simulate a Mace Agriflow water meter via Modbus TCP.
"""

import asyncio
import logging
import os
import random
import struct
import time

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartAsyncTcpServer

from transitions import Machine, State

log = logging.getLogger()

SLEEP_TIME = 120
INIT_TIME = 5


def add_noise(in_num, stdev: float):
    return in_num + ((random.random() - 0.5) * stdev)


def split_i32(value: int):
    high_16 = (value >> 16) & 0xFFFF
    low_16 = value & 0xFFFF
    return high_16, low_16


def split_f32(value: float):
    float_bytes = struct.pack(">f", value)
    float_int = struct.unpack(">I", float_bytes)[0]
    return split_i32(float_int)


class CustomSlaveContext(ModbusSlaveContext):
    def __init__(self, on_read_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_read_callback = on_read_callback

    def getValues(self, fx, address, count=1):
        self.on_read_callback()
        return super().getValues(fx, address, count)


class MaceAgriflowSim:
    states = [
        State(name="sleeping", on_enter=["save_current_state_enter_time"]),
        State(name="awake_init", on_enter=["save_current_state_enter_time"]),
        State(name="awake_rt", on_enter=["save_current_state_enter_time"]),
    ]

    transitions = [
        {"trigger": "awaken", "source": "sleeping", "dest": "awake_init"},
        {"trigger": "initialised", "source": "awake_init", "dest": "awake_rt"},
        {"trigger": "goto_sleep", "source": "awake_rt", "dest": "sleeping"},
    ]

    def __init__(
        self,
        device_id: int,
        host: str,
        port: int,
        velocity_register: int,
        depth_register: int,
        flow_rate_register: int,
        totals_register: int,
        battery_register: int,
        solar_register: int,
    ):
        self.device_id = device_id
        self.host = host
        self.port = port

        self.velocity_reg = velocity_register
        self.depth_reg = depth_register
        self.flow_rate_reg = flow_rate_register
        self.totals_reg = totals_register
        self.battery_reg = battery_register
        self.solar_reg = solar_register

        self.current_flow_vel = 3.5
        self.current_flow_depth = 1.2
        self.current_flow_megs = 160
        self.last_output_flow_megs = self.current_flow_megs
        self.current_battery_volts = 12.8
        self.current_solar_volts = 18.5

        self.last_totals_update_time = time.time()
        self.current_total = 73495  # kilolitres

        self.last_context_read = None
        self.context = None
        self.is_ready = asyncio.Event()

        self.setup_state_machine()

    def setup_state_machine(self):
        self.sm = Machine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial="sleeping",
        )

    def save_current_state_enter_time(self):
        self.current_state_enter_time = time.time()

    def get_time_in_state(self):
        return time.time() - self.current_state_enter_time

    def on_read_callback(self):
        self.last_context_read = time.time()

    async def start_modbus_server(self):
        """Start a TCP Modbus Server."""
        store = self.context = CustomSlaveContext(
            on_read_callback=self.on_read_callback,
            di=ModbusSequentialDataBlock(0x00, [17] * 100),
            co=ModbusSequentialDataBlock(0x00, [17] * 100),
            hr=ModbusSequentialDataBlock(0x00, [0] * 100),
            ir=ModbusSequentialDataBlock(0x00, [17] * 100),
        )

        context = ModbusServerContext(slaves=store, single=True)
        identity = ModbusDeviceIdentification(
            info_name={
                "VendorName": "Doover",
                "ProductCode": "MACESIM",
                "VendorUrl": "https://doover.com",
                "ProductName": "Mace Meter Simulator",
                "ModelName": "Mace Agriflow",
                "MajorMinorRevision": "1.0.0",
            }
        )

        self.is_ready.set()
        return await StartAsyncTcpServer(
            context=context,
            identity=identity,
            address=(self.host, self.port),
            framer="socket",
        )

    def set_register(self, reg: int, value: int):
        log.debug(f"Setting register {reg} to {value}")
        return self.context.setValues(0x04, reg, [int(value)])

    @staticmethod
    def megs_per_day_to_l_per_sec(in_val):
        return (in_val * 1000000) / (60 * 60 * 24)

    def update_totals(self):
        now = time.time()
        dt = now - self.last_totals_update_time
        curr_flow_l_sec = self.megs_per_day_to_l_per_sec(self.current_flow_megs)
        dv = curr_flow_l_sec * 1000 * dt  # kilolitres to add
        self.current_total = self.current_total + dv
        self.last_totals_update_time = now

    def split_and_set_f32(self, reg: int, value: float):
        high, low = split_f32(value)
        self.set_register(reg - 1, high)
        self.set_register(reg, low)

    def split_and_set_i32(self, reg: int, value: int):
        high, low = split_i32(value)
        self.set_register(reg - 1, high)
        self.set_register(reg, low)

    def generate_output_values(self, target_flow: int):
        self.update_totals()

        if self.state == "awake_rt":
            self.split_and_set_f32(
                self.velocity_reg, add_noise(self.current_flow_vel, 0.5)
            )
            self.split_and_set_f32(
                self.depth_reg, add_noise(self.current_flow_depth, 0.5)
            )
            self.split_and_set_f32(self.flow_rate_reg, add_noise(target_flow, 0.5))
            self.split_and_set_f32(self.totals_reg, self.current_total)
            self.split_and_set_f32(self.battery_reg, add_noise(self.current_battery_volts, 0.2))
            self.split_and_set_f32(self.solar_reg, add_noise(self.current_solar_volts, 1.0))
        else:
            for reg in (
                self.velocity_reg,
                self.depth_reg,
                self.flow_rate_reg,
                self.totals_reg,
                self.battery_reg,
                self.solar_reg,
            ):
                self.split_and_set_i32(reg, 0)

    async def main_loop(self):
        self.generate_output_values(self.current_flow_megs)
        log.info(f"{time.time()} - {self.state} - Flow={self.last_output_flow_megs}")

        match self.state:
            case "awake_rt":
                if self.last_context_read is not None:
                    self.last_context_read = None
                    self.save_current_state_enter_time()

                if self.get_time_in_state() > SLEEP_TIME:
                    self.goto_sleep()
                    self.last_context_read = None

            case "awake_init":
                if self.get_time_in_state() > INIT_TIME:
                    self.initialised()

            case "sleeping":
                if self.last_context_read is not None:
                    self.last_context_read = None
                    self.awaken()

    async def run(self):
        errors = 0
        log.info("Starting...")
        t = asyncio.create_task(self.start_modbus_server())

        while True:
            if t.done():
                raise RuntimeError("Modbus server failed.")

            await self.is_ready.wait()
            try:
                await self.main_loop()
                errors = 0
            except Exception as e:
                errors += 1
                if errors > 5:
                    log.error("Too many errors, exiting.")
                    break

                log.error(f"Error in main loop: {e}. Sleeping and retrying...")
                await asyncio.sleep(5)
            else:
                await asyncio.sleep(1)


if __name__ == "__main__":
    sim = MaceAgriflowSim(
        int(os.environ.get("DEVICE_ID", 1)),
        os.environ.get("MODBUS_HOST", "127.0.0.1"),
        int(os.environ.get("MODBUS_PORT", 5020)),
        int(os.environ.get("VELOCITY_REGISTER", 1)),
        int(os.environ.get("DEPTH_REGISTER", 2)),
        int(os.environ.get("FLOW_RATE_REGISTER", 7)),
        int(os.environ.get("TOTALS_REGISTER", 5)),
        int(os.environ.get("BATTERY_REGISTER", 9)),
        int(os.environ.get("SOLAR_REGISTER", 11)),
    )
    logging.basicConfig(
        level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO
    )
    asyncio.run(sim.run())
