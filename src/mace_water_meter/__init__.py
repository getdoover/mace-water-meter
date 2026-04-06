from pydoover.docker import run_app

from .application import MaceWaterMeterApplication
from .app_config import MaceWaterMeterConfig

def main():
    """
    Run the application.
    """
    run_app(MaceWaterMeterApplication(config=MaceWaterMeterConfig()))
