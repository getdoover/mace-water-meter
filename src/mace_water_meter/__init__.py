from pydoover.docker import run_app

from .application import MaceWaterMeterApplication


def main():
    """
    Run the Mace Water Meter application.
    """
    run_app(MaceWaterMeterApplication())
