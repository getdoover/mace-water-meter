"""
Basic tests for the application.

This ensures all modules are importable and that the config is valid.
"""


def test_import_app():
    from mace_water_meter.application import MaceWaterMeterApplication

    assert MaceWaterMeterApplication


def test_config():
    from mace_water_meter.app_config import MaceWaterMeterConfig

    assert isinstance(MaceWaterMeterConfig.to_schema(), dict)


def test_ui():
    from mace_water_meter.app_ui import MaceWaterMeterUI

    assert MaceWaterMeterUI


def test_tags():
    from mace_water_meter.app_tags import MaceWaterMeterTags

    assert MaceWaterMeterTags


def test_state():
    from mace_water_meter.app_state import MaceWaterMeterState

    assert MaceWaterMeterState


def test_record():
    from mace_water_meter.record import Record

    assert Record
