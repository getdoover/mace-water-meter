from pathlib import Path

from pydoover import config
from pydoover.config import ApplicationPosition
from pydoover.docker.modbus import ModbusConfig


class MaceWaterMeterConfig(config.Schema):
    modbus_id = config.Integer("Modbus ID", description="Modbus ID for the meter")
    max_flow = config.Integer(
        "Max Flow", description="Max flow value for the meter", minimum=0
    )
    allow_shutdown = config.Boolean(
        "Allow Shutdown", description="Allow shutdown of the pump", default=True
    )

    flow_register = config.Integer(
        "Flow Register", description="Register for flow", default=7
    )
    total_register = config.Integer(
        "Total Register", description="Register for total", default=5
    )
    battery_register = config.Integer(
        "Battery Register", description="Register for battery voltage", default=9
    )
    solar_register = config.Integer(
        "Solar Register", description="Register for solar voltage", default=11
    )
    velocity_register = config.Integer(
        "Velocity Register", description="Register for velocity", default=None
    )
    depth_register = config.Integer(
        "Depth Register", description="Register for depth", default=None
    )
    stream_index_register = config.Integer(
        "Stream Index Register", description="Register for stream index", default=None
    )

    stay_online_seconds = config.Integer(
        "Stay Online Seconds",
        description="Time to stay online in seconds",
        default=120,
        hidden=True,
    )
    shutdown_sleep_seconds = config.Integer(
        "Shutdown Time",
        description="Time to stay shutdown in seconds",
        default=900,
        hidden=True,
    )

    modbus_config = ModbusConfig()
    position = ApplicationPosition()


def export():
    MaceWaterMeterConfig.export(
        Path(__file__).parents[2] / "doover_config.json",
        "mace_water_meter",
    )
