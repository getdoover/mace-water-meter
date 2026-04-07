from pydoover import ui

from .app_config import MaceWaterMeterConfig
from .app_tags import MaceWaterMeterTags


class MaceWaterMeterUI(ui.UI):
    config: MaceWaterMeterConfig

    last_flow = ui.NumericVariable(
        "Flow (ML/day)",
        value=MaceWaterMeterTags.last_flow,
        form=ui.Widget.radial,
    )

    last_event_counter = ui.NumericVariable(
        "This Event (ML)",
        value=MaceWaterMeterTags.last_event_counter,
    )

    alert_counter = ui.FloatInput(
        "Alert Counter",
        min_val=0,
        help_str="Send a text notification when event total reaches this value (ML)",
    )

    shutdown_counter = ui.FloatInput(
        "Shutdown Counter",
        min_val=0,
        help_str="Stop pumping when event total reaches this value (ML)",
    )

    reset_event = ui.Button("Reset Event", requires_confirm=True)

    last_total = ui.NumericVariable(
        "Meter Total (ML)",
        value=MaceWaterMeterTags.last_total,
    )

    time_last_update = ui.Timestamp(
        "Time Since Last Read",
        value=MaceWaterMeterTags.time_last_update,
    )

    get_now = ui.Button("Get Now")

    maintenance = ui.Submodule(
        "Maintenance",
        children=[
            ui.NumericVariable(
                "Battery (V)",
                value=MaceWaterMeterTags.last_batt_volts,
                precision=1,
                ranges=[
                    ui.Range("Low", 11.5, 12.3, ui.Colour.yellow),
                    ui.Range("Good", 12.3, 13.0, ui.Colour.blue),
                    ui.Range("Charging", 13.0, 14.0, ui.Colour.green),
                    ui.Range("OverCharging", 14.0, 14.5, ui.Colour.red),
                ],
            ),
            ui.NumericVariable(
                "Solar (V)",
                value=MaceWaterMeterTags.last_solar_volts,
                precision=1,
                ranges=[
                    ui.Range("Low", 0, 14.0, ui.Colour.blue),
                    ui.Range("Charging", 14.0, 25, ui.Colour.green),
                ],
            ),
            ui.BooleanVariable(
                "Comms Active",
                value=MaceWaterMeterTags.comms_active,
            ),
        ],
        is_collapsed=True,
    )

    async def setup(self):
        max_flow = self.config.max_flow.value
        precision = 1 if max_flow >= 100 else 2

        self.last_flow.precision = precision
        self.last_flow.ranges = [
            ui.Range(None, 0, max_flow * 0.15, ui.Colour.blue),
            ui.Range(None, max_flow * 0.15, max_flow, ui.Colour.green),
        ]

        self.last_event_counter.precision = precision
        self.last_total.precision = precision

        if not self.config.allow_shutdown.value:
            self.shutdown_counter.hidden = True
